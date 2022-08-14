import copy
from itertools import chain
from typing import Union, Sequence
from collections.abc import ItemsView, KeysView, ValuesView

from sortedcontainers import SortedList, SortedDict


KeyType = Union[str, Sequence[str]]


class _NotGiven(object):

    def __repr__(self):
        return "<not-given>"


class ConfigItemsView(ItemsView):

    def __init__(self, mapping):
        super(ConfigItemsView, self).__init__(mapping)


class ConfigValuesView(ValuesView):

    def __init__(self, mapping):
        super(ConfigValuesView, self).__init__(mapping)


class ConfigKeysView(KeysView):

    def __init__(self, mapping):
        super(ConfigKeysView, self).__init__(mapping)


class ConfigDict(dict):

    """ConfigDict is a mapping for config key-value pairs.

    ConfigDict keys are maintained in increment sorted order, and split by `'.'`.

    ConfigDict keys must be str. A key will be split as a sequence by `'.'`, and store in dict recursively.
    For example, `a.b.c=1` will be stored as `{'a': {'b': {'c': 1}}}`.
    """

    __not_given = _NotGiven()

    def __init__(self, d: dict = None):
        """Initialize config dict instance.

        Optional argument `d` defines init key-value pairs.

        >>> d = {'a': {'b.c': 1}, 'd': 2}
        >>> ConfigDict(d)
        ConfigDict({'a.b.c': 1, 'd': 2})

        :param d: the init key-value pairs.
        """
        super(ConfigDict, self).__init__()
        self.__dict = SortedDict()
        if d is None:
            d = {}
        # Init config dict instance recursively
        for k, v in d.items():
            if isinstance(v, dict):
                self.__put(k, ConfigDict(v), overwrite=True)
            else:
                self.__put(k, v, overwrite=True)

    def clear(self) -> None:
        """
        Remove all items from config dict

        Runtime complexity: `O(n)`
        """
        self.__dict.clear()

    def get(self, key, default=__not_given):
        """
        get the value of key

        :param key:
        :param default:
        :return:
        """
        return self.__get(key, default=default)

    def setdefault(self, key, default=None):
        """Set (key, default) in config dict if key not exists.

        :param key:
        :param default:
        :return:
        """
        self.__put(key, default, overwrite=False)

    def update(self, config_dict, **kwargs) -> None:
        if isinstance(config_dict, ConfigDict):
            self.__dict.update(config_dict.__dict)
        else:
            self.__dict.update(ConfigDict(config_dict).__dict)

    def __iter__(self):
        return self.__generator(has_value=False)

    def __repr__(self):
        return f"ConfigDict({dict(self)})"

    def __len__(self):
        return self.__len_impl()

    def __contains__(self, __key):
        return self.__contains(__key)

    def __getitem__(self, __key):
        return self.__get(__key)

    def __setitem__(self, __key, value):
        """
        Store item in config dict with `key` and corresponding `value`.

        :param __key:
        :param value:
        :return:
        """
        self.__put(__key, value, overwrite=True)

    def __delitem__(self, key):
        """
        Remove item from config dict identified by `key`.

        ``cd.__delitem__(key)`` <==> ``del cd[key]``

        >>> cd = ConfigDict({'a': {'b': 1, 'c': 2}})
        >>> del cd['a.b']
        >>> cd

        >>> del cd['d']

        :param key: `key` for item lookup
        :raises KeyError: if key not found
        """
        self.__del(key)

    @property
    def __dict__(self):
        return self.__items()

    def __eq__(self, other):
        return self.__dict.__eq__(other.__dict)

    def __ne__(self, other):
        return self.__dict.__ne__(other.__dict)

    def copy(self):
        ret = ConfigDict()
        for k, v in self.__dict.items():
            if isinstance(v, ConfigDict):
                ret.__dict[k] = v.copy()
            else:
                ret.__dict[k] = copy.deepcopy(v)
        return ret

    def keys(self):
        return ConfigKeysView(self.__items())

    def values(self):
        return ConfigValuesView(self.__items())

    def items(self):
        return ConfigItemsView(self.__items())

    def __items(self):
        ret = {}

        def _cat_items(cd, items, prefix):
            for k, v in cd.__dict.items():
                real_k = f"{prefix}.{k}" if prefix != "" else k
                if isinstance(v, ConfigDict):
                    _cat_items(v, items, real_k)
                else:
                    items[real_k] = v

        _cat_items(self, ret, "")
        return ret

    def __contains(self, key):
        key_seq = self.__split_key(key)
        return self.__contains_impl(key_seq)

    def __get(self, key, default=__not_given):
        key_seq = self.__split_key(key)
        try:
            return self.__get_impl(key_seq)
        except KeyError:
            if default is self.__not_given:
                raise KeyError(key)
            else:
                return default

    def __put(self, key, value, overwrite=True):
        key_seq = self.__split_key(key)
        try:
            self.__put_impl(key_seq, value, overwrite)
        except KeyError:
            raise KeyError(f"already exists a prefix key of {key}")

    def __del(self, key):
        key_seq = self.__split_key(key)
        try:
            self.__del_impl(key_seq)
        except KeyError:
            raise KeyError(key)

    def __generator(self, has_value=True, *, prefix=""):
        for k, v in self.__dict.items():
            real_k = f"{prefix}.{k}" if prefix else k
            if isinstance(v, ConfigDict):
                for it in v.__generator(has_value, prefix=real_k):
                    yield it
            else:
                if has_value:
                    yield real_k, v
                else:
                    yield real_k

    def __len_impl(self):
        len_ = 0
        for k, v in self.__dict.items():
            if isinstance(v, ConfigDict):
                len_ += v.__len_impl()
            else:
                len_ += 1
        return len_

    def __contains_impl(self, key_seq):
        value = self.__dict.get(key_seq[0], self.__not_given)
        if value is self.__not_given:
            return False
        if len(key_seq) == 1:
            return True
        if not isinstance(value, ConfigDict):
            return False
        return value.__contains_impl(key_seq[1:])

    def __get_impl(self, key_seq):
        v = self.__dict.__getitem__(key_seq[0])
        if len(key_seq) == 1:
            return v
        if not isinstance(v, ConfigDict):
            raise KeyError()
        return v.__get_impl(key_seq[1:])

    def __put_impl(self, key_seq, value, overwrite):
        if len(key_seq) == 1:
            if overwrite or key_seq[0] not in self.__dict:
                self.__dict.__setitem__(key_seq[0], value)
                return value
            return self.__dict.get(key_seq[0])
        if key_seq[0] in self.__dict:
            value_dict = self.__dict.__getitem__(key_seq[0])
        else:
            value_dict = ConfigDict()
            self.__dict.__setitem__(key_seq[0], value_dict)
        if not isinstance(value_dict, ConfigDict):
            raise KeyError()
        return value_dict.__put_impl(key_seq[1:], value, overwrite)

    def __del_impl(self, key_seq):
        if key_seq[0] not in self.__dict:
            raise KeyError()
        if len(key_seq) == 1:
            self.__dict.__delitem__(key_seq[0])
            return
        value = self.__dict.__getitem__(key_seq[0])
        if isinstance(value, ConfigDict):
            value.__del_impl(key_seq[1:])
            if len(value) == 0:
                self.__dict.__delitem__(key_seq[0])
        else:
            raise KeyError()

    def __update_imp(self, values):
        pass

    @classmethod
    def __split_key(cls, key: str):
        if key is None or not isinstance(key, str) or key == "":
            raise KeyError(f"key must be str and not empty")
        return key.split(".")


if __name__ == '__main__':
    cd = ConfigDict({})
    q = cd["qwe"]
    cd["asd"] = "sad"
