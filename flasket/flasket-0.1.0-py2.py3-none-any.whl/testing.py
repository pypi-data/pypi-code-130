import json

import html5lib

from attr import attrs, attrib
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from .mixins import AppMixin


def _build_query_string(query):
    if not query:
        return ""
    if isinstance(query, str):
        return query
    return "&".join(f"{k}={v}" for k, v in sorted(query.items()))


class MockSession:
    def __init__(self, client):
        self._client = client

    def set(self, key, value):
        with self._client.session_transaction() as client_session:
            client_session[key] = value

    # TODO: setitem
    def __getitem__(self, key):
        return self.items[key]

    @property
    # TODO: make function
    def items(self):
        with self._client.session_transaction() as client_session:
            return dict(client_session.items())

    def clear(self):
        with self._client.session_transaction() as client_session:
            client_session.clear()


class ValidatorResponse(TestResponse):
    @classmethod
    def cast(cls, source: TestResponse):
        assert isinstance(source, TestResponse)
        source.__class__ = cls
        assert isinstance(source, TestResponse)
        return source

    def expect(self, status_code=200, content_type=None):
        """
        Assert the results from a call_method call
        """
        # Verify status code
        if status_code:
            message = f"Expected client to return HTTP code {status_code}, received {self.status_code} instead"
            assert status_code == self.status_code, message

        # Set a content-type if this was a post
        if not content_type and self.request.method == "POST":
            if self.request.content_type == "application/json":
                content_type = "application/json"

        # Get the real data
        data = self.data
        try:
            data = self.json
            if data is not None and not content_type:
                content_type = "application/json"
        except json.decoder.JSONDecodeError:
            if not content_type:
                content_type = "text/html"

        if content_type:
            # switch content-type on error
            if self.status_code >= 400 and content_type == "application/json":
                content_type = "application/problem+json"

            # Verify content_type
            content = self.content_type.split(";")[0]
            message = f"Expecting '{content_type}' as content-type but got '{content}'"
            assert content_type == content, message
        else:
            assert data is None, "A content-type is required when response data is not empty"

        # Verify contents
        if content_type == "text/html":
            html5parser = html5lib.HTMLParser(strict=True)
            html5parser.parse(str(self.data.decode("UTF-8")))

        return self


# TODO: remove ref to app
# class MockClient(FlaskClient, AppMixin):
@attrs(kw_only=True)
class MockClient(FlaskClient):
    route = None
    _default_headers = attrib(default=None, init=False)

    def __attrs_post_init__(self: object) -> None:
        self._default_headers = {}

    @classmethod
    def cast(cls, source: FlaskClient) -> object:
        assert isinstance(source, FlaskClient)
        source.__class__ = cls
        assert isinstance(source, FlaskClient)
        source.__init__()
        return source

    @staticmethod
    def any_route(*args, **kwargs):
        # pylint: disable=not-callable
        return MockClient.route(*args, **kwargs)

    # pylint: disable=arguments-differ
    def get(self, url, **kwargs):
        return self.request(url, method="GET", **kwargs)

    # pylint: disable=arguments-differ
    def post(self, url, **kwargs):
        return self.request(url, method="POST", **kwargs)

    def request(self, url, method="GET", session=None, query=None, headers=None, **kwargs):
        """
        Simple request with parameters, without test assertions

        :param url: URL to call
        :param method: Call method, "GET by default
        :param params: Additional GET params to add
        :returns: result from client call method
        """

        # Build a query string
        query_string = _build_query_string(query)
        url = f"{url}?{query_string}"

        # Create or edit the session
        for k, v in (session or {}).items():
            self.session.set(k, v)

        if headers is None:
            headers = {}
        headers = self._default_headers | headers

        if method == "GET":
            response = super().get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = super().post(url, headers=headers, **kwargs)
        else:
            assert False, f"call method '{method}' not implemented"
        return ValidatorResponse.cast(response)

    @property
    def session(self):
        return MockSession(self)

    @property
    def default_headers(self):
        return self._default_headers

    @default_headers.setter
    def default_headers(self, value):
        self._default_headers = value


##TODO
