
from typing import List, TypeVar, Generic

T = TypeVar("T")

class ApiResult(Generic[T]):

    def __init__(self,
                 docs: List[T] = [],
                 total: int = -1,
                 limit: int = -1,
                 offset: int = -1,
                 page: int = -1,
                 pages: int = -1,
                 success: bool = True,
                 message: str = ""):
        self.docs = docs
        self.total = total
        self.limit = limit
        self.offset = offset
        self.page = page
        self.pages = pages
        self.success = success
        self.message = message

