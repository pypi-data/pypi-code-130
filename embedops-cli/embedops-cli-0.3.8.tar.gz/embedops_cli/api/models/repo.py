# coding: utf-8

"""
    EmbedOps API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 1.0.0
    Contact: support@embedops.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class Repo(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        "name": "str",
        "uri": "str",
        "ci_provider": "str",
        "ci_o_auth_token_id": "str",
        "desc": "str",
        "default_branch": "str",
        "created_at": "datetime",
        "id": "str",
        "project_id": "str",
        "updated_at": "datetime",
    }

    attribute_map = {
        "name": "name",
        "uri": "uri",
        "ci_provider": "ciProvider",
        "ci_o_auth_token_id": "ciOAuthTokenId",
        "desc": "desc",
        "default_branch": "defaultBranch",
        "created_at": "createdAt",
        "id": "id",
        "project_id": "projectId",
        "updated_at": "updatedAt",
    }

    def __init__(
        self,
        name=None,
        uri=None,
        ci_provider=None,
        ci_o_auth_token_id=None,
        desc=None,
        default_branch=None,
        created_at=None,
        id=None,
        project_id=None,
        updated_at=None,
    ):  # noqa: E501
        """Repo - a model defined in Swagger"""  # noqa: E501
        self._name = None
        self._uri = None
        self._ci_provider = None
        self._ci_o_auth_token_id = None
        self._desc = None
        self._default_branch = None
        self._created_at = None
        self._id = None
        self._project_id = None
        self._updated_at = None
        self.discriminator = None
        self.name = name
        self.uri = uri
        if ci_provider is not None:
            self.ci_provider = ci_provider
        if ci_o_auth_token_id is not None:
            self.ci_o_auth_token_id = ci_o_auth_token_id
        if desc is not None:
            self.desc = desc
        if default_branch is not None:
            self.default_branch = default_branch
        self.created_at = created_at
        self.id = id
        self.project_id = project_id
        self.updated_at = updated_at

    @property
    def name(self):
        """Gets the name of this Repo.  # noqa: E501


        :return: The name of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Repo.


        :param name: The name of this Repo.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError(
                "Invalid value for `name`, must not be `None`"
            )  # noqa: E501

        self._name = name

    @property
    def uri(self):
        """Gets the uri of this Repo.  # noqa: E501


        :return: The uri of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._uri

    @uri.setter
    def uri(self, uri):
        """Sets the uri of this Repo.


        :param uri: The uri of this Repo.  # noqa: E501
        :type: str
        """
        if uri is None:
            raise ValueError(
                "Invalid value for `uri`, must not be `None`"
            )  # noqa: E501

        self._uri = uri

    @property
    def ci_provider(self):
        """Gets the ci_provider of this Repo.  # noqa: E501


        :return: The ci_provider of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._ci_provider

    @ci_provider.setter
    def ci_provider(self, ci_provider):
        """Sets the ci_provider of this Repo.


        :param ci_provider: The ci_provider of this Repo.  # noqa: E501
        :type: str
        """
        allowed_values = ["github", "gitlab", "bitbucket", ""]  # noqa: E501
        if ci_provider not in allowed_values:
            raise ValueError(
                "Invalid value for `ci_provider` ({0}), must be one of {1}".format(  # noqa: E501
                    ci_provider, allowed_values
                )
            )

        self._ci_provider = ci_provider

    @property
    def ci_o_auth_token_id(self):
        """Gets the ci_o_auth_token_id of this Repo.  # noqa: E501


        :return: The ci_o_auth_token_id of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._ci_o_auth_token_id

    @ci_o_auth_token_id.setter
    def ci_o_auth_token_id(self, ci_o_auth_token_id):
        """Sets the ci_o_auth_token_id of this Repo.


        :param ci_o_auth_token_id: The ci_o_auth_token_id of this Repo.  # noqa: E501
        :type: str
        """

        self._ci_o_auth_token_id = ci_o_auth_token_id

    @property
    def desc(self):
        """Gets the desc of this Repo.  # noqa: E501


        :return: The desc of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._desc

    @desc.setter
    def desc(self, desc):
        """Sets the desc of this Repo.


        :param desc: The desc of this Repo.  # noqa: E501
        :type: str
        """

        self._desc = desc

    @property
    def default_branch(self):
        """Gets the default_branch of this Repo.  # noqa: E501


        :return: The default_branch of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._default_branch

    @default_branch.setter
    def default_branch(self, default_branch):
        """Sets the default_branch of this Repo.


        :param default_branch: The default_branch of this Repo.  # noqa: E501
        :type: str
        """

        self._default_branch = default_branch

    @property
    def created_at(self):
        """Gets the created_at of this Repo.  # noqa: E501


        :return: The created_at of this Repo.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Repo.


        :param created_at: The created_at of this Repo.  # noqa: E501
        :type: datetime
        """
        if created_at is None:
            raise ValueError(
                "Invalid value for `created_at`, must not be `None`"
            )  # noqa: E501

        self._created_at = created_at

    @property
    def id(self):
        """Gets the id of this Repo.  # noqa: E501


        :return: The id of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Repo.


        :param id: The id of this Repo.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def project_id(self):
        """Gets the project_id of this Repo.  # noqa: E501


        :return: The project_id of this Repo.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this Repo.


        :param project_id: The project_id of this Repo.  # noqa: E501
        :type: str
        """
        if project_id is None:
            raise ValueError(
                "Invalid value for `project_id`, must not be `None`"
            )  # noqa: E501

        self._project_id = project_id

    @property
    def updated_at(self):
        """Gets the updated_at of this Repo.  # noqa: E501


        :return: The updated_at of this Repo.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this Repo.


        :param updated_at: The updated_at of this Repo.  # noqa: E501
        :type: datetime
        """
        if updated_at is None:
            raise ValueError(
                "Invalid value for `updated_at`, must not be `None`"
            )  # noqa: E501

        self._updated_at = updated_at

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(Repo, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Repo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
