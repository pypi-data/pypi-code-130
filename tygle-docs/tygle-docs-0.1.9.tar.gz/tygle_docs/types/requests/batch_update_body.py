from typing import List, Optional

from pydantic import BaseModel, Field
from tygle_docs.types.write_control import WriteControl

from .update_request import UpdateRequest, UpdateRequestBody


class BatchUpdateBody(BaseModel):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents/batchUpdate#request-body
    """

    requests: List[UpdateRequestBody] = Field()
    write_control: Optional[WriteControl] = Field(None, alias="writeControl")

    @property
    def BatchUpdate(self):
        requests = [req.UpdateRequest for req in self.requests]
        return BatchUpdate(requests=requests, writeControl=self.write_control)


class BatchUpdate(BaseModel):
    requests: List[UpdateRequest] = Field()
    write_control: Optional[WriteControl] = Field(None, alias="writeControl")
