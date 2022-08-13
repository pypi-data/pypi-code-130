# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import pulpcore.client.pulp_rpm
from pulpcore.client.pulp_rpm.models.rpm_modulemd_obsolete import RpmModulemdObsolete  # noqa: E501
from pulpcore.client.pulp_rpm.rest import ApiException

class TestRpmModulemdObsolete(unittest.TestCase):
    """RpmModulemdObsolete unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test RpmModulemdObsolete
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = pulpcore.client.pulp_rpm.models.rpm_modulemd_obsolete.RpmModulemdObsolete()  # noqa: E501
        if include_optional :
            return RpmModulemdObsolete(
                artifact = '0', 
                relative_path = '0', 
                file = bytes(b'blah'), 
                repository = '0', 
                upload = '0', 
                modified = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                module_name = '0', 
                module_stream = '0', 
                message = '0', 
                override_previous = '0', 
                module_context = '0', 
                eol_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                obsoleted_by_module_name = '0', 
                obsoleted_by_module_stream = '0', 
                snippet = '0'
            )
        else :
            return RpmModulemdObsolete(
                relative_path = '0',
                modified = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                module_name = '0',
                module_stream = '0',
                message = '0',
                override_previous = '0',
                module_context = '0',
                eol_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                obsoleted_by_module_name = '0',
                obsoleted_by_module_stream = '0',
                snippet = '0',
        )

    def testRpmModulemdObsolete(self):
        """Test RpmModulemdObsolete"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
