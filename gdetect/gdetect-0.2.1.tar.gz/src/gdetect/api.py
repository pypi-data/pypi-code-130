"""Api is a module to connect to GLIMPS detect service by url.

This module help use of GLIMPS detect. Main parameters are the token and the url.
If no token are given to constructor, the Api class try to get the 'API_TOKEN' environment variable.
If this variable doesn't exists, a exception is raises.

It's the same for url: try to get environment variable 'API_URL' or raises exception.

Usage examples:

>>> client = Client()
>>> client.push('malware.elf')
9d488d01-23d5-4b9f-894e-c920ea732603
>>> client.get('9d488d01-23d5-4b9f-894e-c920ea732603')
{'uuid': '9d488d01-23d5-4b9f-894e-c920ea732603', 'sha256': '7850d6e51ef6d0bc8c8c1903a24c22a090516afa6f3b4db6e4b3e6dd44462a99', 'sha1': 'e0b77bdd78bf3215221298475c88fb23e4e84f98', 'md5': 'e1c080be1a748d69246ad9c766ad8809', 'ssdeep': '384:MCDKKQOcRpmYLdn6RBOFRFt5rUFX1DiSIlCo3AnupCFNqnrrd1NEZgO8UXWozPLL:P/QOC0Yhn6ROHWFlAcwNEFCnNBxc6nc/', 'is_malware': True, 'score': 3000, 'done': True, 'timestamp': 0, 'filetype': 'elf', 'size': 24728, 'filenames': ['sha256'], 'files': [{...}], 'sid': '7UZy0tbWPSTdNfkzKSW5gS', ...}
"""

import pathlib
import time
import urllib.parse
import urllib3

from dataclasses import dataclass

import requests

from gdetect import exceptions, log


logger = log.get_logger()

base_endpoint = "/api/lite/v2"

class Client:
    """Client class build an object to interact with url.

    The constructor takes 2 parameters: 'url' and 'token'.

    Attributes:
        url (str): URL of the API.
        token (str): The authentication token.
        verify (bool): If `False`, this bypass SSL checks. *Only for testing*.
                       **Not recommended in production !**
        response (Response): A Response dataclass with detailled return.
    """

    def __init__(self, url: str = "", token: str = ""):
        self.url = urllib.parse.urljoin(url, base_endpoint)
        self.token = token
        self.verify = True
        # remove print of requests warning about SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.response = None

    def push(self, filename: str, bypass_cache: bool = False) -> str:
        """Push a file to API endpoint.

        Args:
            filename (str): Fullpath of binary.
            bypass_cache (bool, optional): If True, the file is analyzed, even if a result already exists.

        Returns:
            uuid (str): unique id of analyse

        Raises:
            exceptions.GDetectError: An error occurs. Check :class:`~Api.Response` for details.
        """

        # check inputs
        self._check_token()
        try:
            with open(filename, "rb") as finput:
                # prepare request
                params = {"bypass-cache": f"{bool(bypass_cache)}"}
                files = {"file": (pathlib.Path(filename).name, finput)}
                path = f"{self.url}/submit"

                # send request
                req = self._req(
                    "post",
                    path,
                    headers={"X-Auth-Token": self.token},
                    params=params,
                    files=files,
                    verify=self.verify,
                )
        except Exception as err:
            err_msg = "unable to read given file"
            logger.error("%s: %s", err_msg, err)
            self.response = Response(None, False, err, err_msg)
            raise exceptions.GDetectError

        # send return
        if req.ok:
            resp = req.response.json()
            if "uuid" in resp:
                return resp["uuid"]
            logger.error("something went wrong: %s", req.message)
            raise exceptions.GDetectError
        logger.error("%s: %s", req.message, req.error)
        raise exceptions.GDetectError

    def get(self, uuid: str) -> object:
        """Retrieve analysis result

        Args:
            uuid (str): identification number of submitted file.

        Returns:
            result (object): The json-encoded content of a response, if any.

        Raises:
            exceptions.GDetectError: An error occurs. Check :class:`~Api.Response` for details.
        """

        # check inputs
        self._check_token()
        self._check_uuid(uuid)

        # prepare request
        path = f"{self.url}/results/{uuid}"

        # send request
        req = self._req(
            "get", path, headers={"X-Auth-Token": self.token}, verify=self.verify
        )

        # send return
        if req.ok:
            return req.response.json()
        logger.error("%s: %s", req.message, req.error)
        raise exceptions.GDetectError

    def waitfor(
        self,
        filename: str,
        bypass_cache: bool = False,
        pull_time: int = 5,
        timeout: int = 180,
    ) -> object:
        """Send a file to GLIMPS Detect and wait for a result.

        This function is an 'all-in-one' for sending and getting result.
        The pull time is arbitrary set to 5 seconds, and timout to 3 minutes.

        Args:
            filename (str): Fullpath of binary.
            bypass_cache (bool): If True, the file is analyzed, even if a result already exists.
            pull_time (int): The time to wait (in seconds) between each requests to get a result.
            timeout (int): The maximum time execution of this method in seconds.

        Returns:
            result (object): The json-encoded content of a response, if any.

        Raises:
            exceptions.GDetectError: An error occurs. Check :class:`~Api.Response` for details.
        """

        start_time = time.time()
        # push file, get uuid
        uuid = self.push(filename, bypass_cache=bypass_cache)

        # get result
        while True:
            result = self.get(uuid)
            if result["done"]:
                return result
            if time.time() - start_time > timeout:
                self.response = Response(None, False, TimeoutError, "timeout reached")
                raise exceptions.GDetectError
            time.sleep(pull_time)

    def _check_uuid(self, uuid):
        if len(uuid) == 0:
            logger.error("UUID is empty")
            self.response = Response(None, False, exceptions.BadUUID(), "UUID is empty")
            raise exceptions.GDetectError

    def _check_token(self):
        token = self.token
        if token == "":
            logger.error("no token given")
            self.response = Response(
                None, False, exceptions.NoAuthenticateToken(), "no token given"
            )
            raise exceptions.GDetectError
        if not isinstance(token, str):
            logger.error("token must be type string")
            self.response = Response(
                None,
                False,
                exceptions.BadAuthenticationToken(),
                "token must be type string",
            )
            raise exceptions.GDetectError
        if len(token) != 44:
            logger.error("token have wrong length")
            self.response = Response(
                None,
                False,
                exceptions.BadAuthenticationToken(),
                "token have wrong length",
            )
            raise exceptions.GDetectError
        authorized = "0123456789abcdef-"
        for char in token:
            if char not in authorized:
                logger.error("forbidden character inside token")
                self.response = Response(
                    None,
                    False,
                    exceptions.BadAuthenticationToken(),
                    "forbidden character inside token",
                )
                raise exceptions.GDetectError

    def _req(self, method: str, url: str, **kwargs: str):
        """Process a request to URL with given method and params.

        This function execute the request to the URL with `requests` library.
        The return is wrapped inside a Response dataclass to simplify exceptions
        handling and logging.

        Args:
            method (str): request type (GET, POST,...).
            url (str): URL to join.
            **kwargs (str): named options of requests library.

        Returns:
            Response: a :class:`~Response` object.
        """

        try:
            req = requests.request(method, url, **kwargs)
            code = req.status_code
            if code != 200:
                msg = status_msg(code)
                self.response = Response(None, False, None, msg)
            else:
                self.response = Response(req, True, None, "")
        except requests.ConnectionError as ex:
            self.response = Response(None, False, ex, "unable to connect")
        except requests.HTTPError as ex:
            code = ex.response.status_code
            msg = status_msg(code)
            self.response = Response(None, False, ex, msg)
        except requests.URLRequired as ex:
            self.response = Response(None, False, ex, "an URL is required")
        except requests.TooManyRedirects as ex:
            self.response = Response(None, False, ex, "too many redirects")
        except requests.Timeout as ex:
            self.response = Response(None, False, ex, "request timed out")
        except requests.exceptions.MissingSchema as ex:
            self.response = Response(
                None, False, ex, "the URL schema (e.g. http or https) is missing"
            )
        except requests.exceptions.InvalidSchema as ex:
            self.response = Response(
                None, False, ex, "schema (e.g. http or https) is invalid"
            )
        except requests.exceptions.InvalidURL as ex:
            self.response = Response(
                None, False, ex, "the URL provided somehow invalid"
            )
        except BaseException as ex:
            self.response = Response(None, False, ex, "undefined error")

        return self.response


@dataclass
class Response:
    """A consistent return for the api class

    Attributes:
        response: The requests.Response object if no error. Otherwise, it's None.
        ok: Set at `True` if no exceptions handling.
        error: Original exception if occurs. Otherwise, it's None.
        message: A friendly message for final client (like console or logging).
    """

    response: requests.Response
    ok: bool
    error: Exception
    message: str


def status_msg(code):
    """return explicit message for given HTTP error code"""
    return {
        400: "invalid file submitted",
        401: "invalid token",
        404: "ressource doesn't exists",
        500: "unexpected error from server",
    }.get(code, "unexpected HTTP error")
