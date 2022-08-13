from typing import Callable, Any


class PartialQuery:
    """
    Instances of this class can be provided as path keys only in Registrar.register_path().
    When registered_get()/registered_set() is called with the relevant path label, the function provided below
    will be called and passed one value from the custom query args list;
    a valid path key or KeyQuery should be returned
    """

    __hash__ = None
    """
    As this class is used indirectly to determine the method of access for the state object,
    it will never be used as a direct index. Thus, it should never be set as a key.
    """

    def __init__(self, path_key_getter: Callable[[Any], Any]):
        self.__function = path_key_getter

    def __call__(self, query_args: Any) -> Any:
        return self.__function(query_args)
