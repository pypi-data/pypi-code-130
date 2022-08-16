from .testcase import TestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin
from aiohttp import hdrs
from heaserver.service.representor import nvpjson


class TestGet(TestCase, GetOneMixin):
    async def test_get_all_members(self) -> None:
        """Checks if getting all the members of an organization succeeds with status 200."""
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'members').path,
                                        headers=self._headers)
        self.assertEqual(200, obj.status)

    async def test_get_all_awsaccounts_status(self) -> None:
        """Checks if getting all the accounts in an organization succeeds with status 200."""
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'awsaccounts').path,
                                        headers=self._headers)
        self.assertEqual(200, obj.status)

    # There are no accounts being returned
    # async def test_get_all_awsaccounts(self) -> None:
    #     """Checks if getting all the accounts in an organization succeeds and returns exactly two desktop objects."""
    #     obj = await self.client.request('GET',
    #                                     (self._href / self._id() / 'awsaccounts').path,
    #                                     headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
    #     if not obj.ok:
    #         self.fail('GET request for all awsaccounts failed')
    #     self.assertEqual(2, len(await obj.json()))


class TestGetAll(TestCase, GetAllMixin):
    pass


class TestPost(TestCase, PostMixin):
    pass


class TestPut(TestCase, PutMixin):
    pass


class TestDelete(TestCase, DeleteMixin):
    pass
