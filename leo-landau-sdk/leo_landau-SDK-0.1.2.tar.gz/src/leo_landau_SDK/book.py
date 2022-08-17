from .api_object import ApiObject


class Book(ApiObject):

    @classmethod
    def get_endpoint(cls, book_id):
        if book_id:
            return f"/book/{book_id}"
        return "/book"

    def __init__(self, _id: str = "", name: str = ""):
        self._id = _id
        self.name = name

