from datetime import datetime, timedelta
import re
from clutter.aws import get_secrets

BASE_URL = "http://203.247.66.126:8090/url"
API_KEY = None

# 사용 가능한 수치모델
# key: url path, value: 해당 url path에 속한 수치모델
NWP = {
    "KIM": ["kim_g120", "kim_g128", "kim_g512"],
    "UMGL": ["g100", "g120", "g128", "g512", "g768"],
    "UMKR": ["l015"],
}

# KMA_URL_API의 ERROR NOTICE
ERROR_NOTICES = [
    "The number of requests has reached the limit",  # rate limit
    "The authKey is invalid",  # auth failed
]

# SECRETS_NAME
SECRETS_NAME = "common/kma-url-api"

# Load API Key for Dev.
try:
    secrets = get_secrets(SECRETS_NAME)
    API_KEY = secrets.get("eugene")
except Exception as ex:
    pass


# generate update datetimes
def generate_update_datetimes(start: datetime, end: datetime = None):
    OFFSET_HOUR = 0
    STEP_HOUR = 3

    dates = []

    # correct start datetime
    for _ in range(STEP_HOUR):
        if start.hour % STEP_HOUR == OFFSET_HOUR:
            dates += [start]
            break
        start += timedelta(hours=1)

    # parser end
    if end is not None:
        while True:
            date = dates[-1] + timedelta(hours=STEP_HOUR)
            if date > end:
                break
            dates += [date]

    return dates
