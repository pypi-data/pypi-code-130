class SemanticScholarException(Exception):
    """Semantic Scholar API base exception."""

    status_code: int
    error: str

    def __init__(
        self, status_code: int, error: str = "Unknown Semantic Scholar API error"
    ) -> None:
        super().__init__(error)
        self.status_code = status_code
        self.error = error


class SemanticScholarBadQuery(SemanticScholarException):
    """Semantic Scholar bad query parameters exception."""

    pass


class SemanticScholarNotFound(SemanticScholarException):
    """Semantic Scholar entity not found exception."""

    pass


class SemanticScholarForbidden(SemanticScholarException):
    """Semantic Scholar forbidden exception."""

    pass


class SemanticScholarTooManyRequests(SemanticScholarException):
    """Semantic Scholar Too Many Requests exception."""

    pass
