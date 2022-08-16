import inflect
import itertools

from helper.logging import CriticalException
from rule.rules.abstract import AbstractRule


class ChainRule(AbstractRule):
    @classmethod
    def from_yaml(cls, root_path, loader, yaml_node, host_root_path=None):
        items = yaml_node.get_value(loader)

        try:
            return list(itertools.chain(*items))
        except TypeError as err:
            plural_engine = inflect.engine()

            bad_items = []
            for item_i, item in enumerate(items, start=1):
                try:
                    iter(item)
                except TypeError:
                    bad_items.append(f'{plural_engine.ordinal(item_i)} Item')

            if bad_items:
                raise CriticalException(f'The following items are not iterable: {", ".join(bad_items)}')
            else:
                raise err

    @staticmethod
    def get_yaml_tag():
        return u'!chain'
