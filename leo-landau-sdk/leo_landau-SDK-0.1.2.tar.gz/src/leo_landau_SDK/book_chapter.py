
from .chapter import Chapter

class BookChapter(Chapter):

    @classmethod
    def get_endpoint(cls, book_id):
        if not book_id:
            raise RuntimeError("Book_Chapter requires book_id")
        return f"/book/{book_id}/chapter"
