"""
Creates a test case class for use with the unittest library that is build into Python.
"""

from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.dataadapter import service
from heaobject.user import NONE_USER, TEST_USER
from heaobject.root import Permission
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    service.MONGO_DATA_ADAPTER_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invites': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.dataadapter.DelimitedFileAdapter',
        'version': None,
        'base_url': 'http://localhost/foo',
        'resources': []
    },
        {
            'id': '0123456789ab0123456789ab',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Luximus',
            'invites': [],
            'modified': None,
            'name': 'luximus',
            'owner': NONE_USER,
            'shares': [{
                'type': 'heaobject.root.ShareImpl',
                'invite': None,
                'user': TEST_USER,
                'permissions': [Permission.VIEWER.name]
            }],
            'source': None,
            'type': 'heaobject.dataadapter.DelimitedFileAdapter',
            'version': None,
            'encoding': 'utf-8',
            'line_ending': '\r\n',
        }]}


DataAdapterPermissionsTestCase = \
    get_test_case_cls_default(coll=service.MONGO_DATA_ADAPTER_COLLECTION,
                              href='http://localhost:8080/dataadapters/',
                              wstl_package=service.__package__,
                              fixtures=db_store,
                              get_actions=[
                                  Action(
                                      name='heaserver-data-adapters-data-adapter-get-properties',
                                      rel=['hea-properties']),
                                  Action(name='heaserver-data-adapters-data-adapter-duplicate',
                                         url='http://localhost:8080/dataadapters/{id}/duplicator',
                                         rel=['hea-duplicator'])
                              ],
                              get_all_actions=[
                                  Action(
                                      name='heaserver-data-adapters-data-adapter-get-properties',
                                      rel=['hea-properties']),
                                  Action(name='heaserver-data-adapters-data-adapter-duplicate',
                                         url='http://localhost:8080/dataadapters/{id}/duplicator',
                                         rel=['hea-duplicator'])],
                              duplicate_action_name='heaserver-data-adapters-data-adapter-duplicate-form',
                              put_content_status=404,
                              sub=TEST_USER)
