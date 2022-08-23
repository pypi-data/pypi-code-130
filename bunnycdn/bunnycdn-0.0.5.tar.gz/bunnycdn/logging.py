import requests
from bunnycdn.errors import *
from bunnycdn import BUNNY_LOG_ENDPOINT
from bunnycdn.utils import (
    get_access_key,
    handle_response,
)

def _format_logs(logs: str):
    """ Format logs """
    lines = logs.splitlines()
    formatted_logs = []
    for line in lines:
        segments = line.split("|")
        if segments[0] == "MISS":
            segments[0] = False
        else:
            segments[0] = True
        
        if segments[6] == "-":
            segments[6] = None

        formatted_logs.append({
            "hit": segments[0],
            "status_code": int(segments[1]),
            "timestamp": int(segments[2]),
            "bytes_sent": int(segments[3]),
            "pull_zone_id":int(segments[4]),
            "remote_ip": segments[5],
            "referer_url": segments[6],
            "url": segments[7],
            "edge_location": segments[8],
            "user_agent": segments[9],
            "unique_request_id": segments[10],
            "country_code": segments[11],
        })
    return formatted_logs

def get_logs(pull_zone_id: int, date: str, start: int = 0, end: int = 250):
    """ Get logs
    Args:
        pull_zone_id (int): Pull zone id
        date (str): Date in format MM-DD-YY
        start (int): Start index
        end (int): End index
     """
    # https://logging.bunnycdn.com/08-22-22/863757.log?download=false&status=100,200,300,400,500&search=&start=0&end=250
    url = f"{BUNNY_LOG_ENDPOINT}/{date}/{pull_zone_id}.log?download=false&status=100,200,300,400,500&search=&start={start}&end={end}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return _format_logs(res.text)
    if res.status_code == 404:
        raise NotFound(res.text)
    if res.status_code in [401, 403]:
        raise NotAuthorized(res.text)
    raise InternalServerError(res.text)
