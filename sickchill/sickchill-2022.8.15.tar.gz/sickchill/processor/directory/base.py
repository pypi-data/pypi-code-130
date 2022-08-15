from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import Optional

from guessit import guessit

from sickchill import logger, settings

try:
    import watchdog
    import watchdog.events
    from watchdog.events import FileSystemEventHandler, LoggingEventHandler
    from watchdog.observers import Observer

    class MyEventHandler(FileSystemEventHandler):
        def catch_all_handler(self, event):
            logger.debug(event)

        def on_moved(self, event):
            self.catch_all_handler(event)

        def on_created(self, event):
            self.catch_all_handler(event)

        def on_deleted(self, event):
            self.catch_all_handler(event)

        def on_modified(self, event):
            self.catch_all_handler(event)

except (ModuleNotFoundError, ImportError):
    watchdog = None

    class MyEventHandler:
        pass


# DirectoryProcessor("Movie Processor", Path("completed/movie/downloads"), media_type="movie", method="move")
# DirectoryProcessor("TV Processor", Path("completed/tv/downloads"), media_type="tv", method="hardlink")
# DirectoryProcessor({"Link Processor", Path("location/of/links"), media_type="links", method="snatch"})
class DirectoryProcessor(object):
    TV = 1
    MOVIE = 2
    MUSIC = 3
    EBOOK = 4
    ANIME = 5

    DEFAULT_OPTIONS = {
        "name": "Directory Processor",
        "path": Path(settings.TV_DOWNLOAD_DIR) if settings.TV_DOWNLOAD_DIR else Path(),
        "method": settings.PROCESS_METHOD,
        "media_type": "tv",
    }

    def __init__(self, options: Optional[dict] = DEFAULT_OPTIONS):
        self.options = deepcopy(self.DEFAULT_OPTIONS)
        self.options.update(options)

        if watchdog:
            self.observer = Observer()
        else:
            self.observer = None

    def shutdown(self):
        self.observer.stop()
        self.observer.join()

    def __setitem__(self, key, value):
        self.options[key] = value

    def update(self, options):
        self.options.update(options)

    def auto(self):
        pass

    def process(self):
        pass

    def process_one(self, location: PathLike):
        guess = guessit(location)
        if guess.get("type") == "episode":
            pass

    def watchdog(self):
        if not watchdog:
            return

        self.observer.schedule(MyEventHandler(), self.options["path"], recursive=False)  # Only watch the root of the download directory!
        self.observer.start()
