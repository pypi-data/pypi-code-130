__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
import logging
import statistics
import threading

from datetime import datetime
import time

from urllib.parse import urlparse

import multiprocessing as mp

from pathlib import Path

import requests

import typer

import bitia.config


def get_content_length(url: str) -> int:
    """Find content length of an url"""
    o = urlparse(url)
    if o.scheme == "ftp":
        from ftplib import FTP

        # FixMe: username, password
        ftp = FTP(o.netloc)
        ftp.login()
        return ftp.size(o.path) or -1

    res = requests.head(url, allow_redirects=True)
    return int(res.headers.get("content-length", -1))


def url2filepath(url: str, filename: T.Optional[str] = None) -> Path:
    """Given a url, determine its path in cache"""
    cachedir = bitia.config.cachedir()
    download_dir = cachedir / url
    if filename is None:
        o = urlparse(url)
        filename = o.fragment if o.fragment else Path(o.path).name
        assert filename, f"Could not determine the name of downloaded file from {o}"
    return download_dir / filename


def st_size(path: Path) -> int:
    if path.exists():
        return path.stat().st_size
    return -1


def download_if_not_in_cache(url: str) -> Path:
    filepath_in_cache = url2filepath(url)
    filepath_in_cache.parent.mkdir(parents=True, exist_ok=True)
    download_file(url, filepath_in_cache)

    assert filepath_in_cache.exists()
    return filepath_in_cache


def show_download_progress(remote_size: int, filepath: Path):
    """A callback that monitors the progress of files being downloaded.

    We have already calculated the `Content-Length` of the remote url. When the
    on-disk size of the `filepath` matches `remote_size`, function returns. Else
    it continue polling for the size every n seconds.
    """
    sleepfor = 1.0
    time.sleep(sleepfor)
    size = st_size(filepath)
    added = []
    while size < remote_size:
        left = remote_size - size
        added.append(st_size(filepath) - size)
        size = st_size(filepath)
        eta_min = -1.0
        try:
            eta_min = (left * sleepfor / statistics.mean(added)) / 60.0
            # too-fast or too-slow updates are bad.
            sleepfor = min(30, eta_min * 60 / 200)
        except Exception:
            pass
        ratio = float(size) * 100 / remote_size
        now = datetime.now().isoformat()
        typer.echo(f"{now} <{filepath.name}>: {ratio:05.2f}%, ETA={eta_min:5.1f} mins.")
        time.sleep(sleepfor)


def download_file(url: str, filepath: Path):
    """Download a given url and save content to the given filepath"""
    remote_size = get_content_length(url)
    assert remote_size > 0
    local_size = st_size(filepath)
    if remote_size == local_size:
        logging.info(f"Found in cache: {url}. Will reuse.")
        return

    # Download and use a thread to monitor the progress.
    p = mp.Process(target=show_download_progress, args=(remote_size, filepath))
    p.start()
    logging.info(f"Downloading `{url}` to cache.")
    _, retcode = bitia.common.run_command(
        f"wget --continue --timestamping -o {filepath.name} {url}",
        cwd=filepath.parent,
    )
    p.terminate()
    assert retcode is not None


def cache_download(
    urls: T.List[str], timeout: int = 3600, processes: T.Optional[int] = None
):
    logging.info("Making data available in the CoPR cache")
    with mp.pool.ThreadPool(processes) as pool:
        result = pool.map_async(download_if_not_in_cache, urls)
        result.get(timeout=timeout)
    logging.info("\tDone")


def make_available(urls_or_file: T.Union[str, Path]):
    """Download them in cache"""
    if Path(urls_or_file).exists():
        urls = Path(urls_or_file).read_text(encoding="utf-8").strip().split()
    else:
        urls = str(urls_or_file).split(",")
    cache_download(urls)
