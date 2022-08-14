from django.db.models import QuerySet
from abc import ABC, abstractmethod


class Paginator(ABC):
    @abstractmethod
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """

    @abstractmethod
    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """

    @abstractmethod
    def is_valid_page(self):
        """
        Indicates whether given as parameter page is valid or not
        """

    @abstractmethod
    def result(self):
        """Gets the queryset of data"""

    @abstractmethod
    def paginated_response(self):
        """Final JSon Response"""

    @abstractmethod
    def next_page(self):
        """Get next page"""

    @abstractmethod
    def previous_page(self):
        """Get previous page"""


class BasePaginator(Paginator):
    """
    Paginate the queryset for efficiency of query

    param: url - URL of GET to get the QuerySet response
    type: str
    param: data - QuerySet you want to paginate
    type: QuerySet
    param: page_size - Parameter that was given in url
    type: int
    param: page - Parameter which determines which page we wanna look up
    type: int
    param: serializer - Serializer to serialize gotten queryset
    type: Serializer
    param: **kwargs to populate given serializer
    type: dict
    """

    serializer_class: None
    reverse: bool = False

    def __init__(self, data: QuerySet, page_size: int = 10, page: int = 1,
                 serializer_params: dict = None):
        self.data = data
        self.page_size = page_size
        self.page = page
        self.data_length = len(self.data)
        self.estimate_max_page = self.data_length / self.page_size
        self.max_page = self.math_ceil(self.estimate_max_page)
        self.serializer_params = serializer_params

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def is_valid_page(self):
        return self.max_page >= self.page

    def next_page(self):
        raise NotImplementedError

    def previous_page(self):
        raise NotImplementedError

    def result(self):
        if self.reverse is True:
            end = self.data_length - self.page_size * (self.page - 1)
            start = end - self.page_size if end - self.page_size > 0 else 0
            return self.data[start:end]     # page_size = 15; page = 1; data_length = 16 [1:16]
        return self.data[self.page_size * (self.page - 1):self.page_size * self.page]

    def paginated_response(self):
        raise NotImplementedError

    @staticmethod
    def math_ceil(number: float):
        """
        Example: math_ceil(4.1) -> 5
        """
        integer_number = int(number)
        return integer_number if integer_number == number else integer_number + 1