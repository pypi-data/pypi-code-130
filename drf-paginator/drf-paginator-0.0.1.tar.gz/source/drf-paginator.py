"""By Jamoliddin Bakhriddinov @youngerwolf"""
from django.db.models import QuerySet
from base import BasePaginator


class URLPaginatorResponse(BasePaginator):
    def __init__(self, url: str, data: QuerySet, page_size: int = 10, page: int = 1,
                 serializer_params: dict = None):
        super().__init__(data, page_size, page, serializer_params)
        self.url = url

    def next_page(self):
        if 1 <= self.page < self.max_page:
            return self.generate_url(self.page_size, self.page + 1)
        return None

    def previous_page(self):
        if 2 <= self.page <= self.max_page:
            return self.generate_url(self.page_size, self.page - 1)
        return None

    def generate_url(self, page_size, page):
        return f"{self.url}?page_size={page_size}&page={page}"

    def paginated_response(self):
        response = {
            "count": self.data_length,
            "previous": self.previous_page(),
            "next": self.next_page(),
            "result": self.get_serializer(data=self.result(), **self.serializer_params)
        } if self.is_valid_page() else {"detail": "Invalid page."}
        return response


class NumberPaginatorResponse(BasePaginator):
    def next_page(self):
        if 1 <= self.page < self.max_page:
            return self.page + 1
        return None

    def previous_page(self):
        if 2 <= self.page <= self.max_page:
            return self.page - 1
        return None

    def paginated_response(self):
        serializer = self.get_serializer(self.result(), **self.serializer_params)
        return {
            "count": self.data_length,
            "previous": self.previous_page(),
            "next": self.next_page(),
            "result": serializer.data
        }