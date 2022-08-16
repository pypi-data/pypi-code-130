from .permissionstestcase import PermissionsTestCase
from heaserver.service.testcase.mixin import PermissionsGetOneMixin, PermissionsGetAllMixin, PermissionsPostMixin, \
    PermissionsPutMixin, PermissionsDeleteMixin


class TestGetWithBadPermissions(PermissionsTestCase, PermissionsGetOneMixin):
    pass


class TestGetAllWithBadPermissions(PermissionsTestCase, PermissionsGetAllMixin):
    pass


class TestPostWithBadPermissions(PermissionsTestCase, PermissionsPostMixin):
    pass


class TestPutWithBadPermissions(PermissionsTestCase, PermissionsPutMixin):
    pass


class TestDeleteWithBadPermissions(PermissionsTestCase, PermissionsDeleteMixin):
    pass
