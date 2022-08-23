import collections
import os
import sys
import traceback
import yaml

from copy import deepcopy
from typing import List, Dict

from boltons.fileutils import iter_find_files
from connexion.exceptions import InvalidSpecification, ResolverError
from connexion.resolver import RestyResolver
from flask import jsonify

from ..utils import dicts


def _load_yamlfiles(files: List[str]) -> Dict:
    """
    For every yaml file, load the file and merge with previous

    Parameters
    ----------
    files: List[str]
        list of files to parse and merge

    Returns
    -------
    dict:
        merged dictionary
    """
    try:
        data = {}
        for f in files:
            with open(f, "r", encoding="UTF-8") as fd:
                newdata = yaml.safe_load(fd)
            if newdata:
                data = dicts.deepmerge(data, newdata)
        return data
    except yaml.scanner.ScannerError as err:
        raise type(err)(
            f"yaml scanner error: {err.problem} in '{err.problem_mark.name}', at line {err.problem_mark.line}"
        ) from err
    except yaml.parser.ParserError as err:
        raise type(err)(
            f"yaml parser error: {err.problem} in '{err.problem_mark.name}', at line {err.problem_mark.line}"
        ) from err
    except Exception as err:
        raise type(err)(f"{str(err)} in file {f}") from err


def _find_yamlfiles(paths: List[str], logger: object) -> collections.OrderedDict:
    """
    Find all yaml files in paths, returns a merged dict

    Parameters
    ----------
    paths: List[str]
        list of paths to search

    Returns
    -------
    dict:
        merged dictionary
    """

    # Merge all yml files from ./api directory
    files = []
    for path in paths:
        if logger:
            logger.info(f"Reading OpenAPI files from '{path}'...")
        files.extend(iter_find_files(path, ["*.yml", "*.yaml"]))

    data = _load_yamlfiles(files)

    # sort the keys in /components/schemas, since the UI uses that order
    data["components"]["schemas"] = collections.OrderedDict(
        sorted((data["components"]["schemas"]).items(), key=lambda s: s[0].lower())
    )
    return data


def _remove_path_if_key(specs: Dict, key: str, value: str) -> Dict:
    """
    For every API path in specs, remove it if we find specs[...][key] = value

    Parameters
    ----------
    specs: Dict
        OpenAPI specs

    key: str
        Key to look for

    value: str
        Value to look for

    Returns
    -------
    dict:
        OpenAPI specs without the removed keys
    """
    rv = deepcopy(specs)
    for path in specs.get("paths", {}).keys():
        for method in specs["paths"][path].keys():
            if key not in specs["paths"][path][method]:
                continue
            if specs["paths"][path][method][key] == value:
                del rv["paths"][path][method]
    return rv


class Application:
    def add_url_rules(self: object) -> None:
        """
        Add the '/api/' specific URL rules, and load '/api/' packages.
        """
        # Our main path is the factory and user 'api' directories
        selfpath = os.path.dirname(__file__)
        rootpath = os.path.join(self.rootpath, "api")

        # Merge all yml files from ./api directory
        specs = _find_yamlfiles([selfpath, rootpath], self.logger)

        # Disable all endpoints marked as x-debug=True
        if not self.config["server"]["debug"]:
            specs = _remove_path_if_key(specs, "x-debug", True)

        # https://connexion.readthedocs.io/en/latest/
        try:
            self._cnx.add_api(
                specs,
                resolver=RestyResolver("api"),
                strict_validation=True,
                validate_responses=True,
                options={
                    "swagger_url": "/api/ui",
                    "swagger_ui": self.config["server"]["ui"],
                    "swagger_spec": self.config["server"]["ui"],
                },
            )
        except InvalidSpecification as err:
            raise type(err)(f"OpenAPI error: {err.message}") from err
        except Exception as err:
            # TODO: improve on this (make import error for example)
            print(traceback.print_exc(), file=sys.stderr)
            raise

    def configure(self: object) -> None:
        """
        Configure the '/app/' specific part of the Application
        """
        self.app.config["JSON_SORT_KEYS"] = False

        if self.config["server"]["ui"]:
            self.logger.info("Swagger UI is available at: %s%s" % (self.sitename, "/api/ui"))
        else:
            self.logger.info("Swagger UI not started")

    def handle_error(self: object, err: Exception) -> object:
        """
        Transform exception into a json error

        Parameters
        ----------
        err: Exception
            exception to transform into a response

        Returns
        -------
        object:
            a flask response
        """
        if self.request.handler != "api":
            return

        response = self.make_response(
            jsonify({"detail": err.description, "status": err.code, "title": err.name}),
            err.code,
        )
        response.content_type = "application/problem+json"
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
        # Mark the request as being handled by this application
        if app.request.path.startswith("/api/"):
            app.request.handler = "api"

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
