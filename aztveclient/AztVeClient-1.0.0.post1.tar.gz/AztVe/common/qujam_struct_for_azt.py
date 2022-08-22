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
import dataclasses
import datetime
from typing import List, Dict, Any, Optional, Tuple

from AztVe.common import azt_errors, azt_logger


def _make_round_f(rn=None):
    if rn is None:
        def tmpf1(v):
            return v

        return tmpf1

    def tmpf2(v):
        return round(v, rn) if (type(v) == float) else v

    return tmpf2


class AztStructs:
    def __init__(self, proto_cls, **kwargs):
        # ##########################################################################
        # 1 参数设置 ================================================================
        # ##########################################################################
        self.p_proto_cls = proto_cls

        self.p_price_dec_num: int = kwargs.get("price_dec_num", None)
        self.p_amount_dec_num: int = kwargs.get("amount_dec_num", None)

        self.p_price_dec: str = kwargs.get("price_dec", None)
        self.p_amount_dec: str = kwargs.get("amount_dec", None)
        self.p_adj_price: List[str] = kwargs.get("adj_price", None)
        self.p_adj_amount: List[str] = kwargs.get("adj_amount", None)

        self.p_adj_repeat: List[str] = kwargs.get("adj_repeat", None)
        self.p_adj_repeat_price: List[str] = kwargs.get("adj_repeat_price", None)
        self.p_adj_repeat_amount: List[str] = kwargs.get("adj_repeat_amount", None)

        self.p_adj_map: List[str] = kwargs.get("adj_map", None)
        self.p_adj_map_price: List[str] = kwargs.get("adj_map_price", None)
        self.p_adj_map_amount: List[str] = kwargs.get("adj_map_amount", None)

        self.p_adj_any: Dict[str, Any] = kwargs.get("adj_any", None)
        self.p_adj_time: Dict[str, Optional[str, List[str]]] = kwargs.get("adj_time", None)
        self.p_adj_name: Dict[str, str] = kwargs.get("adj_name", None)

        self.p_merge_name: Dict[str, Tuple[str, List[str]]] = kwargs.get("merge_name", None)

        # ##########################################################################
        # 2 待处理参数 ===============================================================
        # ##########################################################################
        self.m_adj_price_attrs = set() if self.p_adj_price is None else set(self.p_adj_price)
        self.m_adj_amount_attr = set() if self.p_adj_amount is None else set(self.p_adj_amount)

        self.m_adj_repeat_attrs = set() if self.p_adj_repeat is None else set(self.p_adj_repeat)
        self.m_adj_repeat_price_attrs = set() if self.p_adj_repeat_price is None else set(self.p_adj_repeat_price)
        self.m_adj_repeat_amount_attrs = set() if self.p_adj_repeat_amount is None else set(self.p_adj_repeat_amount)

        self.m_adj_map_attrs = set() if self.p_adj_map is None else set(self.p_adj_map)
        self.m_adj_map_price_attrs = set() if self.p_adj_map_price is None else set(self.p_adj_map_price)
        self.m_adj_map_amount_attrs = set() if self.p_adj_map_amount is None else set(self.p_adj_map_amount)

        self.m_adj_any_attrs = set() if self.p_adj_any is None else set(self.p_adj_any)

        self.m_adj_time_attrs = set() if self.p_adj_time is None else set(self.p_adj_time)

        self.m_merge_name = set() if self.p_merge_name is None else set(self.p_merge_name)

        # 3 获取需要处理的属性集合
        self.m_abnormal_attrs = self.m_adj_price_attrs | self.m_adj_amount_attr | self.m_adj_repeat_attrs \
                                | self.m_adj_repeat_price_attrs | self.m_adj_repeat_amount_attrs \
                                | self.m_adj_map_attrs | self.m_adj_map_price_attrs | self.m_adj_map_amount_attrs \
                                | self.m_adj_time_attrs | self.m_adj_any_attrs | self.m_merge_name
        # normal_attrs = None
        # 4 获取小数位数据
        self.m_price_decimal_place = 2 if self.p_price_dec_num is None else self.p_price_dec_num
        self.m_amount_decimal_place = 2 if self.p_amount_dec_num is None else self.p_amount_dec_num
        self.m_price_decimal_pow = 10 ** self.m_price_decimal_place
        self.m_amount_decimal_pow = 10 ** self.m_amount_decimal_place

    def _proto2py(self, cls, proto, rn=None):
        _round_f = _make_round_f(rn)
        params = dict()  # 用于生成py类的参数包
        cls_attrs = cls.__annotations__  # py类中的参数包元组
        all_attrs = cls_attrs.keys()  # py类中所有的参数名
        proto_attrs = dict(zip(all_attrs, all_attrs))  # py类与proto类参数映射

        # 更新更名参数
        if self.p_adj_name is not None:
            proto_attrs.update(self.p_adj_name)

        # 1 不需要处理的属性
        normal_attrs = set(all_attrs) - self.m_abnormal_attrs
        for normal_attr_name in normal_attrs:
            normal_atrr_cls = cls_attrs[normal_attr_name]
            if hasattr(normal_atrr_cls, "__proto2py__"):
                params[normal_attr_name] = normal_atrr_cls.__proto2py__(getattr(proto, proto_attrs[normal_attr_name]),
                                                                        rn)
            else:
                params[normal_attr_name] = _round_f(getattr(proto, normal_attr_name))

        # 处理需要合并的属性
        if self.p_merge_name is not None:
            for merge_name, merge_val in self.p_merge_name.items():
                sep, sep_names = merge_val
                tmpret = sep.join(
                    [getattr(proto, tmp_name) for tmp_name in sep_names if hasattr(proto, tmp_name)])
                if tmpret:
                    params[merge_name] = tmpret

        # 2 需要处理的属性
        # 2.1 int转float的价格
        if self.p_price_dec is not None:
            p_d = self.m_price_decimal_pow
            if hasattr(proto, self.p_price_dec):
                proto_pd = getattr(proto, self.p_price_dec)
                p_d = (10 ** proto_pd) if isinstance(proto_pd, int) else p_d

            for price_attr_name in self.m_adj_price_attrs:
                proto_attr_name = proto_attrs[price_attr_name]
                if hasattr(proto, proto_attr_name):
                    params[price_attr_name] = getattr(proto, proto_attr_name) / p_d

            for repeat_price_attr_name in self.m_adj_repeat_price_attrs:
                proto_attr_name = proto_attrs[repeat_price_attr_name]
                if hasattr(proto, proto_attr_name):
                    params[repeat_price_attr_name] = [inner_price / p_d for inner_price in
                                                      getattr(proto, proto_attr_name)]

            for map_price_attr_name in self.m_adj_map_price_attrs:
                proto_attr_name = proto_attrs[map_price_attr_name]
                if hasattr(proto, proto_attr_name):
                    proto_map_val = getattr(proto, proto_attr_name)
                    params[map_price_attr_name] = {map_idx: proto_map_val[map_idx] / p_d for map_idx in proto_map_val}
        if self.p_amount_dec is not None:
            a_d = self.m_amount_decimal_pow
            if hasattr(proto, self.p_amount_dec):
                proto_ad = getattr(proto, self.p_amount_dec)
                a_d = (10 ** proto_ad) if isinstance(proto_ad, int) else a_d

            for amount_attr_name in self.m_adj_amount_attr:
                proto_attr_name = proto_attrs[amount_attr_name]
                if hasattr(proto, proto_attr_name):
                    params[amount_attr_name] = getattr(proto, proto_attr_name) / a_d

            for repeat_amount_attr_name in self.m_adj_repeat_amount_attrs:
                proto_attr_name = proto_attrs[repeat_amount_attr_name]
                if hasattr(proto, proto_attr_name):
                    params[repeat_amount_attr_name] = [inner_amount / a_d for inner_amount in
                                                       getattr(proto, proto_attr_name)]

            for map_amount_attr_name in self.m_adj_map_amount_attrs:
                proto_attr_name = proto_attrs[map_amount_attr_name]
                if hasattr(proto, proto_attr_name):
                    proto_map_val = getattr(proto, proto_attr_name)
                    params[map_amount_attr_name] = {map_idx: proto_map_val[map_idx] / a_d for map_idx in proto_map_val}

        for repeat_attr_name in self.m_adj_repeat_attrs:
            proto_attr_name = proto_attrs[repeat_attr_name]
            if hasattr(proto, proto_attr_name):
                repeat_attr_cls = cls_attrs[repeat_attr_name]
                if type(repeat_attr_cls) is list:
                    inner_type = repeat_attr_cls[0]
                    if hasattr(inner_type, "__proto2py__"):
                        params[repeat_attr_name] = [inner_type.__proto2py__(inner_proto, rn) for inner_proto in
                                                    getattr(proto, proto_attr_name)]
                    else:
                        params[repeat_attr_name] = list(map(_round_f, getattr(proto, proto_attr_name)))
                else:
                    raise azt_errors.ListTypeError

        for map_attr_name in self.m_adj_map_attrs:
            proto_attr_name = proto_attrs[map_attr_name]
            if hasattr(proto, proto_attr_name):
                proto_map_val = getattr(proto, proto_attr_name)
                map_attr_cls = cls_attrs[map_attr_name]
                if type(map_attr_cls) is dict:
                    val_atrr_cls = list(map_attr_cls.values())[0]
                    if hasattr(val_atrr_cls, "__proto2py__"):
                        params[map_attr_name] = {map_idx: val_atrr_cls.__proto2py__(proto_map_val[map_idx], rn)
                                                 for map_idx in proto_map_val}
                    else:
                        # params[map_attr_name] = dict(proto_map_val)
                        params[map_attr_name] = {_k: _round_f(_v) for _k, _v in proto_map_val.items()}
                else:
                    raise azt_errors.DictTypeError

        for any_attr_name in self.m_adj_any_attrs:
            proto_attr_name = proto_attrs[any_attr_name]
            if hasattr(proto, proto_attr_name):
                any_attr_type = self.p_adj_any[any_attr_name]
                if hasattr(any_attr_type, "__protocls__"):
                    any_attr_proto = any_attr_type.__protocls__()
                    getattr(proto, proto_attr_name).Unpack(any_attr_proto)
                    params[any_attr_name] = any_attr_type.__proto2py__(any_attr_proto, rn)

        for time_attr_name in self.m_adj_time_attrs:
            if hasattr(proto, time_attr_name):
                proto_time_attr_val: str = getattr(proto, time_attr_name)
                if proto_time_attr_val != "":
                    time_format = self.p_adj_time[time_attr_name]
                    if type(time_format) is str:
                        time_format = [time_format]
                    time_transformed = None
                    tf_error = ValueError
                    for t_format in time_format:
                        try:
                            time_transformed = datetime.datetime.strptime(proto_time_attr_val, t_format)
                            break
                        except ValueError as val_error:
                            tf_error = val_error
                            continue
                    if time_transformed is None:
                        azt_logger.error(f"{cls}.{time_attr_name}时间格式转换错误！")
                        raise tf_error
                    params[time_attr_name] = time_transformed
        return cls(**params)

    def _py2proto(self, cls):
        proto = self.p_proto_cls()
        cls_attrs = cls.__annotations__

        normal_attrs = set(cls_attrs.keys()) - self.m_abnormal_attrs

        for normal_attr_name in normal_attrs:
            if hasattr(proto, normal_attr_name):
                normal_attr_val = getattr(cls, normal_attr_name)
                if normal_attr_val is not None:
                    if hasattr(normal_attr_val, "__py2proto__"):
                        setattr(proto, normal_attr_name, normal_attr_val.__py2proto__())
                    else:
                        setattr(proto, normal_attr_name, normal_attr_val)
        if self.p_merge_name is not None:
            for merge_name, merge_val in self.p_merge_name.items():
                sep, sep_names = merge_val
                tmp_val = getattr(cls, merge_name).split(sep)
                for x1, x2 in list(zip(sep_names, tmp_val)):
                    if hasattr(proto, x1):
                        setattr(proto, x1, x2)
        # 2 需要由float转回int的属性
        if self.p_price_dec is not None:
            if hasattr(proto, self.p_price_dec):
                setattr(proto, self.p_price_dec, self.m_price_decimal_place)
            for price_attr_name in self.m_adj_price_attrs:
                if hasattr(proto, price_attr_name):
                    price_attr_val = getattr(cls, price_attr_name)
                    if price_attr_val is not None:
                        setattr(proto, price_attr_name, int(price_attr_val * self.m_price_decimal_pow))
            for repeat_price_attr_name in self.m_adj_repeat_price_attrs:
                if hasattr(proto, repeat_price_attr_name):
                    repeat_price_attr_val = getattr(cls, repeat_price_attr_name)
                    if isinstance(repeat_price_attr_val, list):
                        getattr(proto, repeat_price_attr_name).extend(
                            [repeat_price * self.m_price_decimal_pow for repeat_price in repeat_price_attr_val]
                        )

        if self.p_amount_dec is not None:
            if hasattr(proto, self.p_amount_dec):
                setattr(proto, self.p_amount_dec, self.m_amount_decimal_place)
            for amount_attr_name in self.m_adj_amount_attr:
                if hasattr(proto, amount_attr_name):
                    amount_attr_val = getattr(cls, amount_attr_name)
                    if amount_attr_val is not None:
                        setattr(proto, amount_attr_name, int(amount_attr_val * self.m_amount_decimal_pow))
            for repeat_amount_attr_name in self.m_adj_repeat_amount_attrs:
                if hasattr(proto, repeat_amount_attr_name):
                    repeat_amount_attr_val = getattr(cls, repeat_amount_attr_name)
                    if repeat_amount_attr_val:
                        getattr(proto, repeat_amount_attr_name).extend(
                            [repeat_amount * self.m_amount_decimal_pow for repeat_amount in repeat_amount_attr_val]
                        )

        # 3 repeat
        for repeat_attr_name in self.m_adj_repeat_attrs:
            if hasattr(proto, repeat_attr_name):
                repeat_attr_cls = cls_attrs[repeat_attr_name]
                if type(repeat_attr_cls) is list:
                    inner_type = repeat_attr_cls[0]
                    if hasattr(inner_type, "__py2proto__"):
                        repeat_attr_val = getattr(cls, repeat_attr_name)
                        getattr(proto, repeat_attr_name).extend(
                            [repeat_val.__py2proto__() for repeat_val in repeat_attr_val]
                        )
                    else:
                        getattr(proto, repeat_attr_name).extend(getattr(cls, repeat_attr_name))
            else:
                raise azt_errors.ListTypeError

        # 5 时间格式转换
        for time_attr_name in self.m_adj_time_attrs:
            if hasattr(proto, time_attr_name):
                time_attr_val = getattr(cls, time_attr_name)
                if time_attr_val is None:
                    continue
                if isinstance(time_attr_val, datetime.datetime):
                    time_format = self.p_adj_time[time_attr_name]
                    if type(time_format) is list:
                        time_format = time_format[0]
                    setattr(proto, time_attr_name, time_attr_val.strftime(time_format))
                elif isinstance(time_attr_val, str):
                    setattr(proto, time_attr_name, time_attr_val)
                else:
                    raise azt_errors.DatetimeTypeError
        return proto

    def __call__(self, pycls):
        if not hasattr(pycls, "__proto2py__"):
            setattr(pycls, "__proto2py__", classmethod(lambda x, y, z=None: self._proto2py(x, y, z)))
        if not hasattr(pycls, "__py2proto__"):
            setattr(pycls, "__py2proto__", lambda x: self._py2proto(x))
        if not hasattr(pycls, "__protocls__"):
            setattr(pycls, "__protocls__", self.p_proto_cls)
        return dataclasses.dataclass(pycls)

# #  =============================================================================
# #  GNU Lesser General Public License (LGPL)
# #
# #  Copyright (c) 2022 Qujamlee from www.aztquant.com
# #
# #  This program is free software: you can redistribute it and/or modify
# #  it under the terms of the GNU Lesser General Public License as published by
# #  the Free Software Foundation, either version 3 of the License, or
# #  (at your option) any later version.
# #
# #  This program is distributed in the hope that it will be useful,
# #  but WITHOUT ANY WARRANTY; without even the implied warranty of
# #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# #  GNU Lesser General Public License for more details.
# #
# #  You should have received a copy of the GNU Lesser General Public License
# #  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #  =============================================================================
#
# import dataclasses
# import datetime
# import time
#
# from . import azt_logger
# from . import azt_errors
#
#
# def _verify_params(param, verify_type, default=None):
#     if not isinstance(param, verify_type):
#         return default
#     return param
#
#
# def debug_calc_time(func):
#     def wrapper(*args, **kwargs):
#         obj = args[0]
#         argl = len(args)
#         t1 = time.time()
#         ret = func(*args, **kwargs)
#         t2 = time.time()
#         azt_logger.debug(f"{obj.__class__}.py2proto耗时：{(t2 - t1) * 1000:.4f}ms" if argl == 1 else
#                          f"{obj}.proto2py耗时：{(t2 - t1) * 1000:.4f}ms")
#         return ret
#
#     return wrapper
#
#
# def AztStructs(protocls,
#                  price_dec: str = None, amount_dec: str = None,
#                  adj_price: list = None, adj_amount: list = None,
#                  adj_repeat: list = None, adj_repeat_price: list = None, adj_repeat_amount: list = None,
#                  adj_map: list = None, adj_map_price: list = None, adj_map_amount: list = None,
#                  adj_any: dict = None,
#                  adj_time: dict = None,
#                  adj_name: dict = None,
#                  **kwargs
#                  ):
#     # # 1 参数类型验证
#     # price_dec = _verify_params(price_dec, str)
#     # amount_dec = _verify_params(amount_dec, str)
#     #
#     # adj_price = _verify_params(adj_price, list)
#     # adj_amount = _verify_params(adj_amount, list)
#     #
#     # adj_repeat = _verify_params(adj_repeat, list)
#     # adj_repeat_price = _verify_params(adj_repeat_price, list)
#     # adj_repeat_amount = _verify_params(adj_repeat_amount, list)
#     #
#     # adj_map = _verify_params(adj_map, list)
#     # adj_map_price = _verify_params(adj_map_price, list)
#     # adj_map_amount = _verify_params(adj_map_amount, list)
#     #
#     # adj_any = _verify_params(adj_any, dict)
#     #
#     # adj_time = _verify_params(adj_time, dict)
#     #
#     # adj_name = _verify_params(adj_name, dict)
#
#     # 2 将列表转为集合
#     adj_price_attrs = set() if adj_price is None else set(adj_price)
#     adj_amount_attr = set() if adj_amount is None else set(adj_amount)
#
#     adj_repeat_attrs = set() if adj_repeat is None else set(adj_repeat)
#     adj_repeat_price_attrs = set() if adj_repeat_price is None else set(adj_repeat_price)
#     adj_repeat_amount_attrs = set() if adj_repeat_amount is None else set(adj_repeat_amount)
#
#     adj_map_attrs = set() if adj_map is None else set(adj_map)
#     adj_map_price_attrs = set() if adj_map_price is None else set(adj_map_price)
#     adj_map_amount_attrs = set() if adj_map_amount is None else set(adj_map_amount)
#
#     adj_any_attrs = set() if adj_any is None else set(adj_any)
#
#     adj_time_attrs = set() if adj_time is None else set(adj_time)
#
#     # 3 获取需要处理的属性集合
#     abnormal_attrs = adj_price_attrs | adj_amount_attr | adj_repeat_attrs | adj_repeat_price_attrs \
#                      | adj_repeat_amount_attrs | adj_map_attrs | adj_map_price_attrs | adj_map_amount_attrs \
#                      | adj_time_attrs | adj_any_attrs
#     # normal_attrs = None
#     # 4 获取小数位数据
#     price_decimal_place = _verify_params(kwargs.get("pdp"), int, 2)
#     amount_decimal_place = _verify_params(kwargs.get("adp"), int, 2)
#     price_decimal_pow = 10 ** price_decimal_place
#     amount_decimal_pow = 10 ** amount_decimal_place
#
#     # @debug_calc_time
#     def func_proto2py(cls, proto):
#         params = dict()
#
#         cls_attrs = cls.__annotations__
#         all_attrs = cls_attrs.keys()
#         proto_attrs = dict(zip(all_attrs, all_attrs))
#         if adj_name is not None:
#             proto_attrs.update(adj_name)
#         # 1 不需要处理的属性
#         normal_attrs = set(all_attrs) - abnormal_attrs
#         for normal_attr_name in normal_attrs:
#             normal_atrr_cls = cls_attrs[normal_attr_name]
#             if hasattr(normal_atrr_cls, "__proto2py__"):
#                 params[normal_attr_name] = normal_atrr_cls.__proto2py__(getattr(proto, proto_attrs[normal_attr_name]))
#             else:
#                 params[normal_attr_name] = getattr(proto, normal_attr_name)
#         # 2 需要处理的属性
#         # 2.1 需要由int转float的价格
#         if price_dec is not None:
#             p_d = price_decimal_pow
#             if hasattr(proto, price_dec):
#                 proto_pd = getattr(proto, price_dec)
#                 p_d = (10 ** proto_pd) if isinstance(proto_pd, int) else p_d
#
#             # int转float的价格
#             for price_attr_name in adj_price_attrs:
#                 proto_attr_name = proto_attrs[price_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     params[price_attr_name] = getattr(proto, proto_attr_name) / p_d
#             # repeat转list,需要将价格由int转float
#             for repeat_price_attr_name in adj_repeat_price_attrs:
#                 proto_attr_name = proto_attrs[repeat_price_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     params[repeat_price_attr_name] = [inner_price / p_d for inner_price in
#                                                       getattr(proto, proto_attr_name)]
#             for map_price_attr_name in adj_map_price_attrs:
#                 proto_attr_name = proto_attrs[map_price_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     proto_map_val = getattr(proto, proto_attr_name)
#                     params[map_price_attr_name] = {map_idx: proto_map_val[map_idx] / p_d for map_idx in proto_map_val}
#
#         if amount_dec is not None:
#             a_d = amount_decimal_pow
#             if hasattr(proto, amount_dec):
#                 proto_ad = getattr(proto, amount_dec)
#                 a_d = (10 ** proto_ad) if isinstance(proto_ad, int) else a_d
#             # int转float的数额
#             for amount_attr_name in adj_amount_attr:
#                 proto_attr_name = proto_attrs[amount_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     params[amount_attr_name] = getattr(proto, proto_attr_name) / a_d
#             # repeat转list,需要将数额由int转float
#             for repeat_amount_attr_name in adj_repeat_amount_attrs:
#                 proto_attr_name = proto_attrs[repeat_amount_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     params[repeat_amount_attr_name] = [inner_amount / a_d for inner_amount in
#                                                        getattr(proto, proto_attr_name)]
#
#             for map_amount_attr_name in adj_map_amount_attrs:
#                 proto_attr_name = proto_attrs[map_amount_attr_name]
#                 if hasattr(proto, proto_attr_name):
#                     proto_map_val = getattr(proto, proto_attr_name)
#                     params[map_amount_attr_name] = {map_idx: proto_map_val[map_idx] / a_d for map_idx in proto_map_val}
#
#         # 2.3 repeat转list,需要考虑是否为自定义类型
#         for repeat_attr_name in adj_repeat_attrs:
#             proto_attr_name = proto_attrs[repeat_attr_name]
#             if hasattr(proto, proto_attr_name):
#                 repeat_attr_cls = cls_attrs[repeat_attr_name]
#                 if type(repeat_attr_cls) is list:
#                     inner_type = repeat_attr_cls[0]
#                     if hasattr(inner_type, "__proto2py__"):
#                         params[repeat_attr_name] = [inner_type.__proto2py__(inner_proto) for inner_proto in
#                                                     getattr(proto, proto_attr_name)]
#                     else:
#                         params[repeat_attr_name] = list(getattr(proto, proto_attr_name))
#                 else:
#                     raise azt_errors.ListTypeError
#
#         for map_attr_name in adj_map_attrs:
#             proto_attr_name = proto_attrs[map_attr_name]
#             if hasattr(proto, proto_attr_name):
#                 proto_map_val = getattr(proto, proto_attr_name)
#                 map_attr_cls = cls_attrs[map_attr_name]
#                 if type(map_attr_cls) is dict:
#                     val_atrr_cls = list(map_attr_cls.values())[0]
#                     if hasattr(val_atrr_cls, "__proto2py__"):
#                         params[map_attr_name] = {map_idx: val_atrr_cls.__proto2py__(proto_map_val[map_idx])
#                                                  for map_idx in proto_map_val}
#                     else:
#                         params[map_attr_name] = dict(proto_map_val)
#                 else:
#                     raise azt_errors.DictTypeError
#         for any_attr_name in adj_any_attrs:
#             proto_attr_name = proto_attrs[any_attr_name]
#             if hasattr(proto, proto_attr_name):
#                 any_attr_type = adj_any[any_attr_name]
#                 if hasattr(any_attr_type, "__protocls__"):
#                     any_attr_proto = any_attr_type.__protocls__()
#                     getattr(proto, proto_attr_name).Unpack(any_attr_proto)
#                     params[any_attr_name] = any_attr_type.__proto2py__(any_attr_proto)
#
#         # 时间格式转换
#         for time_attr_name in adj_time_attrs:
#             if hasattr(proto, time_attr_name):
#                 proto_time_attr_val: str = getattr(proto, time_attr_name)
#                 if proto_time_attr_val != "":
#                     time_format = adj_time[time_attr_name]
#                     if type(time_format) is str:
#                         time_format = [time_format]
#                     time_transformed = None
#                     tf_error = ValueError
#                     for t_format in time_format:
#                         try:
#                             time_transformed = datetime.datetime.strptime(proto_time_attr_val, t_format)
#                             break
#                         except ValueError as val_error:
#                             tf_error = val_error
#                             continue
#                     if time_transformed is None:
#                         azt_logger.error(f"{cls}.{time_attr_name}时间格式转换错误！")
#                         raise tf_error
#                     params[time_attr_name] = time_transformed
#         return cls(**params)
#
#     # @debug_calc_time
#     def func_py2proto(self):
#         proto = protocls()
#         cls_attrs = self.__annotations__
#         # 1 不需要处理的属性
#         normal_attrs = set(cls_attrs.keys()) - abnormal_attrs
#
#         for normal_attr_name in normal_attrs:
#             if hasattr(proto, normal_attr_name):
#                 normal_attr_val = getattr(self, normal_attr_name)
#                 if normal_attr_val is not None:
#                     if hasattr(normal_attr_val, "__py2proto__"):
#                         setattr(proto, normal_attr_name, normal_attr_val.__py2proto__())
#                     else:
#                         setattr(proto, normal_attr_name, normal_attr_val)
#         # 2 需要由float转回int的属性
#         if price_dec is not None:
#             if hasattr(proto, price_dec):
#                 setattr(proto, price_dec, price_decimal_place)
#             for price_attr_name in adj_price_attrs:
#                 if hasattr(proto, price_attr_name):
#                     price_attr_val = getattr(self, price_attr_name)
#                     if price_attr_val is not None:
#                         setattr(proto, price_attr_name, int(price_attr_val * price_decimal_pow))
#             for repeat_price_attr_name in adj_repeat_price_attrs:
#                 if hasattr(proto, repeat_price_attr_name):
#                     repeat_price_attr_val = getattr(self, repeat_price_attr_name)
#                     if isinstance(repeat_price_attr_val, list):
#                         getattr(proto, repeat_price_attr_name).extend(
#                             [repeat_price * price_decimal_pow for repeat_price in repeat_price_attr_val]
#                         )
#         if amount_dec is not None:
#             if hasattr(proto, amount_dec):
#                 setattr(proto, amount_dec, amount_decimal_place)
#             for amount_attr_name in adj_amount_attr:
#                 if hasattr(proto, amount_attr_name):
#                     amount_attr_val = getattr(self, amount_attr_name)
#                     if amount_attr_val is not None:
#                         setattr(proto, amount_attr_name, int(amount_attr_val * amount_decimal_pow))
#             for repeat_amount_attr_name in adj_repeat_amount_attrs:
#                 if hasattr(proto, repeat_amount_attr_name):
#                     repeat_amount_attr_val = getattr(self, repeat_amount_attr_name)
#                     if repeat_amount_attr_val:
#                         getattr(proto, repeat_amount_attr_name).extend(
#                             [repeat_amount * amount_decimal_pow for repeat_amount in repeat_amount_attr_val]
#                         )
#         # 3 repeat
#         for repeat_attr_name in adj_repeat_attrs:
#             if hasattr(proto, repeat_attr_name):
#                 repeat_attr_cls = cls_attrs[repeat_attr_name]
#                 if type(repeat_attr_cls) is list:
#                     inner_type = repeat_attr_cls[0]
#                     if hasattr(inner_type, "__py2proto__"):
#                         repeat_attr_val = getattr(self, repeat_attr_name)
#                         getattr(proto, repeat_attr_name).extend(
#                             [repeat_val.__py2proto__() for repeat_val in repeat_attr_val]
#                         )
#                     else:
#                         getattr(proto, repeat_attr_name).extend(getattr(self, repeat_attr_name))
#             else:
#                 raise azt_errors.ListTypeError
#         # 5 时间格式转换
#         for time_attr_name in adj_time_attrs:
#             if hasattr(proto, time_attr_name):
#                 time_attr_val = getattr(self, time_attr_name)
#                 if time_attr_val is None:
#                     continue
#                 if isinstance(time_attr_val, datetime.datetime):
#                     time_format = adj_time[time_attr_name]
#                     if type(time_format) is list:
#                         time_format = time_format[0]
#                     setattr(proto, time_attr_name, time_attr_val.strftime(time_format))
#                 elif isinstance(time_attr_val, str):
#                     setattr(proto, time_attr_name, time_attr_val)
#                 else:
#                     raise azt_errors.DatetimeTypeError
#         return proto
#
#     def wrapper_func(pycls):
#         if not hasattr(pycls, "__proto2py__"):
#             setattr(pycls, "__proto2py__", classmethod(func_proto2py))
#         if not hasattr(pycls, "__py2proto__"):
#             setattr(pycls, "__py2proto__", func_py2proto)
#         if not hasattr(pycls, "__protocls__"):
#             setattr(pycls, "__protocls__", protocls)
#         return dataclasses.dataclass(pycls)
#
#     return wrapper_func
