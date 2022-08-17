from .api_object import ApiObject


class Quote(ApiObject):

    @classmethod
    def get_endpoint(cls, quote_id):
        if quote_id:
            return f"/quote/{quote_id}"
        return "/quote"

    def __init__(self, _id: str = "",
                 dialog: str = "",
                 movie: str = "",
                 character: str = "",
                 id: str = ""):
        self._id = _id
        self.dialog = dialog
        self.movie_id = movie
        self.character_id = character
        self.id = id  # appears to be the same as _id
