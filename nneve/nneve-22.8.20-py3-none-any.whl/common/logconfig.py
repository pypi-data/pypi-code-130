import datetime
import logging
from contextlib import suppress
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

CWD = Path(".").resolve()
LOG_DIR = CWD / "log"
LOG_DIR.mkdir(0o777, True, True)
LOG_FILE_PATH = str(
    LOG_DIR / datetime.datetime.now().strftime("GRC_%y_%m_%d_%H_%M_%S.log")
)


class MarkupStripFormatter(logging.Formatter):
    def format(self, *args: Any, **kwargs: Any) -> str:  # noqa: A003
        s = super().format(*args, **kwargs)
        # render strings with rich
        seg_list = Text.from_markup(s).render(Console())
        # but use only text part to get rid of all formatting
        return "".join(seg.text for seg in seg_list)


def configure_logger(
    is_debug: bool = False,
    is_verbose: bool = False,
) -> None:
    if is_debug:
        log_level = logging.DEBUG
    elif is_verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    stream_handler = RichHandler(
        rich_tracebacks=True, markup=True, omit_repeated_times=False
    )
    root_logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(
        LOG_FILE_PATH, mode="w", encoding="utf-8"
    )

    file_handler.setFormatter(
        MarkupStripFormatter(
            fmt="%(asctime)s [%(levelname)-5.5s]  %(message)s",  # "[%(asctime)s - %(levelname)s]  %(message)s",
            datefmt="%y.%m.%d %H:%M:%S",
        )
    )
    root_logger.addHandler(file_handler)

    if is_debug:
        logging.debug("Configured logger to debug mode.")
    elif is_verbose:
        logging.info("Configured logger to verbose mode.")
    else:
        logging.warning("Configured logger to warning mode.")

    # disable warnings for requests like libraries using urllib3
    with suppress(ImportError):
        import urllib3

        urllib3.disable_warnings()
