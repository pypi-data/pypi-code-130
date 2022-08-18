import json

from .utils import urljoin

class ResourcePool:
    def __init__(self, endpoint, session, timeout=10):
        """Initialize the ResourcePool to the given endpoint. Eg: products"""
        self._endpoint = endpoint
        self._session = session
        self._timeout = timeout

    def get_url(self):
        return self._endpoint

class CreatableResource:
    def create_item(self, item, files=None):
        if files:
            res = self._session.post(self._endpoint, files=files, data=item, timeout=self._timeout)
        else:
            res = self._session.post(self._endpoint, data=json.dumps(item), timeout=self._timeout)
        return res

class GQLResource:
    def query(self, payload, custom_headers=None):
        self._session.headers.update({
            'content-type': 'application/json; charset=utf-8',
            'apollographql-client-name': 'Iron',
            'app-version': '2022.07.31.05',
        })
        if custom_headers:
            self._session.headers.update(custom_headers)        
        res = self._session.post(self._endpoint, data=json.dumps(payload), timeout=self._timeout)
        if custom_headers:
            for k in custom_headers.keys():
                self._session.headers.pop(k)                
        self._session.headers.pop('content-type')
        self._session.headers.pop('apollographql-client-name')
        self._session.headers.pop('app-version')
        return res

class GettableResource:
    def fetch_item(self, code, params=None, custom_headers=None):
        if custom_headers:
            self._session.headers.update(custom_headers)

        url = urljoin(self._endpoint, code)
        res = self._session.get(url, params=params, timeout=self._timeout)

        if custom_headers:
            for k in custom_headers.keys():
                self._session.headers.pop(k)        
        return res

class ListableResource:
    def fetch_list(self, params=None, custom_headers=None):
        if custom_headers:
            self._session.headers.update(custom_headers)

        res = self._session.get(self._endpoint, params=params, timeout=self._timeout)

        if custom_headers:
            for k in custom_headers.keys():
                self._session.headers.pop(k)
        return res

class UpdatableResource:
    def update_create_item(self, item, code=None, params=None):
        if code is None:
            code = item.get('id')
        url = urljoin(self._endpoint, code) if code else self._endpoint
        res = self._session.put(url, data=json.dumps(item), params=params, timeout=self._timeout)
        return res

class DeletableResource:
    def delete_item(self, code):
        url = urljoin(self._endpoint, code)
        res = self._session.delete(url, timeout=self._timeout)
        return res

# Pools

class BrowsePool(
    ResourcePool,
    ListableResource
):
    pass

class GQLPool(
    ResourcePool,
    GQLResource
):
    pass

class ProductActivityPool(
    ResourcePool,
    ListableResource
):
    pass

class ProductsPool(
    ResourcePool,
    ListableResource,
    GettableResource
):
    def activity(self, product_id):
        return ProductActivityPool(
            urljoin(self._endpoint, product_id, 'activity'), self._session
        )
