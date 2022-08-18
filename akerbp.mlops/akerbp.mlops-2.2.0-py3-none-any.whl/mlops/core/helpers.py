# helpers.py
import os
from pathlib import Path
from typing import Union, Optional
from akerbp.mlops.core import logger

logging = logger.get_logger(name="mlops_core")


def get_top_folder(path: Union[Path, str]) -> Union[Path, str]:
    """
    Get the top folder of a path.

    Args:
        path (Union[Path, str]): Path to get the top folder from.

    Returns:
        (Union[Path, str]): top parent folder in path
    """
    if isinstance(path, str):
        return path.split(os.sep)[0]
    elif isinstance(path, Path):
        return path.parents[len(path.parents) - 2]


def as_import_path(file_path: Optional[str]) -> Optional[str]:
    """Return path as an import path for python modules


    Args:
        file_path (str, optional): path to file

    Returns:
        (Union[str, None]): path to .py-file with .py extension removed(for importing modules)
    """
    if file_path:
        if not isinstance(file_path, str):
            file_path = str(file_path)
        return file_path.replace(os.sep, ".").replace(".py", "")
    else:
        logging.debug("Empty file path -> empty import path returned")
        return None


def confirm_prompt(question: str) -> bool:
    """Helper function to ask user for confirmation

    Args:
        question (str): question to ask user

    Returns:
        (bool): True if user confirms, False otherwise
    """
    reply = None
    while reply not in ("y", "n"):
        reply = input(f"{question} (y/n): ").lower()
    return reply == "y"
