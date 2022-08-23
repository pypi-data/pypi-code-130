import requests
from bunnycdn.utils import handle_response, get_access_key

def get_statistics(
    pull_zone: int = -1, 
    server_zone_id: int = -1, #  If set, the statistics will be only returned for the given region ID
    load_errors: bool = False,
    hourly: bool = False,
    date_range: list = [], # [date_from, date_to] # format: yyyy-mm-dd
    ):
    url = f"https://api.bunny.net/statistics?pullZone={pull_zone}&serverZoneId={server_zone_id}&loadErrors={load_errors}&hourly={hourly}"
    if len(date_range) == 2:
        # TODO: validate date format
        date_from = date_range[0]
        date_to = date_range[1]
        url = f"https://api.bunny.net/statistics?dateFrom={date_from}&dateTo={date_to}&pullZone={pull_zone}&serverZoneId={server_zone_id}&loadErrors={load_errors}&hourly={hourly}"

    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    return handle_response(res)