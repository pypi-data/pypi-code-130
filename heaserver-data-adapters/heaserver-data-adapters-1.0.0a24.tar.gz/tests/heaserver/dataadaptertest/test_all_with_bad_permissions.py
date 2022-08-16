from .dataadapterpermissionstestcase import DataAdapterPermissionsTestCase
from heaserver.service.testcase.mixin import PermissionsGetOneMixin, PermissionsGetAllMixin, PermissionsPostMixin, \
    PermissionsPutMixin, PermissionsDeleteMixin


class TestGetComponent(DataAdapterPermissionsTestCase, PermissionsGetOneMixin):
    pass


class TestGetAllComponents(DataAdapterPermissionsTestCase, PermissionsGetAllMixin):
    pass


class TestPostComponent(DataAdapterPermissionsTestCase, PermissionsPostMixin):
    pass


class TestPutComponent(DataAdapterPermissionsTestCase, PermissionsPutMixin):
    pass


class TestDeleteComponent(DataAdapterPermissionsTestCase, PermissionsDeleteMixin):
    pass
