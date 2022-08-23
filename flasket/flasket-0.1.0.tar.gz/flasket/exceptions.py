import os

from flask import Blueprint
from werkzeug import exceptions as exception
from werkzeug.exceptions import default_exceptions

# Notes on exceptions handling and errors:
# https://werkzeug.palletsprojects.com/en/master/exceptions/
# https://tools.ietf.org/html/rfc7807
HTTPException = exception.HTTPException

# 204 No Content
class NoContent(HTTPException):
    code = 204
    name = "No Content"


# 400 Bad Request
BadRequest = exception.BadRequest

# 401 Unauthorized
Unauthorized = exception.Unauthorized

# 403 Forbidden
Forbidden = exception.Forbidden

# 404 NotFound
NotFound = exception.NotFound

# 424 FailedDependency
FailedDependency = exception.FailedDependency

# 500 InternalServerError
InternalServerError = exception.InternalServerError

# 501 NotImplemented
# pylint: disable=redefined-builtin
NotImplemented = exception.NotImplemented

# 503 ServiceUnavailable
ServiceUnavailable = exception.ServiceUnavailable


class Application:
    # Notes on exception handling and errors:
    # https://werkzeug.palletsprojects.com/en/master/exception/
    # https://tools.ietf.org/html/rfc7807
    HTTPException = exception.HTTPException

    # 204 No Content
    NoContent = NoContent

    # 400 Bad Request
    BadRequest = exception.BadRequest

    # 401 Unauthorized
    Unauthorized = exception.Unauthorized

    # 403 Forbidden
    Forbidden = exception.Forbidden

    # 404 NotFound
    NotFound = exception.NotFound

    # 424 FailedDependency
    FailedDependency = exception.FailedDependency

    # 500 InternalServerError
    InternalServerError = exception.InternalServerError

    # 501 NotImplemented
    NotImplemented = exception.NotImplemented

    # 503 ServiceUnavailable
    ServiceUnavailable = exception.ServiceUnavailable

    def add_url_rules(self: object) -> None:
        """
        Add the '/htdocs/' specific URL rules, and load error handlers.
        """
        self.logger.info("Registering error handlers...")
        rootpath = os.path.join(self.rootpath, "htdocs")
        blueprint = Blueprint("errors", __name__, template_folder=rootpath)
        self.app.register_blueprint(blueprint)

        # Register every known exception from Flask
        for error_code in default_exceptions:
            self.app.register_error_handler(error_code, self.handle_error)

    def configure(self: object) -> None:
        """
        Nothing
        """
        return

    def handle_error(self: object, err: Exception) -> object:
        """
        Generate a static simple html error page.

        Parameters
        ----------
        err: Exception
            exception to transform into a response

        Returns
        -------
        object:
            a flask response
        """
        html = "<!doctype html>"
        html += "<html lang=en>"
        html += f"<title>{err.code} {err.name}</title>"
        html += f"<h1>{err.name}</h1>"
        html += f"<p>{err.description}</p>"
        response = self.make_response(html)
        response.status_code = err.code
        return response

    @staticmethod
    def before_request(app: object) -> None:
        """
        Runs once before each request.

        Parameters
        ----------
        app: object
            a flasket Application
        """
        return

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
        return response
