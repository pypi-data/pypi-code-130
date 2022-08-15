import typer

from . import _drivers


def main(
    *,
    driver: str = typer.Argument(_drivers.Driver.CHROME.value),
    ver: str = None,
    list: bool = False,
):
    if list:
        return _list_vers(driver)

    if driver.lower() == _drivers.Driver.CHROME.value:
        return _drivers.Chrome.download(ver)
    raise RuntimeError


def _list_vers(driver: str):
    if driver.lower() == _drivers.Driver.CHROME.value:
        return _drivers.Chrome.list_vers()
    raise RuntimeError


app = typer.Typer(pretty_exceptions_enable=False)
app.command()(main)
app()
