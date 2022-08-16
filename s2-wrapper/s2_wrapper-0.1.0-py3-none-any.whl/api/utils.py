from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple, Union

from s2_wrapper.api import exceptions

if TYPE_CHECKING:
    from httpx import Client

    from s2_wrapper.api.base import BaseEndpoints


def _build_endpoint(api_path: str, endpoint: str) -> str:
    return f"{api_path}{endpoint}"


def _get_arguments(
    func: Callable, func_args: Tuple[Any, ...], func_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Gets a dictionary with the name of the argument and the value of the `func` function.

    Args:
        func: the function from which the arguments have to be obtained
        func_args: the `*args` with which `func` was called.
        func_kwargs: the `**kwargs` with which `func` was called.

    Returns:
        The name of the argument and its value.
    """
    args_names = func.__code__.co_varnames
    arguments = {}
    for position, arg_name in enumerate(args_names):
        if arg_name in func_kwargs:
            arguments[arg_name] = func_kwargs[arg_name]
        else:
            try:
                arguments[arg_name] = func_args[position]
            except IndexError:
                arguments[arg_name] = None
    return arguments


def _make_request(
    client: "Client", method: str, endpoint: str, params: Dict[str, Any] = {}
) -> Dict[str, Any]:
    """Makes ands handles a request to the Semantic Scholar API.

    Args:
        client: the `httpx` client to make the request.
        method: the HTTP method.
        url: the endpoint slug.
        params: the request query parameters

    Returns:
        If successful, a dict with the content of the response.

    Raises:
        s2_wrapper.api.exceptions.SemanticScholarBadQuery: if the API returns a 400 status
            code caused because bad query parameters.
        s2_wrapper.api.exceptions.SemanticScholarForbidden: if the API returns a 403 status
            code caused because the access to the resource is forbidden for the given credentials.
        s2_wrapper.api.exceptions.SemanticScholarNotFound: if the API returns a 404 status
            code caused because no entity could be found for the given query parameters.
        s2_wrapper.api.exceptions.SemanticScholarException: if the API returns a status code
            other than 200, 400, 403 or 404.
    """
    r = client.request(method=method, url=endpoint, params=params)

    content = r.json()

    if r.status_code == 200:
        return content
    elif r.status_code == 400:
        raise exceptions.SemanticScholarBadQuery(
            status_code=r.status_code, error=content["error"]
        )
    elif r.status_code == 403:
        raise exceptions.SemanticScholarForbidden(
            status_code=r.status_code, error=content["message"]
        )
    elif r.status_code == 429:
        raise exceptions.SemanticScholarTooManyRequests(
            status_code=r.status_code, error=content["message"]
        )
    elif r.status_code == 404:
        raise exceptions.SemanticScholarNotFound(
            status_code=r.status_code, error=content["error"]
        )
    else:
        print(content)
        raise exceptions.SemanticScholarException(status_code=r.status_code)


def endpoint(
    method: str,
    endpoint: str,
    query_params_names: Dict[str, Union[Callable, None]] = {},
) -> Callable:
    """A decorator to call an endpoint of the API.

    Args:
        method: the endpoint method.
        endpoint: the endpoint slug.
        query_params_names: from the method, a dict containing the name of the arguments
            that has to be send as query parameter, and optionally a function that transforms
            the value of the argument before sending it.

    Returns:
        The decorated function.
    """

    def decorator(class_method: Callable) -> Callable:
        @wraps(class_method)
        def wrapper(*args, **kwargs) -> Callable:
            # Get the "self" attribute from the method
            endpoints_class: "BaseEndpoints" = args[0]

            # Get a dictionary with all the arguments with which the method was called
            arguments = _get_arguments(class_method, args, kwargs)

            # Build the full API endpoint
            endpoint_ = _build_endpoint(endpoints_class.API_PATH, endpoint).format(
                **arguments
            )

            # Get query parameters
            params = {}
            for param, transformation in query_params_names.items():
                param_value = arguments.get(param)
                if param_value:
                    if transformation:
                        params[param] = transformation(arguments[param])
                    else:
                        params[param] = arguments[param]

            # Make the request
            client = endpoints_class._client
            content = _make_request(
                client=client, method=method, endpoint=endpoint_, params=params
            )

            return class_method(*args, **kwargs, _json=content)

        return wrapper

    return decorator
