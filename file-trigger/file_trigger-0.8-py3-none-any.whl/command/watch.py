import logging
from time import sleep
from threading import Event

from watchdog.observers import Observer  # type: ignore

from ..adapter.event_handler import EventHandler
from ..adapter.executor import CommandExecutor
from ..model.config import Config


def run(*, config: Config, args, timestamp: float, stop: Event):
    logger = logging.getLogger(__name__)

    executor = CommandExecutor(notify_logger=config.notify_logger)
    handler = EventHandler(config=config, executor=executor)
    observer = Observer()

    logger.debug(f"Watch scheduling on root dir: {config.root_dir}")
    observer.schedule(handler, config.root_dir, recursive=config.recursive)
    logger.info(f"Watch scheduled on root dir: {config.root_dir}")

    logger.debug("Watch starting")
    observer.start()
    try:
        main_loop(observer, stop)

    except Exception as e:
        """
        Note: observer-thread errors are not propagated, so not sure this
        is actually needed or is ever called.
        """
        logger.exception(e)
        raise e

    finally:
        executor.shutdown()
        logger.debug("Watch stopping")
        observer.join()
        logger.info("Watch stopped.")


def main_loop(observer: Observer, stop: Event):
    try:
        while not stop.is_set():
            sleep(1)
    except KeyboardInterrupt:
        stop.set()
    finally:
        if stop.is_set():
            observer.stop()
