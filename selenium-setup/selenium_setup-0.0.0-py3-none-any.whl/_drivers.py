"""
https://selenium-python.readthedocs.io/installation.html#drivers
"""


import platform
from enum import Enum
from pathlib import Path
from zipfile import ZipFile

import httpx
import rich.progress


CWD = Path.cwd()


def get_os_info():
    return platform.system(), platform.machine()


class Driver(str, Enum):
    CHROME = 'chrome'


class Chrome:
    name = 'chrome'
    latest_release_url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    link = 'https://chromedriver.storage.googleapis.com/{version}/chromedriver_{operating_system}.zip'
    os_mapping = {
        ('Linux', 'x86_64'): 'linux64',
        # (): 'mac64',
        ('Darwin', 'arm64'): 'mac64_m1',
        ('Windows', 'AMD64'): 'win32',
    }

    @classmethod
    def _download(cls, url: str):
        driver_file = CWD / url.rsplit('/', 1)[-1]
        # return driver_file

        if driver_file.exists():
            print(f'file {driver_file.relative_to(CWD)} exists')
            return driver_file

        with driver_file.open(mode='wb') as _f:
            print(f'downloading to: {driver_file}')
            with httpx.stream("GET", url) as response:
                total = int(response.headers["Content-Length"])
                with rich.progress.Progress(
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    rich.progress.BarColumn(bar_width=None),
                    rich.progress.DownloadColumn(),
                    rich.progress.TransferSpeedColumn(),
                ) as progress:
                    download_task = progress.add_task("Download", total=total)
                    for chunk in response.iter_bytes():
                        _f.write(chunk)
                        progress.update(
                            download_task, completed=response.num_bytes_downloaded
                        )
        return driver_file

    @classmethod
    def _unzip_driver_file(cls, driver_file: Path):
        with ZipFile(file=driver_file) as _z:
            _z.extractall(path=CWD)

    @classmethod
    def download(cls, version: str = None, /):
        os_info = get_os_info()
        print(f'{os_info = }')

        if version is None:
            version = httpx.get(cls.latest_release_url).text
        print(f'{cls.name} {version = }')

        operating_system = cls.os_mapping.get(os_info)
        if operating_system is None:
            raise RuntimeError

        _url = cls.link.format(version=version, operating_system=operating_system)
        driver_file = cls._download(url=_url)

        cls._unzip_driver_file(driver_file)
