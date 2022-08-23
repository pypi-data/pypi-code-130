"""
Main application. It handles returning the WSGI application,
but also returning the potential services it can connect to and use.

On the OpenAPI side, it handles merging multiple yaml files into a single
specification before loading it.
"""

import logging
import os
import random
import string
import sys
import time
import traceback
import uuid

from attr import attrs, attrib
from functools import wraps
from typing import Dict

from connexion import FlaskApp
from connexion import request as current_request
from flask import (
    g,
    current_app,
    make_response,
    redirect,
    render_template,
    session as current_session,
)

from .api.application import Application as ApplicationApi
from .app.application import Application as ApplicationApp
from .clients.clients import Clients
from .exceptions import Application as ApplicationExceptions
from .htdocs import Application as ApplicationStatic
from .logger import Logger
from .mixins import LoggerMixin
from .templates import template_global, g_template_global
from .testing import MockClient
from .utils.packages import load_packages
from .wrappers import endpoint


@template_global
@endpoint
def is_production(app):
    return app.production


@template_global
@endpoint
def is_debug(app):
    return app.debug


class Application(ApplicationApp, ApplicationStatic, ApplicationExceptions, LoggerMixin):
    _subclasses = [ApplicationApp, ApplicationStatic, ApplicationApi, ApplicationExceptions]

    def __init__(self, *args, cfg: Dict, rootpath, **kwargs) -> None:
        # If root path is not set, use an arbitrary folder that does not exist
        # TODO: Can we use app.config["APPLICATION_ROOT"]?
        rootpath = rootpath or "/nonexisting-{os.getpid()}"
        self._rootpath = os.path.realpath(rootpath)

        # Add the directory to sys.path
        if rootpath not in sys.path:
            self.logger.info(f"Adding path '{rootpath}' to sys.path to enable loading API and app files.")
            sys.path.append(rootpath)

        # Initialize loggers
        Logger.configure(self)
        self.logger.info("Creating a new Application...")
        self.logger.info(f"Using root path '{self._rootpath}' for dynamic loading")

        # Initial setup of Flask+Connexion
        import_name = kwargs.get("import_name", __name__)
        self._cnx = FlaskApp(import_name, specification_dir="api")

        # Set a reference to ourself, used almost everywhere
        self.app.config["APPLICATION"] = self

        # Load config from defaults, file and cmdline
        self.app.config["CONFIG"] = cfg

        # https://flask.palletsprojects.com/en/2.2.x/config/
        self.app.config["DEBUG"] = self.config["server"]["debug"]

        # Act upon some other configuration values
        self.__production = self.config["server"].get("production", False)
        self.__debug = self.config["server"].get("debug", False)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

        secret_key = self.config["server"].get("secret_key")
        if secret_key:
            self.app.secret_key = secret_key
        else:
            self.app.secret_key = "".join(random.choices(string.ascii_letters, k=20))
            self.logger.warning("Generated a random secret session key")

        # Load dynamic client loader, they could be used in
        # 'configure' action
        self._clients = Clients(app=self)

        # Load subclasses
        for item in self._subclasses:
            item.add_url_rules(self)
            item.configure(self)

        # Add pre/post request functions
        self.app.before_request(Application.before_request)
        self.app.after_request(Application.after_request)

        # Load all user packages
        self.logger.info("Loading packages...")
        load_packages(self.rootpath, self.logger)

        # Load all jinja2 templates
        self.logger.info("Loading Jinja2 templates...")
        for name, fn in g_template_global.items():
            self.logger.debug(f"Loading Jinja2 template '{name}'...")
            self.app.add_template_global(fn)

    # --------------------------------------------------------------------------
    def __call__(self, environ, start_response):
        """Dispatch to middleware"""
        return self.app(environ, start_response)

    @property
    def request(self):
        return current_request

    @property
    def request_addr(self):
        # TODO: Wrap current_request with this item
        return self.request.headers.get("X-Forwarded-For", self.request.remote_addr)

    @property
    def session(self):
        return current_session

    @staticmethod
    def make_response(*args, **kwargs):
        return make_response(*args, **kwargs)

    @staticmethod
    def render_template(*args, **kwargs):
        return render_template(*args, **kwargs)

    # --------------------------------------------------------------------------
    @staticmethod
    def before_request(*_args, **_kwargs):
        # Set a 'handler' variable to recognize source Application in
        # after_request
        app = current_app.config["APPLICATION"]
        app.request.handler = None

        Logger.before_request(app)

        # Inject template variables
        g.baseurl = app.baseurl

        # Create a X-Request-Id
        app.request.uuid = uuid.uuid4()
        # Save the current time
        app.request.start = time.time()

        for item in Application._subclasses:
            item.before_request(app=app)

    @staticmethod
    def after_request(response, *_args, **_kwargs):
        app = current_app.config["APPLICATION"]

        runtime = round(time.time() - app.request.start, 6)
        response.headers["X-Runtime"] = runtime
        response.headers["X-Request-Id"] = app.request.uuid.hex

        for item in Application._subclasses:
            response = item.after_request(app=app, response=response)

        # Log the request
        Logger.log_request(app, response)
        return response

    # --------------------------------------------------------------------------
    def redirect(self, location, code=308, response=None, headers=None):
        response = redirect(location, code, response)
        for header, value in headers or []:
            response.headers[header] = value
        return response

    # pylint: disable=arguments-differ
    def handle_error(self, err, *_args, **_kwargs):
        for item in Application._subclasses:
            # pylint: disable=assignment-from-no-return
            response = item.handle_error(self, err=err)
            if response:
                return response
        return err

    # --------------------------------------------------------------------------
    @property
    def production(self: object) -> bool:
        return self.__production

    @property
    def debug(self: object) -> bool:
        return self.__debug

    @property
    def rootpath(self: object) -> str:
        """Returns the Application root path (os.getcwd())"""
        return self._rootpath

    @property
    def app(self: object) -> object:
        """Returns the contained Flask app"""
        return self._cnx.app

    @property
    def config(self: object) -> Dict:
        """Returns the user config"""
        # self.app.config is the Flask config
        # self.app.config["CONFIG"] is our config
        return self.app.config["CONFIG"]

    @property
    def host(self: object) -> str:
        """Returns the host the server will bind to depending on value from configuration/command line"""
        return self.config["server"]["listen"]

    @property
    def port(self: object) -> int:
        """Returns the port server will listen on depending on value from configuration/command line"""
        return self.config["server"]["port"]

    @property
    def debug(self: object) -> bool:
        """Returns the debug mode the server will be run in depending on value from configuration/command line"""
        return self.config["server"]["debug"]

    @property
    def sitename(self: object) -> str:
        """Returns a scheme://host:port"""
        if self.port == 80:
            return "http://%s" % self.host
        return "http://%s:%s" % (self.host, self.port)

    @property
    def baseurl(self: object) -> str:
        """Returns expected baseurl {retval.scheme}://{retval.netloc}"""
        baseurl = self.config["server"].get("baseurl", None)
        if baseurl:
            return baseurl
        return self.sitename

    @property
    def clients(self: object) -> object:
        """Returns object of possible clients"""
        return self._clients

    def test_client(self: object) -> object:
        self.app.config["TESTING"] = True
        return MockClient.cast(self.app.test_client())


# TODO
