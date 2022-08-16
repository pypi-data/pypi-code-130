from .foldertestcase import ItemTestCase, FolderTestCase
from heaserver.service.testcase.mixin import DeleteMixin, GetAllMixin, GetOneMixin, PutMixin, PostMixin
from heaserver.service.representor import cj
from aiohttp import hdrs


class TestDeleteFolder(FolderTestCase, DeleteMixin):
    pass


class TestGetFolders(FolderTestCase, GetAllMixin):
    pass


class TestGetFolder(FolderTestCase, GetOneMixin):
    async def test_get_status_opener_choices(self) -> None:
        """Checks if a GET request for the opener for a folder succeeds with status 300."""
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'opener').path,
                                        headers=self._headers)
        self.assertEqual(300, obj.status)

    async def test_get_status_opener_hea_default_exists(self) -> None:
        """
        Checks if a GET request for the opener for a folder succeeds and returns JSON that contains a
        Collection+JSON object with a rel property in its links that contains 'hea-default'.
        """
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'opener').path,
                                        headers={**self._headers, hdrs.ACCEPT: cj.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        received_json = await obj.json()
        rel = received_json[0]['collection']['items'][0]['links'][0]['rel']
        self.assertIn('hea-default', rel)


class TestDeleteItem(ItemTestCase, DeleteMixin):
    pass


class TestGetItems(ItemTestCase, GetAllMixin):
    pass


class TestGetItem(ItemTestCase, GetOneMixin):
    async def test_get_mover_status(self):
        """Checks if a GET request for the mover for an item in a folder succeeds with status 200."""
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'mover').path,
                                        headers=self._headers)
        self.assertEqual(200, obj.status)

    async def test_get_by_name(self):
        self.skipTest('items do not support GET by name')


class TestPostItem(ItemTestCase, PostMixin):
    # async def test_post_mover_status(self):
    #     """Checks if a POST request to post the mover for an item in a folder succeeds with status 201."""
    #     obj = await self.client.request('POST',
    #                                     self._href.path.replace('items/', 'mover'),
    #                                     json=self._body_post,
    #                                     headers=self._headers)
    #     self.assertEqual(201, obj.status)

    async def test_post_then_get(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_nvpjson(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_xwwwformurlencoded(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_status(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_status_nvpjson(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_status_xwwwformurlencoded(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_post_then_get_valid_invites_none(self) -> None:
        self.skipTest('this test is not yet supported')


class TestPutItem(ItemTestCase, PutMixin):
    async def test_put_then_get(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_put_then_get_nvpjson(self) -> None:
        self.skipTest('this test is not yet supported')

    async def test_put_then_get_valid_invites_none(self) -> None:
        self.skipTest('this test is not yet supported')
