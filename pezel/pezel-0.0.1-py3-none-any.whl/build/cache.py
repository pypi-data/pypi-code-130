import diskcache
import hashlib
import json
import pathlib

from metadata import VERSION
from helper.dictionary import set_nested_dict


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes) or isinstance(obj, bytearray):
            return obj.decode()
        if isinstance(obj, pathlib.PosixPath):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class BuildCache(object):
    @staticmethod
    def _get_build_hash(rule, inputs):
        hash_dict = {'rule': rule, 'inputs': inputs}
        return hashlib.sha1(json.dumps(hash_dict, sort_keys=True, cls=ExtendedJSONEncoder).encode("utf-8")).hexdigest()

    def __init__(self, cache_path):
        self.cache = diskcache.FanoutCache(cache_path, eviction_policy='none')

        # TODO: Remove latter
        self.cache.clear()

        if 'version' not in self.cache or self.cache['version'] != VERSION:
            self.cache.clear()
            self.cache['version'] = VERSION

    def build(self, rule, input_rules):
        inputs = rule.get_inputs()
        hash_inputs = rule.get_inputs()
        for input_key, input_rule in input_rules:
            cache = self.cache[input_rule.node_id]
            set_nested_dict(inputs, input_key, cache['out'])
            set_nested_dict(hash_inputs, input_key, cache['build_hash'])

        build_hash = self._get_build_hash(rule.get_yaml_tag(), hash_inputs)

        if rule.node_id in self.cache and self.cache[rule.node_id]['build_hash'] == build_hash:
            return self.cache[rule.node_id]['out'], None

        out, artifacts = rule.run(inputs)
        if artifacts is None:
            self.cache[rule.node_id] = {
                'build_hash': build_hash,
                'out': out}

        return out, artifacts
