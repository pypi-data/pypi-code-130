"""
Flasket Gunicorn middleware and cli helper.
"""
import logging
import multiprocessing

from typing import Dict

from attr import attrs, attrib

from flask.logging import default_handler
from gunicorn.app.base import BaseApplication
from torxtools.pathtools import expandpath


from . import BaseCmdline, BaseFlasketCLI
from ..application import Application


class GunicornApplication(BaseApplication):
    # pylint: disable=abstract-method
    # http://docs.gunicorn.org/en/stable/custom.html
    def __init__(self: object, *args, cfg: Dict, rootpath: str = None, **kwargs) -> None:
        """
        Initialize a Flasket application, and configure Gunicorn

        Parameters
        ----------
        cfg: dict
            dictionary containing configuration for the application

        rootpath: str
            location from where to load packages
        """
        self._application = Application(*args, cfg=cfg, rootpath=rootpath, **kwargs)

        # Rework the configuration
        cfg = self._application.config["server"]
        if cfg["workers"] <= 0:
            # Do not overload the host with default value of 0:
            # if it's a container, it could report host cpus
            cpus = max((multiprocessing.cpu_count() * 2), 1)
            if cfg["workers"] == 0:
                cfg["workers"] = min(cpus, 8)
            else:
                cfg["workers"] = cpus

        self.options = {
            "bind": "%s:%s" % (cfg["listen"], cfg["port"]),
            "pidfile": expandpath(cfg.get("pidfile")),
            "workers": cfg["workers"],
            "accesslog": "/dev/null",
            "errorlog": "/dev/null",
        }

        self._application.logger.info(f"Starting {cfg['workers']} workers...")
        super().__init__()

        # Use the Flask logger to log identically between flask and gunicorn
        # We have to specify a null FileStream handler, we'll remove it on first call
        # by using the _gunicorn identifier
        logger = logging.getLogger("gunicorn.error")
        default_handler._gunicorn = False
        logger.addHandler(default_handler)

    def load_config(self: object) -> None:
        """
        Load Gunicorn configuration ourselves.

        Parameters
        ----------
        parser: object
            an argparse.ArgumentParser
        """
        # Pass the configuration down to gunicorn.app.base.BaseApplication
        cfg = {k: v for k, v in self.options.items() if k in self.cfg.settings and v is not None}
        for k, v in cfg.items():
            self.cfg.set(k.lower(), v)

    def load(self: object) -> None:
        """
        Return our application instance.
        """
        return self._application


class FlasketCmdline(BaseCmdline):
    def add_arguments(self: object, parser: object) -> object:
        """
        Add Gunicorn middleware specific arguments.

        Parameters
        ----------
        parser: object
            an argparse.ArgumentParser

        Returns
        -------
        object:
            an argparse.ArgumentParser
        """
        defaults = self._default_cfg

        workers = defaults["server"]["workers"]
        pidfile = defaults["server"]["pidfile"]
        if pidfile is None:
            pidfile = "none"

        # fmt: off
        parser.add_argument("-w", "--workers", metavar="WORKERS", type=int,
            help=f"Number of thread workers. (default: {workers}. If 0, cpu to use is (cpu_count * 2) with a maximum of 8; if negative, cpu to use is (cpu_count * 2) with no maximum.)")
        parser.add_argument("--pidfile", metavar="FILE", type=str,
            help=f"A filename to use for the PID file. (default: {pidfile})")
        # fmt: on
        return parser


@attrs(kw_only=True)
class FlasketCLI(BaseFlasketCLI):
    # fmt: off
    _cmdline_cfg = attrib(default=FlasketCmdline)
    _forced_cfg = attrib(default={"server": {"debug": False, "production": True, "gunicorn": True,}}, init=False)
    # fmt: on

    def _run(self: object, *args, cfg: Dict, rootpath: str = None, **kwargs) -> None:
        """
        (abstract method)
        Run the middleware

        Parameters
        ----------
        cfg: dict
            dictionary containing configuration for the application

        rootpath: str
            location from where to load packages
        """
        GunicornApplication(*args, cfg=cfg, rootpath=rootpath, **kwargs).run()
