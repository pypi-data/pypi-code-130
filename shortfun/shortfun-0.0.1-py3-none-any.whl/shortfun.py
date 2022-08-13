# pylint: disable=missing-function-docstring
from .underscore import _


def add(val, /, *, left=True):
    if left:
        return lambda x: x + val

    return lambda x: val + x


def and_(val, /, *, left=True):
    if left:
        return lambda x: x and val

    return lambda x: val and x


def delattr(*, obj=None, name=None):  # pylint: disable=redefined-builtin
    if obj is not None:

        if name is not None:
            raise Exception()

        return obj.__delattr__

    if name is None:
        raise Exception()

    return lambda _obj: _obj.__delattr__(name)


def divmod(*, x=None, y=None):  # pylint: disable=redefined-builtin
    if x is not None:

        if y is not None:
            raise Exception()

        return x.__divmod__

    if y is None:
        raise Exception()

    return lambda _x: _x.__divmod__(y)


def div(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x / _y

    if y is None:
        raise Exception()

    return lambda _x: _x / y


def eq(val, /):
    return _ == val


def floordiv(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x // _y

    if y is None:
        raise Exception()

    return lambda _x: _x // y


def format(format_str=None, /, **format_kwargs):  # pylint: disable=redefined-builtin
    if format_str is not None:

        if len(format_kwargs) > 0:
            raise Exception()

        return format_str.__format__

    if len(format_kwargs) == 0:
        raise Exception()

    return lambda _format_str: _format_str.__format__(**format_kwargs)


def ge(rt, /):
    return lambda x: x >= rt


def getattr(*, obj=None, name=None, default=None):  # pylint: disable=redefined-builtin
    if obj is not None:

        if name is not None:
            raise Exception()

        return lambda _name: obj.__getattr__(_name, default)

    if name is None:
        raise Exception()

    return lambda _obj: _obj.__getattr__(name, default)


def gt(rt, /):
    return rt.__gt__


def le(rt, /):
    return lambda x: x <= rt


def lshift(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x << _y

    if y is None:
        raise Exception()

    return lambda _x: _x << y


def mod(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x % _y

    if y is None:
        raise Exception()

    return lambda _x: _x % y


def mult(rt, /):
    return lambda x: x * rt


def ne(rt, /):
    return lambda x: x != rt


def or_(val, /, *, left=True):
    if left:
        return lambda x: x or val

    return lambda x: val or x


def pow(*, x=None, y=None):  # pylint: disable=redefined-builtin
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x**_y

    if y is None:
        raise Exception()

    return lambda _x: _x**y


def round(val=None, /, *, ndigits=None):  # pylint: disable=redefined-builtin
    if val is not None:

        if ndigits is not None:
            raise Exception()

        return val.__round__

    if ndigits is None:
        raise Exception()

    return lambda _val: _val.__round__(ndigits)


def rshift(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x >> _y

    if y is None:
        raise Exception()

    return lambda _x: _x >> y


def sub(*, x=None, y=None):
    if x is not None:

        if y is not None:
            raise Exception()

        return lambda _y: x - _y

    if y is None:
        raise Exception()

    return lambda _x: _x - y


def xor(val, /, *, left=True):
    if left:
        return lambda x: x ^ val

    return lambda x: val ^ x


def setattr(*, obj=None, name=None, value=None):  # pylint: disable=redefined-builtin
    if obj is not None:

        if name is not None:

            if value is not None:
                raise Exception()

            return lambda _value: obj.__getattr__(name, _value)

        if value is not None:
            return lambda _name: obj.__getattr__(_name, value)

        return obj.__getattr__

    if name is not None:

        if value is not None:
            return lambda _obj: _obj.__getattr__(name, value)

        return lambda _obj, _value: _obj.__getattr__(name, _value)

    if value is not None:
        return lambda _obj, _name: _obj.__getattr__(_name, value)

    raise Exception()
