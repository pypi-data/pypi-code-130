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


class Project(object):
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
        "created_at": "datetime",
        "id": "str",
        "org_id": "str",
        "repo_ids": "list[str]",
        "updated_at": "datetime",
    }

    attribute_map = {
        "name": "name",
        "created_at": "createdAt",
        "id": "id",
        "org_id": "orgId",
        "repo_ids": "repoIds",
        "updated_at": "updatedAt",
    }

    def __init__(
        self,
        name=None,
        created_at=None,
        id=None,
        org_id=None,
        repo_ids=None,
        updated_at=None,
    ):  # noqa: E501
        """Project - a model defined in Swagger"""  # noqa: E501
        self._name = None
        self._created_at = None
        self._id = None
        self._org_id = None
        self._repo_ids = None
        self._updated_at = None
        self.discriminator = None
        self.name = name
        self.created_at = created_at
        self.id = id
        self.org_id = org_id
        if repo_ids is not None:
            self.repo_ids = repo_ids
        self.updated_at = updated_at

    @property
    def name(self):
        """Gets the name of this Project.  # noqa: E501


        :return: The name of this Project.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Project.


        :param name: The name of this Project.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError(
                "Invalid value for `name`, must not be `None`"
            )  # noqa: E501

        self._name = name

    @property
    def created_at(self):
        """Gets the created_at of this Project.  # noqa: E501


        :return: The created_at of this Project.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Project.


        :param created_at: The created_at of this Project.  # noqa: E501
        :type: datetime
        """
        if created_at is None:
            raise ValueError(
                "Invalid value for `created_at`, must not be `None`"
            )  # noqa: E501

        self._created_at = created_at

    @property
    def id(self):
        """Gets the id of this Project.  # noqa: E501


        :return: The id of this Project.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Project.


        :param id: The id of this Project.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def org_id(self):
        """Gets the org_id of this Project.  # noqa: E501


        :return: The org_id of this Project.  # noqa: E501
        :rtype: str
        """
        return self._org_id

    @org_id.setter
    def org_id(self, org_id):
        """Sets the org_id of this Project.


        :param org_id: The org_id of this Project.  # noqa: E501
        :type: str
        """
        if org_id is None:
            raise ValueError(
                "Invalid value for `org_id`, must not be `None`"
            )  # noqa: E501

        self._org_id = org_id

    @property
    def repo_ids(self):
        """Gets the repo_ids of this Project.  # noqa: E501


        :return: The repo_ids of this Project.  # noqa: E501
        :rtype: list[str]
        """
        return self._repo_ids

    @repo_ids.setter
    def repo_ids(self, repo_ids):
        """Sets the repo_ids of this Project.


        :param repo_ids: The repo_ids of this Project.  # noqa: E501
        :type: list[str]
        """

        self._repo_ids = repo_ids

    @property
    def updated_at(self):
        """Gets the updated_at of this Project.  # noqa: E501


        :return: The updated_at of this Project.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this Project.


        :param updated_at: The updated_at of this Project.  # noqa: E501
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
        if issubclass(Project, dict):
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
        if not isinstance(other, Project):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
