import json


class ConfigValidator(object):

    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_config_file(path_to_config: str) -> bool:
        with open(path_to_config, "r") as inf:
            jsonconfig: dict = json.load(inf)

            required_fields = ["name", "reshaper", "plotter",
                               "experiment_module", "experiment_class"]

            for field in required_fields:
                assert field in jsonconfig

        assert " " not in jsonconfig["name"], "Name cant have spaces"
        assert "/" not in jsonconfig["name"], "Name cant have slashes"

        return True
