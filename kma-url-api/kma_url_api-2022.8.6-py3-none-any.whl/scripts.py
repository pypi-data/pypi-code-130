import asyncio
import logging
import os
import re
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import click
from click_loglevel import LogLevel
from clutter.logging import logger

from .nwp import convert_to_lola, convert_to_netcdf, download_url, list_download_urls, upload_file
from .const import generate_update_datetimes


@click.group()
def kma_url_api():
    pass


@kma_url_api.command()
@click.option("-s", "--start", type=str, required=True)
@click.option("-e", "--end", type=str)
@click.option("--max-step", type=int, show_default=True)
@click.option("--nwp", type=str, default="l015", show_default=True)
@click.option("--surface", type=str, default="unis", show_default=True)
@click.option("--request-list-timeout", type=int, default=2, show_default=True)
@click.option("--log-level", type=LogLevel(), default=logging.INFO, show_default=True)
def get_download_urls(
    start,
    end,
    max_step,
    nwp,
    surface,
    request_list_timeout,
    log_level,
):
    # set logger config
    logger.setLevel(log_level)

    # conf for list_download_urls
    get_urls_conf = {
        "max_step": max_step,
        "nwp": nwp,
        "surface": surface,
        "timeout_sec": request_list_timeout,
    }

    # parse start and end
    start = re.sub("[^0-9]", "", start) + "00"
    start = datetime.strptime(start[:10], "%Y%m%d%H")
    if end is not None:
        end = re.sub("[^0-9]", "", end) + "00"
        end = datetime.strptime(end[:10], "%Y%m%d%H")

    # get update datetimes
    dates = generate_update_datetimes(start=start, end=end)

    # async task
    async def task():
        for date in dates:
            # get list_urls
            list_urls = await list_download_urls(str_datetime=date.strftime("%Y%m%d%H"), **get_urls_conf)
            logger.info(f"[KMA-URL-API] Got {len(list_urls)} URLs, Sample: {list_urls[-1]}")

    asyncio.run(task())


@kma_url_api.command()
@click.option("--url", type=str, required=True)
@click.option("--check-size", type=int, default=None)
@click.option("--stage-dir", type=str, default=".")
@click.option("--bucket", type=str, default="s3-ml-datasets", show_default=True)
@click.option("--dst-dir", type=str, default="kma-url-api/l015", show_default=True)
@click.option("--log-level", type=LogLevel(), default=logging.INFO, show_default=True)
def url_to_s3(
    url,
    check_size,
    stage_dir,
    bucket,
    dst_dir,
    log_level,
):
    logger.setLevel(log_level)

    async def task():

        t0 = time.time()
        logger.info(f"Start Download {url}")
        filepath = await download_url(url=url, size=check_size, stage_dir=stage_dir)
        logger.info(f"Finish Download, {time.time() - t0} sec.")

        t1 = time.time()
        logger.info(f"Start Convert to Lola {filepath}")
        filepath = convert_to_lola(filepath)
        logger.info(f"Finish Convert to Lola, {time.time() - t1} sec.")

        t2 = time.time()
        logger.info(f"Start Convert to NetCDF {filepath}")
        filepath = convert_to_netcdf(filepath)
        logger.info(f"Finish Convert to NetCDF, {time.time() - t2} sec.")

        logger.info(f"Start Uploading to Bucket '{bucket}', Folder '{dst_dir}'")
        result = upload_file(filepath, bucket=bucket, objkey=os.path.join(dst_dir, Path(filepath).name))

        logger.info(f"UPLOAD FINISHED {result}")

    try:
        asyncio.run(task())
    except Exception as ex:
        logger.error(f"[KMA-URL-API] Stop! - {ex}")
