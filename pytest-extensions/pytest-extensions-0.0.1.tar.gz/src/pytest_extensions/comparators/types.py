from typing import Iterable, Sequence, Callable

from . import BaseComparator


def starts_with_vowel(name):
    # TODO: detect vowel sound
    if name[0] in ["a", "e", "i", "o", "u"]:
        return True
    return False


class TypeComparator(BaseComparator):
    def __init__(self, types, display=None):
        super(TypeComparator, self).__init__(display=display)

        self.types = types

        if display is None:
            if isinstance(types, Iterable):
                raise Exception("display is required when multiple types are passed")
            else:
                prefix = 'an' if starts_with_vowel(types.__name__) else "a"
                self.display = display or f"{prefix}_{types.__name__}"

    def __eq__(self, other):
        return isinstance(other, self.types)


class Anything(BaseComparator):
    def __eq__(self, other):
        return True

    def __repr__(self):
        return "anything"


# source: https://docs.python.org/3/library/stdtypes.html

# Numeric Types
a_numeric = TypeComparator((int, float, complex), display="a_numeric")
an_int = TypeComparator(int)
a_float = TypeComparator(float)
a_complex = TypeComparator(complex)

# Iterator Types
# https://docs.python.org/3/glossary.html#term-iterable
an_iterable = TypeComparator(Iterable, display="an_iterable")

# Sequence Types
a_sequence = TypeComparator(Sequence, display="a_sequence")
a_list = TypeComparator(list)
a_tuple = TypeComparator(tuple)
a_range = TypeComparator(range)

a_str = TypeComparator(str)

a_bytes = TypeComparator(bytes)
a_bytearray = TypeComparator(bytearray)

# Set Types
a_set = TypeComparator(set)
a_frozenset = TypeComparator(frozenset)

# Mapping Types
a_dict = TypeComparator(dict)

# Other Types
a_callable = TypeComparator(Callable, display="a_callable")
a_type = TypeComparator(type)
an_ellipsis = TypeComparator(type(Ellipsis))  # You should compare directly to Ellipsis
an_object = TypeComparator(object)

# TODO:
#a_module = TypeComparator([module])
#a_function = TypeComparator([function])
#a_method = TypeComparator([method])

# Boolean Values
a_bool = TypeComparator(bool)

# Misc
anything = Anything()  # should be identical to an_object
