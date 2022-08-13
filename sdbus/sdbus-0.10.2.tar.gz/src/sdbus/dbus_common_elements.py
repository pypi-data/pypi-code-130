# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020-2022 igo95862

# This file is part of python-sdbus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from __future__ import annotations

from inspect import getfullargspec
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from .dbus_common_funcs import (
    _is_property_flags_correct,
    _method_name_converter,
)
from .sd_bus_internals import is_interface_name_valid, is_member_name_valid


class DbusSomethingCommon:
    def __init__(self) -> None:
        self.interface_name: Optional[str] = None
        self.serving_enabled: bool = True


class DbusSomethingAsync(DbusSomethingCommon):
    ...


class DbusSomethingSync(DbusSomethingCommon):
    ...


class DbusInterfaceMetaCommon(type):
    def __new__(cls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any],
                interface_name: Optional[str] = None,
                serving_enabled: bool = True,
                ) -> DbusInterfaceMetaCommon:
        if interface_name is not None:
            try:
                assert is_interface_name_valid(interface_name), (
                    f"Invalid interface name: \"{interface_name}\"; "
                    'Interface names must be composed of 2 or more elements '
                    'separated by a dot \'.\' character. All elements must '
                    'contain at least one character, constist of ASCII '
                    'characters, first character must not be digit and '
                    'length must not exceed 255 characters.'
                )
            except NotImplementedError:
                ...

        new_cls = super().__new__(cls, name, bases, namespace)

        return new_cls


MEMBER_NAME_REQUIREMENTS = (
    'Member name must only contain ASCII characters, '
    'cannot start with digit, '
    'must not contain dot \'.\' and be between 1 '
    'and 255 characters in length.'
)


class DbusMethodCommon(DbusSomethingCommon):

    def __init__(
            self,
            original_method: FunctionType,
            method_name: Optional[str],
            input_signature: str,
            input_args_names: Sequence[str],
            result_signature: str,
            result_args_names: Sequence[str],
            flags: int):

        assert not isinstance(input_args_names, str), (
            "Passed a string as input args"
            " names. Did you forget to put"
            " it in to a tuple ('string', ) ?")

        assert not any(' ' in x for x in input_args_names), (
            "Can't have spaces in argument input names"
            f"Args: {input_args_names}")

        assert not any(' ' in x for x in result_args_names), (
            "Can't have spaces in argument result names."
            f"Args: {result_args_names}")

        if method_name is None:
            method_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(method_name), (
                f"Invalid method name: \"{method_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        super().__init__()
        self.original_method = original_method
        self.args_spec = getfullargspec(original_method)
        self.args_names = self.args_spec.args[1:]  # 1: because of self
        self.num_of_args = len(self.args_names)
        self.args_defaults = (
            self.args_spec.defaults
            if self.args_spec.defaults is not None
            else ())
        self.default_args_start_at = self.num_of_args - len(self.args_defaults)

        self.method_name = method_name
        self.input_signature = input_signature
        self.input_args_names: Sequence[str] = (
            self.args_names
            if result_args_names and not input_args_names
            else input_args_names)

        self.result_signature = result_signature
        self.result_args_names = result_args_names
        self.flags = flags

        self.__doc__ = original_method.__doc__

    def _rebuild_args(
            self,
            function: FunctionType,
            *args: Any,
            **kwargs: Dict[str, Any]) -> List[Any]:
        # 3 types of arguments
        # *args - should be passed directly
        # **kwargs - should be put in a proper order
        # defaults - should be retrieved and put in proper order

        # Strategy:
        # Iterate over arg names
        # Use:
        # 1. Arg
        # 2. Kwarg
        # 3. Default

        # a, b, c, d, e
        #       ^ defaults start here
        # 5 - 3 = [2]
        # ^ total args
        #     ^ number of default args
        # First arg that supports default is
        # (total args - number of default args)
        passed_args_iter = iter(args)
        default_args_iter = iter(self.args_defaults)

        new_args_list: List[Any] = []

        for i, a_name in enumerate(self.args_spec.args[1:]):
            try:
                next_arg = next(passed_args_iter)
            except StopIteration:
                next_arg = None

            if i >= self.default_args_start_at:
                next_default_arg = next(default_args_iter)
            else:
                next_default_arg = None

            next_kwarg = kwargs.get(a_name)

            if next_arg is not None:
                new_args_list.append(next_arg)
            elif next_kwarg is not None:
                new_args_list.append(next_kwarg)
            elif next_default_arg is not None:
                new_args_list.append(next_default_arg)
            else:
                raise TypeError('Could not flatten the args')

        return new_args_list


class DbusPropertyCommon(DbusSomethingCommon):
    def __init__(self,
                 property_name: Optional[str],
                 property_signature: str,
                 flags: int,
                 original_method: FunctionType):
        if property_name is None:
            property_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(property_name), (
                f"Invalid property name: \"{property_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        assert _is_property_flags_correct(flags), (
            'Incorrect number of Property flags. '
            'Only one of DbusPropertyConstFlag, DbusPropertyEmitsChangeFlag, '
            'DbusPropertyEmitsInvalidationFlag or DbusPropertyExplicitFlag '
            'is allowed.'
        )

        super().__init__()
        self.property_name: str = property_name
        self.property_signature = property_signature
        self.flags = flags


class DbusSingalCommon(DbusSomethingCommon):
    def __init__(self,
                 signal_name: Optional[str],
                 signal_signature: str,
                 args_names: Sequence[str],
                 flags: int,
                 original_method: FunctionType):
        if signal_name is None:
            signal_name = ''.join(
                _method_name_converter(original_method.__name__))

        try:
            assert is_member_name_valid(signal_name), (
                f"Invalid signal name: \"{signal_name}\"; "
                f"{MEMBER_NAME_REQUIREMENTS}"
            )
        except NotImplementedError:
            ...

        super().__init__()
        self.signal_name = signal_name
        self.signal_signature = signal_signature
        self.args_names = args_names
        self.flags = flags

        self.__doc__ = original_method.__doc__
        self.__annotations__ = original_method.__annotations__


class DbusBindedAsync:
    ...


class DbusBindedSync:
    ...


T = TypeVar('T')


class DbusOverload:
    def __init__(self, original: T):
        self.original = original
        self.setter_overload: Optional[Callable[[Any, T], None]] = None

    def setter(self, new_setter: Optional[Callable[[Any, T], None]]) -> None:
        self.setter_overload = new_setter
