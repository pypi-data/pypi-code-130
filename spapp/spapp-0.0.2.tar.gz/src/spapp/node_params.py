import re
import json
from collections import OrderedDict
from spapp.exception import InvalidParamError


class NodeParams(object):
    def __init__(self, cli_params, node_info):
        params = node_info.get('params')
        self._parse_params(cli_params, params)

    def _parse_params(self, cli_params, params):
        regex = r"--([^\s]+)\s+(?:(?P<quote>[\'\"])(.*?)(?P=quote)|([^\'\"\s]+))"
        groups = re.findall(regex, cli_params, flags=re.S)
        params_set = {}
        for group in groups:
            params_set[group[0]] = group[2] if group[2] else group[3]

        self._params = OrderedDict()
        for key, value in params.items():
            if key.startswith('__'):
                continue

            self._params[key] = params_set.get(key)

    def get(self, name):
        if name not in self._params:
            raise InvalidParamError(f'invalid param name {name}')

        return self._params.get(name)

    def __str__(self):
        return json.dumps(dict(self._params))
