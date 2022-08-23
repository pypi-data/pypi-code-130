import os
import requests
from bunnycdn import BUNNY_API_ENDPOINT
from bunnycdn.errors import *


def get_region_list() -> dict:
    """ get list of regions """
    res = requests.get(f"{BUNNY_API_ENDPOINT}/region")
    return handle_response(res)

def get_region_codes() -> list:
    """ get region codes from region list """
    return [region.get('RegionCode') for region in get_region_list()]

# NOTE: their endpoint does not seem to function as expected
# I am leaving this here as a reference in case they fix it.
# def get_countries() -> dict:
#     """ get list of countries """
#     headers = {
#         "Accept": "application/json",
#         "AccessKey": "null"
#     }
#     res = requests.get(f"{BUNNY_API_ENDPOINT}/country", headers=headers)
#     return handle_response(res)

def get_access_key() -> str:
    """ get access key from environment variable """
    bunny_api_key = os.environ.get('BUNNY_ACCESS_KEY', None)
    if bunny_api_key is None:
        raise ValueError('BUNNY_ACCESS_KEY environment variable is not set')
    return bunny_api_key

def handle_response(res: requests.Response) -> dict:
    """ a generic api response handler """
    # print(res)
    if res.status_code in [200, 201]:
        return res.json()
    if res.status_code == 204:
        return {"Message": "Success"}
    elif res.status_code == 400: # 400 Bad Request
        raise BadRequest(res.json().get('Message'))
    elif res.status_code == 401:
        raise NotAuthorized(res.json().get('Message'))
    elif res.status_code == 404:
        # print(res.text)
        raise NotFound(res.json().get('Message'))
    elif res.status_code == 500:
        raise InternalServerError(res.json().get('Message'))
