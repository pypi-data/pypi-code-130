import logging
import os
from pathlib import Path


def install_application(template="template.yaml", values=None):
    if values is None:
        values = ["values.yaml"]
    logging.info(f"Values: {values}")

    # First find all directories with app.yamls
    found_paths = find_file_paths('app.yaml')
    for p in found_paths:
        logging.info("p")
    # Then check if the template.yaml is in the current directory


def find_file_paths(target_regex):
    found_paths = []
    for path in Path(os.getcwd()).rglob(target_regex):
        found_paths.append(path)
    return found_paths
