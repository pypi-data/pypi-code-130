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
from atexit import register
import uuid
from .azt_logger import _logger


def make_new_str_id():
    return str(uuid.uuid4())


class DefaultSpi:
    def __init__(self, spi):
        self.__spi = spi

    def __getattr__(self, item):
        return getattr(self.__spi, item, self._defalut)

    def _defalut(self, *args, **kwargs):
        pass


def convert_meta(metacls, *bases):
    class TmpMeta(metacls):
        def __new__(cls, name, _, attrs):
            return metacls(name, bases, attrs)

    return type.__new__(TmpMeta, "TmpMeta", (), {})


class MetaApi(type):
    objs = []

    def __call__(cls, *args, **kwargs):
        obj = super(MetaApi, cls).__call__(*args, **kwargs)
        cls.objs.append(obj)
        return obj


@register
def __atexit():
    for obj in MetaApi.objs:
        if hasattr(obj, "_is_logined") and obj._is_logined():
            obj.Logout()
        elif hasattr(obj, "_is_closed") and not obj._is_closed():
            obj._stop()
        obj.Join()
    _logger.log("程序已退出，欢迎下次使用！")


class AztApiObject(convert_meta(MetaApi, object)):
    pass
