from __future__ import annotations

from typing import Any


class DependencyContainer:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename: str = self._parse_basename()
        self.imports: list[Any] = []

    def _parse_basename(self) -> str:
        return self.filepath.replace("/", ".").replace("\\", ".")

    def add_import(
        self,
        imports: list[Any],
    ) -> None:
        self.imports = imports
