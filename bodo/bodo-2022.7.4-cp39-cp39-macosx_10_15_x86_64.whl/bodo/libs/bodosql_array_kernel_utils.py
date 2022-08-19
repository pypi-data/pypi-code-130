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
    fmqha__eako = [bodo.utils.utils.is_array_typ(ulkz__mccks, True) for
        ulkz__mccks in arg_types]
    crq__fqeq = not any(fmqha__eako)
    ykaza__gsq = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    ivwes__vmyf = 0
    fahd__lvor = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            ivwes__vmyf += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                fahd__lvor = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            ivwes__vmyf += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                fahd__lvor = i
    bnkx__tkd = support_dict_encoding and ivwes__vmyf == 1 and fahd__lvor >= 0
    rvswk__yyg = bnkx__tkd and out_dtype == bodo.string_array_type and (any
        (arg_types[i] == bodo.none and propagate_null[i] for i in range(len
        (arg_types))) or 'bodo.libs.array_kernels.setna' in scalar_text)
    tilyp__tzb = scalar_text.splitlines()[0]
    tgk__eei = len(tilyp__tzb) - len(tilyp__tzb.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    vqauq__wmkrl = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for sih__unqqi, hgw__efif in arg_sources.items():
            vqauq__wmkrl += f'   {sih__unqqi} = {hgw__efif}\n'
    if crq__fqeq and array_override == None:
        if ykaza__gsq:
            vqauq__wmkrl += '   return None'
        else:
            for i in range(len(arg_names)):
                vqauq__wmkrl += f'   arg{i} = {arg_names[i]}\n'
            for wrjl__zyy in scalar_text.splitlines():
                vqauq__wmkrl += ' ' * 3 + wrjl__zyy[tgk__eei:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            vqauq__wmkrl += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                vqauq__wmkrl += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            ikjak__fpyb = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if fmqha__eako[i]:
                    ikjak__fpyb = f'len({arg_names[i]})'
                    break
        if bnkx__tkd:
            if out_dtype == bodo.string_array_type:
                vqauq__wmkrl += (
                    f'   indices = {arg_names[fahd__lvor]}._indices.copy()\n')
                vqauq__wmkrl += (
                    f'   has_global = {arg_names[fahd__lvor]}._has_global_dictionary\n'
                    )
                vqauq__wmkrl += (
                    f'   {arg_names[i]} = {arg_names[fahd__lvor]}._data\n')
            else:
                vqauq__wmkrl += (
                    f'   indices = {arg_names[fahd__lvor]}._indices\n')
                vqauq__wmkrl += (
                    f'   {arg_names[i]} = {arg_names[fahd__lvor]}._data\n')
        vqauq__wmkrl += f'   n = {ikjak__fpyb}\n'
        if bnkx__tkd:
            if out_dtype == bodo.string_array_type:
                vqauq__wmkrl += (
                    '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                    )
            else:
                vqauq__wmkrl += (
                    '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n'
                    )
            vqauq__wmkrl += '   for i in range(n):\n'
        else:
            vqauq__wmkrl += (
                '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            vqauq__wmkrl += '   numba.parfors.parfor.init_prange()\n'
            vqauq__wmkrl += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if ykaza__gsq:
            vqauq__wmkrl += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if fmqha__eako[i]:
                    if propagate_null[i]:
                        vqauq__wmkrl += f"""      if bodo.libs.array_kernels.isna({arg_names[i]}, i):
"""
                        vqauq__wmkrl += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        vqauq__wmkrl += '         continue\n'
            for i in range(len(arg_names)):
                if fmqha__eako[i]:
                    vqauq__wmkrl += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    vqauq__wmkrl += f'      arg{i} = {arg_names[i]}\n'
            for wrjl__zyy in scalar_text.splitlines():
                vqauq__wmkrl += ' ' * 6 + wrjl__zyy[tgk__eei:] + '\n'
        if bnkx__tkd:
            if rvswk__yyg:
                vqauq__wmkrl += '   numba.parfors.parfor.init_prange()\n'
                vqauq__wmkrl += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                vqauq__wmkrl += (
                    '      if not bodo.libs.array_kernels.isna(indices, i):\n')
                vqauq__wmkrl += '         loc = indices[i]\n'
                vqauq__wmkrl += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                vqauq__wmkrl += (
                    '            bodo.libs.array_kernels.setna(indices, i)\n')
            if out_dtype == bodo.string_array_type:
                vqauq__wmkrl += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            else:
                vqauq__wmkrl += """   res2 = bodo.utils.utils.alloc_type(len(indices), out_dtype, (-1,))
"""
                vqauq__wmkrl += '   numba.parfors.parfor.init_prange()\n'
                vqauq__wmkrl += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                vqauq__wmkrl += (
                    '      if bodo.libs.array_kernels.isna(indices, i):\n')
                vqauq__wmkrl += (
                    '         bodo.libs.array_kernels.setna(res2, i)\n')
                vqauq__wmkrl += '      else:\n'
                vqauq__wmkrl += '         loc = indices[i]\n'
                vqauq__wmkrl += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                vqauq__wmkrl += (
                    '            bodo.libs.array_kernels.setna(res2, i)\n')
                vqauq__wmkrl += '         else:\n'
                vqauq__wmkrl += '            res2[i] = res[loc]\n'
                vqauq__wmkrl += '   res = res2\n'
            vqauq__wmkrl += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            vqauq__wmkrl += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    cfgth__fzchr = {}
    exec(vqauq__wmkrl, {'bodo': bodo, 'math': math, 'numba': numba, 'np':
        np, 'out_dtype': out_dtype, 'pd': pd}, cfgth__fzchr)
    qeu__qdoo = cfgth__fzchr['impl']
    return qeu__qdoo


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        lybfk__ewps = [(f'{arg_names[0]}{[usg__spof]}' if usg__spof != i else
            'None') for usg__spof in range(container_length)]
        ccjf__hgb = [(f'{arg_names[0]}{[usg__spof]}' if usg__spof != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{usg__spof}])') for
            usg__spof in range(container_length)]
        vqauq__wmkrl = f"def impl({', '.join(arg_names)}):\n"
        vqauq__wmkrl += f'   if {arg_names[0]}[{i}] is None:\n'
        vqauq__wmkrl += (
            f"      return {func_name}(({', '.join(lybfk__ewps)}))\n")
        vqauq__wmkrl += f'   else:\n'
        vqauq__wmkrl += f"      return {func_name}(({', '.join(ccjf__hgb)}))"
    else:
        lybfk__ewps = [(arg_names[usg__spof] if usg__spof != i else 'None') for
            usg__spof in range(len(arg_names))]
        ccjf__hgb = [(arg_names[usg__spof] if usg__spof != i else
            f'bodo.utils.indexing.unoptional({arg_names[usg__spof]})') for
            usg__spof in range(len(arg_names))]
        vqauq__wmkrl = f"def impl({', '.join(arg_names)}):\n"
        vqauq__wmkrl += f'   if {arg_names[i]} is None:\n'
        vqauq__wmkrl += f"      return {func_name}({', '.join(lybfk__ewps)})\n"
        vqauq__wmkrl += f'   else:\n'
        vqauq__wmkrl += f"      return {func_name}({', '.join(ccjf__hgb)})"
    cfgth__fzchr = {}
    exec(vqauq__wmkrl, {'bodo': bodo, 'numba': numba}, cfgth__fzchr)
    qeu__qdoo = cfgth__fzchr['impl']
    return qeu__qdoo


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
    mhi__gepo = is_valid_string_arg(arg)
    vbsan__fdtrv = is_valid_binary_arg(arg)
    if mhi__gepo or vbsan__fdtrv:
        return mhi__gepo
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
    dam__tvui = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            dam__tvui.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            dam__tvui.append(arg_types[i].data)
        else:
            dam__tvui.append(arg_types[i])
    if len(dam__tvui) == 0:
        return bodo.none
    elif len(dam__tvui) == 1:
        if bodo.utils.utils.is_array_typ(dam__tvui[0]):
            return bodo.utils.typing.to_nullable_type(dam__tvui[0])
        elif dam__tvui[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(dam__tvui[0]))
    else:
        hoki__qpcbz = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                hoki__qpcbz.append(dam__tvui[i].dtype)
            elif dam__tvui[i] == bodo.none:
                pass
            else:
                hoki__qpcbz.append(dam__tvui[i])
        if len(hoki__qpcbz) == 0:
            return bodo.none
        pfdf__rabiz, imkgo__dchjk = bodo.utils.typing.get_common_scalar_dtype(
            hoki__qpcbz)
        if not imkgo__dchjk:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(pfdf__rabiz))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    fbnls__xilm = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            fbnls__xilm = len(arg)
            break
    if fbnls__xilm == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    ltfa__mhcx = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            ltfa__mhcx.append(arg)
        else:
            ltfa__mhcx.append([arg] * fbnls__xilm)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*ehkqt__fgv)) for ehkqt__fgv in
            zip(*ltfa__mhcx)])
    else:
        return pd.Series([scalar_fn(*ehkqt__fgv) for ehkqt__fgv in zip(*
            ltfa__mhcx)], dtype=dtype)
