"""
Creates a test case class for use with the unittest library that is built into Python.
"""
from heaserver.service.testcase import expectedvalues
from heaserver.service.testcase.awss3microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase.collection import CollectionKey
from heaserver.bucket import service
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.service.testcase.dockermongo import DockerMongoManager, RealRegistryContainerConfig
from heaserver.service.testcase.testenv import DockerContainerConfig
from heaobject.user import NONE_USER
from heaobject.registry import Resource
from heaobject.volume import DEFAULT_FILE_SYSTEM
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    service.MONGODB_BUCKET_COLLECTION: [{
        'id': 'hci-foundation-1',
        'created': '2022-05-17T00:00:00+00:00',
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'object_count': None,
        'size': None,
        'display_name': 'hci-foundation-1',
        'invites': [],
        'modified': None,
        'name': 'hci-foundation-1',
        'owner': NONE_USER,
        'shares': [],
        'source': 'AWS Simple Cloud Storage (S3)',
        'type': 'heaobject.bucket.AWSBucket',
        'version': None,
        'arn': None,
        'versioned': None,
        'encrypted': False,
        'region': 'us-west-1',
        'permission_policy': None,
        'tags': [],
        's3_uri': 's3://hci-foundation-1/',
        'locked': False,
        'mime_type': 'application/x.awsbucket'
    },
        {
            'id': 'hci-foundation-2',
            'created': '2022-05-17T00:00:00+00:00',
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'object_count': None,
            'size': None,
            'display_name': 'hci-foundation-2',
            'invites': [],
            'modified': None,
            'name': 'hci-foundation-2',
            'owner': NONE_USER,
            'shares': [],
            'source': 'AWS Simple Cloud Storage (S3)',
            'type': 'heaobject.bucket.AWSBucket',
            'version': None,
            'arn': None,
            'versioned': None,
            'encrypted': False,
            'region': 'us-west-1',
            'permission_policy': None,
            'tags': [],
            's3_uri': 's3://hci-foundation-2/',
            'locked': False,
            'mime_type': 'application/x.awsbucket'
        }

    ],
    CollectionKey(name='filesystems', db_manager_cls=DockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'version': None
    }],
    CollectionKey(name='volumes', db_manager_cls=DockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'My Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.Volume',
        'version': None,
        'file_system_name': 'amazon_web_services',
        'credential_id': None  # Let boto3 try to find the user's credentials.
    }]}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a24'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0a10'
volume_microservice = DockerContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                            resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                base_path='/volumes',
                                                                file_system_name=DEFAULT_FILE_SYSTEM),
                                                       Resource(resource_type_name='heaobject.volume.FileSystem',
                                                                base_path='/filesystems',
                                                                file_system_name=DEFAULT_FILE_SYSTEM)],
                                            db_manager_cls=DockerMongoManager)


def get_test_case_cls(*args, **kwargs):
    """Get a test case class specifically for this microservice."""

    class MyTestCase(get_test_case_cls_default(*args, **kwargs)):
        def __init__(self, *args_, **kwargs_):
            super().__init__(*args_, **kwargs_)
            if self._body_post:
                modified_data = {**db_store[self._coll][0], 'name': 'tritimus', 'display_name': 'tritimus',
                                 's3_uri': 's3://tritimus/', 'versioned': False}
                if 'id' in modified_data:
                    del modified_data['id']
                self._body_post = expectedvalues._create_template(modified_data)

    return MyTestCase


TestCase = \
    get_test_case_cls(coll=service.MONGODB_BUCKET_COLLECTION,
                      wstl_package=service.__package__,
                      href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/',
                      fixtures=db_store,
                      db_manager_cls=MockS3Manager,
                      get_actions=[Action(name='heaserver-buckets-bucket-get-properties',
                                          rel=['hea-properties']),
                                   Action(name='heaserver-buckets-bucket-get-open-choices',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/opener',
                                          rel=['hea-opener-choices']),
                                   Action(name='heaserver-buckets-bucket-duplicate',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/duplicator',
                                          rel=['hea-duplicator'])
                                   ],
                      get_all_actions=[Action(name='heaserver-buckets-bucket-get-properties',
                                              rel=['hea-properties']),
                                       Action(name='heaserver-buckets-bucket-get-open-choices',
                                              url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/opener',
                                              rel=['hea-opener-choices']),
                                       Action(name='heaserver-buckets-bucket-duplicate',
                                              url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/duplicator',
                                              rel=['hea-duplicator'])],
                      duplicate_action_name='heaserver-buckets-bucket-duplicate-form',
                      exclude=['body_put'],
                      registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
                      other_docker_images=[volume_microservice])
