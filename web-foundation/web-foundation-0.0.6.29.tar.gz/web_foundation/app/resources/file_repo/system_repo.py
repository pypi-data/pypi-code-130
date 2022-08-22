import os.path
from enum import Enum
from pathlib import Path
from typing import Type, Any, List

from aiofiles import open
from aiofiles.base import AiofilesContextManager

from web_foundation.app.errors.io.files import SectionNotFound, FileNotExist, NothingToWrite, OsIOError
from web_foundation.app.resources.file_repo.repo import FileRepository, AppFileSections


class SystemFileRepository(FileRepository):
    _root: Path

    def __init__(self, root: Path, sections: Type[Enum] = AppFileSections):
        super(SystemFileRepository, self).__init__(sections)
        self._root = root
        self._sections = sections
        self._create_sections()

    def _create_sections(self):
        for section in self._sections:
            folder = os.path.join(self._root, str(section.value))
            if not self._check_exist(folder, raises=False):
                os.mkdir(folder)

    def _check_exist(self, path: str, raises: bool = True) -> bool:
        exist = os.path.exists(path)
        if not exist and raises:
            raise FileNotExist(message=f"File not exists in path {path}")
        return exist

    def _check_full_path(self, filename: str, section: Enum, raises: bool = True):
        if section not in self._sections:
            raise SectionNotFound(message=f"Not found {section} in {self._sections}")
        full_path = os.path.join(self._root, str(section.value), filename)
        self._check_exist(full_path, raises=raises)
        return full_path

    # overload
    async def _open_section(self, section: Enum) -> List[str]:
        path = os.path.join(self._root, str(section.value))
        self._check_exist(path)
        return os.listdir(path)

    # overload
    async def get_file_fullpath(self, filename: str, section: Enum) -> str:
        return self._check_full_path(filename, section, raises=False)

    # overload
    async def stash(self, filename: str, section: Enum, data: Any, raises: bool = True, **kwargs) -> None:
        full_path = self._check_full_path(filename, section, raises=raises)
        if not data:
            raise NothingToWrite(message="No data to write")
        try:
            async with open(full_path, **kwargs) as target_file:
                await target_file.write(data)
        except Exception as e:
            raise OsIOError(message="Can't write to file", ex=e)

    # overload
    async def take(self, filename: str, section: Enum, raises: bool = True,
                   **kwargs) -> AiofilesContextManager:
        full_path = self._check_full_path(filename, section, raises=raises)
        try:
            return open(full_path, **kwargs)
        except Exception as e:
            raise OsIOError(message="Can't open file", ex=e)
