import requests
from bunnycdn import BUNNY_API_ENDPOINT
from bunnycdn.utils import (
    get_access_key,
    get_region_codes,
    handle_response,
)

def get_storage_zone_by_id(storage_zone_id: int) -> dict:
    """ Get storage zone """
    url = f"{BUNNY_API_ENDPOINT}/storagezone/{storage_zone_id}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    return handle_response(res)

# TODO: implement get_storage_zone_by_name()
# this would essentially iterate over all storage zones and return the first one that matches the name
# def get_storage_zone_by_name(storage_zone_name: str) -> dict:

def list_storage_zones(page:int = 0, per_page:int = 1000, include_deleted: bool = False) -> dict:
    """ List storage zones """
    if include_deleted:
        show_deleted = 'true'
    else:
        show_deleted = 'false'

    url = f"{BUNNY_API_ENDPOINT}/storagezone?page={page}&perPage={per_page}&includeDeleted={show_deleted}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    return handle_response(res)

def add_storage_zone(
    name: str,
    primary_region: str = 'NY',
    storage_tier: str = 'standard',
    replication_regions: list = [],
    origin_url: str = None,
):
    """ Add storage zone """
    url = f"{BUNNY_API_ENDPOINT}/storagezone"
    if storage_tier not in ['standard', 'edge']:
        raise ValueError(f'{storage_tier} is not a valid storage tier')
    
    if storage_tier == 'standard':
        zone_tier = 0
    elif storage_tier == 'edge':
        zone_tier = 1

    if primary_region.upper() not in get_region_codes():
        raise ValueError(f'{primary_region} is not a valid region')
    
    for region in replication_regions:
        if region.upper() not in get_region_codes():
            raise ValueError(f'{region} is not a valid region')
    
    payload = {
        "Name": name,
        "Region": primary_region.upper(),
        "ZoneTier": zone_tier, # 0 for standard, 1 for edge
        "ReplicationRegions": list(map(lambda x: x.upper(), replication_regions)),
    }
    if origin_url is not None:
        payload['OriginUrl'] = origin_url

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "AccessKey": get_access_key(),
    }

    res = requests.post(url, json=payload, headers=headers)
    return handle_response(res)


def update_storage_zone(
    storage_zone_id: int, 
    replication_regions: list = [],
    origin_url: str = None,
    custom_404_file_path: str = None,
    rewrite_404_to_200: bool = False,
    ):
    """ Update storage zone """
    url = f"{BUNNY_API_ENDPOINT}/storagezone/{storage_zone_id}"
    for region in replication_regions:
        if region.upper() not in get_region_codes():
            raise ValueError(f'{region} is not a valid region')
    
    payload = {}
    if origin_url is not None:
        payload['OriginUrl'] = origin_url
    
    if custom_404_file_path is not None:
        payload['Custom404FilePath'] = custom_404_file_path
    
    if rewrite_404_to_200:
        payload['Rewrite404To200'] = True
    else:
        payload['Rewrite404To200'] = False

    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.post(url, json=payload, headers=headers)
    return handle_response(res)

def delete_storage_zone(storage_zone_id: int):
    """ Delete storage zone """
    url = f"{BUNNY_API_ENDPOINT}/storagezone/{storage_zone_id}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.delete(url, headers=headers)
    return handle_response(res)

def reset_storage_zone_password(storage_zone_id: int, readonly: bool = False):
    """ Reset storage zone passwords """
    url = f"{BUNNY_API_ENDPOINT}/storagezone/{storage_zone_id}/resetPassword"
    if readonly:
        url = f"{BUNNY_API_ENDPOINT}/storagezone/resetReadOnlyPassword?id={storage_zone_id}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.post(url, headers=headers)
    return handle_response(res)
