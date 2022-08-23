"""
Flasket Flask middleware and cli helper.
"""

import argparse

from typing import Dict

from attr import attrs, attrib

from . import BaseCmdline, BaseFlasketCLI
from ..application import Application


class FlasketCmdline(BaseCmdline):
    def add_arguments(self: object, parser: object) -> object:
        """
        Add Flask middleware specific arguments.

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
        debug = {True: "enabled", False: "disabled"}[defaults["server"]["debug"]]

        # fmt: off
        parser.add_argument("--debug", action="store_true", default=None,
            help=f"Enable debug mode. Disable with --no-debug. (default: {debug})")
        parser.add_argument("--no-debug", action="store_false", default=None, dest="debug",
            help=argparse.SUPPRESS)
        # fmt: on
        return parser


@attrs(kw_only=True)
class FlasketCLI(BaseFlasketCLI):
    # fmt: off
    _cmdline_cfg = attrib(default=FlasketCmdline)
    _forced_cfg = attrib(default={"server": {"production": False, "flask": True,}}, init=False)
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
        app = Application(*args, cfg=cfg, rootpath=rootpath, **kwargs)
        app.app.run(host=app.host, port=app.port, debug=app.debug, use_reloader=False)
