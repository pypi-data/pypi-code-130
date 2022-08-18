""" wenxin global variables """
import os

# http request
TIMEOUT_SECS = 600
MAX_CONNECTION_RETRIES = 2
REQUEST_SLEEP_TIME = 20
ACCESS_TOKEN_URL = "https://wenxin.baidu.com/moduleApi/portal/api/oauth/token"
API_REQUEST_URLS = ["https://wenxin.baidu.com/moduleApi/portal/api/rest/1.0/ernie/1.0/tuning",
                    "https://wenxin.baidu.com/moduleApi/portal/api/rest/1.0/ernie/3.0.28/zeus"]

VILG_CREATE_URL = "https://wenxin.baidu.com/moduleApi/portal/api/rest/1.0/ernievilg/v1/txt2img"
VILG_RETRIEVE_URL = "https://wenxin.baidu.com/moduleApi/portal/api/rest/1.0/ernievilg/v1/getImg"

ak = os.environ.get("WENXINAPI_AK", None)
sk = os.environ.get("WENXINAPI_SK", None)
access_token = os.environ.get("WENXINAPI_ACCESS_TOKEN", None)
debug = False
proxy = None
