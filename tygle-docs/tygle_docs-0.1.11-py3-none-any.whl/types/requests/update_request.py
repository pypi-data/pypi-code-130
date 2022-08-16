from typing import ClassVar, Dict, Type

from pydantic import BaseModel
from tygle_docs.types.responses import UpdateResponse


class UpdateRequestBody(BaseModel):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents/request#request
    """

    response_type: ClassVar[Type[UpdateResponse]] = UpdateResponse
    key: ClassVar[str]

    @property
    def UpdateRequest(self):
        return UpdateRequest(
            response_type=self.response_type, request_body={self.key: self}
        )


class UpdateRequest(BaseModel):
    response_type: Type[UpdateResponse]
    request_body: Dict[str, UpdateRequestBody]
