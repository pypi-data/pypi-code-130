import re
from deepdiff.helper import convert_item_or_items_into_compiled_regexes_else_none


class BaseOperator:

    def __init__(self, regex_paths=None, types=None):
        if regex_paths:
            self.regex_paths = convert_item_or_items_into_compiled_regexes_else_none(regex_paths)
        else:
            self.regex_paths = None
        self.types = types

    def match(self, level) -> bool:
        if self.regex_paths:
            for pattern in self.regex_paths:
                matched = re.search(pattern, level.path()) is not None
                if matched:
                    return True
        if self.types:
            for type_ in self.types:
                if isinstance(level.t1, type_) and isinstance(level.t2, type_):
                    return True
        return False

    def give_up_diffing(self, level, diff_instance) -> bool:
        raise NotImplementedError('Please implement the diff function.')
