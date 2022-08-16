from pathlib import Path
from typing import Any, List

from hartware_lib.utils import filesystem


class DirectoryAdapter:
    def __init__(self, dir_path: Path):
        self.dir_path = dir_path

    def create_dir(self) -> None:
        filesystem.create_dir(self.dir_path)

    def delete_dir(self) -> None:
        filesystem.delete_dir(self.dir_path)

    def delete_file(self, filename: str) -> None:
        filesystem.delete_file(self.dir_path / filename)

    def search(self, filename_regex: str = "*") -> List[Path]:
        return filesystem.search_files(self.dir_path / "**" / filename_regex)

    def dir_exists(self) -> bool:
        return filesystem.exists(self.dir_path)

    def file_exists(self, filename: str) -> bool:
        return filesystem.exists(self.dir_path / filename)

    def read_file(self, filename: str) -> str:
        return filesystem.read_file(self.dir_path / filename)

    def save_file(self, filename: str, data: str = "") -> None:
        filesystem.write_file(self.dir_path / filename, data)

    def read_json_file(self, filename: str, **kwargs: Any) -> dict:
        return filesystem.read_json_file(self.dir_path / filename, **kwargs)

    def save_json_file(self, filename: str, data: dict, **kwargs: Any) -> None:
        filesystem.write_json_file(self.dir_path / filename, data, **kwargs)

    async def async_read_file(self, filename: str) -> str:
        return await filesystem.async_read_file(self.dir_path / filename)

    async def async_save_file(self, filename: str, data: str = "") -> None:
        await filesystem.async_write_file(self.dir_path / filename, data)

    async def async_read_json_file(self, filename: str, **kwargs: Any) -> dict:
        return await filesystem.async_read_json_file(self.dir_path / filename, **kwargs)

    async def async_save_json_file(
        self, filename: str, data: dict, **kwargs: Any
    ) -> None:
        await filesystem.async_write_json_file(self.dir_path / filename, data, **kwargs)
