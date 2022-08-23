import os

from flask import send_from_directory


class Application:
    def add_url_rules(self: object) -> None:
        """
        Handle all other paths
        """
        self.app.add_url_rule("/<path:path>", view_func=self.send_static_file)

    def configure(self: object) -> None:
        """
        Do nothing
        """

    def handle_error(self: object, err: Exception) -> object:
        """
        Do nothing
        """
        pass

    @staticmethod
    def before_request(app: object) -> None:
        """
        Do nothing
        """
        return

    @staticmethod
    def after_request(app: object, response: object) -> object:
        """
        Do nothing
        """
        return response

    def send_static_file(self: object, path: str = "") -> object:
        """
        Search for a file in htdocs, and if it exists, then return it

        Parameters
        ----------
        path: str
            url path as recieved by Flask

        Returns
        -------
        object:
            a flask response
        """
        self.request.handler = "htdocs"

        rootpath = os.path.join(self.rootpath, "htdocs")
        filepath = os.path.join(rootpath, path)
        filepath = os.path.realpath(filepath)

        # File must exist
        if not os.path.exists(filepath):
            raise self.NotFound

        return send_from_directory(rootpath, path)
