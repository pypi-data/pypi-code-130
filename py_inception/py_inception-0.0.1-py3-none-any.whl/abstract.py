from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from . import maze

class AExporter(ABC):
    maze: maze.Maze
    def __init__(self, maze):
        self.maze = maze
    
    @abstractmethod
    def export(self, name: str):
        pass

from . import extractor

class AArchitect(ABC):
    e: extractor.Extractor | None
    next: AArchitect | None
    
    def __init__(self):
        self.e = None
        self.next = None

    def set_next(self, arch: AArchitect):
        self.next = arch

    def set_extractor(self, e):
        self.e = e

    def reset(self):
        pass

    @abstractmethod
    def parse(self, var: Any, parse_as: str = "object", *, metadata: dict | None = None):
        pass
