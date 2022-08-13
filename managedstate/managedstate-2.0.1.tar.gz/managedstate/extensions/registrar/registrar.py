from objectextensions import Extension

from typing import Sequence, List, Any, Dict

from ...state import State
from ...methods import Methods as StateMethods
from .constants import Keys
from .partialquery import PartialQuery


class Registrar(Extension):
    """
    Allows specific get and set operations to be registered under a shorthand label for ease of use later
    """

    @staticmethod
    def can_extend(target_cls):
        return issubclass(target_cls, State)

    @staticmethod
    def extend(target_cls):
        Extension._wrap(target_cls, "__init__", Registrar.__wrap_init)

        Extension._set_property(target_cls, "registered_paths", Registrar.__registered_paths)
        Extension._set(target_cls, "register_path", Registrar.__register_path)
        Extension._set(target_cls, "registered_get", Registrar.__registered_get)
        Extension._set(target_cls, "registered_set", Registrar.__registered_set)

    def __wrap_init(self, *args, **kwargs):
        yield
        Extension._set(self, "_registered_paths", {})

    def __registered_paths(self) -> Dict[str, Dict[str, Sequence[Any]]]:
        """
        Returns a copy of the current path registry
        """

        return StateMethods.try_copy(self._registered_paths)

    def __register_path(self, registered_path_label: str, path_keys: Sequence[Any], defaults: Sequence[Any] = ()) -> None:
        """
        Saves the provided path keys and defaults under the provided label, so that a custom get or set can be
        carried out at later times simply by providing the label again in a call to registered_get() or registered_set()
        """

        registered_path = {Keys.PATH_KEYS: path_keys, Keys.DEFAULTS: defaults}
        self._registered_paths[registered_path_label] = registered_path

    def __registered_get(self, registered_path_label: str, custom_query_args: Sequence[Any] = ()) -> Any:
        """
        Calls get(), passing in the path keys and defaults previously provided in register().
        If any of these path keys are instances of PartialQuery, each will be called and passed one value from
        the custom query args list and is expected to return a valid path key or KeyQuery
        """

        registered_path = self._registered_paths[registered_path_label]
        path_keys = Registrar.__process_registered_path_keys(
            registered_path[Keys.PATH_KEYS], custom_query_args
        )
        defaults = registered_path[Keys.DEFAULTS]

        self._extension_data[Keys.REGISTERED_PATH_LABEL] = registered_path_label
        self._extension_data[Keys.CUSTOM_QUERY_ARGS] = custom_query_args

        result = self.get(path_keys, defaults)

        del self._extension_data[Keys.REGISTERED_PATH_LABEL]
        del self._extension_data[Keys.CUSTOM_QUERY_ARGS]

        return result

    def __registered_set(self, value: Any, registered_path_label: str, custom_query_args: Sequence[Any] = ()) -> None:
        """
        Calls set(), passing in the path keys and defaults previously provided in register().
        If any of these path keys are instances of PartialQuery, each will be called and passed one value from
        the custom query args list and is expected to return a valid path key or KeyQuery
        """

        registered_path = self._registered_paths[registered_path_label]
        path_keys = Registrar.__process_registered_path_keys(
            registered_path[Keys.PATH_KEYS], custom_query_args
        )
        defaults = registered_path[Keys.DEFAULTS]

        self._extension_data[Keys.REGISTERED_PATH_LABEL] = registered_path_label
        self._extension_data[Keys.CUSTOM_QUERY_ARGS] = custom_query_args

        result = self.set(value, path_keys, defaults)

        del self._extension_data[Keys.REGISTERED_PATH_LABEL]
        del self._extension_data[Keys.CUSTOM_QUERY_ARGS]

    @staticmethod
    def __process_registered_path_keys(path_keys: Sequence[Any], custom_query_args: Sequence[Any]) -> List[Any]:
        """
        Used internally to coalesce instances of PartialQuery before path keys are passed to set()/get()
        """

        working_args = list(custom_query_args)
        result = []

        for path_node in path_keys:
            if type(path_node) is PartialQuery:
                result.append(path_node(working_args.pop(0)))
            else:
                result.append(path_node)

        return result
