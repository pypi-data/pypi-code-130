"""Aqara iot enums."""

from dataclasses import dataclass
from enum import IntEnum

class AuthType(IntEnum):
    """Aqara Cloud Auth Type."""

    # Aqara账号授权:0、项目授权:1、虚拟账号授权:2
    AQARA_SMART_HOME = 0
    PROJECT = 1
    VIRTUAL = 2


AQARA_OAUTH2_AUTHORIZE = "/v3.0/open/authorize"

# 获取访问令牌
AQARA_OAUTH2_ACCESS_TOKEN = "/v3.0/open/access_token"


class AqaraCloudOpenAPIEndpoint:
    """Aqara Cloud Open API Endpoint."""

    # "/v3.0/open/api"

    # 中国大陆
    CHINA = "https://open-cn.aqara.com"
    #CHINA = "https://developer-test.aqara.com"

    # 美国
    AMERICA = "https://open-usa.aqara.com"

    # 韩国
    COREA = "https://open-kr.aqara.com"

    # 俄罗斯
    RUSSIA = "https://open-ru.aqara.com"

    # 欧洲
    EUROPE = "https://open-ger.aqara.com"


PATH_OPEN_API = "/v3.0/open/api"
PATH_AUTH = "/v3.0/open/authorize"
PATH_ACCESS_TOKEN = "/v3.0/open/access_token"


@dataclass
class AppInfo:
    """Describe App Info"""

    APP_ID: str
    APP_KEY: str
    KEY_ID: str


DEV = AppInfo(
    "948907588893974528e53aac",
    "gchwjfo48nd0da9d3nlne8iblxorbyzl",
    "K.948907589003026432",
)

#正式环境
CN = AppInfo(
    "941380790062239744112522",
    "tqvq2ol7va9v8u2w518qxedqxvx0e46i",
    "K.941380790108377088",
)
#测试环境
#CN =  AppInfo('948907588893974528e53aac','gchwjfo48nd0da9d3nlne8iblxorbyzl','K.948907589003026432')
RU = AppInfo(
    "941380790062239744112522",
    "jsuyarvooi34k29qx94h48teivj3ua62",
    "K.941380790112571394",
)

# appid: 941380790062239744112522
# appkey: xpwmpncu4xdff3jqaqy8bv2idx1hcql4
# keyid: K.941380790125154304
EU = AppInfo(
    "941380790062239744112522",
    "xpwmpncu4xdff3jqaqy8bv2idx1hcql4",
    "K.941380790125154304",
)
US = AppInfo(
    "941380790062239744112522",
    "ndgyidx44igy4knq8obzycag3qcsh679",
    "K.941380790112571392",
)
KR = AppInfo(
    "941380790062239744112522",
    "vb5vhgri0luvxhpgoac603z25gitxues",
    "K.941380790120960000",
)
APPS: dict[str, AppInfo] = {
    "China": CN,
    "dev": DEV,
    "Europe": EU,
    "Russia": RU,
    "United States": US,
    "South Korea": KR,
}


EMPTY_PATH = ""


@dataclass
class Country:
    """Describe a supported country."""

    country_code: str
    endpoint: str = AqaraCloudOpenAPIEndpoint.EUROPE


AQARA_COUNTRIES = [
    Country("China", AqaraCloudOpenAPIEndpoint.CHINA),
    Country("Europe", AqaraCloudOpenAPIEndpoint.EUROPE),
    Country("South Korea", AqaraCloudOpenAPIEndpoint.COREA),
    Country("Russia", AqaraCloudOpenAPIEndpoint.RUSSIA),
    Country("United States", AqaraCloudOpenAPIEndpoint.AMERICA),
]
