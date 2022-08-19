from dataclasses import dataclass

from .DataClass import DataClass


# noinspection SpellCheckingInspection
@dataclass
class DiyObject(DataClass):
    category: int = None
    is_thumb: int = None
    top_id: int = None
    is_paid: int = None
    diy_flag: int = None
    comment: int = None
    diy_user_nickname: str = None
    diy_background_url: str = None
    is_original: int = None
    is_noticed: int = None
    thumb: int = None
    collect: int = None
    is_fans: int = None
    is_creator: int = None
    diy_user_id: str = None
    diy_user_headurl: str = None
    created_at: int = None
