import os

from flask import Blueprint

# pylint: disable=relative-beyond-top-level
from ..utils.packages import load_packages, load_package


class Application:
    def add_url_rules(self: object) -> None:
        """
        Add the '/app/' specific URL rules, and load '/app/' packages.
        """
        rootpath = os.path.join(self.rootpath, "app")
        if not os.path.exists(rootpath):
            self.logger.warning(f"Path '{rootpath}' does not exist")

        blueprint = Blueprint("app", __name__, template_folder=rootpath)

        # Add url rules for everything /app/*
        blueprint.add_url_rule("/", view_func=lambda: self.redirect("/app/"))
        blueprint.add_url_rule("/app/", view_func=self.send_app_file)
        blueprint.add_url_rule("/app/<path:path>", view_func=self.send_app_file)
        self.app.register_blueprint(blueprint)

        # Load all jinja2 templates
        self.logger.info(f"Loading 'app' templates from packages in '{rootpath}'...")
        load_packages(rootpath, self.logger)

    def configure(self: object) -> None:
        """
        Configure the '/app/' specific part of the Application
        """
        self.app.config["EXPLAIN_TEMPLATE_LOADING"] = os.getenv("EXPLAIN_TEMPLATE_LOADING")
        self.app.config["TEMPLATES_AUTO_RELOAD"] = not self.production

        self.app.jinja_env.trim_blocks = True
        self.app.jinja_env.lstrip_blocks = True

        # Cache values
        # pylint: disable=attribute-defined-outside-init
        self.__rootpath_app = os.path.join(self.rootpath, "app")

    def handle_error(self: object, err: Exception) -> None:
        """
        Nothing

        Parameters
        ----------
        err: Exception
            exception to transform into a response

        Returns
        -------
        object:
            a flask response
        """
        return

    @staticmethod
    def before_request(app: object) -> None:
        """
        Runs once before each request.

        Parameters
        ----------
        app: object
            a flasket Application
        """
        # Mark the request as being handled by this application
        if app.request.path.startswith("/app/"):
            app.request.handler = "app"

    @staticmethod
    def after_request(app: object, response: object) -> object:
        """
        Runs once after each request.

        Parameters
        ----------
        app: object
            a flasket Application

        response: object
            a flask response
        """
        if app.request.handler != "app":
            return response

        # We assume that everything in /app/ is dynamic
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = 0
        return response

    def send_app_file(self: object, path: str = "") -> object:
        """
        For every request, figure out which template to return.

        Parameters
        ----------
        path: str
            url path as recieved by Flask

        Returns
        -------
        object:
            a flask response
        """
        # TODO: Cache path, package, and method function
        # Find the module, and run 'get'
        filepath = os.path.join(self.__rootpath_app, path)
        if path == "" or path[-1:] == "/":
            filepath += "index"
        filepath += ".py"

        if not os.path.exists(filepath):
            raise self.NotFound

        # When not production, reload
        package = os.path.relpath(filepath).replace("/", ".").replace(".py", "")
        pkg = load_package(package, not self.production)

        # TODO: use method, not only get
        return pkg.get(path=path)
