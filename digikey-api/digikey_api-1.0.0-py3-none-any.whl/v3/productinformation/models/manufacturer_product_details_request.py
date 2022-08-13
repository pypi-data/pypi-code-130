# coding: utf-8

"""
    PartSearch Api

    Search for products and retrieve details and pricing.  # noqa: E501

    OpenAPI spec version: v3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class ManufacturerProductDetailsRequest(object):
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
        'manufacturer_product': 'str',
        'record_count': 'int',
        'record_start_position': 'int',
        'filters': 'Filters',
        'sort': 'SortParameters',
        'requested_quantity': 'int',
        'search_options': 'list[SearchOption]'
    }

    attribute_map = {
        'manufacturer_product': 'ManufacturerProduct',
        'record_count': 'RecordCount',
        'record_start_position': 'RecordStartPosition',
        'filters': 'Filters',
        'sort': 'Sort',
        'requested_quantity': 'RequestedQuantity',
        'search_options': 'SearchOptions'
    }

    def __init__(self, manufacturer_product=None, record_count=None, record_start_position=None, filters=None, sort=None, requested_quantity=None, search_options=None):  # noqa: E501
        """ManufacturerProductDetailsRequest - a model defined in Swagger"""  # noqa: E501

        self._manufacturer_product = None
        self._record_count = None
        self._record_start_position = None
        self._filters = None
        self._sort = None
        self._requested_quantity = None
        self._search_options = None
        self.discriminator = None

        self.manufacturer_product = manufacturer_product
        if record_count is not None:
            self.record_count = record_count
        if record_start_position is not None:
            self.record_start_position = record_start_position
        if filters is not None:
            self.filters = filters
        if sort is not None:
            self.sort = sort
        if requested_quantity is not None:
            self.requested_quantity = requested_quantity
        if search_options is not None:
            self.search_options = search_options

    @property
    def manufacturer_product(self):
        """Gets the manufacturer_product of this ManufacturerProductDetailsRequest.  # noqa: E501

        Manufacturer product name to search on.  # noqa: E501

        :return: The manufacturer_product of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: str
        """
        return self._manufacturer_product

    @manufacturer_product.setter
    def manufacturer_product(self, manufacturer_product):
        """Sets the manufacturer_product of this ManufacturerProductDetailsRequest.

        Manufacturer product name to search on.  # noqa: E501

        :param manufacturer_product: The manufacturer_product of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: str
        """
        if manufacturer_product is None:
            raise ValueError("Invalid value for `manufacturer_product`, must not be `None`")  # noqa: E501
        if manufacturer_product is not None and len(manufacturer_product) > 250:
            raise ValueError("Invalid value for `manufacturer_product`, length must be less than or equal to `250`")  # noqa: E501
        if manufacturer_product is not None and len(manufacturer_product) < 1:
            raise ValueError("Invalid value for `manufacturer_product`, length must be greater than or equal to `1`")  # noqa: E501

        self._manufacturer_product = manufacturer_product

    @property
    def record_count(self):
        """Gets the record_count of this ManufacturerProductDetailsRequest.  # noqa: E501

        Number of products to return between 1 and 50.  # noqa: E501

        :return: The record_count of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: int
        """
        return self._record_count

    @record_count.setter
    def record_count(self, record_count):
        """Sets the record_count of this ManufacturerProductDetailsRequest.

        Number of products to return between 1 and 50.  # noqa: E501

        :param record_count: The record_count of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: int
        """
        if record_count is not None and record_count > 50:  # noqa: E501
            raise ValueError("Invalid value for `record_count`, must be a value less than or equal to `50`")  # noqa: E501
        if record_count is not None and record_count < 1:  # noqa: E501
            raise ValueError("Invalid value for `record_count`, must be a value greater than or equal to `1`")  # noqa: E501

        self._record_count = record_count

    @property
    def record_start_position(self):
        """Gets the record_start_position of this ManufacturerProductDetailsRequest.  # noqa: E501

        The starting index of the records returned. This is used to paginate beyond 50 results.  # noqa: E501

        :return: The record_start_position of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: int
        """
        return self._record_start_position

    @record_start_position.setter
    def record_start_position(self, record_start_position):
        """Sets the record_start_position of this ManufacturerProductDetailsRequest.

        The starting index of the records returned. This is used to paginate beyond 50 results.  # noqa: E501

        :param record_start_position: The record_start_position of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: int
        """

        self._record_start_position = record_start_position

    @property
    def filters(self):
        """Gets the filters of this ManufacturerProductDetailsRequest.  # noqa: E501


        :return: The filters of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: Filters
        """
        return self._filters

    @filters.setter
    def filters(self, filters):
        """Sets the filters of this ManufacturerProductDetailsRequest.


        :param filters: The filters of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: Filters
        """

        self._filters = filters

    @property
    def sort(self):
        """Gets the sort of this ManufacturerProductDetailsRequest.  # noqa: E501


        :return: The sort of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: SortParameters
        """
        return self._sort

    @sort.setter
    def sort(self, sort):
        """Sets the sort of this ManufacturerProductDetailsRequest.


        :param sort: The sort of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: SortParameters
        """

        self._sort = sort

    @property
    def requested_quantity(self):
        """Gets the requested_quantity of this ManufacturerProductDetailsRequest.  # noqa: E501

        The quantity of the product you are looking to purchase. This is used with the SortByUnitPrice SortOption as price varies at differing quantities.  # noqa: E501

        :return: The requested_quantity of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: int
        """
        return self._requested_quantity

    @requested_quantity.setter
    def requested_quantity(self, requested_quantity):
        """Sets the requested_quantity of this ManufacturerProductDetailsRequest.

        The quantity of the product you are looking to purchase. This is used with the SortByUnitPrice SortOption as price varies at differing quantities.  # noqa: E501

        :param requested_quantity: The requested_quantity of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: int
        """

        self._requested_quantity = requested_quantity

    @property
    def search_options(self):
        """Gets the search_options of this ManufacturerProductDetailsRequest.  # noqa: E501

        Filters the search results by the included SearchOption.  # noqa: E501

        :return: The search_options of this ManufacturerProductDetailsRequest.  # noqa: E501
        :rtype: list[SearchOption]
        """
        return self._search_options

    @search_options.setter
    def search_options(self, search_options):
        """Sets the search_options of this ManufacturerProductDetailsRequest.

        Filters the search results by the included SearchOption.  # noqa: E501

        :param search_options: The search_options of this ManufacturerProductDetailsRequest.  # noqa: E501
        :type: list[SearchOption]
        """

        self._search_options = search_options

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if issubclass(ManufacturerProductDetailsRequest, dict):
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
        if not isinstance(other, ManufacturerProductDetailsRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
