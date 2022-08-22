#  =============================================================================
#  GNU Lesser General Public License (LGPL)
#
#  Copyright (c) 2022 Qujamlee from www.aztquant.com
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  =============================================================================
from .utils import convert_meta


class QujamFuncSwitchMeta(type):
    _switchs = dict()

    def __call__(cls, *args, **kwargs):
        switch_name = args[0]
        obj = cls._switchs.get(switch_name, None)
        if not obj:
            obj = super(QujamFuncSwitchMeta, cls).__call__(*args, **kwargs)
            cls._switchs[switch_name] = obj
        return obj


class QujamFuncSwitch(convert_meta(QujamFuncSwitchMeta, object)):
    def __init__(self, name):
        self._switch_map = dict()
        self._name = name
        self._new_case = None
        self._cls = None

    def set_cls(self, cls):
        self._cls = cls

    @classmethod
    def set_func_switch(cls, name, case):
        fs = cls(name)
        fs._new_case = case
        return fs

    def __call__(self, fn):
        self._switch_map[self._new_case] = fn.__name__
        return fn

    def __getitem__(self, item):
        return getattr(self._cls, self._switch_map[item])
