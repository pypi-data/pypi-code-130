from .testcase import TestCase, db_store as fixtures
from .permissionstestcase import PermissionsTestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin, \
    PermissionsPostMixin, PermissionsPutMixin, PermissionsGetOneMixin, PermissionsGetAllMixin, PermissionsDeleteMixin, \
    _copy_heaobject_dict_with
from heaserver.service.testcase.expectedvalues import _create_template
from heaserver.service.representor import cj, nvpjson
from aiohttp import hdrs
import aiohttp.client_exceptions
from yarl import URL
from datetime import date


class TestGet(TestCase, GetOneMixin):
    pass


class TestGetAll(TestCase, GetAllMixin):
    pass


class TestPost(TestCase, PostMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        modified_data = {**fixtures[self._coll][0], **{'name': 'tritimus', 'first_name': 'Tritimus',
                                                       'last_name': 'Maximus', 'display_name': 'Tritimus Maximus'}}
        if 'id' in modified_data:
            del modified_data['id']
        self._body_post = _create_template(modified_data)

    async def test_post_then_get_bad_display_name(self):
        """
        Checks if, during a POST request, the display name of the Person object is updated to reflect the first and
        last names of the person by performing a GET request and comparing the input with the output. The test is
        skipped if the body to POST (``_body_post``) is not defined.
        """
        if self._body_post:
            body_post = _copy_heaobject_dict_with(cj.to_nvpjson(self._body_post), {'display_name': 'Bob'})
            response = await self.client.request('POST',
                                                 (self._href / '').path,
                                                 json=body_post,
                                                 headers={**self._headers, hdrs.CONTENT_TYPE: nvpjson.MIME_TYPE})
            response2 = await self.client.request('GET',
                                                  URL(response.headers.get(hdrs.LOCATION)).path,
                                                  headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
            for k, v in body_post.items():
                if isinstance(v, date):
                    body_post[k] = v.isoformat()
            try:
                received_json = next(iter(await response2.json()), None)
                if received_json is None:
                    self.fail('No JSON received')
                self.assertNotEqual(body_post['display_name'], received_json.get('display_name'))
            except aiohttp.client_exceptions.ContentTypeError as e:
                raise AssertionError(f'POST did not post, so GET failed: {e}') from e
        else:
            self.skipTest('_body_post not defined')


class TestPut(TestCase, PutMixin):
    pass


class TestDelete(TestCase, DeleteMixin):
    pass


class TestPostWithBadPermissions(PermissionsTestCase, PermissionsPostMixin):
    """A test case class for testing POST requests with bad permissions."""
    pass


class TestPutWithBadPermissions(PermissionsTestCase, PermissionsPutMixin):
    """A test case class for testing PUT requests with bad permissions."""
    async def test_put_content_bad_permissions(self) -> None:
        self.skipTest('PUT content not defined')

    async def test_put_content_no_permissions_status(self) -> None:
        self.skipTest('PUT content not defined')

    async def test_put_content_some_permissions_status(self) -> None:
        self.skipTest('PUT content not defined')


class TestGetOneWithBadPermissions(PermissionsTestCase, PermissionsGetOneMixin):
    """A test case class for testing GET one requests with bad permissions."""
    async def test_get_content_bad_permissions(self) -> None:
        self.skipTest('GET content not defined')

    async def test_get_content_bad_permissions_status(self) -> None:
        self.skipTest('GET content not defined')


class TestGetAllWithBadPermissions(PermissionsTestCase, PermissionsGetAllMixin):
    """A test case class for testing GET all requests with bad permissions."""
    pass


class TestDeleteWithBadPermissions(PermissionsTestCase, PermissionsDeleteMixin):
    """A test case class for testing DELETE requests with bad permissions."""
    pass
