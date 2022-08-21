#!/usr/bin/env python3

from os.path import isfile

from yaml import parser, safe_dump, safe_load


def read_fasts() -> list:

    yaml_file_name = __get_file_name()

    fasts = []

    if isfile(yaml_file_name):

        try:

            with open(yaml_file_name, encoding="utf-8-sig") as yaml_file:
                fasts = safe_load(yaml_file)

        except parser.ParserError:

            print(f"Unable to parse: {yaml_file_name}")

    return fasts


def write_fasts(fasts: list) -> None:

    for fast in fasts:

        fast["started"] = fast["started"].replace(microsecond=0)

        if fast.get("stopped") is not None:
            fast["stopped"] = fast["stopped"].replace(microsecond=0)

    yaml_file_name = __get_file_name()

    with open(yaml_file_name, encoding="utf-8-sig", mode="w") as yaml_file:
        safe_dump(fasts, yaml_file)


def __get_file_name() -> str:

    return "fasts.yaml"
