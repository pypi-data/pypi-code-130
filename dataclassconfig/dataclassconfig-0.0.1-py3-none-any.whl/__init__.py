import typing as tp
from dataclasses import dataclass
from pathlib import Path

import dacite
import yaml  # type: ignore


class Config:
    def __init_subclass__(cls):
        dataclass(cls)

    @classmethod
    def load(cls, fp):
        """loads configuration state from file-like object

        Args:
            fp: file-like configuration object

        Returns:
            configuration state
        """
        data = fp
        if isinstance(fp, str):
            fp = Path(fp)
        if isinstance(fp, Path):
            with open(fp.expanduser(), "rb") as file:
                data = file.read()
        try:
            state = yaml.safe_load(data)
        except Exception:
            data = data.read()
            state = yaml.safe_load(data)
        return cls.from_dict(state)

    @classmethod
    def from_dict(cls, state: tp.Dict):
        """loads the configuration state from a dictionary

        Args:
            state (tp.Dict): dictionary containing configuration

        Returns:
            configuration state
        """
        return dacite.from_dict(
            data_class=cls,
            data=state,
            config=dacite.Config(cast=[Path]),
        )
