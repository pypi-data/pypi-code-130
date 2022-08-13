from typing import Any, Callable, TypeVar

T = TypeVar("T")


class UnderscoreShortFun:
    # Binary+ operations
    # TODO: might as well do unary: negation, positive, etc...

    def __add__(self, rt: float) -> Callable[[float], float]:
        return lambda x: x + rt

    def __and__(self, rt: bool) -> Callable[[bool], bool]:
        return lambda x: x & rt

    def __delattr__(self, rt: str):
        raise Exception("Cannot use delattr with _.")

    def __divmod__(self, rt):
        return lambda x: divmod(x, rt)

    def __eq__(self, rt) -> Callable[[Any], bool]:
        return lambda x: x == rt

    def __floordiv__(self, rt):
        return lambda x: x // rt

    def __format__(self, *rt_args, **rt_kwargs):
        raise Exception("Cannot use format with _.")

    def __ge__(self, rt: Any) -> Callable[[Any], bool]:
        return lambda x: x >= rt

    def __getattr__(self, attr_name: str):
        return lambda cls: getattr(cls, attr_name)

    def __gt__(self, rt) -> Callable[[Any], bool]:
        return lambda x: x > rt

    def __le__(self, rt) -> Callable[[Any], bool]:
        return lambda x: x <= rt

    def __lshift__(self, rt):
        return lambda x: x << rt

    def __lt__(self, rt) -> Callable[[Any], bool]:
        return lambda x: x < rt

    def __mod__(self, rt) -> Callable[[float], float]:
        return lambda x: x % rt

    def __mul__(self, rt) -> Callable[[float], float]:
        return lambda x: x * rt

    def __ne__(self, rt) -> Callable[[Any], bool]:
        return lambda x: x != rt

    def __or__(self, rt):
        return lambda x: x | rt

    def __pow__(self, rt) -> Callable[[float], float]:
        return lambda x: x**rt

    def __radd__(self, lft) -> Callable[[float], float]:
        return lambda x: lft + x

    def __rand__(self, lft: bool):
        return lambda x: lft & x

    def __rdivmod__(self, lft):
        return lambda x: divmod(lft, x)

    def __rfloordiv__(self, lft) -> Callable[[float], int]:
        return lambda x: lft // x

    def __rlshift__(self, lft):
        return lambda x: lft << x

    def __rmod__(self, lft):
        return lambda x: lft % x

    def __rmul__(self, lft):
        return lambda x: lft * x

    def __ror__(self, lft):
        return lambda x: lft | x

    def __round__(self, ndigits: int) -> Callable[[float], int]:
        return lambda x: round(x, ndigits)

    def __rpow__(self, lft):
        return lambda x: lft**x

    def __rrshift__(self, lft):
        return lambda x: lft >> x

    def __rshift__(self, rt):
        return lambda x: x >> rt

    def __rsub__(self, lft):
        return lambda x: lft - x

    def __rtruediv__(self, lft) -> Callable[[float], float]:
        return lambda x: lft / x

    def __rxor__(self, rt):
        return lambda x: rt ^ x

    def __setattr__(self, attr_name, attr_value):
        raise Exception("Cannot use setattr with _.")

    def __sub__(self, rt):
        return lambda x: x - rt

    def __truediv__(self, rt):
        return lambda x: x / rt

    def __xor__(self, rt):
        return lambda x: x ^ rt


_ = UnderscoreShortFun()
