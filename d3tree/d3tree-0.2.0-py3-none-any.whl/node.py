import reprlib
import sys
from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class Node(list):
    name: str
    children: Union["Node", List] = field(default_factory=lambda: [])

    def insert_node(self, path: List[str]) -> None:
        if not path:
            return

        child_name: str = path[0]
        grandchildren: List[str] = path[1:]

        for child in self.children:
            if child.name == child_name:
                break
        else:
            child = Node(name=child_name)
            self.children.append(child)

        child.insert_node(path=grandchildren)

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        reprlib.aRepr.maxlevel = sys.getrecursionlimit()
        return f"""{{"name":"{self.name}","children":[{','.join(map(repr, self.children))}]}}"""
