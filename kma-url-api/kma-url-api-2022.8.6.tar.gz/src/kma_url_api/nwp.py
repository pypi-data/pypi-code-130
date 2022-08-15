import asyncio
import logging
import logging.config
import os
import re
import subprocess
import time
import traceback
from typing import Union
from urllib.parse import urlencode
from pathlib import Path
from datetime import datetime

import aiohttp
import boto3
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt

from .const import API_KEY, BASE_URL, ERROR_NOTICES, NWP


logger = logging.getLogger(__name__)

################################################################
# Helpers
################################################################
# generate endpoint
def _generate_endpoint(*url_or_paths, **query_params):
    url_or_paths = [x.strip("/") for x in url_or_paths]
    return "?".join(["/".join(url_or_paths), urlencode(query_params)])


# split filename and size
def _split_filname_and_size(x):
    return tuple(x.replace(" ", "").replace("\n", "").split(",")[:2])


# async file writer
async def _writer(filepath: str, content: bytes):
    with open(filepath, "wb") as f:
        f.write(content)


################################################################
# Get Download URLs
################################################################
async def list_download_urls(
    str_datetime: str,
    max_step: int = 48,
    nwp: str = "l015",
    surface: str = "unis",
    apiKey: str = API_KEY,
    timeout_sec: int = 1,
    allow_redirects: bool = False,
    max_retry: int = 120,
):
    """
    Examples
    --------
    >>>
    """
    LIST_PATH = "nwp_file_list.php"
    DOWNLOAD_PATH = "nwp_file_down.php"
    DELIM = "="

    # argument - model
    model = None
    for model, sub_models in NWP.items():
        if nwp in sub_models:
            break

    # argument - apiKey
    assert apiKey is not None, "API Key is Required!"

    # tenacity function
    @retry(stop=stop_after_attempt(max_retry))
    async def _request_get(url: str, timeout: int, allow_redirects: bool):
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, timeout=timeout, allow_redirects=allow_redirects) as resp:
                return await resp.text()

    # handle arguments
    str_datetime = re.sub("[^0-9]", "", str_datetime)
    ymd, hh = str_datetime[:8], str_datetime[8:10]

    # gen url
    query = {
        "nwp": model,
        "tmfc": ymd,
        "authKey": apiKey,
    }
    url = _generate_endpoint(BASE_URL, LIST_PATH, **query)

    # request
    resp_text = await _request_get(url=url, timeout=timeout_sec, allow_redirects=allow_redirects)
    for notice in ERROR_NOTICES:
        if notice in resp_text:
            raise ReferenceError(notice)

    # parse response
    list_urls = [_split_filname_and_size(line) for line in resp_text.split(DELIM)]

    # filter results
    tmfc = ymd if hh is None else ymd + hh
    for cond in [nwp, surface, tmfc]:
        if cond is not None:
            list_urls = [url for url in list_urls if cond in url[0]]

    if max_step is not None:
        steps = [f"h0{ef:02d}" for ef in range(max_step + 1)]
        list_urls = [url for url in list_urls if any([step in url[0] for step in steps])]

    # filename to url
    list_urls = [(f"{BASE_URL}/{DOWNLOAD_PATH}?file={fn}&authKey={apiKey}", size) for fn, size in list_urls]

    return list_urls


################################################################
# Download URL
################################################################
async def download_url(
    url: Union[str, tuple],
    size: int = None,
    stage_dir: str = ".",
    timeout_sec: int = 300,
    max_retry: int = 10,
    allow_redirects=True,
):
    filename = None
    query = url.split("?")[-1].split("&")
    for q in query:
        if q.startswith("file="):
            filename = q.split("=")[-1]
    assert filename is not None

    prefix = datetime.strptime(filename.split(".")[1], "%Y%m%d%H").strftime("%Y__%m__%d__%H__")
    filepath = os.path.join(stage_dir, prefix + filename)

    # check filepath
    if os.path.exists(filepath):
        if os.path.getsize(filepath) == size:
            # skip download
            logger.info(f"[KMA-URL-API] File Exists, Skip Download! {filepath}")
            return filepath
        else:
            # remove exist file if size does not match
            os.remove(filepath)

    # retry helper
    @retry(stop=stop_after_attempt(max_retry))
    async def _download(url, filepath, timeout, allow_redirects=True):
        # request
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, timeout=timeout, allow_redirects=allow_redirects) as resp:
                content = await resp.read()
                await _writer(filepath=filepath, content=content)

    # download file
    try:
        t0 = time.time()
        logger.info(f"[KMA-URL-API] Start Download {url} to {filepath}")
        await _download(url=url, filepath=filepath, timeout=timeout_sec, allow_redirects=allow_redirects)
    except Exception as ex:
        logger.error(f"[KMA-URL-API] Download Failed! {url}, {ex}")
        traceback.print_exc()
        raise ex

    # validation
    filesize = os.path.getsize(filepath)
    if size is not None and filesize != size:
        _err = f"file size does not matched! - Target {size}, Downloaded {filesize}"
        logger.error(f"[KMA-URL-API] Download Failed! {url}, {_err}")
        raise ReferenceError(_err)

    # logging
    logger.info(f"[KMA-URL-API] Download Succeed! {filepath} ({filesize//1e3} kB) - {time.time() - t0:.3f} sec.")

    return filepath


################################################################
# Convert to LOLA (LONLAT)
################################################################
def convert_to_lola(
    filepath: str,
    remove_src: bool = False,
):
    # constant
    LOLA_SUFFIX = "lola"
    LOLA_LON = "121.825:425:0.025"
    LOLA_LAT = "32.250:425:0.025"

    # generate lola output name, remove if exists
    fn, ext = filepath.rsplit(".", 1)
    lola_output = ".".join([fn, LOLA_SUFFIX, ext])
    if os.path.exists(lola_output):
        logger.warning(f"[KMA-URL-API] LOLA Converted File Exists, We Will Skip LOLCA Converting - {lola_output}")
    else:
        # GRIB XY to GRIB Lon-Lat
        # ex. kwgrib2 -lola 121.825:850:0.0125 32.250:850:0.0125 test_lola.gb2 grib l015_v070_erlo_unis_h000.2022062800.gb2
        t0 = time.time()
        try:
            cmd = ["kwgrib2", "-lola", LOLA_LON, LOLA_LAT, lola_output, "grib", filepath]
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # raise Error if stderr is not ""
            if (_error := proc.stderr.decode("utf-8")) != "":
                raise ReferenceError(_error)
            # remove source if remove_src
            if remove_src:
                os.remove(filepath)
            # logging
            logger.info(f"[KMA-URL-API] LOLA Convert Succeed! {time.time() - t0:.3f} sec.")
        except Exception as ex:
            proc.kill()
            raise ex

    return lola_output


################################################################
# Convert to NetCDF
################################################################
def convert_to_netcdf(
    filepath: str,
    remove_src: bool = False,
):
    # generate netcdf output name, remove if exists
    fn, ext = filepath.rsplit(".", 1)
    nc_output = f"{fn}.nc"
    if os.path.exists(nc_output):
        logger.info(f"[KMA-URL-API] NetCDF Converted File Exists, We Will Skip NetCDF Converting - {nc_output}")
    else:
        # GRIB Lon-Lat to
        t1 = time.time()
        try:
            cmd = ["kwgrib2", "-netcdf", nc_output, filepath]
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # raise Error if stderr is not ""
            if (_error := proc.stderr.decode("utf-8")) != "":
                raise ReferenceError(_error)
            # remove source if remove_src
            if remove_src:
                os.remove(filepath)
            # logging
            logger.info(f"[KMA-URL-API] NetCDF Convert Succeed! {time.time() - t1:.3f} sec.")
        except Exception as ex:
            proc.kill()
            raise ex

    # logging
    logger.debug(f"[KMA-URL-API] Success Convert {filepath} to {nc_output}.")

    return nc_output


################################################################
# Upload to S3
################################################################
# upload to s3
def upload_file(
    filepath: str,
    bucket: str,
    objkey: str,
    remove_src: bool = False,
) -> str:

    session = boto3.Session()
    s3 = session.client("s3")

    try:
        t0 = time.time()
        s3.upload_file(filepath, bucket, objkey.replace("__", "/"))
        logger.debug(f"[KMA-URL-API] Upload Finished, {time.time() - t0:.3f} sec.")
        if remove_src:
            os.remove(filepath)
    except ClientError as ex:
        logging.error(ex)

    return f"s3://{bucket}/{objkey}"


if __name__ == "__main__":

    import sys

    dt = sys.argv[1]

    logging.basicConfig(level=logging.DEBUG)
    logger.info("INFO WORK?")

    async def main():

        urls = await list_download_urls(str_datetime=dt, max_step=1)
        print(f"Get {len(urls)} URLs, Sample: {urls[0]}")

        print(f"Start Download {urls[0]}")
        filepath = await download_url(urls[0])

        print(f"Start Converting to Lola {filepath}")
        filepath = convert_to_lola(filepath)

        print(f"Start Converting to NetCDF {filepath}")
        filepath = convert_to_netcdf(filepath)

        bucket = "s3-ml-common"
        _dir = "test"
        print(f"Start Uploading to Bucket '{bucket}', Folder '{_dir}'")
        result = upload_file(filepath, bucket=bucket, objkey=os.path.join(_dir, Path(filepath).name))

        print(f"UPLOAD FINISHED {result}")

    asyncio.run(main())
