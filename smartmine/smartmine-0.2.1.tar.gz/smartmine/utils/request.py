import json
import requests
from pathlib import Path

from smartmine.utils.model import ServiceName
from smartmine.utils.service import get_default_option_name, get_default_option_value

API_BASE_URL = "https://api.smartmine.net/api/v1"


def login(username: str, password: str) -> str:
    url = f"{API_BASE_URL}/login"
    response = requests.post(
        url=url, data=json.dumps({"username": username, "password": password})
    )
    response.raise_for_status()
    response_content = response.json()
    assert response_content["status"] == "ok"
    return response_content["token"]


def get_request_token(service_name: ServiceName, bearer_token: str) -> str:
    url = f"{API_BASE_URL}/service/{service_name.value}/request-token"

    service_options = {
        "service_options_selection": [
            {
                "service_name": service_name.value,
                "option_name": get_default_option_name(service_name),
                "option_value": get_default_option_value(service_name),
            }
        ],
        "units_used": 1,
    }
    response = requests.post(
        url=url,
        data=json.dumps(service_options),
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    response.raise_for_status()
    response_content = response.json()
    return response_content["token"]


def upload_file(
    service_name: ServiceName, file_path: str, bearer_token: str, request_token: str
) -> None:
    url = f"{API_BASE_URL}/service/{service_name.value}/upload"

    with open(file_path, "rb") as f:
        response = requests.post(
            url=url,
            params={"service": "image-super-resolution"},
            files=[("file", (Path(file_path).name, f, "multipart/form-data"))],
            headers={"Authorization": f"Bearer {bearer_token}", "token": request_token},
        )
        response.raise_for_status()


def process_request(
    service_name: ServiceName, bearer_token: str, request_token: str
) -> None:
    url = f"{API_BASE_URL}/service/{service_name.value}/process"

    response = requests.post(
        url=url,
        headers={"Authorization": f"Bearer {bearer_token}", "token": request_token},
    )
    response.raise_for_status()


def download_result(
    service_name: ServiceName, save_path: str, bearer_token: str, request_token: str
) -> None:
    url = f"{API_BASE_URL}/service/{service_name.value}/download-result"

    response = requests.get(
        url=url,
        headers={"Authorization": f"Bearer {bearer_token}", "token": request_token},
    )
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)
