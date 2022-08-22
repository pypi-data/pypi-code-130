from dataclasses import make_dataclass
from typing import List
import json
from typing import Tuple
from typing import Any

from naveen.experiment.config.config_validator import ConfigValidator


class DynamicConfigMaker(object):

    # figure out type anno here is too hard
    def from_json(self, config_file: str):  # type: ignore

        validator: ConfigValidator = ConfigValidator()
        assert validator.is_valid_config_file(config_file)

        with open(config_file, "r") as inf:
            jsonconfig = json.load(inf)
            jsonconfig['filename'] = config_file

        # https://stackoverflow.com/questions/52534427/dynamically-add-fields-to-dataclass-objects
        fields: List[Tuple[str, Any]] = []
        fields.append(("name", str))
        fields.append(("reshaper", List[str]))
        fields.append(("plotter", List[str]))
        for k, v in jsonconfig.items():
            if k not in ["name", "reshaper", "plotter"]:
                fields.append((k, type(v)))

        X = make_dataclass('DynamicConfig', fields)

        # https://www.reddit.com/r/learnpython/comments/9h74no/convert_dict_to_dataclass/
        return X(**jsonconfig)
