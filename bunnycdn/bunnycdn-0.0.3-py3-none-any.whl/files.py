import requests
from bunnycdn.utils import handle_response
from bunnycdn.storage_zones import get_storage_zone_by_id

def list_files(
    storage_zone_id: int,
    path: str,
    ):
    try:
        sz = get_storage_zone_by_id(storage_zone_id)
        url = f"https://{sz.get('StorageHostname')}/{sz.get('Name')}/{path}"
        headers = {
            "Accept": "*/*",
            "AccessKey": sz.get("Password"),
        }
        res = requests.get(url, headers=headers)
        return handle_response(res)
    
    # TODO: handle errors
    except Exception as e:
        print(e)

def upload_file(
    storage_zone_id: int,
    path: str,
    file_name: str,
    file_content: str,
    ):
    try:
        sz = get_storage_zone_by_id(storage_zone_id)
        url = f"https://{sz.get('StorageHostname')}/{sz.get('Name')}/{path}/{file_name}"
        headers = {
            "Content-Type": "application/octet-stream",
            "AccessKey": sz.get("Password"),
        }
        res = requests.put(url, headers=headers, data=file_content)
        return handle_response(res)
    
    # TODO: handle errors
    except Exception as e:
        print(e)

def delete_file(
    storage_zone_id: int,
    path: str,
    file_name: str,
    ):
    try:
        sz = get_storage_zone_by_id(storage_zone_id)
        url = f"https://{sz.get('StorageHostname')}/{sz.get('Name')}/{path}/{file_name}"
        headers = {
            "AccessKey": sz.get("Password"),
        }
        res = requests.delete(url, headers=headers)
        return handle_response(res)
    
    # TODO: handle errors
    except Exception as e:
        print(e)

def download_file(
    storage_zone_id: int,
    path: str,
    file_name: str,
    ):
    try:
        sz = get_storage_zone_by_id(storage_zone_id)
        url = f"https://{sz.get('StorageHostname')}/{sz.get('Name')}/{path}/{file_name}"
        headers = {
            "AccessKey": sz.get("Password"),
        }
        res = requests.get(url, headers=headers)
        return res.content

    # TODO: handle errors
    except Exception as e:
        print(e)
