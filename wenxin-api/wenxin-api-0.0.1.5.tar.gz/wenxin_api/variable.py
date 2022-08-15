""" wenxin global variables """
import os

# http request
TIMEOUT_SECS = 600
MAX_CONNECTION_RETRIES = 2
REQUEST_SLEEP_TIME = 20
ACCESS_TOKEN_URL = "https://wenxin.baidu.com/younger/portal/api/oauth/token"
API_REQUEST_URLS = ["http://dev020001.bcc-szth.baidu.com:8880/portal/api/rest/1.0/ernie/1.0/tuning",
                    "http://10.255.132.22:8080/task/deal_requests",
                    "http://dev020001.bcc-szth.baidu.com:8880/file/openApi/upload"]

ak = os.environ.get("WENXINAPI_AK", None)
sk = os.environ.get("WENXINAPI_SK", None)
access_token = os.environ.get("WENXINAPI_ACCESS_TOKEN", None)
debug = False
proxy=None

# proxy = "http://172.19.56.199:3128"
ak = "UXeG4CTgCvKYdS4cl9WuucFWqE0CDMhW"
sk = "FaRRfW7LCMqNCnYZvWWGQ8QDZ8CgSjqC"
access_token = "24.4ae5605c2a7fc359b331b3aec50fbe00.86400000.1660618683571.195f390cdf7402eb67c60125bc05f6a2-38764"
