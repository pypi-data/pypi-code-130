__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T

import typer

app = typer.Typer()


#
# Utilities
#
@app.command("make_available")
@app.command("download")
def make_available(urls_or_file):
    """Make the data available from a given user input.

    Parameters
    ----------
    urls_or_file : str, Path
        urls as csv or a file containing url. One one each line.
    """
    import bitia.infra.cache

    bitia.infra.cache.make_available(urls_or_file)


@app.command("ensure")
def ensure(executables: T.List[str]):
    """Ensure that following executables are available.
    This is meant to work inside the container.

    Parameters
    ----------
    executables:
        List of executables.
    """
    from bitia.infra.packages import PackageManger

    pm = PackageManger()
    pm.ensures(executables)


if __name__ == "__main__":
    app()
