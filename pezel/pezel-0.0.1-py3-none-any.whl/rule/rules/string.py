import pystache
import yaml

from helper.logging import CriticalException
from rule.rules.abstract import AbstractRule


class MustacheRule(AbstractRule):
    @classmethod
    def from_yaml(cls, root_path, loader, yaml_node, host_root_path=None):
        if isinstance(yaml_node.node, yaml.ScalarNode):
            data = {'string': yaml_node.get_value(loader), 'values': {}}
        elif isinstance(yaml_node.node, yaml.MappingNode):
            data = yaml_node.get_value(loader)
        else:
            raise CriticalException(f'Unknown Node type {type(yaml.MappingNode)}.')

        return pystache.render(data['string'], {**loader.global_vars, **data['values']})

    @staticmethod
    def get_yaml_tag():
        return u'!mustache_str'
