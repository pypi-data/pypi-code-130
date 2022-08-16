import json

import datetime
import requests
import traceback
import functools

from typing import Dict
from urllib.parse import urlparse
from haptik_code_library.haptik_requests import const


class RequestDataCreator():
    """
    API-metadata creator class:
        Creates and returns json format of api-requests' metadata for every request made.
        this metadata is appended to self.api_metadata list.
    Returns:
        json (dict): metadata containing api's request related info
    eg:
        {
            "url": "https://mock.codes/400",
            "status_code": 400,
            "request_type": "GET",
            "time_elapsed": 0.317265,
            "exception": None
        }
    """
    def __init__(self, url: str, status_code: int, request_type: str, time_elapsed: float, exception: str,
                 kwargs: dict) -> None:
        """
        Constructor with required keys assigned to class-instance and used later to return json-format of api-metadata.

        Args:
            url (str): API URL
            status_code (int): status code of response, eg: 200/300/400/500
            request_type (str): HTTP request type, eg: GET/PUT/POST/DELETE
            time_elapsed (float): time taken by request to get response from url given in seconds
            exception (str): exception's name (eg. Timeout) or traceback of unhandled error
            kwargs (dict): keyword arguments passed
        """
        self.url = url
        self.status_code = status_code
        self.request_type = request_type
        self.time_elapsed = time_elapsed
        self.exception = exception
        self.kwargs = kwargs

    def to_json(self) -> Dict:
        """
        Construct and return json of api-requests metadata for every request made.

        Returns:
            json (dict): json-structure with api-metadata
        """
        return {
            'url': self.url,
            'status_code': self.status_code,
            'request_type': self.request_type and self.request_type.upper(),
            'time_elapsed': self.time_elapsed,
            'exception': self.exception,
            **self.update_timeout_data()
        }

    def update_timeout_data(self):
        """
        Update timeout data in json-response
        If timeout occurs, then append field timeout_in_seconds in json-response

        Returns:
            json (dict): If timeout exception, returns dict with key = timeout_in_seconds with value in seconds,
                         else returns empty json
        """
        if self.exception == const.TIMEOUT_EXCEPTION:
            return {'timeout_in_seconds': self.kwargs.get('timeout')}
        return {}


class HaptikRequests():
    """
    Custom request class, built on top of request-library, to provide api-related metadata for every http-method call.
    Contains methods to make api call of http-methods and store data in instance of a class and return in response
    Provides api-related metadata, as request's url, time taken to execute, status code, exception if any.
    Appends metadata of every api-request, to reqsponse dictionary via decorator in list of dictionaries.
    """
    def __init__(self) -> None:
        """
        Constructor: Initialize api_metadata list, which stores each api-request call's metadata by appending to itself
        """
        self.api_metadata = []

    def store_api_metadata(self, start_time: datetime, url: str, request_type: str,
                           response: requests.models.Response(), exception: str = None, kwargs: dict = {}) -> None:
        """
        Store every api-call metadata in api_metadata list and gets data in json-format and appends on every api-call

        Args:
            start_time (datetime): timestamp at which request is started, to calculate time taken by request to execute
            url (str): API URL
            request_type (str): HTTP request type, eg: GET/PUT/POST/DELETE
            response (requests.models.Response): request's response instance, by default initialized to None
            exception (str, optional): exception's name (eg. Timeout) or traceback of unhandled error
            kwargs (dict, optional): keyword arguments passed

        Returns:
            None
        """
        try:
            current_time = datetime.datetime.now()
            time_elapsed = (current_time - start_time).total_seconds() if start_time else None

            url_parser_obj = urlparse(url)
            url = url_parser_obj.scheme + "://" + url_parser_obj.hostname + url_parser_obj.path

            request_metadata = RequestDataCreator(
                url=url,
                status_code=response.status_code if response is not None else None,
                request_type=request_type if request_type else None,
                time_elapsed=time_elapsed,
                exception=exception,
                kwargs=kwargs,
            )

            data = request_metadata.to_json()

            self.api_metadata.append(data)

        except Exception as exception:
            exception_traceback = str(traceback.format_exc())
            print(f"Exception occured as: {exception}, with traceback = {exception_traceback}")

    def get_api_metadata(self):
        """
        Get api_metadata from class instance(HaptikRequests),
            as self.api_metadata contains list of dictionaries with each api-call made with HTTP method

        Returns:
            api_metadata(str): json-dumped string contains list of dictionaries with each api's metadata
        """
        try:
            print(f"\n self.api_metadata = {self.api_metadata}")
            return json.dumps(self.api_metadata)
        except Exception as e:
            print(f"\n Exception occured: {e}")
            return json.dumps({})

    def make_request(self, request_type: str, url: str, data: dict = None, json: dict = None,
                     **kwargs) -> requests.models.Response():
        """
        Make request to python's request library and Store api-related metadata in class's api_metadata object

        Args:
            request_type (str): HTTP Method as GET/PUT/POST/DELETE
            url (str): API URL
            data (dict, optional): method body, default = None.
            json (dict, optional): json data, default = None.
            kwargs (dict): keyword arguments passed
        Returns:
            response (requests.models.Response()): API Response of HTTP method call
        """
        response = requests.models.Response()
        response.status_code = None

        start_time = datetime.datetime.now()
        exception = None
        try:
            method_to_call = getattr(requests, request_type)
            response = method_to_call(url=url, data=data, json=json, **kwargs)

        except requests.exceptions.HTTPError:
            exception = const.HTTP_ERROR
        except requests.exceptions.Timeout:
            exception = const.TIMEOUT_EXCEPTION
            response.status_code = const.TIMEOUT_STATUS_CODE
            response.timeout = kwargs.get('timeout')

        except requests.exceptions.RequestException:
            exception = const.REQUEST_EXCEPTION
        except Exception as e:
            print(f"\n Exception occured: {e}")
            exception = e

        finally:
            self.store_api_metadata(start_time=start_time, url=url, request_type=request_type, response=response, exception=exception, kwargs=kwargs)  # noqa E501
            return response

    def add_api_metadata_to_response(self):
        """
        Decorator which handles exception occured in caller function and returns api_metadata from instance of a class,
        which contains json format of api-requests' metadata for every request made.

        Handles exception in code occurs, and appends it's data to self.api_metadata, which finally fetched and return 
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    response = func(*args, **kwargs)
                except Exception:
                    response = {}
                    exception = str(traceback.format_exc())

                    # To capture code-node unhandled errors
                    self.store_api_metadata(start_time=None, url=None, request_type=None, response=None, exception=exception)  # noqa E501

                finally:
                    response['api_metadata'] = self.get_api_metadata()
                    print(f"\n decorator add_api_metadata_to_response() returned response = {response}")
                    return response

            return wrapper
        return decorator

    def request(self, method, url, data=None, json=None, **kwargs):
        return self.make_request(request_type=method.lower(), url=url, data=data, json=json, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='post', url=url, data=data, json=json, **kwargs)

    def get(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='get', url=url, data=data, json=json, **kwargs)

    def options(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='options', url=url, data=data, json=json, **kwargs)

    def head(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='head', url=url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='put', url=url, data=data, json=json, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='patch', url=url, data=data, json=json, **kwargs)

    def delete(self, url, data=None, json=None, **kwargs):
        return self.make_request(request_type='delete', url=url, data=data, json=json, **kwargs)
