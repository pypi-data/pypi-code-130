import sys
from . import java_home as _java_home, lookup_property as _lookup_property


def java_home():
    if len(sys.argv) != 1:
        print(f"Usage: {sys.argv[0]}", file=sys.stderr)
        return 1
    print(_java_home())
    return 0


def java_property():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <property.name>", file=sys.stderr)
        return 1
    print(_lookup_property(sys.argv[1]))
    return 0
