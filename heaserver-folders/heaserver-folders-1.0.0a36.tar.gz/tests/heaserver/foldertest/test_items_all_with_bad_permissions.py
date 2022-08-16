from .folderpermissionstestcase import ItemPermissionsTestCase, FolderPermissionsTestCase
from heaserver.service.testcase.mixin import PermissionsDeleteMixin, PermissionsGetAllMixin, PermissionsGetOneMixin, \
    PermissionsPutMixin, PermissionsPostMixin


class TestDeleteFolderWithBadPermissions(FolderPermissionsTestCase, PermissionsDeleteMixin):
    pass


class TestGetFoldersWithBadPermissions(FolderPermissionsTestCase, PermissionsGetAllMixin):
    pass


class TestGetFolderWithBadPermissions(FolderPermissionsTestCase, PermissionsGetOneMixin):
    pass


class TestDeleteItemWithBadPermissions(ItemPermissionsTestCase, PermissionsDeleteMixin):
    async def test_delete_some_permissions_status(self) -> None:
        self.skipTest('this test is not yet supported')


class TestGetItemsWithBadPermissions(ItemPermissionsTestCase, PermissionsGetAllMixin):
    pass


class TestGetItemWithBadPermissions(ItemPermissionsTestCase, PermissionsGetOneMixin):
    async def test_get_mover_status(self):
        """
        Checks if a GET request for the mover for an item in a folder fails with status 404 when the user has bad
        permissions.
        """
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'mover').path,
                                        headers=self._headers)
        self.assertEqual(404, obj.status)


class TestPostItemWithBadPermissions(ItemPermissionsTestCase, PermissionsPostMixin):
    pass


class TestPutItemWithBadPermissions(ItemPermissionsTestCase, PermissionsPutMixin):
    pass
