from typing import List
from typing import Optional

from pydantic.fields import Field

from .content import TikTokContentModel
from .base import BaseModelORM


class TikTokUserModel(BaseModelORM):
    id: str = Field(..., alias="uid")
    name: str = Field(..., alias="nickname")
    username: str = Field(..., alias="unique_id")
    description: Optional[str] = Field(None, alias="signature")
    description_url: Optional[str] = Field(None, alias="bio_url")
    following_count: Optional[int] = Field(None, alias="following_count")
    followers_count: Optional[int] = Field(None, alias="follower_count")
    likes_count: Optional[int] = Field(None, alias="total_favorited")
    verified: Optional[int] = Field(0, alias="verification_type")

    avatar_168x168: Optional[TikTokContentModel]
    avatar_300x300: Optional[TikTokContentModel]
    avatar_larger: Optional[TikTokContentModel]
    avatar_medium: Optional[TikTokContentModel]
    avatar_thumb: Optional[TikTokContentModel]
    cover_url: Optional[List[TikTokContentModel]]