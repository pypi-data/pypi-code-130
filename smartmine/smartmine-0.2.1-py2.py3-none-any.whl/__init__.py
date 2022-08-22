import os
import re
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from smartmine.utils.model import ServiceName
from smartmine.utils.request import (
    login,
    get_request_token,
    upload_file,
    process_request,
    download_result,
)
from smartmine.utils.credentials import check_credentials

username = None
password = None
bearer_token = None
api_base = "https://api.smartmine.net/api/v1"


def process_image(service_name: ServiceName, load_path: str, save_path: str):
    global bearer_token
    check_credentials(username=username, password=password)
    bearer_token = login(username=username, password=password)
    _process_single_image(
        service_name=service_name, load_path=load_path, save_path=save_path
    )


def bulk_process_images(
    service_name: ServiceName, load_dir: str, save_dir: Optional[str] = None
):
    global bearer_token

    # Default to the user's Downloads folder if the save directory is not set
    if not save_dir:
        save_dir = str(Path.home() / "Downloads")

    # Get a list of the image files in the load directory
    files = [
        os.path.join(load_dir, f)
        for f in os.listdir(load_dir)
        if re.match(r".*\.(jpg|jpeg|png|JPG|JPEG|PNG)", f)
    ]
    if not files:
        raise FileNotFoundError(f"Found no JPEG or PNG files in {load_dir}")

    check_credentials(username=username, password=password)
    bearer_token = login(username=username, password=password)

    for load_path in tqdm(files, desc="Bulk processing images"):
        # Use the same filename as the input file when saving the result
        save_path = Path(save_dir) / Path(load_path).name
        _process_single_image(
            service_name=service_name, load_path=load_path, save_path=save_path
        )


def _process_single_image(service_name: ServiceName, load_path: str, save_path: str):
    request_token = get_request_token(
        service_name=service_name, bearer_token=bearer_token
    )
    upload_file(
        service_name=service_name,
        file_path=load_path,
        bearer_token=bearer_token,
        request_token=request_token,
    )
    process_request(
        service_name=service_name,
        bearer_token=bearer_token,
        request_token=request_token,
    )
    download_result(
        service_name=service_name,
        save_path=save_path,
        bearer_token=bearer_token,
        request_token=request_token,
    )


if __name__ == "__main__":
    bulk_process_images(
        service_name=ServiceName.image_restoration,
        load_dir="examples/images/",
        save_dir=str(Path.home() / "Downloads"),
    )
