import os

from tabulate import tabulate

from .uow_json import load_uow_json
from .commit import _prepare_api_calls
from . import get_uow_info, get_fetch_events


def _check_fetched_file_status(event, fetch_path):
    """Performes some very basic checks:
    1) Does the file exist?
    2) Is the file the same size?

    If the file exists and is the same size, assume ok.
    If the file exists and is a different size, assume modified
    If the file does not exists (or has been renamed) assume deleted

    Note that if a file has been modified but the size is the same, this method
    will return OK. This is because to check the actual difference we would
    need to hash the file (which can take a very long time) or keep a copy of
    the fetched file somewhere away from the user to compare.
    """
    expected_size = event["file_size"]

    file_exists = os.path.exists(fetch_path)

    if file_exists and os.path.getsize(fetch_path) == expected_size:
        return "OK"
    elif file_exists:
        return "MODIFIED"
    else:
        return "DELETED"


def _print_fetch_events_table(events):
    print("Fetched Files:")
    table = []
    for event in events:
        fetch_name = f"{event['id']}_{event['file_name']}"
        fetch_path = os.path.join("0.existing_files", fetch_name)

        file_status = _check_fetched_file_status(event, fetch_path)

        row = []
        row.append(event["id"])
        row.append(file_status)
        row.append(fetch_path)

        table.append(row)

    if len(table) > 0:
        print(tabulate(table, headers=["id", "status", "file path"]))
        print(
            (
                "OK: The file present and seems fine\n"
                "MODIFIED: The file appears to be modified, a commit using this "
                "file will not likly succeed, fetch it again to fix\n"
                "DELETED: The file is no longer present on the system or has been "
                "renamed, if not using a deleted file for a commit, just ignore"
            )
        )
    else:
        print("No Files Fetched")


def _print_new_files_table():
    print("\nNew Files:")
    _, basedir = get_uow_info()
    files = []
    for _, _, fils in os.walk(os.path.join(basedir, "1.new_files")):
        files = [[file] for file in fils if not file.startswith(".")]
        break
    if len(files) > 0:
        print(tabulate(files, headers=["file name"]))
    else:
        print("No new files (in 1.new_files)")


def do_status():
    """Print the status of a uow directory"""
    config, _ = get_uow_info()
    fetch_events = get_fetch_events()
    _print_fetch_events_table(fetch_events)
    _print_new_files_table()
    uow_json = load_uow_json()
    print("\nWhat would happen if a commit was done (may take a while):")
    _prepare_api_calls(uow_json, fetch_events, for_human=True)
    print(
        f"\n All files the note would be attached to the cruise id: {config['cruise_id']}"
    )
