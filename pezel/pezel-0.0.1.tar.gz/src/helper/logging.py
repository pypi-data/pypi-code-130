import logging
import logging.config
import traceback


class CriticalException(Exception):
    def __init__(self, user_msg, dev_msg=None, stack_trace=None):
        self.user_msg = user_msg
        self.dev_msg = dev_msg
        self.stack_trace = traceback.format_stack()[:-1] if stack_trace is None else stack_trace
        self.failed_build_node = None
        self.failed_execution_node = None
        self.failed_execution_image = None
        self.failed_execution_container = None

    @classmethod
    def build_from_exception(cls, err):
        return cls(str(err), stack_trace=traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__))

    def log(self, user_log, dev_log):
        if self.failed_build_node is not None:
            user_log.error(f'Failure while building {self.failed_build_node.str()}')

        if self.failed_execution_node is not None:
            docker_str = f' using docker image {self.failed_execution_image}' if self.failed_execution_image else ''
            container_str = f' using on container {self.failed_execution_container}' if self.failed_execution_container else ''
            user_log.error(f'Failure while executing {self.failed_execution_node.str()}{docker_str}{container_str}')

        user_log.error(self.user_msg)

        if self.dev_msg is not None:
            dev_log.error(self.dev_msg)

        dev_log.error(f'Stack Trace:\n{"".join(self.stack_trace)}')

    def set_failed_build_node(self, node):
        self.failed_build_node = self.failed_build_node if self.failed_build_node else node

    def set_failed_execution_node(self, node):
        self.failed_execution_node = self.failed_execution_node if self.failed_execution_node else node

    def set_failed_execution_docker(self, image, container=None):
        self.failed_execution_image = self.failed_execution_image if self.failed_execution_image else image
        self.failed_execution_container = self.failed_execution_container if self.failed_execution_container else container


class LogFormatter(logging.Formatter):
    def __init__(self, *args, formats=None, **kwargs):
        if formats is None:
            formats = {}

        super().__init__(*args, **kwargs)
        self.formats = formats

    def format(self, record):
        format_orig = self._style._fmt

        if record.levelno in self.formats:
            self._style._fmt = self.formats[record.levelno]
        result = logging.Formatter.format(self, record)

        self._style._fmt = format_orig

        return result


def build_logger(name, formatter, level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


dev_log_root = build_logger(
    'pezel_app',
    LogFormatter(fmt='%(name)s - %(levelname)s: %(message)s '),
    level=logging.CRITICAL + 1)
user_log_root = build_logger(
    'user',
    LogFormatter(fmt='%(message)s', formats={logging.ERROR: 'ERROR: %(message)s'}))
