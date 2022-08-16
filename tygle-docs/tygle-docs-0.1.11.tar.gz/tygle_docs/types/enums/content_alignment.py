from enum import Enum


class ContentAlignment(str, Enum):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents#ContentAlignment
    """

    CONTENT_ALIGNMENT_UNSPECIFIED = "CONTENT_ALIGNMENT_UNSPECIFIED"
    CONTENT_ALIGNMENT_UNSUPPORTED = "CONTENT_ALIGNMENT_UNSUPPORTED"
    TOP = "TOP"
    MIDDLE = "MIDDLE"
    BOTTOM = "BOTTOM"
