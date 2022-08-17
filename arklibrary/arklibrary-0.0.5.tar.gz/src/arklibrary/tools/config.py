from pathlib import Path
import json


class Config:
    __config = None

    @classmethod
    def get(cls):
        if cls.__config:
            return cls.__config
        path = Path.cwd() / Path("config.json")
        assert path.exists(), "Unable to find the config file."
        with open(path, 'r') as r:
            cls.__config = json.load(r)

    @classmethod
    def admin_password(cls):
        return cls.get()['admin_password']

    @classmethod
    def ark_lnk_path(cls):
        return cls.get()['ark_lnk_path']

    @classmethod
    def admin_player_id(cls):
        return cls.get()['admin_player_id']

