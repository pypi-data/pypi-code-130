import os
import oead

from pathlib import Path
from typing import Any
from oead import yaz0, byml


def get_src_dir() -> Path:
    return Path(os.path.dirname(os.path.realpath(__file__)))

DEFAULTS = byml.from_binary(
    yaz0.decompress(Path(f"{get_src_dir()}\\data\\defaults.sbyml").read_bytes())
)

def get_item_tables(prefixes: list) -> list:

    if type(prefixes) is str:
        return get_item_table(prefixes)

    ret: list = []
    for prefix in prefixes:
        ret += get_item_table(prefix)

    return ret

def get_item_table(prefix: str) -> list:

    count = -1
    add = list()
    rem = list()

    if prefix in DEFAULTS["ItemTableData"]:
        count = DEFAULTS["ItemTableData"][prefix]["len"]
        add = [int(i) for i in DEFAULTS["ItemTableData"][prefix]["add"]]
        rem = [int(i) for i in DEFAULTS["ItemTableData"][prefix]["rem"]]

    if count == -1:
        raise Exception(f"Could not find data for '{prefix}'")

    return [
        prefix + (f"0{i+1}" if len(str(i + 1)) == 2 else f"00{i+1}")
        for i in list(range(count)) + list(_i - 1 for _i in add)
        if i + 1 not in rem
    ]


def get_evaluated_weights(type: str = "") -> list:
    return [
        name for name in DEFAULTS[type] for _ in range(DEFAULTS[f"Weights{type}"][name])
    ]


def is_enemy(config_name: str) -> bool:
    return (
        config_name[0:5] == "Enemy"
        if not any(flag in config_name for flag in DEFAULTS["BlacklistFlags"])
        else False
    )


def to_oead(obj) -> Any:

    # Get the object type
    obj_type = type(obj)

    # Check teh obnject type
    if obj_type not in [int, float, list, dict]:
        return obj

    # Handle int values
    if obj_type is int:
        try:
            return oead.S32(obj)
        except:
            return oead.U32(obj)

    # Handle float values
    elif obj_type is float:
        return oead.F32(obj)

    # Handle list values
    elif obj_type is list:

        # Create temp python std list
        _list = list()
        for item in list(obj):
            _list.append(to_oead(item))

        return oead.byml.Array(_list)

    # Handle dict values
    elif obj_type is dict:

        # Create temp python std dict
        _dict = dict()
        for key, value in dict(obj).items():
            _dict[to_oead(key)] = to_oead(value)

        return _dict
