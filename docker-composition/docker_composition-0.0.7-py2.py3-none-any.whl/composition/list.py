import logging
import time
import humanize

from composition.applications import Context, Application


def setup_column_logging():
    root = logging.getLogger()
    hdlr = root.handlers[0]
    fmt = logging.Formatter('%(app_name)-15s %(version)-10s %(compose_name)-20s %(time)-10s')
    hdlr.setFormatter(fmt)


def setup_default_logging_format():
    root = logging.getLogger()
    hdlr = root.handlers[0]
    fmt = logging.Formatter('%(message)s')
    hdlr.setFormatter(fmt)


def list_applications():
    setup_column_logging()
    time.sleep(1)
    # Print the headings
    logging.info("", extra={
        "app_name": "APP NAME",
        "version": "VERSION",
        "compose_name": "COMPOSE NAME",
        "time": "UPTIME"}
    )
    # Print the installed applications
    for app in Context.applications:  # type: Application
        time_delta = time.time() - app.start_timestamp
        # Utilise logging to set reasonable columns
        logging.info("", extra={"app_name": app.name, "version": app.version, "compose_name": app.compose_name, "time": humanize.naturaldelta(time_delta)})
    setup_default_logging_format()
