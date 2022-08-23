"""
Handle everything command line when starting server from one of the
provided Python helper scripts
"""
import argparse
import os
import sys
import traceback

from typing import Dict, List, Optional

from attr import attrs, attrib
from yaml import safe_load

from boltons.iterutils import remap
from torxtools import xdgtools
from torxtools.cfgtools import which
from torxtools.pathtools import expandpath

from .. import defaults
from ..utils.dicts import deepmerge

__all__ = []


def _read(cfgfile: str) -> Dict:
    """
    Convenience function in order to be mocked.

    Parameters
    ----------
    cfgfile: str
        a single path representing a yaml file.

    Returns
    -------
    dict:
        a dictionary
    """
    with open(cfgfile, "r", encoding="UTF-8") as fd:
        data = safe_load(fd)
    return data or {}


def _merge_default_dicts(theirs: Optional[Dict]) -> Dict:
    """
    Convenience function that takes the default configuration
    dictionary supplied by user and applies our defaults in
    order to have no keys missing.

    Parameters
    ----------
    theirs: dict
        their dictionary

    Returns
    -------
    dict:
        a dictionary
    """
    # create a merged dict to ensure that unspecified options
    # have our defaults
    ours = defaults.default_configuration(theirs)
    return deepmerge(ours, theirs or {})


# ------------------------------------------------------------------------------
# BaseCmdline
# ------------------------------------------------------------------------------
@attrs(kw_only=True)
class BaseCmdline:
    _default_cfg = attrib(default=None)

    def __attrs_post_init__(self: object) -> None:
        """
        ctor
        """
        # create a merged dict to ensure that unspecified options
        # have our defaults
        self._default_cfg = _merge_default_dicts(self._default_cfg)

    def add_arguments(self: object, parser: object) -> object:
        """
        (abstract method)
        Add middleware specific arguments.

        Parameters
        ----------
        parser: object
            an argparse.ArgumentParser

        Returns
        -------
        object:
            an argparse.ArgumentParser
        """
        return parser

    def _transform(self: object, args: Dict) -> Dict:
        """
        Function to convert flat argument list to a dictionary for Flasket configuration.

        Parameters
        ----------
        args: dict
            a flat dictionary

        Returns
        -------
        dict:
            a valid minimal Flasket configuration dictionary
        """
        # None arguments will be ignored
        # cf. flasket/defaults.py
        # pylint: disable=unnecessary-lambda-assignment
        drop_none = lambda _p, k, v: k is not None and v is not None

        return remap(
            {
                "cfgfile": args.get("cfgfile"),
                "server": {
                    "debug": args.get("debug"),
                    "listen": args.get("listen"),
                    "port": args.get("port"),
                    "ui": args.get("ui"),
                    "workers": args.get("workers"),
                    "pidfile": args.get("pidfile"),
                },
            },
            visit=drop_none,
        )

    def __call__(self: object, argv: Optional[List[str]] = None) -> Dict:
        """
        Parse the argument list argv and return a dictionary augmented with the values
        specified on command line.

        Parameters
        ----------
        argv: List[str]
            sys.argv[1:] if None

        Returns
        -------
        dict:
            a valid Flasket configuration dictionary
        """
        # pylint: disable=redefined-outer-name
        defaults = self._default_cfg

        if argv is None:
            argv = sys.argv[1:]

        # Sets environment variables for XDG paths
        xdgtools.setenv()

        # argument_default=None does not set the default to None for boolean options,
        # so we'll specifically set default=None for those values
        #
        # Default values aren't actually added/set here, but in the BaseSettings,
        # We only care about values that were specified.
        parser = argparse.ArgumentParser(
            description=defaults["server"]["description"],
            argument_default=None,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Prepare some variables
        cfgname = defaults["cfgname"]
        search_paths = defaults["cfgfile_search_paths"]
        search_paths = [e.format(cfgname=cfgname) for e in search_paths]
        b_ui = {True: "enabled", False: "disabled"}[defaults["server"]["ui"]]

        # fmt: off
        parser.add_argument("-l", "--listen", metavar="HOST",
            help=f'The ip to listen on (default: {defaults["server"]["listen"]})')
        parser.add_argument("-p", "--port", metavar="PORT", type=int,
            help=f'The port to listen on (default: {defaults["server"]["port"]})')
        parser.add_argument("-c", "--cfgfile", metavar="CFGFILE",
            help=f"Use CFGFILE as configuration file, otherwise first file found in search path is used. (default search path: {search_paths})")
        parser.add_argument("--ui", action="store_true", default=None,
            help=f"Enable the OpenAPI UI. Disable with --no-ui. (default: {b_ui})")
        parser.add_argument("--no-ui", action="store_false", default=None, dest="ui",
            help=argparse.SUPPRESS)
        # fmt: on

        # Potentially add extra arguments depending on the middleware
        parser = self.add_arguments(parser)

        # Parse the arguments, transform into a minimal dictionary, and update defaults
        # from ctor
        args = vars(parser.parse_args(argv))
        args = self._transform(args)

        return args


# ------------------------------------------------------------------------------
# BaseSettings
# ------------------------------------------------------------------------------
@attrs(kw_only=True)
class BaseSettings:
    _cmdline_cfg = attrib(default=None)
    _default_cfg = attrib(default=None)
    _forced_cfg = attrib(default=None)

    def __attrs_post_init__(self: object) -> None:
        """
        ctor
        """
        self._default_cfg = self._default_cfg or {}
        self._forced_cfg = self._forced_cfg or {}

    def __call__(self: object, argv: Optional[List[str]] = None) -> Dict:
        """
        Convert argv into a configuration dictionary.

        Parameters
        ----------
        argv: List[str]
            sys.argv[1:] if None

        Returns
        -------
        dict:
            a valid Flasket configuration dictionary
        """
        # Get the command line parameters as configuration dictionary
        if self._cmdline_cfg is None:
            cmdline_cfg = {}
        elif isinstance(self._cmdline_cfg, dict):
            cmdline_cfg = self._cmdline_cfg
        elif isinstance(self._cmdline_cfg, object) and not isinstance(self._cmdline_cfg, type(lambda: 1)):
            cmdline_cfg = self._cmdline_cfg(default_cfg=self._default_cfg)(argv=argv)
        elif callable(self._cmdline_cfg):
            cmdline_cfg = self._cmdline_cfg(argv=argv, default_cfg=self._default_cfg)
        else:
            raise NotImplementedError

        # cfgfile can exist in cmdline,
        # but could also have been set in defaults
        cfgfile = cmdline_cfg.get("cfgfile", self._default_cfg.get("cfgfile"))
        if cfgfile is None:
            # build the search path if it's valid
            search_paths = self._default_cfg.get("cfgfile_search_paths")
            cfgname = self._default_cfg.get("cfgname")
            if search_paths and cfgname:
                search_paths = [e.format(cfgname=cfgname) for e in search_paths]
                cfgfile = which(cfgfile, expandpath(search_paths))

        cfgdata_file = _read(cfgfile) or {}

        # We merge in the inverse order of priority
        cfgdata = self._default_cfg
        cfgdata = deepmerge(cfgdata, cfgdata_file)
        cfgdata = deepmerge(cfgdata, cmdline_cfg)
        cfgdata = deepmerge(cfgdata, self._forced_cfg)
        return cfgdata


# ------------------------------------------------------------------------------
# BaseFlasketCLI
# ------------------------------------------------------------------------------
@attrs(kw_only=True)
class BaseFlasketCLI:
    _cmdline_cfg = attrib(default=None)
    _default_cfg = attrib(default=defaults.default_configuration())
    _settings_cfg = attrib(default=BaseSettings)
    _forced_cfg = attrib(default=None, init=False)

    def __attrs_post_init__(self: object) -> None:
        """
        ctor
        """
        # create a merged dict to ensure that unspecified options
        # have our defaults
        self._default_cfg = _merge_default_dicts(self._default_cfg)

    # pylint: disable=unused-argument
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
        return

    def run(self: object, *args, argv: Optional[List[str]] = None, rootpath: str = None, **kwargs) -> None:
        """
        Run a Flasket with automatic parsing of command line and configuration file.

        Parameters
        ----------
        argv: List[str]
            sys.argv[1:] if None

        rootpath: str
            Path from which to dynamically load app, api and htdoc resources.
        """
        # Empty/None settings have no sense since it'll
        # block the start of Flask/Gunicorn.
        try:
            if self._settings_cfg is None:
                cfg = self._default_cfg
            elif isinstance(self._settings_cfg, dict):
                cfg = self._settings_cfg
            elif isinstance(self._settings_cfg, object) and not isinstance(self._settings_cfg, type(lambda: 1)):
                cfg = self._settings_cfg(
                    cmdline_cfg=self._cmdline_cfg, default_cfg=self._default_cfg, forced_cfg=self._forced_cfg
                )(argv=argv)
            elif callable(self._settings_cfg):
                cfg = self._settings_cfg(
                    argv=argv, cmdline_cfg=self._cmdline_cfg, default_cfg=self._default_cfg, forced_cfg=self._forced_cfg
                )
            else:
                raise NotImplementedError

            self._run(*args, cfg=cfg, rootpath=rootpath, **kwargs)
        except Exception as err:
            if os.environ.get("FLASKET_TRACEBACK"):
                print(traceback.print_exc(), file=sys.stderr)
            else:
                print(f"error: {err}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
