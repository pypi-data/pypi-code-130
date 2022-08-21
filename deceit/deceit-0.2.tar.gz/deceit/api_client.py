import json
import logging
import posixpath
import requests
from requests import PreparedRequest
from requests.models import Request, Response

from .adapters import RetryAdapter
from .encoders import JsonEncoder
from .exceptions import ApiException



class ApiClient:
    def __init__(self, *args, base_url=None, default_timeout=None,
                 exception_class=None, **kwargs):
        self.base_url = base_url
        adapter = RetryAdapter(timeout=default_timeout)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.log = logging.getLogger(__name__)
        self.exception_class = exception_class or ApiException

    def presend(self, request: PreparedRequest):
        """
        override this function to do things like logging requests
        """
        pass

    def postsend(self, request: PreparedRequest, response: Response):
        """
        override this function to do things like logging responses
        """
        pass

    def headers(self, *args, **kwargs):
        return {}

    def send(self, method, route, params=None, form_data=None, json_data=None, **kwargs):
        headers = self.headers()
        headers.update(kwargs.pop('headers', None) or {})
        base_url = self.base_url
        url = posixpath.join(base_url, route) if base_url else route
        if json_data:
            body = json.dumps(json_data, cls=JsonEncoder)
            headers.setdefault('content-type', 'application/json')
        else:
            body = form_data
            headers.setdefault('content-type', 'application/x-www-form-urlencoded')
        request = Request(
            method, url, headers=headers, data=body,
            params=params, **kwargs)
        request = self.session.prepare_request(request)
        self.presend(request)
        response = self.session.send(request)
        self.postsend(request, response)
        if response.status_code // 100 != 2:
            raise self.exception_class.from_response(response)
        try:
            return response.json()
        except json.JSONDecodeError:
            return response

    def get(self, route, params=None, **kwargs):
        return self.send('get', route, params=params, **kwargs)

    def post(self, route, form_data=None, json_data=None, **kwargs):
        return self.send('post', route, form_data=form_data, json_data=json_data, **kwargs)

    def put(self, route, form_data=None, json_data=None, **kwargs):
        return self.send('put', route, form_data=form_data, json_data=json_data, **kwargs)

    def delete(self, route, params=None, form_data=None, json_data=None, **kwargs):
        return self.send('delete', route, params=params, form_data=form_data, json_data=json_data, **kwargs)

    def patch(self, route, params=None, form_data=None, json_data=None, **kwargs):
        return self.send('patch', route, params=params, form_data=form_data, json_data=json_data, **kwargs)
