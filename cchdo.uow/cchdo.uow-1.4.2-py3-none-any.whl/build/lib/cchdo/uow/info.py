import json

from . import get_uow_info


def _print_file_list(uow_info, key):
    if key is None:
        print(json.dumps(uow_info["cruise_metadata"], indent=2))
    elif str(key) in uow_info["file_metadata"]:
        print(json.dumps(uow_info["file_metadata"][str(key)], indent=2))
    else:
        print("No Files")


def do_info(file_id):
    """Print the entire metadata object for a file"""
    uow_info, _ = get_uow_info()
    _print_file_list(uow_info, file_id)
