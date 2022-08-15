"""
Common utilities for all BodoSQL array kernels
"""
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
    vjp__dzl = [bodo.utils.utils.is_array_typ(rxma__vzzuv, True) for
        rxma__vzzuv in arg_types]
    atopk__bghg = not any(vjp__dzl)
    rsc__bcxry = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    xbm__xel = 0
    qogij__jphjw = -1
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            xbm__xel += 1
            if arg_types[i] == bodo.dict_str_arr_type:
                qogij__jphjw = i
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            xbm__xel += 1
            if arg_types[i].dtype == bodo.dict_str_arr_type:
                qogij__jphjw = i
    bgnfb__ylqp = support_dict_encoding and xbm__xel == 1 and qogij__jphjw >= 0
    woa__dga = bgnfb__ylqp and out_dtype == bodo.string_array_type and (any
        (arg_types[i] == bodo.none and propagate_null[i] for i in range(len
        (arg_types))) or 'bodo.libs.array_kernels.setna' in scalar_text)
    xwgy__tgv = scalar_text.splitlines()[0]
    uijq__iddxh = len(xwgy__tgv) - len(xwgy__tgv.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    kobc__fwxz = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for wpey__uaa, apvh__lzgqi in arg_sources.items():
            kobc__fwxz += f'   {wpey__uaa} = {apvh__lzgqi}\n'
    if atopk__bghg and array_override == None:
        if rsc__bcxry:
            kobc__fwxz += '   return None'
        else:
            for i in range(len(arg_names)):
                kobc__fwxz += f'   arg{i} = {arg_names[i]}\n'
            for bqgf__azw in scalar_text.splitlines():
                kobc__fwxz += ' ' * 3 + bqgf__azw[uijq__iddxh:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            kobc__fwxz += '   return answer'
    else:
        for i in range(len(arg_names)):
            if bodo.hiframes.pd_series_ext.is_series_type(arg_types[i]):
                kobc__fwxz += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        if array_override != None:
            ovq__eno = f'len({array_override})'
        else:
            for i in range(len(arg_names)):
                if vjp__dzl[i]:
                    ovq__eno = f'len({arg_names[i]})'
                    break
        if bgnfb__ylqp:
            if out_dtype == bodo.string_array_type:
                kobc__fwxz += (
                    f'   indices = {arg_names[qogij__jphjw]}._indices.copy()\n'
                    )
                kobc__fwxz += (
                    f'   has_global = {arg_names[qogij__jphjw]}._has_global_dictionary\n'
                    )
                kobc__fwxz += (
                    f'   {arg_names[i]} = {arg_names[qogij__jphjw]}._data\n')
            else:
                kobc__fwxz += (
                    f'   indices = {arg_names[qogij__jphjw]}._indices\n')
                kobc__fwxz += (
                    f'   {arg_names[i]} = {arg_names[qogij__jphjw]}._data\n')
        kobc__fwxz += f'   n = {ovq__eno}\n'
        if bgnfb__ylqp:
            if out_dtype == bodo.string_array_type:
                kobc__fwxz += (
                    '   res = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                    )
            else:
                kobc__fwxz += (
                    '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n'
                    )
            kobc__fwxz += '   for i in range(n):\n'
        else:
            kobc__fwxz += (
                '   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
            kobc__fwxz += '   numba.parfors.parfor.init_prange()\n'
            kobc__fwxz += (
                '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if rsc__bcxry:
            kobc__fwxz += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if vjp__dzl[i]:
                    if propagate_null[i]:
                        kobc__fwxz += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        kobc__fwxz += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        kobc__fwxz += '         continue\n'
            for i in range(len(arg_names)):
                if vjp__dzl[i]:
                    kobc__fwxz += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    kobc__fwxz += f'      arg{i} = {arg_names[i]}\n'
            for bqgf__azw in scalar_text.splitlines():
                kobc__fwxz += ' ' * 6 + bqgf__azw[uijq__iddxh:] + '\n'
        if bgnfb__ylqp:
            if woa__dga:
                kobc__fwxz += '   numba.parfors.parfor.init_prange()\n'
                kobc__fwxz += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                kobc__fwxz += (
                    '      if not bodo.libs.array_kernels.isna(indices, i):\n')
                kobc__fwxz += '         loc = indices[i]\n'
                kobc__fwxz += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                kobc__fwxz += (
                    '            bodo.libs.array_kernels.setna(indices, i)\n')
            if out_dtype == bodo.string_array_type:
                kobc__fwxz += """   res = bodo.libs.dict_arr_ext.init_dict_arr(res, indices, has_global)
"""
            else:
                kobc__fwxz += """   res2 = bodo.utils.utils.alloc_type(len(indices), out_dtype, (-1,))
"""
                kobc__fwxz += '   numba.parfors.parfor.init_prange()\n'
                kobc__fwxz += (
                    '   for i in numba.parfors.parfor.internal_prange(len(indices)):\n'
                    )
                kobc__fwxz += (
                    '      if bodo.libs.array_kernels.isna(indices, i):\n')
                kobc__fwxz += (
                    '         bodo.libs.array_kernels.setna(res2, i)\n')
                kobc__fwxz += '      else:\n'
                kobc__fwxz += '         loc = indices[i]\n'
                kobc__fwxz += (
                    '         if bodo.libs.array_kernels.isna(res, loc):\n')
                kobc__fwxz += (
                    '            bodo.libs.array_kernels.setna(res2, i)\n')
                kobc__fwxz += '         else:\n'
                kobc__fwxz += '            res2[i] = res[loc]\n'
                kobc__fwxz += '   res = res2\n'
            kobc__fwxz += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, len(indices), 1), None)'
                )
        else:
            kobc__fwxz += (
                '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
                )
    xoa__eprq = {}
    exec(kobc__fwxz, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, xoa__eprq)
    wfkzd__nmixc = xoa__eprq['impl']
    return wfkzd__nmixc


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        ulzj__ciy = [(f'{arg_names[0]}{[pddoj__tpu]}' if pddoj__tpu != i else
            'None') for pddoj__tpu in range(container_length)]
        ndjv__xvfn = [(f'{arg_names[0]}{[pddoj__tpu]}' if pddoj__tpu != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{pddoj__tpu}])'
            ) for pddoj__tpu in range(container_length)]
        kobc__fwxz = f"def impl({', '.join(arg_names)}):\n"
        kobc__fwxz += f'   if {arg_names[0]}[{i}] is None:\n'
        kobc__fwxz += f"      return {func_name}(({', '.join(ulzj__ciy)}))\n"
        kobc__fwxz += f'   else:\n'
        kobc__fwxz += f"      return {func_name}(({', '.join(ndjv__xvfn)}))"
    else:
        ulzj__ciy = [(arg_names[pddoj__tpu] if pddoj__tpu != i else 'None') for
            pddoj__tpu in range(len(arg_names))]
        ndjv__xvfn = [(arg_names[pddoj__tpu] if pddoj__tpu != i else
            f'bodo.utils.indexing.unoptional({arg_names[pddoj__tpu]})') for
            pddoj__tpu in range(len(arg_names))]
        kobc__fwxz = f"def impl({', '.join(arg_names)}):\n"
        kobc__fwxz += f'   if {arg_names[i]} is None:\n'
        kobc__fwxz += f"      return {func_name}({', '.join(ulzj__ciy)})\n"
        kobc__fwxz += f'   else:\n'
        kobc__fwxz += f"      return {func_name}({', '.join(ndjv__xvfn)})"
    xoa__eprq = {}
    exec(kobc__fwxz, {'bodo': bodo, 'numba': numba}, xoa__eprq)
    wfkzd__nmixc = xoa__eprq['impl']
    return wfkzd__nmixc


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
    gcn__nvm = is_valid_string_arg(arg)
    qupy__ngv = is_valid_binary_arg(arg)
    if gcn__nvm or qupy__ngv:
        return gcn__nvm
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
    ctns__qhpz = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            ctns__qhpz.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            ctns__qhpz.append(arg_types[i].data)
        else:
            ctns__qhpz.append(arg_types[i])
    if len(ctns__qhpz) == 0:
        return bodo.none
    elif len(ctns__qhpz) == 1:
        if bodo.utils.utils.is_array_typ(ctns__qhpz[0]):
            return bodo.utils.typing.to_nullable_type(ctns__qhpz[0])
        elif ctns__qhpz[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(ctns__qhpz[0]))
    else:
        iki__dmda = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                iki__dmda.append(ctns__qhpz[i].dtype)
            elif ctns__qhpz[i] == bodo.none:
                pass
            else:
                iki__dmda.append(ctns__qhpz[i])
        if len(iki__dmda) == 0:
            return bodo.none
        akhv__ejcuo, bip__atke = bodo.utils.typing.get_common_scalar_dtype(
            iki__dmda)
        if not bip__atke:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(akhv__ejcuo))


def vectorized_sol(args, scalar_fn, dtype, manual_coercion=False):
    ybg__swp = -1
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            ybg__swp = len(arg)
            break
    if ybg__swp == -1:
        return dtype(scalar_fn(*args)) if manual_coercion else scalar_fn(*args)
    vfwo__vblo = []
    for arg in args:
        if isinstance(arg, (pd.core.arrays.base.ExtensionArray, pd.Series,
            np.ndarray, pa.Array)):
            vfwo__vblo.append(arg)
        else:
            vfwo__vblo.append([arg] * ybg__swp)
    if manual_coercion:
        return pd.Series([dtype(scalar_fn(*wgmr__cyvbi)) for wgmr__cyvbi in
            zip(*vfwo__vblo)])
    else:
        return pd.Series([scalar_fn(*wgmr__cyvbi) for wgmr__cyvbi in zip(*
            vfwo__vblo)], dtype=dtype)
