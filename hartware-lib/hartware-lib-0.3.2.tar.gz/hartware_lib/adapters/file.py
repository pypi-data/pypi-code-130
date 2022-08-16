from pathlib import Path
from typing import Any

from hartware_lib.utils import filesystem


class FileAdapter:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def create_parent_dir(self) -> None:
        filesystem.create_dir(self.file_path.parent)

    def delete_parent_dir(self) -> None:
        filesystem.delete_dir(self.file_path.parent)

    def delete(self) -> None:
        filesystem.delete_file(self.file_path)

    def exists(self) -> bool:
        return filesystem.exists(self.file_path)

    def read(self) -> str:
        return filesystem.read_file(self.file_path)

    def save(self, data: str = "") -> None:
        filesystem.write_file(self.file_path, data)

    def read_json(self, **kwargs: Any) -> dict:
        return filesystem.read_json_file(self.file_path, **kwargs)

    def save_json(self, data: dict, **kwargs: Any) -> None:
        filesystem.write_json_file(self.file_path, data, **kwargs)

    async def async_read(self) -> str:
        return await filesystem.async_read_file(self.file_path)

    async def async_save(self, data: str = "") -> None:
        await filesystem.async_write_file(self.file_path, data)

    async def async_read_json(self, **kwargs: Any) -> dict:
        return await filesystem.async_read_json_file(self.file_path, **kwargs)

    async def async_save_json(self, data: dict, **kwargs: Any) -> None:
        await filesystem.async_write_json_file(self.file_path, data, **kwargs)
