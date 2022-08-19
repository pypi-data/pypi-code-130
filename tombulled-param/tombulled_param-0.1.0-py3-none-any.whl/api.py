import functools
import inspect
from inspect import BoundArguments, Signature
from typing import Any, Callable, Dict, Tuple, TypeVar

from typing_extensions import ParamSpec

from .enums import ParameterType
from .models import Arguments, Parameter, ParameterSpecification
from .sentinels import Missing

PS = ParamSpec("PS")
RT = TypeVar("RT")


def _get_bound_arguments(
    func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    signature: Signature = inspect.signature(func)

    bound_arguments: BoundArguments = signature.bind(*args, **kwargs)

    bound_arguments.apply_defaults()

    bound_args: Dict[str, Any] = dict(zip(signature.parameters, bound_arguments.args))
    bound_kwargs: Dict[str, Any] = bound_arguments.kwargs

    return (bound_args, bound_kwargs)


def get_arguments(
    func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]
) -> Arguments:
    new_args: Dict[str, Any]
    new_kwargs: Dict[str, Any]

    new_args, new_kwargs = _get_bound_arguments(func, args, kwargs)

    source: Dict[str, Any]
    for source in (new_args, new_kwargs):
        parameter: str
        argument: Any
        for parameter, argument in source.items():
            if isinstance(argument, ParameterSpecification):
                if not argument.has_default():
                    raise ValueError(f"{func.__name__}() missing argument: {parameter}")
                else:
                    source[parameter] = argument.get_default()
            else:
                source[parameter] = argument

    return Arguments(
        args=tuple(new_args.values()),
        kwargs=new_kwargs,
        arguments={**new_args, **new_kwargs},
    )


def _parse(value: Any, /) -> Any:
    if value is inspect._empty:
        return Missing

    return value


def get_params(func: Callable[PS, RT], /) -> Dict[str, Parameter]:
    params: Dict[str, Parameter] = {}

    parameter: inspect.Parameter
    for parameter in inspect.signature(func).parameters.values():
        spec: ParameterSpecification = (
            parameter.default
            if isinstance(parameter.default, ParameterSpecification)
            else ParameterSpecification(default=_parse(parameter.default))
        )

        param: Parameter = Parameter(
            name=parameter.name,
            annotation=_parse(parameter.annotation),
            type=getattr(ParameterType, parameter.kind.name),
            spec=spec,
        )

        params[parameter.name] = param

    return params


def params(func: Callable[PS, RT], /) -> Callable[PS, RT]:
    @functools.wraps(func)
    def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
        arguments: Arguments = get_arguments(func, args, kwargs)

        return func(*arguments.args, **arguments.kwargs)

    return wrapper
