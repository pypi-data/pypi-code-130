"""
This module is a custom loader for Python which enables importing http files
directly into Python programs simply through usage of the `import` statement.
You can import this module with `import httpfile.loader` and then afterwards you
can `import your_http_file` which will automatically compile and instantiate
`your_http_file.http` and hook it up into Python's module system.
"""

import sys
import os.path

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

import httpx

from httpfile import parse_httpfile, HttpTarget


# Mostly copied from
# https://stackoverflow.com/questions/43571737/how-to-implement-an-import-hook-that-can-modify-the-source-code-on-the-fly-using

class _HttpfileMetaFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):  # type: ignore
        if path is None or path == "":
            path = [os.getcwd()]  # top level import --
            path.extend(sys.path)
        if "." in fullname:
            *parents, name = fullname.split(".")
        else:
            name = fullname
        for entry in path:
            py = os.path.join(str(entry), name + ".py")
            if os.path.exists(py):
                continue
            httpfile_name = os.path.join(str(entry), name + ".http")
            if os.path.exists(httpfile_name):
                return spec_from_file_location(fullname, httpfile_name, loader=_HttpfileLoader(httpfile_name))

        return None


def create_request(http_target: HttpTarget):
    def http_request(**params):
        method = http_target.method
        http_url = http_target.get_url(**params)
        http_headers = http_target.get_http_headers(**params)
        if method == "GET":
            return httpx.get(http_url, headers=http_headers)
        elif method == "DELETE":
            return httpx.delete(http_url, headers=http_headers)
        elif method == "POST":
            return httpx.post(http_url, headers=http_headers, content=http_target.get_http_body(**params))
        elif method == "PUT":
            return httpx.put(http_url, headers=http_headers, content=http_target.get_http_body(**params))
        elif method == "GRAPHQL":
            graphql_doc = http_target.get_graphql_document(**params)
            return httpx.post(http_url, headers=http_headers, json=graphql_doc)
        else:
            raise Exception("http request not found: " + http_target.name)

    return http_request


def create_async_request(http_target: HttpTarget):
    async def async_http_request(**params):
        method = http_target.method
        http_url = http_target.get_url(**params)
        http_headers = http_target.get_http_headers(**params)
        async with httpx.AsyncClient() as client:
            if method == "GET":
                return await client.get(http_url, headers=http_headers)
            elif method == "DELETE":
                return await client.delete(http_url, headers=http_headers)
            elif method == "POST":
                return await client.post(http_url, headers=http_headers, content=http_target.get_http_body(**params))
            elif method == "PUT":
                return await client.put(http_url, headers=http_headers, content=http_target.get_http_body(**params))
            elif method == "GRAPHQL":
                graphql_doc = http_target.get_graphql_document(**params)
                return await client.post(http_url, headers=http_headers, json=graphql_doc)
            else:
                raise Exception("http request not found: " + http_target.name)

    return async_http_request


class _HttpfileLoader(Loader):
    def __init__(self, filename: str):
        self.filename = filename

    def create_module(self, spec):  # type: ignore
        return None  # use default module creation semantics

    def exec_module(self, module):  # type: ignore
        with open(self.filename) as f:
            httpfile_text = f.read()
            targets = parse_httpfile(httpfile_text)
        for target in targets:
            module.__dict__[target.name] = create_request(target)
        for target in targets:
            module.__dict__["async_" + target.name] = create_async_request(target)


sys.meta_path.insert(0, _HttpfileMetaFinder())
