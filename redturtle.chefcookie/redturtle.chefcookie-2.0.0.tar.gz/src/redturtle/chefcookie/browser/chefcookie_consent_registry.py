from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
import json
import logging
import logging.handlers
import time
import zc.lockfile
import os

cclogger = logging.getLogger("chefcookie_logger")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


class LogInfo(object):
    """
    This approach is taken from collective.fingerpointing
    """

    def __init__(self):
        self.logger = logging.getLogger("redturtle.chefcookie")
        self.logfile = None
        self.handler = None
        self.configure()

    def configure(self):
        config = {
            "file-log": "{}{}".format(
                os.environ.get("CLIENT_HOME"),
                "/../log/redturtle.chefcookie.log",
            ),
            "file-log-max-size": 20971520,
            "file-log-old-files": 365,
        }
        self.logfile = config.get("file-log", None)

        self.logger.setLevel(logging.INFO)

        # first remove old handler if set:
        if self.handler is not None:
            self.logger.removeHandler(self.handler)

        # if either of maxBytes or backupCount is zero, rollover never occurs
        maxBytes = int(config.get("file-log-max-size", 20971520))
        backupCount = int(config.get("file-log-old-files", 365))
        self.handler = logging.handlers.RotatingFileHandler(
            self.logfile,
            maxBytes=maxBytes,
            backupCount=backupCount,
            delay=True,  # defer file creation to first emit
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        cclogger.info("Logging information to " + self.logfile)

    def __call__(self, *args, **kwargs):
        """Log information to a file handling access from multiple instances.
        This code was taken from ZEO/ClientStorage.py.
        """

        # otherwise, try to lock the self.logfile then writing to it
        lockfilename = self.logfile + ".lock"
        n = 0

        while 1:
            try:
                # A content_template with hostname makes the implementation
                # container save, where each process in the different
                # containers is likely to have the same PID.
                # https://pypi.python.org/pypi/zc.lockfile#hostname-in-lock-file
                lock = zc.lockfile.LockFile(
                    lockfilename,
                    content_template="{pid};{hostname}",
                )
                try:
                    self.logger.info(*args, **kwargs)
                finally:
                    # even if logging fails: release the lock.
                    lock.close()
            except zc.lockfile.LockError:
                time.sleep(0.01)
                n += 1
                if n > 60000:
                    raise
            else:
                break


log_info = LogInfo()


class ConsentTracking(BrowserView):
    """ """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        body = self.request.get("BODY", None)
        if not body:
            self.request.response.setStatus(500)
            return dict(
                error=dict(
                    type="InternalServerError",
                    message="Not able to set information",
                )
            )
        else:
            try:
                body = json.loads(body)
                log_info(
                    "Client date: {date}; Action: {action}; Url: {url}; Viewport: {viewport}; Providers: {providers}".format(
                        **body
                    )
                )
                self.request.response.setStatus(204)
                return object()
            except Exception:
                pass
        return dict(
            error=dict(
                type="InternalServerError",
                message="Not able to set information",
            )
        )
