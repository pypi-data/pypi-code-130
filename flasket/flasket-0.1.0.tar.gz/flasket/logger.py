# pylint: disable=unused-private-member
import logging
import sys

from flask.logging import default_handler


class Logger:
    @staticmethod
    def configure(app: object) -> None:
        """
        Re-configure the loggers.

        Parameters
        ----------
        app: object
            a flasket Application
        """
        app.__logger_first_request = False

        # Set default logging to a simple timestamp and message
        # default_handler is StreamHandler(stream=sys.stderr)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        default_handler.setStream(sys.stderr)
        default_handler.setLevel(logging.INFO)
        default_handler.setFormatter(formatter)

        # stderr
        logger = logging.getLogger("stderr")
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # request
        formatter = logging.Formatter("[%(asctime)s] - %(message)s")
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)
        logger = logging.getLogger("request")
        logger.addHandler(handler)

    @staticmethod
    def before_request(app: object) -> None:
        """
        Runs only once to remove extra-loggers.

        Parameters
        ----------
        app: object
            a flasket Application
        """
        if app.__logger_first_request:
            return
        app.__logger_first_request = True

        # Remove the FileHandlers from the logger
        for name in ["gunicorn.error", "gunicorn.access"]:
            logger = logging.getLogger(name)
            for handler in logger.handlers:
                if handler._gunicorn:
                    logger.removeHandler(handler)

        # Delete the werkzeug logger
        logger = logging.getLogger("werkzeug")
        for handler in logger.handlers:
            logger.removeHandler(handler)

    @staticmethod
    def log_request(app: object, response: object) -> None:
        """
        Log the request on the request logger.

        Parameters
        ----------
        app: object
            a flasket Application

        response: object
            a flask response
        """
        url = app.request.path
        if app.request.args:
            url = app.request.full_path
        header = app.request.headers.get("User-Agent", "")
        message = f'{app.request_addr} - "{app.request.method} {url}" {response.status_code} - {header}'

        logger = logging.getLogger("request")
        logger.warning(message)
