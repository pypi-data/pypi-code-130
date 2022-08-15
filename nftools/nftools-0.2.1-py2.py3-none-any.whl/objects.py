import logging
from subprocess import CompletedProcess


class ExtendedCompletedProcess(CompletedProcess):

    def __init__(self, obj):
        super().__init__(obj.args, obj.returncode, obj.stdout, obj.stderr)
        self.stdout = self.clean(self.stdout)
        self.stderr = self.clean(self.stderr)

    @staticmethod
    def clean(b: bytes):
        return b.decode('utf-8').strip()


class ColorFormatter(logging.Formatter):
    """Formatter for coloring log messages with ASCII escape codes"""
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    cyan = '\x1B[36m'
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: bold_red + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class ColorHandler(logging.StreamHandler):

    def __init__(self, level=logging.DEBUG, formatter=ColorFormatter()):
        super().__init__()
        self.setLevel(level)
        self.setFormatter(formatter)
