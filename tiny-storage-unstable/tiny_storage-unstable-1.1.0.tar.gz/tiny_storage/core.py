"""Module implementing all external functionality."""


import os
import sys
from pathlib import Path

import yaml
from .internals import pull, push, put


class SafetyException(Exception):
    pass


class Type:
    """Container for storage types."""

    local = lambda name: Path(f"{name}.yaml")

    if sys.platform.startswith("linux"):
        user = lambda name: os.getenv("HOME") / Path(f".{name}.yaml")
        user_config = lambda name: os.getenv("HOME") / Path(f".config/{name}.yaml")
        global_data = lambda name: Path(f"/var/lib/{name}.yaml")
        global_config = lambda name: Path(f"/etc/{name}.yaml")

    elif sys.platform.startswith("win"):
        user = lambda name: os.getenv("APPDATA") / Path(f"{name}/{name}.yaml")
        user_config = lambda name: os.getenv("APPDATA") / Path(f"{name}/config.yaml")
        global_data = lambda name: os.getenv("PROGRAMDATA") / Path(f"{name}/data.yaml")
        global_config = lambda name: os.getenv("PROGRAMDATA") / Path(
            f"{name}/config.yaml"
        )


class Unit:
    """Storage unit containing all application data of given type.

    Attributes:
        name: Name of the application
        type: Type of data you are storing
    """

    def __init__(self, name, type=None):
        self.name = name
        self.type = type or getattr(Type, "user", Type.local)

    def __call__(self, key):
        return Entry(self, key)


class Entry:
    def __init__(self, unit, key):
        self.unit = unit
        self.key = key

    def _act(self, function, value):
        path = Path(self.unit.type(self.unit.name))

        if path.exists():
            data = yaml.safe_load(path.read_text()) or {}
        else:
            data = {}

        was_modified, result = function(data, self.key.split("."), value)

        if was_modified:
            if not path.parent.exists():
                path.parent.mkdir(parents=True)

            with open(path, "w") as f:
                try:
                    yaml.safe_dump(data, f)
                except yaml.representer.RepresenterError as ex:
                    raise SafetyException(
                        "One of the passed types is not safe to store in your "
                        "unit. Replace it with primitive type or make it a "
                        "subclass of yaml.YAMLObject."
                    ) from ex

        return was_modified, result

    def pull(self, value=None):
        """Get the content of the entry or `value`

        Args:
            value: Default value

        Returns:
            Content of the entry
        """
        return self._act(pull, value)[1]

    def push(self, value=True):
        """Set the content of the entry with force.

        Overwrites existing entries and creates intermediate ones
        if needed.

        Args:
            value: Value you are pushing; should be a of yaml-safe type

        Returns:
            `value` argument

        Raises:
            yaml.representer.RepresenterError
        """
        return self._act(push, value)[1]

    def put(self, value=True):
        """Set the content of the entry without force.

        Does not overwrite existing entries, but can create intermediate
        ones if needed.

        Args:
            value: Value you are putting; should be a of yaml-safe type

        Returns:
            Resulting value of the entry
        """
        return self._act(put, value)[1]

    def try_push(self, value=True):
        """Set the content of the entry with force.

        Overwrites existing entries and creates intermediate ones
        if needed.

        Args:
            value: Value you are pushing; should be a of yaml-safe type

        Returns:
            Did `value` differ from previous value
        """
        return self._act(push, value)[0]

    def try_put(self, value=True):
        """Set the content of the entry without force.

        Does not overwrite existing entries, but can create
        intermediate ones if needed.

        Args:
            value: Value you are putting; should be a of yaml-safe type

        Returns:
            True if entry was created, False if entry already existed
        """
        return self._act(put, value)[0]
