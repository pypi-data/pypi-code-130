import click

import json
import os
import errno
from collections import Counter
from datetime import datetime

from . import get_uow_info

from jsonschema import Draft4Validator

ALLOWED_FORMATS = ["whp_netcdf", "exchange", "woce", "text", "pdf"]
ALLOWED_DATA_TYPES = [
    "bottle",
    "ctd",
    "documentation",
    "summary",
    "large_volume",
    "trace_metals",
]
ALLOWED_ROLES = ["dataset", "unprocessed", "merged", "hidden", "archive", "residual"]
ALLOWED_ACTIONS = ["new", "merge"]

REPLACES_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "file": {"type": "string"},
        "action": {"enum": ["new"]},
        "replaces": {"type": "string"},
        "from": {"type": "array", "items": {"type": "string"}},
    },
    "requried": ["file", "action", "replaces"],
    "additionalProperties": False,
}

MERGE_FILE_SCHEMA = {
    "type": "object",
    "properties": {"file": {"type": "string"}, "action": {"enum": ["merge"]}},
    "requried": ["file", "action"],
    "additionalProperties": False,
}

NEW_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "file": {"type": "string"},
        "action": {"enum": ["new"]},
        "data_format": {"type": "string", "enum": ALLOWED_FORMATS},
        "data_type": {"type": "string", "enum": ALLOWED_DATA_TYPES},
        "role": {"type": "string", "enum": ALLOWED_ROLES},
        "from": {"type": "array", "items": {"type": "string"}},
    },
    "requried": ["file", "action", "data_format", "data_type", "role"],
    "additionalProperties": False,
}

UOW_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "oneOf": [REPLACES_FILE_SCHEMA, MERGE_FILE_SCHEMA, NEW_FILE_SCHEMA]
            },
        },
        "processing_note": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "data_type": {"type": "string"},
                "action": {"type": "string"},
                "summary": {"type": "string"},
                "name": {"type": "string"},
                "notes": {"type": "string"},
            },
            "requried": ["date", "data_type", "action", "summary", "name", "notes"],
            "additionalProperties": False,
        },
    },
    "requried": ["files", "processing_note"],
    "additionalProperties": False,
}

uow_validator = Draft4Validator(UOW_JSON_SCHEMA)


def _validate_uow_json(uow_json):
    if not uow_validator.is_valid(uow_json):
        for error in uow_validator.iter_errors(uow_json):
            print(error.message)
        raise click.Abort()


def _ensure_unique_files(uow_json):
    _, basedir = get_uow_info()
    files = uow_json["files"]
    cnt = Counter()
    for file in files:
        cnt[file["file"]] += 1

    duplicates = []
    for file_name, count in cnt.items():
        if count > 1:
            duplicates.append(file_name)
    if duplicates:
        print("Duplicated files in uow.json:", *duplicates, sep="\n")
        raise click.Abort()

    for file_name, count in cnt.items():
        full_path = os.path.join(basedir, file_name)
        if not os.path.exists(full_path):
            print(f"file {file_name} does not appear to exist")
            raise click.Abort()


def _ensure_from_in_files(uow_json):
    files = {file["file"] for file in uow_json["files"]}

    for file in uow_json["files"]:
        try:
            from_list = {f for f in file["from"]}
        except KeyError:
            continue
        if from_list != from_list & files:
            print(
                f"file {file['file']} has entrys in its from list not in the files list"
            )
            raise click.Abort()


def _ensure_replaces_in_files(uow_json):
    files = {file["file"] for file in uow_json["files"]}

    for file in uow_json["files"]:
        try:
            replaces = file["replaces"]
        except KeyError:
            continue
        if replaces not in files:
            print((f"file {file['file']} replaces a file not also in the files" "list"))
            raise click.Abort()


def _check_processing_note(uow_json):
    notes = uow_json["processing_note"]["notes"]
    date = uow_json["processing_note"]["date"]

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("processing note date is not in YYYY-MM-DD format")
        raise click.Abort()

    if notes.startswith("@"):
        _, basedir = get_uow_info()
        path = notes[1:]
        full_path = os.path.join(basedir, path)
        if not os.path.exists(full_path):
            print(f"The processing note file doesn't seem to exist:\n{path}")
            raise click.Abort()


def _check_uow_json(uow_json):
    print("\nchecking uow.json:")
    _validate_uow_json(uow_json)
    _ensure_unique_files(uow_json)
    _ensure_from_in_files(uow_json)
    _ensure_replaces_in_files(uow_json)
    _check_processing_note(uow_json)
    print("    uow.json looks (structurally) OK")


def load_uow_json():
    _, basedir = get_uow_info()

    json_path = os.path.join(basedir, "uow.json")

    try:
        with open(json_path, "r") as f:
            uow_json = f.read()
    except IOError as e:
        if e.errno == errno.ENOENT:
            print("no uow.json file")
            raise click.Abort()
        else:
            print(
                (
                    "Error while reading uow.json, please include the following "
                    "traceback with any bug reports:"
                )
            )
            raise

    try:
        uow_json = json.loads(uow_json)
    except ValueError:
        print((f"JSON load error, is this file valid JSON?:\n{json_path}"))
        raise click.Abort()
    _check_uow_json(uow_json)
    return uow_json
