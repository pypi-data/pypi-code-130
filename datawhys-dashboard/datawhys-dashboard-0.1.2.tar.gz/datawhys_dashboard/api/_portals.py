from io import BytesIO

from ._base import request


def portal_create(data: BytesIO, name: str, description: str = None, **kwargs):
    """
    Create a new portal.
    """

    headers = {"Content-Type": None}  # this allows requests to manage the content-type
    files = {"data_file": (name, data)}
    params = {"description": description}

    return request(
        "POST", "portals/", headers=headers, files=files, data=params, **kwargs
    )
