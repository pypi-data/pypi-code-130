import click

from ..scriptify import scriptify_python


@click.command()
@click.argument('file_name')
def scriptify_py(file_name: str) -> None:
    """
    Convert a python script into a generator that
    can be used to parameterize the original script.

    A file will created named generated_<filename>.py

    :param file_name:
    :type file_name: str
    :returns:

    """
    scriptify_python(file_name)
