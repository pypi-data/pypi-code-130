from dataclasses import dataclass

from .DataClass import DataClass
from .Diy import DiyObject
from .Image import Image


# noinspection SpellCheckingInspection
@dataclass
class MusicInfo(DataClass):
    is_np: str = None
    diy: DiyObject = None
    kg_hash: str = None
    crbtValidity: str = None
    ringId: str = None
    thumb_cnt: str = None
    url: str = None
    fakeplaytimes: int = None
    price: str = None
    flag: str = None
    playtimes: str = None
    coverurl: str = None
    singerName: str = None
    tracker_url: str = None
    ext: str = None
    url_valid_duration: str = None
    filename: str = None
    comment_cnt: str = None
    hash: str = None
    gotoEnable: str = None
    settingtimes: str = None
    image: Image = None
    duration: str = None
    gotoRemarks: str = None
    tag_type: int = None
    subtype: int = None
    type: int = None
    gotoName: str = None
    gotourl: str = None
    collect: int = None
    ringName: str = None
    remarks: str = None
    is_kugou: int = None
    ringDesc: str = None
    tone_quality: int = None
