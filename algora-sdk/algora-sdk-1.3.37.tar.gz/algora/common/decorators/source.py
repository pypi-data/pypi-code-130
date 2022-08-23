import functools
from typing import Optional, Callable, Tuple, Dict, Any

from typing_extensions import Literal

from algora.common.data_source import Source, AsyncSource
from algora.common.model import DataRequest


def source(get_data_method: Callable[[DataRequest], Any] = None,
           *,
           name: Optional[str] = None,
           source_type: Literal['sync', 'async'] = 'sync'):
    """
    Data source function, containing name and asynchronous get_data functionality. Alternative to creating a Source
    class.

    Args:
        get_data_method (Callable[[DataRequest], Any]): Data request-response function to wrap
        name (Optional[str]): Data source name
        source_type (Literal['sync', 'async']): Type of source, either synchronous or asynchronous

    Returns:
        An synchronous or asynchronous source class containing the decorated method
    """

    @functools.wraps(get_data_method)
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args: Tuple, **kwargs: Dict[str, Any]):
            """
            Wrapper for the decorated function.

            Args:
                *args: args for the function
                **kwargs: keyword args for the function

            Returns:

            """
            source_cls = AsyncSource if source_type == 'async' else Source
            cls = type(name, (source_cls,), {})
            setattr(cls, "get_data", f)
            setattr(cls, "name", lambda: name)
            return cls

        return wrap

    if get_data_method is None:
        return decorator
    return decorator(get_data_method)
