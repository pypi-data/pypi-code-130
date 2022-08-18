# aclint: py3
import logging
import re
from rich.text import Text
from rich._log_render import LogRender
from rich.logging import RichHandler
from rich.traceback import Traceback
from types import TracebackType
from typing import Dict, Type, Optional
import sys

DATETIME_FORMAT = "%Y-%m-%d_%Hh%Mm%Ss"


class RedactingFilter(logging.Filter):
    redactions: Dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self.redactions = {}

    # Remove sensitive information from URLs
    def _filter(self, s: str) -> str:
        s = re.sub(r":\/\/(.*?)\@", r"://<USERNAME>:<PASSWORD>@", s)
        for needle, replace in self.redactions.items():
            s = s.replace(needle, replace)
        return s

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._filter(record.msg)
        return True

    # Redact specific strings; e.g., authorization tokens.  This won't
    # retroactively redact stuff you've already leaked, so make sure
    # you redact things as soon as possible
    def redact(self, needle: str, replace: str = "<REDACTED>") -> None:
        # Don't redact empty strings; this will lead to something
        # that looks like s<REDACTED>t<REDACTED>r<REDACTED>...
        if needle == "":
            return
        self.redactions[needle] = replace


class RevupRichHandler(RichHandler):
    def get_level_text(self, record: logging.LogRecord) -> Text:
        self._log_render.show_level = True

        if record.levelname == "WARNING":
            return Text.styled("W:", style="bold yellow")

        if record.levelname == "ERROR":
            return Text.styled("E:", style="bold red")

        self._log_render.show_level = False
        return Text()

    def set_render(self, log_render: LogRender) -> None:
        self._log_render = log_render


def configure_logger(debug: bool, redactions: Dict[str, str]) -> None:
    log_filter = RedactingFilter()
    for k, v in redactions.items():
        log_filter.redact(k, v)
    handler = RevupRichHandler()
    handler.addFilter(log_filter)
    handler.set_render(
        LogRender(
            show_time=False,
            show_level=True,
            show_path=False,
            level_width=1,
        )
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    def excepthook(
        type_: Type[BaseException],
        value: BaseException,
        traceback: Optional[TracebackType],
    ) -> None:
        logging.info(
            str(
                Traceback.from_exception(
                    type_,
                    value,
                    traceback,
                    show_locals=True,
                ).__rich_console__()
            )
        )

    sys.excepthook = excepthook
