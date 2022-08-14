from dataclasses import dataclass
import json
from typing import Any, Optional, List, Set, Dict

from ..model.command import Command


@dataclass
class HandlerConfig:
    name: str
    template: str
    events: Optional[Set[str]]
    commands: List[Command]

    def __str__(self) -> str:
        events_str = (
            "None"
            if self.events is None
            else f"{{ {', '.join([e for e in self.events])} }}"
        )
        return "\n".join(
            [
                f"{self.name}:",
                "-" * (len(self.name) + 1),
                f"  template = {self.template}",
                f"  events = {events_str}",
                "",
                f"{self.name} Commands:",
                "-" * (len(self.name) + 10),
            ]
            + [str(c) + "\n" for c in self.commands]
        )


@dataclass
class Config:
    root_dir: str
    recursive: bool
    patterns: Optional[List[str]]
    ignore_patterns: Optional[List[str]]
    ignore_directories: bool
    root_dir_aliases: List[str]
    notify_logger: Optional[str]
    handlers: List[HandlerConfig]
    logging: Dict[str, Any]

    def __str__(self) -> str:
        str_patterns = (
            "None" if self.patterns is None else "[" + ", ".join(self.patterns) + "]"
        )
        str_ignore_patterns = (
            "None"
            if self.ignore_patterns is None
            else "[" + ", ".join(self.ignore_patterns) + "]"
        )
        str_notify_logger = "None" if self.notify_logger is None else self.notify_logger
        return "\n".join(
            [
                "Configuration:",
                "==============",
                f"  root_dir = {self.root_dir}",
                f"  recursive = {self.recursive}",
                f"  ignore_directories = {self.ignore_directories}",
                f"  patterns = {str_patterns}",
                f"  ignore_patterns = {str_ignore_patterns}",
                f"  root_dir_aliases = [{', '.join(self.root_dir_aliases)}]",
                f"  notify_logger = {str_notify_logger}",
                "",
                "Handlers:",
                "=========",
            ]
            + [str(h) for h in self.handlers]
            + [
                "",
                "Logging:",
                "========",
                json.dumps(self.logging, indent=2),
            ]
        )
