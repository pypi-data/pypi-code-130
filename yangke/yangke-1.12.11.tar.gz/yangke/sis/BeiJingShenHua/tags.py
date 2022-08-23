from enum import Enum, unique
from yangke.base import get_key_value


# @unique
@get_key_value
class TagsRead(Enum):
    主汽门前压力 = "N1DCS.TOTALMW"
    主汽门前温度 = "N2DCS.TOTALMW"
    高压蒸汽流量1号炉 = ""
    高压蒸汽流量2号炉 = ""
    高压蒸汽减温水流量1号炉 = ""
    高压蒸汽减温水流量2号炉 = ""
    高排压力 = "N3DCS.TOTALMW"
    高排温度 = "N3DCS.TOTALMW"
    中压主汽门前压力 = "N3DCS.TOTALMW"
    中压主汽门前温度 = "N3DCS.TOTALMW"
    中压给水流量1号炉 = ""
    中压给水流量2号炉 = ""
    FGH流量1号炉 = ""
    FGH流量2号炉 = ""
    再热减温水流量1 = ""
    再热减温水流量2 = ""
    低压蒸汽流量1 = "N3DCS.TOTALMW"
    低压蒸汽流量2 = "N3DCS.TOTALMW"
    低压蒸汽压力1 = "N3DCS.TOTALMW"
    低压蒸汽压力2 = "N3DCS.TOTALMW"
    低压蒸汽温度1 = "N3DCS.TOTALMW"
    低压蒸汽温度2 = "N3DCS.TOTALMW"
    供热管道出水热量 = ""
    供热管道回水热量 = ""
    热井出水压力 = ""
    热井出水温度 = ""
    凝结水流量1号炉 = ""
    凝结水流量2号炉 = ""
    减温水至杂项流量 = ""
    发电机有功功率_steam = ""
    大气压力 = ""
    环境温度 = ""
    环境湿度 = ""
    当前背压 = ""


# @unique
@get_key_value
class TagsWrite(Enum):
    建议运行方式 = ""
    最优运行方式下背压 = ""
