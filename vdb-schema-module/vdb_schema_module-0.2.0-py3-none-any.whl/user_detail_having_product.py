from typing import Optional

from pydantic import BaseModel, Field


class UserDetailHavingProductModel(BaseModel):
    created_on: Optional[str] = Field(alias="created_on")
    modified_on: Optional[str] = Field(alias="modified_on")
    product_id: int = Field(alias="product_id")
    UserDetail_UDKey: int = Field(alias="UserDetail_UDKey")
    user_detail_having_product_id: int = Field(alias="user_detail_having_product_id")
