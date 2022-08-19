"""YAML utility tools"""
import os
from re import match

import yaml
from jinja2 import Template

from codebox import dir_tools
from codebox import dict_tools


def load(
    path: str,
    recursive: bool = False,
    match_pattern: str = None,
    ignore_empty: bool = False,
    parse_jinja: bool = False,
    jinja_context: dict = None,
) -> dict:
    """Loads and parses a file or a folder containing yaml files.
    All existing dictionaries will be deeply merged.
    Merge order respects file path sorted by name.

    Args:
        path (str): File or directory path.
        recursive (bool, optional): Defaults to False. Whether or not to include subdirectoties.
        match_pattern (str, optional): A regular expression to be used to filter the files to be load
            based on the file's full name.
        ignore_empty (bool, optional): Whether to ignore empty files.
        parse_jinja (bool, optional): Whether to parse Jinja code.
        jinja_context (dict, optional): The Jinja Context.

    Returns:
        dict

    """

    files = []
    if os.path.isdir(path):
        files = sorted(dir_tools.list_files(path, recursive))
    else:
        files = [path]

    data = dict()
    for _file in files:
        if match_pattern and not match(match_pattern, _file):
            continue
        with open(_file) as fobj:
            try:
                file_content = fobj.read()
                if parse_jinja:
                    template = Template(file_content)
                    file_content = template.render(jinja_context or dict())

                data = dict_tools.merge(data, yaml.load(file_content, Loader=yaml.FullLoader))

            except AttributeError:
                if not ignore_empty:
                    raise

    return data
