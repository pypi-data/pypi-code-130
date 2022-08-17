from .api_object import ApiObject


class Chapter(ApiObject):

    @classmethod
    def get_endpoint(cls, chapter_id):
        if chapter_id:
            raise RuntimeError("Not working in SDK, need to investigate further")
            # return f"chapter/{chapter_id}"
        return "/chapter"

    def __init__(self, _id: str = "", chapterName: str = "", book=None):
        self._id = _id
        self.chapter_name = chapterName
        self.book_id = book

