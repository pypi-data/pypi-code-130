# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from pulpcore.client.pulp_rpm.configuration import Configuration


class RpmModulemdObsoleteResponse(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'pulp_href': 'str',
        'pulp_created': 'datetime',
        'artifact': 'str',
        'modified': 'datetime',
        'module_name': 'str',
        'module_stream': 'str',
        'message': 'str',
        'override_previous': 'str',
        'module_context': 'str',
        'eol_date': 'datetime',
        'obsoleted_by_module_name': 'str',
        'obsoleted_by_module_stream': 'str'
    }

    attribute_map = {
        'pulp_href': 'pulp_href',
        'pulp_created': 'pulp_created',
        'artifact': 'artifact',
        'modified': 'modified',
        'module_name': 'module_name',
        'module_stream': 'module_stream',
        'message': 'message',
        'override_previous': 'override_previous',
        'module_context': 'module_context',
        'eol_date': 'eol_date',
        'obsoleted_by_module_name': 'obsoleted_by_module_name',
        'obsoleted_by_module_stream': 'obsoleted_by_module_stream'
    }

    def __init__(self, pulp_href=None, pulp_created=None, artifact=None, modified=None, module_name=None, module_stream=None, message=None, override_previous=None, module_context=None, eol_date=None, obsoleted_by_module_name=None, obsoleted_by_module_stream=None, local_vars_configuration=None):  # noqa: E501
        """RpmModulemdObsoleteResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pulp_href = None
        self._pulp_created = None
        self._artifact = None
        self._modified = None
        self._module_name = None
        self._module_stream = None
        self._message = None
        self._override_previous = None
        self._module_context = None
        self._eol_date = None
        self._obsoleted_by_module_name = None
        self._obsoleted_by_module_stream = None
        self.discriminator = None

        if pulp_href is not None:
            self.pulp_href = pulp_href
        if pulp_created is not None:
            self.pulp_created = pulp_created
        if artifact is not None:
            self.artifact = artifact
        self.modified = modified
        self.module_name = module_name
        self.module_stream = module_stream
        self.message = message
        self.override_previous = override_previous
        self.module_context = module_context
        self.eol_date = eol_date
        self.obsoleted_by_module_name = obsoleted_by_module_name
        self.obsoleted_by_module_stream = obsoleted_by_module_stream

    @property
    def pulp_href(self):
        """Gets the pulp_href of this RpmModulemdObsoleteResponse.  # noqa: E501


        :return: The pulp_href of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp_href

    @pulp_href.setter
    def pulp_href(self, pulp_href):
        """Sets the pulp_href of this RpmModulemdObsoleteResponse.


        :param pulp_href: The pulp_href of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._pulp_href = pulp_href

    @property
    def pulp_created(self):
        """Gets the pulp_created of this RpmModulemdObsoleteResponse.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The pulp_created of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._pulp_created

    @pulp_created.setter
    def pulp_created(self, pulp_created):
        """Sets the pulp_created of this RpmModulemdObsoleteResponse.

        Timestamp of creation.  # noqa: E501

        :param pulp_created: The pulp_created of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: datetime
        """

        self._pulp_created = pulp_created

    @property
    def artifact(self):
        """Gets the artifact of this RpmModulemdObsoleteResponse.  # noqa: E501

        Artifact file representing the physical content  # noqa: E501

        :return: The artifact of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._artifact

    @artifact.setter
    def artifact(self, artifact):
        """Sets the artifact of this RpmModulemdObsoleteResponse.

        Artifact file representing the physical content  # noqa: E501

        :param artifact: The artifact of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._artifact = artifact

    @property
    def modified(self):
        """Gets the modified of this RpmModulemdObsoleteResponse.  # noqa: E501

        Obsolete modified time.  # noqa: E501

        :return: The modified of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._modified

    @modified.setter
    def modified(self, modified):
        """Sets the modified of this RpmModulemdObsoleteResponse.

        Obsolete modified time.  # noqa: E501

        :param modified: The modified of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and modified is None:  # noqa: E501
            raise ValueError("Invalid value for `modified`, must not be `None`")  # noqa: E501

        self._modified = modified

    @property
    def module_name(self):
        """Gets the module_name of this RpmModulemdObsoleteResponse.  # noqa: E501

        Modulemd name.  # noqa: E501

        :return: The module_name of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._module_name

    @module_name.setter
    def module_name(self, module_name):
        """Sets the module_name of this RpmModulemdObsoleteResponse.

        Modulemd name.  # noqa: E501

        :param module_name: The module_name of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and module_name is None:  # noqa: E501
            raise ValueError("Invalid value for `module_name`, must not be `None`")  # noqa: E501

        self._module_name = module_name

    @property
    def module_stream(self):
        """Gets the module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501

        Modulemd's stream.  # noqa: E501

        :return: The module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._module_stream

    @module_stream.setter
    def module_stream(self, module_stream):
        """Sets the module_stream of this RpmModulemdObsoleteResponse.

        Modulemd's stream.  # noqa: E501

        :param module_stream: The module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and module_stream is None:  # noqa: E501
            raise ValueError("Invalid value for `module_stream`, must not be `None`")  # noqa: E501

        self._module_stream = module_stream

    @property
    def message(self):
        """Gets the message of this RpmModulemdObsoleteResponse.  # noqa: E501

        Obsolete description.  # noqa: E501

        :return: The message of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this RpmModulemdObsoleteResponse.

        Obsolete description.  # noqa: E501

        :param message: The message of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and message is None:  # noqa: E501
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def override_previous(self):
        """Gets the override_previous of this RpmModulemdObsoleteResponse.  # noqa: E501

        Reset previous obsoletes.  # noqa: E501

        :return: The override_previous of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._override_previous

    @override_previous.setter
    def override_previous(self, override_previous):
        """Sets the override_previous of this RpmModulemdObsoleteResponse.

        Reset previous obsoletes.  # noqa: E501

        :param override_previous: The override_previous of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._override_previous = override_previous

    @property
    def module_context(self):
        """Gets the module_context of this RpmModulemdObsoleteResponse.  # noqa: E501

        Modulemd's context.  # noqa: E501

        :return: The module_context of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._module_context

    @module_context.setter
    def module_context(self, module_context):
        """Sets the module_context of this RpmModulemdObsoleteResponse.

        Modulemd's context.  # noqa: E501

        :param module_context: The module_context of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._module_context = module_context

    @property
    def eol_date(self):
        """Gets the eol_date of this RpmModulemdObsoleteResponse.  # noqa: E501

        End of Life date.  # noqa: E501

        :return: The eol_date of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._eol_date

    @eol_date.setter
    def eol_date(self, eol_date):
        """Sets the eol_date of this RpmModulemdObsoleteResponse.

        End of Life date.  # noqa: E501

        :param eol_date: The eol_date of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: datetime
        """

        self._eol_date = eol_date

    @property
    def obsoleted_by_module_name(self):
        """Gets the obsoleted_by_module_name of this RpmModulemdObsoleteResponse.  # noqa: E501

        Obsolete by module name.  # noqa: E501

        :return: The obsoleted_by_module_name of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._obsoleted_by_module_name

    @obsoleted_by_module_name.setter
    def obsoleted_by_module_name(self, obsoleted_by_module_name):
        """Sets the obsoleted_by_module_name of this RpmModulemdObsoleteResponse.

        Obsolete by module name.  # noqa: E501

        :param obsoleted_by_module_name: The obsoleted_by_module_name of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._obsoleted_by_module_name = obsoleted_by_module_name

    @property
    def obsoleted_by_module_stream(self):
        """Gets the obsoleted_by_module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501

        Obsolete by module stream.  # noqa: E501

        :return: The obsoleted_by_module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501
        :rtype: str
        """
        return self._obsoleted_by_module_stream

    @obsoleted_by_module_stream.setter
    def obsoleted_by_module_stream(self, obsoleted_by_module_stream):
        """Sets the obsoleted_by_module_stream of this RpmModulemdObsoleteResponse.

        Obsolete by module stream.  # noqa: E501

        :param obsoleted_by_module_stream: The obsoleted_by_module_stream of this RpmModulemdObsoleteResponse.  # noqa: E501
        :type: str
        """

        self._obsoleted_by_module_stream = obsoleted_by_module_stream

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, RpmModulemdObsoleteResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RpmModulemdObsoleteResponse):
            return True

        return self.to_dict() != other.to_dict()
