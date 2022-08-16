from pydantic import BaseModel, Field


class UserPayTVModel(BaseModel):
    paytvprovider_id: int = Field(alias="paytvprovider_id")
    UserDetail_UDKey: int = Field(alias="UserDetail_UDKey")
