import click

from tabulate import tabulate
from . import get_uow_info


def _get_list_row(id, file_meta):
    table_headers = [
        "id",
        "role",
        "data type",
        "data format",
        "last submit date",
        "last submit by",
        "file name",
    ]
    row = []
    row.append(id)
    row.append(file_meta["role"])
    row.append(file_meta["data_type"])
    row.append(file_meta["data_format"])
    if len(file_meta["submissions"]) > 0:
        row.append(file_meta["submissions"][0]["date"])
        row.append(file_meta["submissions"][0]["name"])
    else:
        row.append("")
        row.append("")
    row.append(file_meta["file_name"])
    return table_headers, row


def _print_file_list(uow_info, key):
    file_list = []
    if key == "all":
        for file in uow_info["file_metadata"]:
            file_meta = uow_info["file_metadata"][file]
            headers, row = _get_list_row(file, file_meta)
            file_list.append(row)
    elif key == "other":
        for file in uow_info["file_metadata"]:
            file_meta = uow_info["file_metadata"][file]
            if file_meta["role"] in ["dataset", "unprocessed", "merged"]:
                continue
            headers, row = _get_list_row(file, file_meta)
            file_list.append(row)
    else:
        for file in uow_info["file_metadata"]:
            file_meta = uow_info["file_metadata"][file]
            if file_meta["role"] != key:
                continue
            headers, row = _get_list_row(file, file_meta)
            file_list.append(row)

    if len(file_list) > 0:
        click.echo(tabulate(file_list, headers=headers))
    else:
        click.echo("No Files")


def do_list(list_option):
    """List files available for fetching"""
    uow_info, _ = get_uow_info()
    _print_file_list(uow_info, list_option)
