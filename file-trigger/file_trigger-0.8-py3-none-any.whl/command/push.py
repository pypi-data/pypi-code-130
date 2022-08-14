import logging
import os.path
from typing import Optional, List

import guilogger

from ..adapter.event_handler import EventHandler
from ..adapter.executor import CommandExecutor
from ..model.config import Config
from ..util.watchdog import event_from_type_and_file_names


def run(*, config: Config, args, timestamp: float, stop):
    if args.gui:
        _gui_run(config, timestamp, args)
    else:
        _run(config, timestamp, args)


def _run(
    config: Config,
    timestamp: float,
    args,
    log_handler: Optional[logging.Handler] = None,
):
    root_logger = logging.getLogger()
    if log_handler is not None:
        root_logger.addHandler(log_handler)

    logger = logging.getLogger(__name__)
    executor = CommandExecutor(notify_logger=config.notify_logger)
    handler = EventHandler(config=config, executor=executor)

    file = args.file
    if not os.path.isabs(file):
        file = os.path.abspath(file)
    u_file = unaliased_file(file, config.root_dir, config.root_dir_aliases)
    if not file == u_file:
        logger.info(f"Note: detected aliased file {file}, processing as {u_file}")

    event = event_from_type_and_file_names(args.event, u_file)
    handler.dispatch(event)

    executor.shutdown()
    if hasattr(logger, "done"):
        logger.done()


_gui_run = guilogger.app(
    level=logging.INFO, title="file-trigger", max_steps=10, close_after=True
)(_run)


def unaliased_file(file: str, root_dir: str, aliases: List[str]) -> str:
    file_lc = file.lower()
    try:
        return next(
            root_dir + file.replace(alias, "", 1)
            for alias in aliases
            if file_lc.startswith(alias.lower())
        )
    except StopIteration:
        return file
