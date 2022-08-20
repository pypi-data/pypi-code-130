# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsonrpc2pyclient']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'jsonrpc2-objects>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'jsonrpc2-pyclient',
    'version': '2.2.12',
    'description': 'Python JSON-RPC 2.0 client library.',
    'long_description': '<div align="center">\n<!-- Title: -->\n  <h1>JSON RPC PyClient</h1>\n<!-- Labels: -->\n  <!-- First row: -->\n  <img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg"\n   height="20"\n   alt="License: AGPL v3">\n  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"\n   height="20"\n   alt="Code style: black">\n  <img src="https://img.shields.io/pypi/v/jsonrpc2-pyclient.svg"\n   height="20"\n   alt="PyPI version">\n  <a href="https://gitlab.com/mburkard/jsonrpc-pyclient/-/blob/main/CONTRIBUTING.md">\n    <img src="https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=00b250"\n     height="20"\n     alt="Contributions Welcome">\n  </a>\n  <h3>A library for creating JSON RPC 2.0 clients in Python with async support</h3>\n</div>\n\n## Install\n\n```shell\npoetry add jsonrpc2-pyclient\n```\n\n```shell\npip install jsonrpc2-pyclient\n```\n\n### RPCClient Abstract Class\n\nJSON-RPC 2.0 is transport agnostic. This library provides an abstract\nclass that can be extended to create clients for different transports.\n\n### Implementations\n\nTo make client for a transport, extend the `RPCClient` class and\nimplement the `_send_and_get_json` which takes a request as a str and is\nexpected to return a JSON-RPC 2.0 response as a str or byte string.\n`RPCClient` has a `call` method that uses this internally.\n\nA default HTTP implementation is provided:\n\n```python\nclass RPCHTTPClient(RPCClient):\n    """A JSON-RPC HTTP Client."""\n\n    def __init__(self, url: str, headers: Optional[Headers] = None) -> None:\n        self._client = httpx.Client()\n        headers = headers or {}\n        headers["Content-Type"] = "application/json"\n        self._client.headers = headers\n        self.url = url\n        super(RPCHTTPClient, self).__init__()\n\n    def __del__(self) -> None:\n        self._client.close()\n\n    @property\n    def headers(self) -> Headers:\n        """HTTP headers to be sent with each request."""\n        return self._client.headers\n\n    @headers.setter\n    def headers(self, headers) -> None:\n        self._client.headers = headers\n\n    def _send_and_get_json(self, request_json: str) -> Union[bytes, str]:\n        return self._client.post(self.url, content=request_json).content\n```\n\n### Usage\n\nThe `RPCClient` will handle forming requests and parsing responses.\nTo call a JSON-RPC 2.0 method with an implementation of `RPCClient`,\ncall the `call` method, passing it the name of the method to call and\nthe params.\n\nIf the response is JSON-RPC 2.0 result object, only the result will be\nreturned, none of the wrapper.\n\nIf the response is JSON-RPC 2.0 error response, and exception will be\nthrown for the error.\n\n```python\nfrom jsonrpc2pyclient.httpclient import RPCHTTPClient\nfrom jsonrpcobjects.errors import JSONRPCError\n\nclient = RPCHTTPClient("http://localhost:5000/api/v1/")\ntry:\n    res = client.call("divide", [0, 0])\n    print(f"JSON-RPC Result: {res}")\nexcept JSONRPCError as e:\n    print(f"JSON-RPC Error: {e}")\n```\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/jsonrpc2-pyclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
