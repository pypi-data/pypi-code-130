from . import _drivers


def _download(driver: str, version: str):
    if driver.lower() == _drivers.Driver.CHROME.value:
        return _drivers.Chrome.download(version)
    raise RuntimeError


def main(
    *,
    driver: str = _drivers.Driver.CHROME.value,
    version: str = None,
):
    _download(
        driver=driver,
        version=version,
    )
