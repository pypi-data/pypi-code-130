"""Contains functions to read/write localisation data"""


from collections import OrderedDict
from pathlib import Path
from re import sub
from typing import Mapping, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString


def _initialize_yaml() -> YAML:
    yaml = YAML()
    print()
    # error: Incompatible types in assignment (expression has type "float", variable has type "None")
    yaml.width = float("inf")  # type: ignore
    yaml.allow_unicode = True
    yaml.encoding = "utf-8"
    yaml.indent = 2
    # error: Incompatible types in assignment (expression has type "bool", variable has type "None")
    yaml.preserve_quotes = True  # type: ignore
    # error: error: Incompatible types in assignment (expression has type "str", variable has type "None")
    yaml.line_break = "\n"  # type: ignore
    yaml.block_seq_indent = 2
    yaml.allow_duplicate_keys = True
    return yaml


def _replace_whitespace_before_keys(path: Path) -> None:
    content = path.read_bytes()
    new_content = []
    for line in content.split(b"\n"):
        new_content.append(sub(rb"^(\s\s)", b" ", line, count=1))
    path.write_bytes(b"\n".join(new_content))


def _replace_clrf_with_lf(path: Path) -> None:
    content = path.read_bytes()
    crlf_symbol = b"\r\n"
    lf_symbol = b"\n"
    content = content.replace(crlf_symbol, lf_symbol)
    path.write_bytes(content)


def _save_as_utf_8_bom(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8-sig"), encoding="utf-8-sig")
    ## path.write_bytes(b"feff" + path.read_bytes())
    # import codecs
    # import mmap


#
## Open file for read and write and then immediately map the whole file for write
# with open(path, "r+b") as f, mmap.mmap(
#    f.fileno(), 0, access=mmap.ACCESS_WRITE
# ) as mm:
#    origsize = mm.size()
#    bomlen = len(codecs.BOM_UTF8)
#    # Allocate additional space for BOM
#    mm.resize(origsize + bomlen)
#
#    # Copy file contents down to make room for BOM
#    # This reads and writes the whole file, and is unavoidable
#    mm.move(bomlen, 0, origsize)
#
#    # Insert the BOM before the shifted data
#    mm[:bomlen] = codecs.BOM_UTF8


def read_localisation(
    path: Path,
) -> OrderedDict[str, OrderedDict[str, Union[str, int]]]:
    """Reads a localisation file and returns its content as a dict

    Arguments:
        path: a localisation path

    Returns:
        a dict of similar structure as the path
    """

    def _recursively_convert_to_ordered_dict(item):
        new_item = OrderedDict()
        if not item:
            return new_item
        for key, value in item.items():
            if isinstance(value, CommentedMap):
                new_item[key] = _recursively_convert_to_ordered_dict(value)
            else:
                new_item[key] = value
        return new_item

    yaml_representation = _initialize_yaml().load(path)
    return _recursively_convert_to_ordered_dict(yaml_representation)


def write_localisation(
    payload: Mapping[str, Mapping[str, Union[str, int]]], destination: Path
) -> None:
    """Writes a dict-like object to the destination

    Arguments:
        payload: a dict-like structure mirroring the localisation structure
        destination: where to write the file
    """
    if payload:
        if len(payload.keys()) > 1:
            raise RuntimeError(f"Too many language keys: {payload.keys()}")
        language_key = list(payload.keys())[0]
        inner_dict = CommentedMap()
        for key, value in payload[language_key].items():
            inner_dict[key] = DoubleQuotedScalarString(str(value))
        transformed_payload = {language_key: inner_dict}
        _initialize_yaml().dump(transformed_payload, destination)
    else:
        destination.touch()
    _replace_whitespace_before_keys(destination)
    _replace_clrf_with_lf(destination)
    _save_as_utf_8_bom(destination)
