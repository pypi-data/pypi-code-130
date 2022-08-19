from io import TextIOWrapper, FileIO
from typing import (
    Dict,
    List,
    overload,
    Generator,
    Literal,
    AsyncGenerator,
)
import redis
from pathlib import Path
import hashlib


from buffy.buffyserver.api.v1.models import (
    Response,
    Request,
    RequestCacheConfiguration,
)
from buffy.tools.utils import url_to_path_dir_name

"""Backend brainstorming notes

* Store large bynaries files
* provide hash per file

"""


class StorageInterface:
    def test_connection(self) -> bool:
        raise NotImplementedError

    def list_requests(
        self,
        group_name: str = None,  # Request.group_name
    ) -> List[Request]:
        raise NotImplementedError
        return [Request(id=1, url="blaaa", group_name=group_name)]

    def get_request(self, request_id: str) -> Request:
        """_summary_

        Args:
            request_id (str): _description_

        Returns:
            Request: _description_
        """
        raise NotImplementedError
        return Request(
            id=2, url="https://largefile.com/mysource", group_name="mydownloaderapp"
        )

    def create_request(self, request: Request) -> Request:

        raise NotImplementedError

    def update_request(self, request: Request) -> Request:
        raise NotImplementedError

    def list_responses(self, request_id: str) -> List[Response]:
        raise NotImplementedError

    def create_response(self, response: Response) -> Response:
        raise NotImplementedError

    def update_response(self, response: Response) -> Response:
        raise NotImplementedError

    @overload
    def get_response(self, response_id: str) -> Response:
        raise NotImplementedError

    @overload
    def get_response(self, request_id: str = None, version: str = "latest") -> Response:
        """_summary_

        Args:
            request_id (str, optional): _description_. Defaults to None.
            version (str, optional): _description_. Defaults to "latest".

        Raises:
            NotImplementedError: _description_

        Returns:
            Response: _description_
        """
        raise NotImplementedError

    def update_response(self, response: Response):
        raise NotImplementedError

    def delete_response(self, response: Response):
        raise NotImplementedError

    ## ↓ CONTENT/FILE HANDLING ↓

    @overload
    async def read_response_content(
        self,
        response: Response,
        as_text: bool = Literal[False],
    ) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    async def read_response_content(
        self,
        response: Response,
        as_text: bool = Literal[True],
    ) -> AsyncGenerator[str, None]:

        raise NotImplementedError

    def write_response_content(
        self,
        response: Response,
    ) -> FileIO:
        raise NotImplementedError

    def update_response_content_writing(
        self,
        response: Response,
    ):
        raise NotImplementedError

    def close_response_content_writing(self):
        raise NotImplementedError

    def get_response_content_hash(self, response: Response, cached_hash: bool = True):
        raise NotImplementedError
