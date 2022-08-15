from typing import Dict, Optional

from pydantic import BaseModel, Extra

INDEX_URL = r"https://app.bupt.edu.cn/ncov/wap/default/index"
LOGIN_URL = r"https://auth.bupt.edu.cn/authserver/login"
REPORT_URL = r"https://app.bupt.edu.cn/ncov/wap/default/index"
REPORT_POST_URL = r"https://app.bupt.edu.cn/ncov/wap/default/save"


class BUPT_Model(BaseModel, extra=Extra.ignore):
    user: int
    account: str = None
    password: str = None
    cookie: str = None
    check_in_time: str = None
    check_in_status: bool = None


class New_Form_Model(BaseModel, extra=Extra.ignore):
    id: int
    uid: str
    date: str
    created: int


class Report_Form_Model(BaseModel, extra=Extra.ignore):
    ismoved: str
    jhfjrq: str
    jhfjjtgj: str
    jhfjhbcc: str
    szgj: str
    szcs: str
    zgfxdq: str
    mjry: str
    csmjry: str
    ymjzxgqk: str
    xwxgymjzqk: str
    tw: str
    sfcxtz: str
    sfjcbh: str
    sfcxzysx: str
    qksm: str
    sfyyjc: str
    jcjgqr: str
    remark: str
    address: str
    geo_api_info: str
    area: str
    province: str
    city: str
    sfzx: str
    sfjcwhry: str
    sfjchbry: str
    sfcyglq: str
    gllx: str
    glksrq: str
    jcbhlx: str
    jcbhrq: str
    bztcyy: str
    sftjhb: str
    sftjwh: str
    sfsfbh: str
    xjzd: str
    jcwhryfs: str
    jchbryfs: str
    szsqsfybl: str
    sfygtjzzfj: int
    gtjzzfjsj: str
    sfjzxgym: str
    sfjzdezxgym: str
    jcjg: str
    created_uid: int
    date: str
    uid: str
    created: int
    id: int


class Geo_Info(BaseModel, extra=Extra.ignore):
    province: str
    city: str
    area: str
    address: str


class Report_Response(BaseModel, extra=Extra.ignore):
    e: Optional[int]
    m: str
    d: Dict
