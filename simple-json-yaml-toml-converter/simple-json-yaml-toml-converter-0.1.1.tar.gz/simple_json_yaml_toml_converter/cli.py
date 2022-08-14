import json
import logging
import re
import sys
from typing import List, Optional, Type

import click
import toml
import yaml

logger = logging.getLogger(__name__)


class Filetype:
    extensions: List[str]

    @classmethod
    def serialize(cls, dictionary):
        raise NotImplementedError

    @classmethod
    def deserialize(cls, file) -> dict:
        raise NotImplementedError


class Json(Filetype):
    extensions = ["json"]

    @classmethod
    def serialize(cls, dictionary):
        return json.dumps(dictionary)

    @classmethod
    def deserialize(cls, file):
        return json.load(file)


class Yaml(Filetype):
    extensions = ["yaml"]

    @classmethod
    def serialize(cls, dictionary):
        return yaml.dump(dictionary)

    @classmethod
    def deserialize(cls, file):
        return yaml.load(file, Loader=yaml.FullLoader)


class Toml(Filetype):
    extensions = ["toml"]

    @classmethod
    def serialize(cls, dictionary):
        return toml.dumps(dictionary)

    @classmethod
    def deserialize(cls, file):
        return toml.load(file)


FILETYPES = [Json, Yaml, Toml]


def get_filetype(file_extension: str) -> Type[Filetype]:
    result: Optional[Type[Filetype]] = None
    for filetype in FILETYPES:
        if file_extension in filetype.extensions:
            result = filetype
            break
    if not result:
        raise ValueError
    return result


@click.command
@click.argument("input_files", nargs=-1, type=str)
@click.option("-o", "--output-format", type=str)
@click.option("--debug/--no-debug", type=bool, default=False)
@click.option("-e", "--encoding", type=str, default="utf-8")
def command(input_files, output_format, debug, encoding):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    output_filetype = get_filetype(output_format)
    for filename in input_files:
        extension = re.search("[^\.]*$", filename).group()
        logger.debug("Input file extension: %s", extension)
        input_file_filetype = get_filetype(extension)
        content = None
        with open(filename, "r", encoding=encoding) as file:
            content = input_file_filetype.deserialize(file)
        output = output_filetype.serialize(content)
        sys.stdout.write(output)


if __name__ == "__main__":
    command()
