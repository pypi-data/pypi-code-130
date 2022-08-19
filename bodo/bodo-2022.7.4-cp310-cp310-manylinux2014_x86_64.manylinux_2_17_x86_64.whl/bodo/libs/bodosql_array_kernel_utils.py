"""
Common utilities for all BodoSQL array kernels
"""
import math
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from numba.core import types
import bodo
from bodo.utils.typing import is_overload_bool, is_overload_constant_bytes, is_overload_constant_number, is_overload_constant_str, is_overload_int, raise_bodo_error


def gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
    out_dtype, arg_string=None, arg_sources=None, array_override=None,
    support_dict_encoding=True):
    abq__pwjy = [bodo.utils.utils.is_array_typ(gstfj__erkct, True) for
        gstfj__erkct in arg_types]
    kvby__zgde = not any(abq__pwjy)
    zaw__jfp = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    xgky__afc = 0
    mib__meai = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            xgky__afc += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                mib__meai = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            xgky__afc += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                mib__meai = i
    bnoz__byghn = support_dict_encoding and xgky__afc == 1 and mib__meai >= 0
    yca__czjm = bnoz__byghn and out_dtype == bodo.string_array_type and (any
        (arg_types[i] == bodo.none and propagate_null[i] for i in range(len
        (arg_types))) or 'bodo.libs.array_kernels.setna' in scalar_text)
    ymbgd__uroqt = scalar_text.splitlines()[0]
    vxm__zxc = len(ymbgd__uroqt) - len(ymbgd__uroqt.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    zmo__pym = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for btnh__rqnht, sut__qwk in arg_sources.items():
            zmo__pym += f'   {btnh__rqnht} = {sut__qwk}\n'
    if kvby__zgde and array_override == None:
        if zaw__jfp:
            zmo__pym += '   return None'
        else:
            for i in range(len(arg_names)):
                zmo__pym += f'   arg{i} = {arg_names[i]}\n'
            for vuqbq__pegma in scalar_text.splitlines():
                zmo__pym += ' ' * 3 + vuqbq__pegma[vxm__zxc:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            zmo__pym += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                zmo__pym += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            fdwz__tgol = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if abq__pwjy[i]:
                    fdwz__tgol = f'len({arg_names[i]})'
                    break
        if bnoz__byghn:
            if out_dtype == bodo.string_array_type:
                zmo__pym += (
                    f'   indices = {arg_names[mib__meai]}._indices.copy()\n')
                zmo__pym += (
                    f'   has_global = {arg_names[mib__meai]}._has_global_dictionary\n'
                    )
                zmo__pym += (
                    f'   {arg_names[i]} = {arg_names[mib__meai]}._data\n')
            else:
                zmo__pym += f'   indices = {arg_names[mib__meai]}._indices\n'
                zmo__pym += (
                    f'   {arg_names[i]} = {arg_names[mib__meai]}._data\n')
        zmo__pym += f'   n = {fdwz__tgol}\n'
        if bnoz__byghn:
            if out_dtype == bodo.string_array_type:
                zmo__pym += (
                    '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                    )
            else:
                zmo__pym += (
                    '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n'
                    )
            zmo__pym += '   for i in range(n):\n'
        else:
            zmo__pym += (
                '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            zmo__pym += '   numba.parfors.parfor.init_prange()\n'
            zmo__pym += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if zaw__jfp:
            zmo__pym += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if abq__pwjy[i]:
                    if propagate_null[i]:
                        zmo__pym += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        zmo__pym += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        zmo__pym += '         continue\n'
            for i in range(len(arg_names)):
                if abq__pwjy[i]:
                    zmo__pym += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    zmo__pym += f'      arg{i} = {arg_names[i]}\n'
            for vuqbq__pegma in scalar_text.splitlines():
                zmo__pym += ' ' * 6 + vuqbq__pegma[vxm__zxc:] + '\n'
        if bnoz__byghn:
            if yca__czjm:
                zmo__pym += '   numba.parfors.parfor.init_prange()\n'
                zmo__pym += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                zmo__pym += (
                    '      if not bodo.libs.array_kernels.isna(indices, i):\n')
                zmo__pym += '         loc = indices[i]\n'
                zmo__pym += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                zmo__pym += (
                    '            bodo.libs.array_kernels.setna(indices, i)\n')
            if out_dtype == bodo.string_array_type:
                zmo__pym += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            else:
                zmo__pym += """   res2 = bodo.utils.utils.alloc_type(len(indices), out_dtype, (-1,))
"""
                zmo__pym += '   numba.parfors.parfor.init_prange()\n'
                zmo__pym += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                zmo__pym += (
                    '      if bodo.libs.array_kernels.isna(indices, i):\n')
                zmo__pym += '         bodo.libs.array_kernels.setna(res2, i)\n'
                zmo__pym += '      else:\n'
                zmo__pym += '         loc = indices[i]\n'
                zmo__pym += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                zmo__pym += (
                    '            bodo.libs.array_kernels.setna(res2, i)\n')
                zmo__pym += '         else:\n'
                zmo__pym += '            res2[i] = res[loc]\n'
                zmo__pym += '   res = res2\n'
            zmo__pym += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            zmo__pym += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    wzhrw__oqg = {}
    exec(zmo__pym, {'bodo': bodo, 'math': math, 'numba': numba, 'np': np,
        'out_dtype': out_dtype, 'pd': pd}, wzhrw__oqg)
    ljdi__vra = wzhrw__oqg['impl']
    return ljdi__vra


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        gyw__szvp = [(f'{arg_names[0]}{[val__rncjw]}' if val__rncjw != i else
            'None') for val__rncjw in range(container_length)]
        bbh__qyzw = [(f'{arg_names[0]}{[val__rncjw]}' if val__rncjw != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{val__rncjw}])'
            ) for val__rncjw in range(container_length)]
        zmo__pym = f"def impl({', '.join(arg_names)}):\n"
        zmo__pym += f'   if {arg_names[0]}[{i}] is None:\n'
        zmo__pym += f"      return {func_name}(({', '.join(gyw__szvp)}))\n"
        zmo__pym += f'   else:\n'
        zmo__pym += f"      return {func_name}(({', '.join(bbh__qyzw)}))"
    else:
        gyw__szvp = [(arg_names[val__rncjw] if val__rncjw != i else 'None') for
            val__rncjw in range(len(arg_names))]
        bbh__qyzw = [(arg_names[val__rncjw] if val__rncjw != i else
            f'bodo.utils.indexing.unoptional({arg_names[val__rncjw]})') for
            val__rncjw in range(len(arg_names))]
        zmo__pym = f"def impl({', '.join(arg_names)}):\n"
        zmo__pym += f'   if {arg_names[i]} is None:\n'
        zmo__pym += f"      return {func_name}({', '.join(gyw__szvp)})\n"
        zmo__pym += f'   else:\n'
        zmo__pym += f"      return {func_name}({', '.join(bbh__qyzw)})"
    wzhrw__oqg = {}
    exec(zmo__pym, {'bodo': bodo, 'numba': numba}, wzhrw__oqg)
    ljdi__vra = wzhrw__oqg['impl']
    return ljdi__vra


def verify_int_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, types.Integer) and not (bodo
        .utils.utils.is_array_typ(arg, True) and isinstance(arg.dtype,
        types.Integer)) and not is_overload_int(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be an integer, integer column, or null'
            )


def verify_int_float_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, (types.Integer, types.
        Float, types.Boolean)) and not (bodo.utils.utils.is_array_typ(arg, 
        True) and isinstance(arg.dtype, (types.Integer, types.Float, types.
        Boolean))) and not is_overload_constant_number(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a numeric, numeric column, or null'
            )


def is_valid_string_arg(arg):
    return not (arg not in (types.none, types.unicode_type) and not
        isinstance(arg, types.StringLiteral) and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == types.unicode_type) and 
        not is_overload_constant_str(arg))


def is_valid_binary_arg(arg):
    return not (arg != bodo.bytes_type and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == bodo.bytes_type) and not
        is_overload_constant_bytes(arg) and not isinstance(arg, types.Bytes))


def verify_string_arg(arg, f_name, a_name):
    if not is_valid_string_arg(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a string, string column, or null'
            )


def verify_binary_arg(arg, f_name, a_name):
    if not is_valid_binary_arg(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be binary data or null')


def verify_string_binary_arg(arg, f_name, a_name):
    dif__jbo = is_valid_string_arg(arg)
    clmmc__ssws = is_valid_binary_arg(arg)
    if dif__jbo or clmmc__ssws:
        return dif__jbo
    else:
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a binary data, string, string column, or null'
            )


def verify_boolean_arg(arg, f_name, a_name):
    if arg not in (types.none, types.boolean) and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == types.boolean
        ) and not is_overload_bool(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a boolean, boolean column, or null'
            )


def verify_datetime_arg(arg, f_name, a_name):
    if arg not in (types.none, bodo.datetime64ns, bodo.pd_timestamp_type,
        bodo.hiframes.datetime_date_ext.DatetimeDateType()) and not (bodo.
        utils.utils.is_array_typ(arg, True) and arg.dtype in (bodo.
        datetime64ns, bodo.hiframes.datetime_date_ext.DatetimeDateType())):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a datetime, datetime column, or null'
            )


def get_common_broadcasted_type(arg_types, func_name):
    cfx__fyoh = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            cfx__fyoh.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            cfx__fyoh.append(arg_types[i].data)
        else:
            cfx__fyoh.append(arg_types[i])
    if len(cfx__fyoh) == 0:
        return bodo.none
    elif len(cfx__fyoh) == 1:
        if bodo.utils.utils.is_array_typ(cfx__fyoh[0]):
            return bodo.utils.typing.to_nullable_type(cfx__fyoh[0])
        elif cfx__fyoh[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(cfx__fyoh[0]))
    else:
        igmf__rhr = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                igmf__rhr.append(cfx__fyoh[i].dtype)
            elif cfx__fyoh[i] == bodo.none:
                pass
            else:
                igmf__rhr.append(cfx__fyoh[i])
        if len(igmf__rhr) == 0:
            return bodo.none
        enjkv__liwz, thwsd__mxarg = bodo.utils.typing.get_common_scalar_dtype(
            igmf__rhr)
        if not thwsd__mxarg:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(enjkv__liwz))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    axq__ice = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            axq__ice = len(arg)
            break
    if axq__ice == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    kzi__gdua = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            kzi__gdua.append(arg)
        else:
            kzi__gdua.append([arg] * axq__ice)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*jkkj__xup)) for jkkj__xup in zip
            (*kzi__gdua)])
    else:
        return pd.Series([scalar_fn(*jkkj__xup) for jkkj__xup in zip(*
            kzi__gdua)], dtype=dtype)
