from dataclasses import dataclass, field
from typing import List

from .DataClass import DataClass
from .Diy import DiyObject
from .Image import Image


@dataclass
class MicInfo(DataClass):
    room_in_id: int = None
    player_2: int = None
    room_type: int = None
    status: int = None
    is_pwd: int = None
    player_1: int = None
    is_player: int = None


# noinspection SpellCheckingInspection
@dataclass
class CrbtObject(DataClass):
    filename: str = None
    diy: DiyObject = None
    url_valid_duration: int = None
    comment_cnt: int = None
    tracker_url: str = None
    hash: str = None
    type: int = None
    crbtValidity: str = None
    gotoEnable: int = None
    is_kugou: int = None
    image: Image = None
    thumb_cnt: int = None
    url: str = None
    gotourl: str = None
    collect: int = None
    flag: int = None
    is_np: int = None
    price: int = None
    duration: str = None
    gotoRemarks: str = None
    playtimes: int = None
    ringId: str = None
    coverurl: str = None
    singerName: str = None
    gotoName: str = None
    ringName: str = None
    subtype: int = None
    ext: str = None
    remarks: str = None
    tone_quality: int = None
    ringDesc: str = None
    settingtimes: int = None


@dataclass
class Account(DataClass):
    is_fans: int = None
    dan: int = None
    background_url: str = None
    nickname: str = None
    sex: int = None
    is_noticed: int = None
    mic_info: MicInfo = None
    signature: str = None
    user_id: str = None
    image_url: str = None
    created_at: int = None
    is_creator: str = None
    kugou_id: str = None
    public_id: int = None
    key: int = None
    birthday: str = None


# noinspection SpellCheckingInspection
@dataclass
class VideoObject(DataClass):
    weight: int = None
    audit_num: int = None
    collect_status: int = None
    video_type: int = None
    is_kugoumv: int = None
    collect_cnt: int = None
    video_hash: int = None
    hot: int = None
    white: int = None
    price: int = None
    video_gif: int = None
    created_at: int = None
    set_cnt: int = None
    old_video_hash: int = None
    is_p: int = None
    is_like: int = None
    filename: int = None
    play_cnt: int = None
    account: Account = None
    cover_thumb_url: str = None
    old_filename: str = None
    video_gif_hash: str = None
    published_at: int = None
    plat: str = None
    comment_count: str = None
    ringName: str = None
    cover_url: str = None
    share_num: str = None
    machine_estimate: int = None
    ring_head_url: str = None
    publisher_id: str = None
    white_nickname: str = None
    video_id: str = None
    duration: int = None
    status: int = None
    pay_ring_id: str = None
    week_set_cnt: int = None
    like_cnt: int = None
    img_machine_estimate: int = None
    is_best: int = None
    is_crbt: str = None
    content: str = None
    is_ad: int = None
    remarks: str = None
    video_url: str = None
    is_full: int = None
    white_id: str = None


# noinspection SpellCheckingInspection
@dataclass
class ImageObject(DataClass):
    play_cnt: int = None
    account: Account = None
    collect_status: int = None
    collect_cnt: int = None
    cover_url: str = None
    user_id: str = None
    share_cnt: str = None
    is_like: int = None
    create_time: int = None
    status: int = None
    like_cnt: int = None
    is_mulit_cover: int = None
    set_cnt: int = None
    title: str = None
    thumb_cover_url: str = None
    remarks: str = None
    comment_count: int = None
    mulit_cover_urls: List[str] = None
    image_id: str = None


# noinspection SpellCheckingInspection
@dataclass
class AudioObject(DataClass):
    is_np: int = None
    diy: DiyObject = None
    crbtValidity: str = None
    ringId: str = None
    thumb_cnt: int = None
    url: str = None
    price: int = None
    flag: int = None
    playtimes: int = None
    collect: int = None
    singerName: str = None
    tracker_url: str = None
    ext: str = None
    url_valid_duration: int = None
    filename: str = None
    comment_cnt: int = None
    hash: str = None
    gotoEnable: int = None
    is_kugou: int = None
    image: Image = None
    duration: str = None
    gotoRemarks: str = None
    tag_type: int = None
    subtype: int = None
    settingtimes: int = None
    gotoName: str = None
    coverurl: str = None
    tone_quality: str = None
    remarks: str = None
    type: int = None
    ringName: str = None
    ringDesc: str = None
    gotourl: str = None


# noinspection SpellCheckingInspection
@dataclass
class CompleteSearchResponse(DataClass):
    # 用户
    user_list: List[Account] = field(default_factory=list)
    # 彩铃
    crbt_list: List[CrbtObject] = field(default_factory=list)
    # 圈子
    circle_list: List[dict] = field(default_factory=list)
    # 视频
    video_list: List[VideoObject] = field(default_factory=list)
    # 图片
    image_list: List[ImageObject] = field(default_factory=list)
    # 铃声
    audio_list: List[AudioObject] = field(default_factory=list)
