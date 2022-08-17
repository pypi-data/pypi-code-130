import os

import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper


# params = {"access_token", "somethingsomething"}

ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
SANDBOX_URL = "https://sandbox.zenodo.org/api/deposit/depositions"

#r = requests.post(SANDBOX_URL, params=params, json={})
#bucket_url = r.jon()["links"]["bucket"]
#
#filepath = "/path/to/file"
#file_size = os.stat(filepath).st_size
#name = "name_of_file"
#with open(filepath, "r") as fp:
#    with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
#        wrapped_file = CallbackIOWrapper(t.update, fp, "read")
#        requests.put(f"{bucket_url}/{name_of_file}", data=wrapped_file, params=params)
#    # r = requests.put(f"{bucket_url}/{name_of_file}", data=fp, params=params)


def upload(filepath, access_token):
    params = {"access_token": access_token}
    print(f"{params=!r}")

    #r = requests.get(SANDBOX_URL, params=params)
    #if not r.ok:
    #    msg = r.json().get("message", "")
    #    raise requests.exceptions.HTTPError(f"{r!r} {msg}")
    #else:
    #    print(r.json())

    r = requests.post(SANDBOX_URL, params=params, json={})  #, headers={"Content-Type": "application/json"})
    if not r.ok:
        msg = r.json().get("message", "")
        raise requests.exceptions.HTTPError(f"{r!r} {msg}")

    # TODO: check if file exist
    file_size = os.stat(filepath).st_size
    print(f"{file_size=}")

    # Upload file with progress bar, see
    # https://gist.github.com/tyhoff/b757e6af83c1fd2b7b83057adf02c139
    bucket_url = r.json()["links"]["bucket"]
    upload_url = f"{bucket_url}/{filepath.name}"
    with open(filepath, "rb") as fp:
        with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
            wrapped_file = CallbackIOWrapper(t.update, fp, "read")
            requests.put(upload_url, data=wrapped_file, params=params)

    print("Done.")
