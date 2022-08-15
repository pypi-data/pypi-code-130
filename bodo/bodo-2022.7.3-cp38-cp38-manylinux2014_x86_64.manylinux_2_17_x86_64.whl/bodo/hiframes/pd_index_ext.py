import datetime
import operator
import warnings
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_nan, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        if isinstance(val.dtype, pd.core.arrays.integer._IntegerDtype):
            lddat__llxv = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(lddat__llxv)
        else:
            dtype = types.int64
        return NumericIndexType(dtype, get_val_type_maybe_str_literal(val.
            name), IntegerArrayType(dtype))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def tzval(self):
        return self.data.tz if isinstance(self.data, bodo.DatetimeArrayType
            ) else None

    def copy(self):
        return DatetimeIndexType(self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.hiframes.
            pd_timestamp_ext.PandasTimestampType(self.tzval))

    @property
    def pandas_type_name(self):
        return self.data.dtype.type_name

    @property
    def numpy_type_name(self):
        return str(self.data.dtype)


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    if isinstance(val.dtype, pd.DatetimeTZDtype):
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name),
            DatetimeArrayType(val.tz))
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    vnmhx__bwhoc = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()'
        )
    check_unsupported_args('copy', hxn__ahoao, idx_cpy_arg_defaults, fn_str
        =vnmhx__bwhoc, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    vka__ntf = c.pyapi.import_module_noblock(kznj__aivka)
    fjusn__ghtei = numba.core.cgutils.create_struct_proxy(typ)(c.context, c
        .builder, val)
    c.context.nrt.incref(c.builder, typ.data, fjusn__ghtei.data)
    szpo__avn = c.pyapi.from_native_value(typ.data, fjusn__ghtei.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, fjusn__ghtei.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, fjusn__ghtei.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([szpo__avn])
    yik__fdu = c.pyapi.object_getattr_string(vka__ntf, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', wznej__seg)])
    tmzaj__sft = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(szpo__avn)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(vka__ntf)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tmzaj__sft


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        ruq__gouh = c.pyapi.object_getattr_string(val, 'array')
    else:
        ruq__gouh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, ruq__gouh).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    dtype = _dt_index_data_typ.dtype
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    yxrqk__zjhq.dict = lmjkd__poij
    c.pyapi.decref(ruq__gouh)
    c.pyapi.decref(wznej__seg)
    return NativeValue(yxrqk__zjhq._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xzd__vzykw, msgn__ancn = args
        fjusn__ghtei = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        fjusn__ghtei.data = xzd__vzykw
        fjusn__ghtei.name = msgn__ancn
        context.nrt.incref(builder, signature.args[0], xzd__vzykw)
        context.nrt.incref(builder, signature.args[1], msgn__ancn)
        dtype = _dt_index_data_typ.dtype
        fjusn__ghtei.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return fjusn__ghtei._getvalue()
    bntd__qpeqm = DatetimeIndexType(name, data)
    sig = signature(bntd__qpeqm, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    hor__avfi = args[0]
    if equiv_set.has_shape(hor__avfi):
        return ArrayAnalysis.AnalyzeResult(shape=hor__avfi, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    poway__ibk = 'def impl(dti):\n'
    poway__ibk += '    numba.parfors.parfor.init_prange()\n'
    poway__ibk += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    poway__ibk += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    poway__ibk += '    n = len(A)\n'
    poway__ibk += '    S = np.empty(n, np.int64)\n'
    poway__ibk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    poway__ibk += '        val = A[i]\n'
    poway__ibk += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        poway__ibk += '        S[i] = ts.' + field + '()\n'
    else:
        poway__ibk += '        S[i] = ts.' + field + '\n'
    poway__ibk += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ckmj__kjn = {}
    exec(poway__ibk, {'numba': numba, 'np': np, 'bodo': bodo}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        krvk__rnydh = len(A)
        S = np.empty(krvk__rnydh, np.bool_)
        for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
            val = A[i]
            wqmgd__iyxbq = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(wqmgd__iyxbq
                .year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        krvk__rnydh = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            krvk__rnydh)
        for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
            val = A[i]
            wqmgd__iyxbq = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(wqmgd__iyxbq.year, wqmgd__iyxbq.month,
                wqmgd__iyxbq.day)
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        jpzd__htzzz = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(jpzd__htzzz)):
            if not bodo.libs.array_kernels.isna(jpzd__htzzz, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jpzd__htzzz[i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        jpzd__htzzz = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(jpzd__htzzz)):
            if not bodo.libs.array_kernels.isna(jpzd__htzzz, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jpzd__htzzz[i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):

    def impl(A, tz):
        return init_datetime_index(A._data.tz_convert(tz), A._name)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.DatetimeIndex()')
    hjrrj__ovyrw = dict(freq=freq, tz=tz, normalize=normalize, closed=
        closed, ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst,
        dtype=dtype, copy=copy)
    kpv__dvo = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        mgcs__blobc = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(mgcs__blobc)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        jaxan__gxdh = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            jpzd__htzzz = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            krvk__rnydh = len(jpzd__htzzz)
            S = np.empty(krvk__rnydh, jaxan__gxdh)
            aon__dvx = rhs.value
            for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jpzd__htzzz[i]) - aon__dvx)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        jaxan__gxdh = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            jpzd__htzzz = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            krvk__rnydh = len(jpzd__htzzz)
            S = np.empty(krvk__rnydh, jaxan__gxdh)
            aon__dvx = lhs.value
            for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    aon__dvx - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(jpzd__htzzz[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    nng__kikxl = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    poway__ibk = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        poway__ibk += '  dt_index, _str = lhs, rhs\n'
        wtoa__jzr = 'arr[i] {} other'.format(nng__kikxl)
    else:
        poway__ibk += '  dt_index, _str = rhs, lhs\n'
        wtoa__jzr = 'other {} arr[i]'.format(nng__kikxl)
    poway__ibk += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    poway__ibk += '  l = len(arr)\n'
    poway__ibk += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    poway__ibk += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    poway__ibk += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    poway__ibk += '    S[i] = {}\n'.format(wtoa__jzr)
    poway__ibk += '  return S\n'
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'numba': numba, 'np': np}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.Index()')
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    if not is_overload_none(dtype):
        jvgf__vscp = parse_dtype(dtype, 'pandas.Index')
        ziso__fanuu = False
    else:
        jvgf__vscp = getattr(data, 'dtype', None)
        ziso__fanuu = True
    if isinstance(jvgf__vscp, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or jvgf__vscp == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or jvgf__vscp == types.NPTimedelta('ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(jvgf__vscp, (types.Integer, types.Float, types.Boolean)):
            if ziso__fanuu:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    mgcs__blobc = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        mgcs__blobc, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    mgcs__blobc = bodo.utils.conversion.coerce_to_array(data)
                    vwl__ufifx = bodo.utils.conversion.fix_arr_dtype(
                        mgcs__blobc, jvgf__vscp)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        vwl__ufifx, name)
        elif jvgf__vscp in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                kbl__zqz = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = kbl__zqz[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                kbl__zqz = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                unkc__osjfu = kbl__zqz[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    unkc__osjfu, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            ehs__ggzc = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(ehs__ggzc[ind])
        return impl

    def impl(I, ind):
        ehs__ggzc = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        unkc__osjfu = ehs__ggzc[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(unkc__osjfu,
            name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            ugsqn__vay = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = ugsqn__vay[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            ugsqn__vay = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            unkc__osjfu = ugsqn__vay[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(
                unkc__osjfu, name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    xcu__vatu = False
    mbj__ozuf = False
    if closed is None:
        xcu__vatu = True
        mbj__ozuf = True
    elif closed == 'left':
        xcu__vatu = True
    elif closed == 'right':
        mbj__ozuf = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return xcu__vatu, mbj__ozuf


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, inline='always')
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    hjrrj__ovyrw = dict(tz=tz, normalize=normalize, closed=closed)
    kpv__dvo = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    ttjkl__hbl = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        ttjkl__hbl = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    poway__ibk = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    poway__ibk += ttjkl__hbl
    if is_overload_none(start):
        poway__ibk += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        poway__ibk += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        poway__ibk += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        poway__ibk += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        poway__ibk += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            poway__ibk += '  b = start_t.value\n'
            poway__ibk += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            poway__ibk += '  b = start_t.value\n'
            poway__ibk += '  addend = np.int64(periods) * np.int64(stride)\n'
            poway__ibk += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            poway__ibk += '  e = end_t.value + stride\n'
            poway__ibk += '  addend = np.int64(periods) * np.int64(-stride)\n'
            poway__ibk += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        poway__ibk += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        poway__ibk += '  delta = end_t.value - start_t.value\n'
        poway__ibk += '  step = delta / (periods - 1)\n'
        poway__ibk += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        poway__ibk += '  arr1 *= step\n'
        poway__ibk += '  arr1 += start_t.value\n'
        poway__ibk += '  arr = arr1.astype(np.int64)\n'
        poway__ibk += '  arr[-1] = end_t.value\n'
    poway__ibk += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    poway__ibk += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'np': np, 'pd': pd}, ckmj__kjn)
    f = ckmj__kjn['f']
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        muq__yar = pd.Timedelta('1 day')
        if start is not None:
            muq__yar = pd.Timedelta(start)
        qgg__ahj = pd.Timedelta('1 day')
        if end is not None:
            qgg__ahj = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        xcu__vatu, mbj__ozuf = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            czz__fzq = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = muq__yar.value
                mdah__afk = b + (qgg__ahj.value - b
                    ) // czz__fzq * czz__fzq + czz__fzq // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = muq__yar.value
                cxy__hzy = np.int64(periods) * np.int64(czz__fzq)
                mdah__afk = np.int64(b) + cxy__hzy
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                mdah__afk = qgg__ahj.value + czz__fzq
                cxy__hzy = np.int64(periods) * np.int64(-czz__fzq)
                b = np.int64(mdah__afk) + cxy__hzy
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            bhzz__dljo = np.arange(b, mdah__afk, czz__fzq, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            vnon__kjcxv = qgg__ahj.value - muq__yar.value
            step = vnon__kjcxv / (periods - 1)
            lagnq__hplr = np.arange(0, periods, 1, np.float64)
            lagnq__hplr *= step
            lagnq__hplr += muq__yar.value
            bhzz__dljo = lagnq__hplr.astype(np.int64)
            bhzz__dljo[-1] = qgg__ahj.value
        if not xcu__vatu and len(bhzz__dljo) and bhzz__dljo[0
            ] == muq__yar.value:
            bhzz__dljo = bhzz__dljo[1:]
        if not mbj__ozuf and len(bhzz__dljo) and bhzz__dljo[-1
            ] == qgg__ahj.value:
            bhzz__dljo = bhzz__dljo[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(bhzz__dljo)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    xicdx__ijvwb = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        krvk__rnydh = len(A)
        gpsz__uhu = bodo.libs.int_arr_ext.alloc_int_array(krvk__rnydh, np.
            uint32)
        qjo__cdby = bodo.libs.int_arr_ext.alloc_int_array(krvk__rnydh, np.
            uint32)
        tnun__vbvj = bodo.libs.int_arr_ext.alloc_int_array(krvk__rnydh, np.
            uint32)
        for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(gpsz__uhu, i)
                bodo.libs.array_kernels.setna(qjo__cdby, i)
                bodo.libs.array_kernels.setna(tnun__vbvj, i)
                continue
            gpsz__uhu[i], qjo__cdby[i], tnun__vbvj[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((gpsz__uhu,
            qjo__cdby, tnun__vbvj), idx, xicdx__ijvwb)
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.pd_timedelta_type
            )

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', _timedelta_index_data_typ), ('name', fe_type
            .name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, opq__pukph)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    vka__ntf = c.pyapi.import_module_noblock(kznj__aivka)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    szpo__avn = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([szpo__avn])
    kws = c.pyapi.dict_pack([('name', wznej__seg)])
    yik__fdu = c.pyapi.object_getattr_string(vka__ntf, 'TimedeltaIndex')
    tmzaj__sft = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(szpo__avn)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(vka__ntf)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tmzaj__sft


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    abn__lxaut = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, abn__lxaut).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(abn__lxaut)
    c.pyapi.decref(wznej__seg)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    dtype = _timedelta_index_data_typ.dtype
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xzd__vzykw, msgn__ancn = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = xzd__vzykw
        timedelta_index.name = msgn__ancn
        context.nrt.incref(builder, signature.args[0], xzd__vzykw)
        context.nrt.incref(builder, signature.args[1], msgn__ancn)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    bntd__qpeqm = TimedeltaIndexType(name)
    sig = signature(bntd__qpeqm, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    vnmhx__bwhoc = idx_typ_to_format_str_map[TimedeltaIndexType].format(
        'copy()')
    check_unsupported_args('TimedeltaIndex.copy', hxn__ahoao,
        idx_cpy_arg_defaults, fn_str=vnmhx__bwhoc, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        krvk__rnydh = len(data)
        anoe__pamdh = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            anoe__pamdh = min(anoe__pamdh, val)
        ftl__smab = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            anoe__pamdh)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ftl__smab, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        krvk__rnydh = len(data)
        sxhx__zkg = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            sxhx__zkg = max(sxhx__zkg, val)
        ftl__smab = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            sxhx__zkg)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(ftl__smab, count)
    return impl


def gen_tdi_field_impl(field):
    poway__ibk = 'def impl(tdi):\n'
    poway__ibk += '    numba.parfors.parfor.init_prange()\n'
    poway__ibk += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    poway__ibk += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    poway__ibk += '    n = len(A)\n'
    poway__ibk += '    S = np.empty(n, np.int64)\n'
    poway__ibk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    poway__ibk += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        poway__ibk += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        poway__ibk += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        poway__ibk += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        poway__ibk += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    poway__ibk += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    ckmj__kjn = {}
    exec(poway__ibk, {'numba': numba, 'np': np, 'bodo': bodo}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    hjrrj__ovyrw = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    kpv__dvo = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        mgcs__blobc = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(mgcs__blobc)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name=f'RangeIndexType({name_typ})'
            )
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    vnmhx__bwhoc = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', hxn__ahoao,
        idx_cpy_arg_defaults, fn_str=vnmhx__bwhoc, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    mymmy__tbv = c.pyapi.import_module_noblock(kznj__aivka)
    xgz__lhzma = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    twyv__wnfr = c.pyapi.from_native_value(types.int64, xgz__lhzma.start, c
        .env_manager)
    gdcfy__ciwym = c.pyapi.from_native_value(types.int64, xgz__lhzma.stop,
        c.env_manager)
    dbhgs__alxp = c.pyapi.from_native_value(types.int64, xgz__lhzma.step, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, xgz__lhzma.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, xgz__lhzma.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([twyv__wnfr, gdcfy__ciwym, dbhgs__alxp])
    kws = c.pyapi.dict_pack([('name', wznej__seg)])
    yik__fdu = c.pyapi.object_getattr_string(mymmy__tbv, 'RangeIndex')
    pwlg__blt = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(twyv__wnfr)
    c.pyapi.decref(gdcfy__ciwym)
    c.pyapi.decref(dbhgs__alxp)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(mymmy__tbv)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return pwlg__blt


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    fre__rcfrl = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if fre__rcfrl:
            raise_bodo_error('Step must not be zero')
        mxfgu__rfc = cgutils.is_scalar_zero(builder, args[2])
        sfiu__fgz = context.get_python_api(builder)
        with builder.if_then(mxfgu__rfc):
            sfiu__fgz.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        xgz__lhzma = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        xgz__lhzma.start = args[0]
        xgz__lhzma.stop = args[1]
        xgz__lhzma.step = args[2]
        xgz__lhzma.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return xgz__lhzma._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, rhcwi__mqu = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    twyv__wnfr = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, twyv__wnfr).value
    gdcfy__ciwym = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, gdcfy__ciwym).value
    dbhgs__alxp = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, dbhgs__alxp).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(twyv__wnfr)
    c.pyapi.decref(gdcfy__ciwym)
    c.pyapi.decref(dbhgs__alxp)
    c.pyapi.decref(wznej__seg)
    xgz__lhzma = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xgz__lhzma.start = start
    xgz__lhzma.stop = stop
    xgz__lhzma.step = step
    xgz__lhzma.name = name
    return NativeValue(xgz__lhzma._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        xda__qzg = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(xda__qzg.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        xda__qzg = 'RangeIndex(...) must be called with integers'
        raise BodoError(xda__qzg)
    net__gwtn = 'start'
    nfp__bhjh = 'stop'
    mxtnj__yre = 'step'
    if is_overload_none(start):
        net__gwtn = '0'
    if is_overload_none(stop):
        nfp__bhjh = 'start'
        net__gwtn = '0'
    if is_overload_none(step):
        mxtnj__yre = '1'
    poway__ibk = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    poway__ibk += '  return init_range_index({}, {}, {}, name)\n'.format(
        net__gwtn, nfp__bhjh, mxtnj__yre)
    ckmj__kjn = {}
    exec(poway__ibk, {'init_range_index': init_range_index}, ckmj__kjn)
    kjhpd__acgng = ckmj__kjn['_pd_range_index_imp']
    return kjhpd__acgng


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                nizo__tymh = numba.cpython.unicode._normalize_slice(idx, len(I)
                    )
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * nizo__tymh.start
                stop = I._start + I._step * nizo__tymh.stop
                step = I._step * nizo__tymh.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    vnmhx__bwhoc = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', hxn__ahoao,
        idx_cpy_arg_defaults, fn_str=vnmhx__bwhoc, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xzd__vzykw, msgn__ancn, rhcwi__mqu = args
        zdo__ospmn = signature.return_type
        chge__zxvj = cgutils.create_struct_proxy(zdo__ospmn)(context, builder)
        chge__zxvj.data = xzd__vzykw
        chge__zxvj.name = msgn__ancn
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        chge__zxvj.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return chge__zxvj._getvalue()
    jyb__rjdh = get_overload_const_str(freq)
    bntd__qpeqm = PeriodIndexType(jyb__rjdh, name)
    sig = signature(bntd__qpeqm, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    mymmy__tbv = c.pyapi.import_module_noblock(kznj__aivka)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        yxrqk__zjhq.data)
    ruq__gouh = c.pyapi.from_native_value(bodo.IntegerArrayType(types.int64
        ), yxrqk__zjhq.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yxrqk__zjhq.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, yxrqk__zjhq.name,
        c.env_manager)
    ayan__fhgvf = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', ruq__gouh), ('name', wznej__seg),
        ('freq', ayan__fhgvf)])
    yik__fdu = c.pyapi.object_getattr_string(mymmy__tbv, 'PeriodIndex')
    pwlg__blt = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(ruq__gouh)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(ayan__fhgvf)
    c.pyapi.decref(mymmy__tbv)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return pwlg__blt


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    oak__mtsng = c.pyapi.object_getattr_string(val, 'asi8')
    oqap__pzmmx = c.pyapi.call_method(val, 'isna', ())
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    vka__ntf = c.pyapi.import_module_noblock(kznj__aivka)
    yxkw__juwbh = c.pyapi.object_getattr_string(vka__ntf, 'arrays')
    ruq__gouh = c.pyapi.call_method(yxkw__juwbh, 'IntegerArray', (
        oak__mtsng, oqap__pzmmx))
    data = c.pyapi.to_native_value(arr_typ, ruq__gouh).value
    c.pyapi.decref(oak__mtsng)
    c.pyapi.decref(oqap__pzmmx)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(vka__ntf)
    c.pyapi.decref(yxkw__juwbh)
    c.pyapi.decref(ruq__gouh)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(types.int64, types.int64), types.DictType(types.int64,
        types.int64)(), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


class CategoricalIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, self.dtype.elem_type)


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        carep__objos = get_categories_int_type(fe_type.data.dtype)
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(carep__objos, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            opq__pukph)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    vka__ntf = c.pyapi.import_module_noblock(kznj__aivka)
    oorz__mcfzg = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, oorz__mcfzg.data)
    szpo__avn = c.pyapi.from_native_value(typ.data, oorz__mcfzg.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, oorz__mcfzg.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, oorz__mcfzg.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([szpo__avn])
    kws = c.pyapi.dict_pack([('name', wznej__seg)])
    yik__fdu = c.pyapi.object_getattr_string(vka__ntf, 'CategoricalIndex')
    tmzaj__sft = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(szpo__avn)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(vka__ntf)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tmzaj__sft


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    abn__lxaut = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, abn__lxaut).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(abn__lxaut)
    c.pyapi.decref(wznej__seg)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        xzd__vzykw, msgn__ancn = args
        oorz__mcfzg = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        oorz__mcfzg.data = xzd__vzykw
        oorz__mcfzg.name = msgn__ancn
        context.nrt.incref(builder, signature.args[0], xzd__vzykw)
        context.nrt.incref(builder, signature.args[1], msgn__ancn)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        oorz__mcfzg.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return oorz__mcfzg._getvalue()
    bntd__qpeqm = CategoricalIndexType(data, name)
    sig = signature(bntd__qpeqm, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    vnmhx__bwhoc = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', hxn__ahoao,
        idx_cpy_arg_defaults, fn_str=vnmhx__bwhoc, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, opq__pukph)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    vka__ntf = c.pyapi.import_module_noblock(kznj__aivka)
    flpcb__pgd = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, flpcb__pgd.data)
    szpo__avn = c.pyapi.from_native_value(typ.data, flpcb__pgd.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, flpcb__pgd.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, flpcb__pgd.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([szpo__avn])
    kws = c.pyapi.dict_pack([('name', wznej__seg)])
    yik__fdu = c.pyapi.object_getattr_string(vka__ntf, 'IntervalIndex')
    tmzaj__sft = c.pyapi.call(yik__fdu, args, kws)
    c.pyapi.decref(szpo__avn)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(vka__ntf)
    c.pyapi.decref(yik__fdu)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tmzaj__sft


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    abn__lxaut = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, abn__lxaut).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(abn__lxaut)
    c.pyapi.decref(wznej__seg)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xzd__vzykw, msgn__ancn = args
        flpcb__pgd = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        flpcb__pgd.data = xzd__vzykw
        flpcb__pgd.name = msgn__ancn
        context.nrt.incref(builder, signature.args[0], xzd__vzykw)
        context.nrt.incref(builder, signature.args[1], msgn__ancn)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        flpcb__pgd.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return flpcb__pgd._getvalue()
    bntd__qpeqm = IntervalIndexType(data, name)
    sig = signature(bntd__qpeqm, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    Int64Index = pd.Int64Index
    UInt64Index = pd.UInt64Index
    Float64Index = pd.Float64Index


@typeof_impl.register(Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    vnmhx__bwhoc = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hxn__ahoao, idx_cpy_arg_defaults,
        fn_str=vnmhx__bwhoc, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    mymmy__tbv = c.pyapi.import_module_noblock(kznj__aivka)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, yxrqk__zjhq.data)
    ruq__gouh = c.pyapi.from_native_value(typ.data, yxrqk__zjhq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yxrqk__zjhq.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, yxrqk__zjhq.name,
        c.env_manager)
    rrbd__ond = c.pyapi.make_none()
    awk__dxpva = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    pwlg__blt = c.pyapi.call_method(mymmy__tbv, 'Index', (ruq__gouh,
        rrbd__ond, awk__dxpva, wznej__seg))
    c.pyapi.decref(ruq__gouh)
    c.pyapi.decref(rrbd__ond)
    c.pyapi.decref(awk__dxpva)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(mymmy__tbv)
    c.context.nrt.decref(c.builder, typ, val)
    return pwlg__blt


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        zdo__ospmn = signature.return_type
        yxrqk__zjhq = cgutils.create_struct_proxy(zdo__ospmn)(context, builder)
        yxrqk__zjhq.data = args[0]
        yxrqk__zjhq.name = args[1]
        context.nrt.incref(builder, zdo__ospmn.data, args[0])
        context.nrt.incref(builder, zdo__ospmn.name_typ, args[1])
        dtype = zdo__ospmn.dtype
        yxrqk__zjhq.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return yxrqk__zjhq._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    abn__lxaut = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, abn__lxaut).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(abn__lxaut)
    c.pyapi.decref(wznej__seg)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    dtype = typ.dtype
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        cmd__zsze = dict(dtype=dtype)
        zuese__orwb = dict(dtype=None)
        check_unsupported_args(func_str, cmd__zsze, zuese__orwb,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                mgcs__blobc = bodo.utils.conversion.coerce_to_ndarray(data)
                fonin__fha = bodo.utils.conversion.fix_arr_dtype(mgcs__blobc,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(fonin__fha
                    , name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                mgcs__blobc = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    mgcs__blobc = mgcs__blobc.copy()
                fonin__fha = bodo.utils.conversion.fix_arr_dtype(mgcs__blobc,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(fonin__fha
                    , name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((Int64Index, 'pandas.Int64Index',
        np.int64), (UInt64Index, 'pandas.UInt64Index', np.uint64), (
        Float64Index, 'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type if data_typ is None else data_typ
        super(StringIndexType, self).__init__(name=
            f'StringIndexType({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ, self.data)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        assert data_typ is None or data_typ == binary_array_type, 'data_typ must be binary_array_type'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    fset__tbxz = typ.data
    scalar_type = typ.data.dtype
    abn__lxaut = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(fset__tbxz, abn__lxaut).value
    wznej__seg = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, wznej__seg).value
    c.pyapi.decref(abn__lxaut)
    c.pyapi.decref(wznej__seg)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yxrqk__zjhq.data = data
    yxrqk__zjhq.name = name
    acxy__grosf, lmjkd__poij = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(scalar_type, types.int64), types.DictType(scalar_type,
        types.int64)(), [])
    yxrqk__zjhq.dict = lmjkd__poij
    return NativeValue(yxrqk__zjhq._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    fset__tbxz = typ.data
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    mymmy__tbv = c.pyapi.import_module_noblock(kznj__aivka)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, fset__tbxz, yxrqk__zjhq.data)
    ruq__gouh = c.pyapi.from_native_value(fset__tbxz, yxrqk__zjhq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yxrqk__zjhq.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, yxrqk__zjhq.name,
        c.env_manager)
    rrbd__ond = c.pyapi.make_none()
    awk__dxpva = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    pwlg__blt = c.pyapi.call_method(mymmy__tbv, 'Index', (ruq__gouh,
        rrbd__ond, awk__dxpva, wznej__seg))
    c.pyapi.decref(ruq__gouh)
    c.pyapi.decref(rrbd__ond)
    c.pyapi.decref(awk__dxpva)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(mymmy__tbv)
    c.context.nrt.decref(c.builder, typ, val)
    return pwlg__blt


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    jteh__fdfd = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, jteh__fdfd


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        zyu__jrz = 'bytes_type'
    else:
        zyu__jrz = 'string_type'
    poway__ibk = 'def impl(context, builder, signature, args):\n'
    poway__ibk += '    assert len(args) == 2\n'
    poway__ibk += '    index_typ = signature.return_type\n'
    poway__ibk += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    poway__ibk += '    index_val.data = args[0]\n'
    poway__ibk += '    index_val.name = args[1]\n'
    poway__ibk += '    # increase refcount of stored values\n'
    poway__ibk += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    poway__ibk += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    poway__ibk += '    # create empty dict for get_loc hashmap\n'
    poway__ibk += '    index_val.dict = context.compile_internal(\n'
    poway__ibk += '       builder,\n'
    poway__ibk += (
        f'       lambda: numba.typed.Dict.empty({zyu__jrz}, types.int64),\n')
    poway__ibk += f'        types.DictType({zyu__jrz}, types.int64)(), [],)\n'
    poway__ibk += '    return index_val._getvalue()\n'
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    vnmhx__bwhoc = idx_typ_to_format_str_map[typ].format('copy()')
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hxn__ahoao, idx_cpy_arg_defaults,
        fn_str=vnmhx__bwhoc, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if is_str_arr_type(arr_typ):
        return StringIndexType(name_typ, arr_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.DatetimeArrayType):
        return DatetimeIndexType(name_typ, arr_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


def _verify_setop_compatible(func_name, I, other):
    if not is_pd_index_type(other) and not isinstance(other, (SeriesType,
        types.Array)):
        raise BodoError(
            f'pd.Index.{func_name}(): unsupported type for argument other: {other}'
            )
    zxy__lyh = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    rme__zcm = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if zxy__lyh != rme__zcm:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {zxy__lyh} and {rme__zcm}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    hjrrj__ovyrw = dict(sort=sort)
    ubb__clve = dict(sort=None)
    check_unsupported_args('Index.union', hjrrj__ovyrw, ubb__clve,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    mlkxd__cpbf = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        yhpf__qfetd = bodo.utils.conversion.coerce_to_array(I)
        tzk__hzr = bodo.utils.conversion.coerce_to_array(other)
        vrt__ijktq = bodo.libs.array_kernels.concat([yhpf__qfetd, tzk__hzr])
        pug__qgolt = bodo.libs.array_kernels.unique(vrt__ijktq)
        return mlkxd__cpbf(pug__qgolt, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    hjrrj__ovyrw = dict(sort=sort)
    ubb__clve = dict(sort=None)
    check_unsupported_args('Index.intersection', hjrrj__ovyrw, ubb__clve,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    mlkxd__cpbf = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        yhpf__qfetd = bodo.utils.conversion.coerce_to_array(I)
        tzk__hzr = bodo.utils.conversion.coerce_to_array(other)
        lahy__grpmh = bodo.libs.array_kernels.unique(yhpf__qfetd)
        kvkxe__dhxp = bodo.libs.array_kernels.unique(tzk__hzr)
        vrt__ijktq = bodo.libs.array_kernels.concat([lahy__grpmh, kvkxe__dhxp])
        qkob__harz = pd.Series(vrt__ijktq).sort_values().values
        ycmd__cdcd = bodo.libs.array_kernels.intersection_mask(qkob__harz)
        return mlkxd__cpbf(qkob__harz[ycmd__cdcd], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    hjrrj__ovyrw = dict(sort=sort)
    ubb__clve = dict(sort=None)
    check_unsupported_args('Index.difference', hjrrj__ovyrw, ubb__clve,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    mlkxd__cpbf = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        yhpf__qfetd = bodo.utils.conversion.coerce_to_array(I)
        tzk__hzr = bodo.utils.conversion.coerce_to_array(other)
        lahy__grpmh = bodo.libs.array_kernels.unique(yhpf__qfetd)
        kvkxe__dhxp = bodo.libs.array_kernels.unique(tzk__hzr)
        ycmd__cdcd = np.empty(len(lahy__grpmh), np.bool_)
        bodo.libs.array.array_isin(ycmd__cdcd, lahy__grpmh, kvkxe__dhxp, False)
        return mlkxd__cpbf(lahy__grpmh[~ycmd__cdcd], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    hjrrj__ovyrw = dict(result_name=result_name, sort=sort)
    ubb__clve = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', hjrrj__ovyrw,
        ubb__clve, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    mlkxd__cpbf = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        yhpf__qfetd = bodo.utils.conversion.coerce_to_array(I)
        tzk__hzr = bodo.utils.conversion.coerce_to_array(other)
        lahy__grpmh = bodo.libs.array_kernels.unique(yhpf__qfetd)
        kvkxe__dhxp = bodo.libs.array_kernels.unique(tzk__hzr)
        qmoh__jhjsb = np.empty(len(lahy__grpmh), np.bool_)
        vczpx__enh = np.empty(len(kvkxe__dhxp), np.bool_)
        bodo.libs.array.array_isin(qmoh__jhjsb, lahy__grpmh, kvkxe__dhxp, False
            )
        bodo.libs.array.array_isin(vczpx__enh, kvkxe__dhxp, lahy__grpmh, False)
        ggap__ksos = bodo.libs.array_kernels.concat([lahy__grpmh[~
            qmoh__jhjsb], kvkxe__dhxp[~vczpx__enh]])
        return mlkxd__cpbf(ggap__ksos, None)
    return impl


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    hjrrj__ovyrw = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value
        )
    ubb__clve = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', hjrrj__ovyrw, ubb__clve,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(bhzz__dljo)):
                    if not bodo.libs.array_kernels.isna(bhzz__dljo, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(bhzz__dljo.dtype, bhzz__dljo[i])
                            )
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(bhzz__dljo)):
                    if not bodo.libs.array_kernels.isna(bhzz__dljo, i):
                        val = bhzz__dljo[i]
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)
    if isinstance(I, CategoricalIndexType):

        def impl(I, val):
            key = bodo.utils.conversion.unbox_if_timestamp(val)
            if not is_null_value(I._dict):
                _init_engine(I, False)
                bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
                fcgum__klk = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(bhzz__dljo.dtype, key))
                return fcgum__klk in I._dict
            else:
                xda__qzg = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(xda__qzg)
                bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(bhzz__dljo)):
                    if not bodo.libs.array_kernels.isna(bhzz__dljo, i):
                        if bhzz__dljo[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            xda__qzg = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(xda__qzg)
            bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(bhzz__dljo)):
                if not bodo.libs.array_kernels.isna(bhzz__dljo, i):
                    if bhzz__dljo[i] == key:
                        ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    hjrrj__ovyrw = dict(method=method, tolerance=tolerance)
    kpv__dvo = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.get_loc')
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            xda__qzg = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(xda__qzg)
            bhzz__dljo = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(bhzz__dljo)):
                if bhzz__dljo[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        whyh__eba = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                krvk__rnydh = len(I)
                nfio__flp = np.empty(krvk__rnydh, np.bool_)
                for i in numba.parfors.parfor.internal_prange(krvk__rnydh):
                    nfio__flp[i] = not whyh__eba
                return nfio__flp
            return impl
        poway__ibk = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if whyh__eba else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        ckmj__kjn = {}
        exec(poway__ibk, {'bodo': bodo, 'np': np, 'numba': numba}, ckmj__kjn)
        impl = ckmj__kjn['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for isq__gpgfx in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(isq__gpgfx, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I, 'Index.values'
        )
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload(len, no_unliteral=True)
def overload_multi_index_len(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I)[0])


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(MultiIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)[0]),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_increasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(bhzz__dljo, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_decreasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(bhzz__dljo, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        nfio__flp = bodo.libs.array_kernels.duplicated((bhzz__dljo,))
        return nfio__flp
    return impl


@overload_method(NumericIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'any', no_unliteral=True, inline='always')
def overload_index_any(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) > 0 and (I._start != 0 or len(I) > 1)
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(NumericIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'all', no_unliteral=True, inline='always')
def overload_index_all(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) == 0 or I._step > 0 and (I._start > 0 or I._stop <= 0
                ) or I._step < 0 and (I._start < 0 or I._stop >= 0
                ) or I._start % I._step != 0
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    hjrrj__ovyrw = dict(keep=keep)
    kpv__dvo = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    poway__ibk = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        poway__ibk += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        poway__ibk += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    hor__avfi = args[0]
    if isinstance(self.typemap[hor__avfi.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(hor__avfi):
        return ArrayAnalysis.AnalyzeResult(shape=hor__avfi, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    hjrrj__ovyrw = dict(na_action=na_action)
    ohz__mmpx = dict(na_action=None)
    check_unsupported_args('Index.map', hjrrj__ovyrw, ohz__mmpx,
        package_name='pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    jwkq__lbnpb = numba.core.registry.cpu_target.typing_context
    zmmcg__ubtr = numba.core.registry.cpu_target.target_context
    try:
        uziup__ggkr = get_const_func_output_type(mapper, (dtype,), {},
            jwkq__lbnpb, zmmcg__ubtr)
    except Exception as mdah__afk:
        raise_bodo_error(get_udf_error_msg('Index.map()', mdah__afk))
    hpry__rrkj = get_udf_out_arr_type(uziup__ggkr)
    func = get_overload_const_func(mapper, None)
    poway__ibk = 'def f(I, mapper, na_action=None):\n'
    poway__ibk += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    poway__ibk += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    poway__ibk += '  numba.parfors.parfor.init_prange()\n'
    poway__ibk += '  n = len(A)\n'
    poway__ibk += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    poway__ibk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    poway__ibk += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    poway__ibk += '    v = map_func(t2)\n'
    poway__ibk += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    poway__ibk += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    zipg__wkx = bodo.compiler.udf_jit(func)
    ckmj__kjn = {}
    exec(poway__ibk, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': zipg__wkx, '_arr_typ': hpry__rrkj, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'data_arr_type': hpry__rrkj.dtype
        }, ckmj__kjn)
    f = ckmj__kjn['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    adag__pntmd, osdll__mda = sig.args
    if adag__pntmd != osdll__mda:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    adag__pntmd, osdll__mda = sig.args
    if adag__pntmd != osdll__mda:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            poway__ibk = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(lhs)
"""
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                poway__ibk += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                poway__ibk += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            ckmj__kjn = {}
            exec(poway__ibk, {'bodo': bodo, 'op': op}, ckmj__kjn)
            impl = ckmj__kjn['impl']
            return impl
        if is_index_type(rhs):
            poway__ibk = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(rhs)
"""
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                poway__ibk += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                poway__ibk += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            ckmj__kjn = {}
            exec(poway__ibk, {'bodo': bodo, 'op': op}, ckmj__kjn)
            impl = ckmj__kjn['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    bhzz__dljo = bodo.utils.conversion.coerce_to_array(data)
                    lblo__wjiv = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    nfio__flp = op(bhzz__dljo, lblo__wjiv)
                    return nfio__flp
                return impl3
            count = len(lhs.data.types)
            poway__ibk = 'def f(lhs, rhs):\n'
            poway__ibk += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            ckmj__kjn = {}
            exec(poway__ibk, {'op': op, 'np': np}, ckmj__kjn)
            impl = ckmj__kjn['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    bhzz__dljo = bodo.utils.conversion.coerce_to_array(data)
                    lblo__wjiv = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    nfio__flp = op(lblo__wjiv, bhzz__dljo)
                    return nfio__flp
                return impl4
            count = len(rhs.data.types)
            poway__ibk = 'def f(lhs, rhs):\n'
            poway__ibk += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            ckmj__kjn = {}
            exec(poway__ibk, {'op': op, 'np': np}, ckmj__kjn)
            impl = ckmj__kjn['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


@numba.njit(no_cpython_wrapper=True)
def range_index_to_numeric(I):
    return init_numeric_index(np.arange(I._start, I._stop, I._step), bodo.
        hiframes.pd_index_ext.get_index_name(I))


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opq__pukph = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, opq__pukph)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    vnmhx__bwhoc = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    hxn__ahoao = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hxn__ahoao, idx_cpy_arg_defaults,
        fn_str=vnmhx__bwhoc, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    kznj__aivka = c.context.insert_const_string(c.builder.module, 'pandas')
    mymmy__tbv = c.pyapi.import_module_noblock(kznj__aivka)
    yxrqk__zjhq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, yxrqk__zjhq.data)
    ruq__gouh = c.pyapi.from_native_value(typ.data, yxrqk__zjhq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yxrqk__zjhq.name)
    wznej__seg = c.pyapi.from_native_value(typ.name_typ, yxrqk__zjhq.name,
        c.env_manager)
    rrbd__ond = c.pyapi.make_none()
    awk__dxpva = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    pwlg__blt = c.pyapi.call_method(mymmy__tbv, 'Index', (ruq__gouh,
        rrbd__ond, awk__dxpva, wznej__seg))
    c.pyapi.decref(ruq__gouh)
    c.pyapi.decref(rrbd__ond)
    c.pyapi.decref(awk__dxpva)
    c.pyapi.decref(wznej__seg)
    c.pyapi.decref(mymmy__tbv)
    c.context.nrt.decref(c.builder, typ, val)
    return pwlg__blt


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        zdo__ospmn = signature.return_type
        yxrqk__zjhq = cgutils.create_struct_proxy(zdo__ospmn)(context, builder)
        yxrqk__zjhq.data = args[0]
        yxrqk__zjhq.name = args[1]
        context.nrt.incref(builder, zdo__ospmn.data, args[0])
        context.nrt.incref(builder, zdo__ospmn.name_typ, args[1])
        return yxrqk__zjhq._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
@overload_attribute(MultiIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    elif isinstance(I, MultiIndexType):
        poway__ibk = 'def _impl_nbytes(I):\n'
        poway__ibk += '    total = 0\n'
        poway__ibk += '    data = I._data\n'
        for i in range(I.nlevels):
            poway__ibk += f'    total += data[{i}].nbytes\n'
        poway__ibk += '    return total\n'
        nubva__axxnu = {}
        exec(poway__ibk, {}, nubva__axxnu)
        return nubva__axxnu['_impl_nbytes']
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'to_series', inline='always')
@overload_method(DatetimeIndexType, 'to_series', inline='always')
@overload_method(TimedeltaIndexType, 'to_series', inline='always')
@overload_method(RangeIndexType, 'to_series', inline='always')
@overload_method(StringIndexType, 'to_series', inline='always')
@overload_method(BinaryIndexType, 'to_series', inline='always')
@overload_method(CategoricalIndexType, 'to_series', inline='always')
def overload_index_to_series(I, index=None, name=None):
    if not (is_overload_constant_str(name) or is_overload_constant_int(name
        ) or is_overload_none(name)):
        raise_bodo_error(
            f'Index.to_series(): only constant string/int are supported for argument name'
            )
    if is_overload_none(name):
        qylw__ldopw = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        qylw__ldopw = 'name'
    poway__ibk = 'def impl(I, index=None, name=None):\n'
    poway__ibk += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        poway__ibk += '    new_index = I\n'
    elif is_pd_index_type(index):
        poway__ibk += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        poway__ibk += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        poway__ibk += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        poway__ibk += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        poway__ibk += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        poway__ibk += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        poway__ibk += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    poway__ibk += f'    new_name = {qylw__ldopw}\n'
    poway__ibk += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'np': np}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(NumericIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'to_frame', inline='always', no_unliteral=True
    )
@overload_method(StringIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(BinaryIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(CategoricalIndexType, 'to_frame', inline='always',
    no_unliteral=True)
def overload_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        uhi__cnbw = 'I'
    elif is_overload_false(index):
        uhi__cnbw = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    poway__ibk = 'def impl(I, index=True, name=None):\n'
    poway__ibk += '    data = bodo.utils.conversion.index_to_array(I)\n'
    poway__ibk += f'    new_index = {uhi__cnbw}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        quku__pkltr = ColNamesMetaType((0,))
    elif is_overload_none(name):
        quku__pkltr = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        quku__pkltr = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        quku__pkltr = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    poway__ibk += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        quku__pkltr}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        uhi__cnbw = 'I'
    elif is_overload_false(index):
        uhi__cnbw = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    poway__ibk = 'def impl(I, index=True, name=None):\n'
    poway__ibk += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    poway__ibk += f'    new_index = {uhi__cnbw}\n'
    vcddr__epyo = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * vcddr__epyo:
        quku__pkltr = ColNamesMetaType(tuple(range(vcddr__epyo)))
    elif is_overload_none(name):
        quku__pkltr = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if vcddr__epyo != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {vcddr__epyo} names, not {len(names)}'
                )
        if all(is_overload_constant_str(ahfhm__iooi) or
            is_overload_constant_int(ahfhm__iooi) for ahfhm__iooi in names):
            quku__pkltr = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    poway__ibk += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    ckmj__kjn = {}
    exec(poway__ibk, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        quku__pkltr}, ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(NumericIndexType, 'to_numpy', inline='always')
@overload_method(DatetimeIndexType, 'to_numpy', inline='always')
@overload_method(TimedeltaIndexType, 'to_numpy', inline='always')
@overload_method(RangeIndexType, 'to_numpy', inline='always')
@overload_method(StringIndexType, 'to_numpy', inline='always')
@overload_method(BinaryIndexType, 'to_numpy', inline='always')
@overload_method(CategoricalIndexType, 'to_numpy', inline='always')
@overload_method(IntervalIndexType, 'to_numpy', inline='always')
def overload_index_to_numpy(I, dtype=None, copy=False, na_value=None):
    hjrrj__ovyrw = dict(dtype=dtype, na_value=na_value)
    kpv__dvo = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(copy):
        raise_bodo_error('Index.to_numpy(): copy argument must be a boolean')
    if isinstance(I, RangeIndexType):

        def impl(I, dtype=None, copy=False, na_value=None):
            return np.arange(I._start, I._stop, I._step)
        return impl
    if is_overload_true(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I).copy()
        return impl
    if is_overload_false(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I)
        return impl

    def impl(I, dtype=None, copy=False, na_value=None):
        data = bodo.hiframes.pd_index_ext.get_index_data(I)
        return data.copy() if copy else data
    return impl


@overload_method(NumericIndexType, 'to_list', inline='always')
@overload_method(RangeIndexType, 'to_list', inline='always')
@overload_method(StringIndexType, 'to_list', inline='always')
@overload_method(BinaryIndexType, 'to_list', inline='always')
@overload_method(CategoricalIndexType, 'to_list', inline='always')
@overload_method(DatetimeIndexType, 'to_list', inline='always')
@overload_method(TimedeltaIndexType, 'to_list', inline='always')
@overload_method(NumericIndexType, 'tolist', inline='always')
@overload_method(RangeIndexType, 'tolist', inline='always')
@overload_method(StringIndexType, 'tolist', inline='always')
@overload_method(BinaryIndexType, 'tolist', inline='always')
@overload_method(CategoricalIndexType, 'tolist', inline='always')
@overload_method(DatetimeIndexType, 'tolist', inline='always')
@overload_method(TimedeltaIndexType, 'tolist', inline='always')
def overload_index_to_list(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            qodsi__see = list()
            for i in range(I._start, I._stop, I.step):
                qodsi__see.append(i)
            return qodsi__see
        return impl

    def impl(I):
        qodsi__see = list()
        for i in range(len(I)):
            qodsi__see.append(I[i])
        return qodsi__see
    return impl


@overload_attribute(NumericIndexType, 'T')
@overload_attribute(DatetimeIndexType, 'T')
@overload_attribute(TimedeltaIndexType, 'T')
@overload_attribute(RangeIndexType, 'T')
@overload_attribute(StringIndexType, 'T')
@overload_attribute(BinaryIndexType, 'T')
@overload_attribute(CategoricalIndexType, 'T')
@overload_attribute(PeriodIndexType, 'T')
@overload_attribute(MultiIndexType, 'T')
@overload_attribute(IntervalIndexType, 'T')
def overload_T(I):
    return lambda I: I


@overload_attribute(NumericIndexType, 'size')
@overload_attribute(DatetimeIndexType, 'size')
@overload_attribute(TimedeltaIndexType, 'size')
@overload_attribute(RangeIndexType, 'size')
@overload_attribute(StringIndexType, 'size')
@overload_attribute(BinaryIndexType, 'size')
@overload_attribute(CategoricalIndexType, 'size')
@overload_attribute(PeriodIndexType, 'size')
@overload_attribute(MultiIndexType, 'size')
@overload_attribute(IntervalIndexType, 'size')
def overload_size(I):
    return lambda I: len(I)


@overload_attribute(NumericIndexType, 'ndim')
@overload_attribute(DatetimeIndexType, 'ndim')
@overload_attribute(TimedeltaIndexType, 'ndim')
@overload_attribute(RangeIndexType, 'ndim')
@overload_attribute(StringIndexType, 'ndim')
@overload_attribute(BinaryIndexType, 'ndim')
@overload_attribute(CategoricalIndexType, 'ndim')
@overload_attribute(PeriodIndexType, 'ndim')
@overload_attribute(MultiIndexType, 'ndim')
@overload_attribute(IntervalIndexType, 'ndim')
def overload_ndim(I):
    return lambda I: 1


@overload_attribute(NumericIndexType, 'nlevels')
@overload_attribute(DatetimeIndexType, 'nlevels')
@overload_attribute(TimedeltaIndexType, 'nlevels')
@overload_attribute(RangeIndexType, 'nlevels')
@overload_attribute(StringIndexType, 'nlevels')
@overload_attribute(BinaryIndexType, 'nlevels')
@overload_attribute(CategoricalIndexType, 'nlevels')
@overload_attribute(PeriodIndexType, 'nlevels')
@overload_attribute(MultiIndexType, 'nlevels')
@overload_attribute(IntervalIndexType, 'nlevels')
def overload_nlevels(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(I._data)
    return lambda I: 1


@overload_attribute(NumericIndexType, 'empty')
@overload_attribute(DatetimeIndexType, 'empty')
@overload_attribute(TimedeltaIndexType, 'empty')
@overload_attribute(RangeIndexType, 'empty')
@overload_attribute(StringIndexType, 'empty')
@overload_attribute(BinaryIndexType, 'empty')
@overload_attribute(CategoricalIndexType, 'empty')
@overload_attribute(PeriodIndexType, 'empty')
@overload_attribute(MultiIndexType, 'empty')
@overload_attribute(IntervalIndexType, 'empty')
def overload_empty(I):
    return lambda I: len(I) == 0


@overload_attribute(NumericIndexType, 'is_all_dates')
@overload_attribute(DatetimeIndexType, 'is_all_dates')
@overload_attribute(TimedeltaIndexType, 'is_all_dates')
@overload_attribute(RangeIndexType, 'is_all_dates')
@overload_attribute(StringIndexType, 'is_all_dates')
@overload_attribute(BinaryIndexType, 'is_all_dates')
@overload_attribute(CategoricalIndexType, 'is_all_dates')
@overload_attribute(PeriodIndexType, 'is_all_dates')
@overload_attribute(MultiIndexType, 'is_all_dates')
@overload_attribute(IntervalIndexType, 'is_all_dates')
def overload_is_all_dates(I):
    if isinstance(I, (DatetimeIndexType, TimedeltaIndexType, PeriodIndexType)):
        return lambda I: True
    else:
        return lambda I: False


@overload_attribute(NumericIndexType, 'inferred_type')
@overload_attribute(DatetimeIndexType, 'inferred_type')
@overload_attribute(TimedeltaIndexType, 'inferred_type')
@overload_attribute(RangeIndexType, 'inferred_type')
@overload_attribute(StringIndexType, 'inferred_type')
@overload_attribute(BinaryIndexType, 'inferred_type')
@overload_attribute(CategoricalIndexType, 'inferred_type')
@overload_attribute(PeriodIndexType, 'inferred_type')
@overload_attribute(MultiIndexType, 'inferred_type')
@overload_attribute(IntervalIndexType, 'inferred_type')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Integer):
            return lambda I: 'integer'
        elif isinstance(I.dtype, types.Float):
            return lambda I: 'floating'
        elif isinstance(I.dtype, types.Boolean):
            return lambda I: 'boolean'
        return
    if isinstance(I, StringIndexType):

        def impl(I):
            if len(I._data) == 0:
                return 'empty'
            return 'string'
        return impl
    baptv__kqf = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = baptv__kqf[type(I)]
    return lambda I: inferred_type


@overload_attribute(NumericIndexType, 'dtype')
@overload_attribute(DatetimeIndexType, 'dtype')
@overload_attribute(TimedeltaIndexType, 'dtype')
@overload_attribute(RangeIndexType, 'dtype')
@overload_attribute(StringIndexType, 'dtype')
@overload_attribute(BinaryIndexType, 'dtype')
@overload_attribute(CategoricalIndexType, 'dtype')
@overload_attribute(MultiIndexType, 'dtype')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Boolean):
            return lambda I: np.dtype('O')
        dtype = I.dtype
        return lambda I: dtype
    if isinstance(I, CategoricalIndexType):
        dtype = bodo.utils.utils.create_categorical_type(I.dtype.categories,
            I.data, I.dtype.ordered)
        return lambda I: dtype
    spl__ecjs = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = spl__ecjs[type(I)]
    return lambda I: dtype


@overload_attribute(NumericIndexType, 'names')
@overload_attribute(DatetimeIndexType, 'names')
@overload_attribute(TimedeltaIndexType, 'names')
@overload_attribute(RangeIndexType, 'names')
@overload_attribute(StringIndexType, 'names')
@overload_attribute(BinaryIndexType, 'names')
@overload_attribute(CategoricalIndexType, 'names')
@overload_attribute(IntervalIndexType, 'names')
@overload_attribute(PeriodIndexType, 'names')
@overload_attribute(MultiIndexType, 'names')
def overload_names(I):
    if isinstance(I, MultiIndexType):
        return lambda I: I._names
    return lambda I: (I._name,)


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index_from_index(I, name)


def init_index_from_index(I, name):
    gudsw__tmec = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in gudsw__tmec:
        init_func = gudsw__tmec[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


def get_index_constructor(I):
    tnavs__zuu = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in tnavs__zuu:
        return tnavs__zuu[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            azb__pgdw = len(I)
            if azb__pgdw == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (azb__pgdw - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(bhzz__dljo)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            azb__pgdw = len(I)
            if azb__pgdw == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (azb__pgdw - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(bhzz__dljo)
    return impl


@overload_method(NumericIndexType, 'argmin', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(PeriodIndexType, 'argmin', no_unliteral=True, inline='always')
def overload_index_argmin(I, axis=0, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmin()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step < 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmin(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(bhzz__dljo)))
        return bodo.libs.array_ops.array_op_idxmin(bhzz__dljo, index)
    return impl


@overload_method(NumericIndexType, 'argmax', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argmax', no_unliteral=True, inline='always')
def overload_index_argmax(I, axis=0, skipna=True):
    hjrrj__ovyrw = dict(axis=axis, skipna=skipna)
    kpv__dvo = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmax()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step > 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmax(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(bhzz__dljo))
        return bodo.libs.array_ops.array_op_idxmax(bhzz__dljo, index)
    return impl


@overload_method(NumericIndexType, 'unique', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(IntervalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'unique', no_unliteral=True, inline=
    'always')
def overload_index_unique(I):
    mlkxd__cpbf = get_index_constructor(I)

    def impl(I):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        ztka__geozy = bodo.libs.array_kernels.unique(bhzz__dljo)
        return mlkxd__cpbf(ztka__geozy, name)
    return impl


@overload_method(RangeIndexType, 'unique', no_unliteral=True, inline='always')
def overload_range_index_unique(I):

    def impl(I):
        return I.copy()
    return impl


@overload_method(NumericIndexType, 'nunique', inline='always')
@overload_method(BinaryIndexType, 'nunique', inline='always')
@overload_method(StringIndexType, 'nunique', inline='always')
@overload_method(CategoricalIndexType, 'nunique', inline='always')
@overload_method(DatetimeIndexType, 'nunique', inline='always')
@overload_method(TimedeltaIndexType, 'nunique', inline='always')
@overload_method(PeriodIndexType, 'nunique', inline='always')
def overload_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        krvk__rnydh = bodo.libs.array_kernels.nunique(bhzz__dljo, dropna)
        return krvk__rnydh
    return impl


@overload_method(RangeIndexType, 'nunique', inline='always')
def overload_range_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        start = I._start
        stop = I._stop
        step = I._step
        return max(0, -(-(stop - start) // step))
    return impl


@overload_method(NumericIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(TimedeltaIndexType, 'isin', no_unliteral=True, inline='always'
    )
def overload_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            ztk__ovqc = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            krvk__rnydh = len(A)
            nfio__flp = np.empty(krvk__rnydh, np.bool_)
            bodo.libs.array.array_isin(nfio__flp, A, ztk__ovqc, False)
            return nfio__flp
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        nfio__flp = bodo.libs.array_ops.array_op_isin(A, values)
        return nfio__flp
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            ztk__ovqc = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            krvk__rnydh = len(A)
            nfio__flp = np.empty(krvk__rnydh, np.bool_)
            bodo.libs.array.array_isin(nfio__flp, A, ztk__ovqc, False)
            return nfio__flp
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        nfio__flp = bodo.libs.array_ops.array_op_isin(A, values)
        return nfio__flp
    return impl


@register_jitable
def order_range(I, ascending):
    step = I._step
    if ascending == (step > 0):
        return I.copy()
    else:
        start = I._start
        stop = I._stop
        name = get_index_name(I)
        azb__pgdw = len(I)
        zom__vfwhf = start + step * (azb__pgdw - 1)
        wvs__kpgt = zom__vfwhf - step * azb__pgdw
        return init_range_index(zom__vfwhf, wvs__kpgt, -step, name)


@overload_method(NumericIndexType, 'sort_values', no_unliteral=True, inline
    ='always')
@overload_method(BinaryIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(RangeIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
def overload_index_sort_values(I, return_indexer=False, ascending=True,
    na_position='last', key=None):
    hjrrj__ovyrw = dict(return_indexer=return_indexer, key=key)
    kpv__dvo = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Index.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Index.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    if isinstance(I, RangeIndexType):

        def impl(I, return_indexer=False, ascending=True, na_position=
            'last', key=None):
            return order_range(I, ascending)
        return impl
    mlkxd__cpbf = get_index_constructor(I)
    kovw__smaoh = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(bhzz__dljo), 1, None)
        zvop__udep = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            bhzz__dljo,), index, kovw__smaoh)
        yfxqf__pznac = zvop__udep.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        nfio__flp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            yfxqf__pznac, 0)
        return mlkxd__cpbf(nfio__flp, name)
    return impl


@overload_method(NumericIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(BinaryIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(CategoricalIndexType, 'argsort', no_unliteral=True, inline
    ='always')
@overload_method(DatetimeIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(RangeIndexType, 'argsort', no_unliteral=True, inline='always')
def overload_index_argsort(I, axis=0, kind='quicksort', order=None):
    hjrrj__ovyrw = dict(axis=axis, kind=kind, order=order)
    kpv__dvo = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        bhzz__dljo = bodo.hiframes.pd_index_ext.get_index_data(I)
        nfio__flp = bodo.hiframes.series_impl.argsort(bhzz__dljo)
        return nfio__flp
    return impl


@overload_method(NumericIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'where', no_unliteral=True, inline='always'
    )
@overload_method(TimedeltaIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'where', no_unliteral=True, inline='always')
def overload_index_where(I, cond, other=np.nan):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.where()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('where',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        apxdn__ilgh = 'None'
    else:
        apxdn__ilgh = 'other'
    poway__ibk = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        poway__ibk += '  arr = np.arange(I._start, I._stop, I._step)\n'
        mlkxd__cpbf = 'init_numeric_index'
    else:
        poway__ibk += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    poway__ibk += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    poway__ibk += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {apxdn__ilgh})\n'
        )
    poway__ibk += f'  return constructor(out_arr, name)\n'
    ckmj__kjn = {}
    mlkxd__cpbf = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(poway__ibk, {'bodo': bodo, 'np': np, 'constructor': mlkxd__cpbf},
        ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(NumericIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(DatetimeIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'putmask', no_unliteral=True, inline
    ='always')
@overload_method(RangeIndexType, 'putmask', no_unliteral=True, inline='always')
def overload_index_putmask(I, cond, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.putmask()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.putmask()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('putmask',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        apxdn__ilgh = 'None'
    else:
        apxdn__ilgh = 'other'
    poway__ibk = 'def impl(I, cond, other):\n'
    poway__ibk += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        poway__ibk += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        poway__ibk += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    poway__ibk += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    poway__ibk += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {apxdn__ilgh})\n'
        )
    poway__ibk += f'  return constructor(out_arr, name)\n'
    ckmj__kjn = {}
    mlkxd__cpbf = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(poway__ibk, {'bodo': bodo, 'np': np, 'constructor': mlkxd__cpbf},
        ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(NumericIndexType, 'repeat', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'repeat', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'repeat', no_unliteral=True, inline='always')
def overload_index_repeat(I, repeats, axis=None):
    hjrrj__ovyrw = dict(axis=axis)
    kpv__dvo = dict(axis=None)
    check_unsupported_args('Index.repeat', hjrrj__ovyrw, kpv__dvo,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    poway__ibk = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        poway__ibk += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        poway__ibk += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        poway__ibk += (
            '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    poway__ibk += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    poway__ibk += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    poway__ibk += '    return constructor(out_arr, name)'
    ckmj__kjn = {}
    mlkxd__cpbf = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(poway__ibk, {'bodo': bodo, 'np': np, 'constructor': mlkxd__cpbf},
        ckmj__kjn)
    impl = ckmj__kjn['impl']
    return impl


@overload_method(NumericIndexType, 'is_integer', inline='always')
def overload_is_integer_numeric(I):
    truth = isinstance(I.dtype, types.Integer)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_floating', inline='always')
def overload_is_floating_numeric(I):
    truth = isinstance(I.dtype, types.Float)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_boolean', inline='always')
def overload_is_boolean_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_numeric', inline='always')
def overload_is_numeric_numeric(I):
    truth = not isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_object', inline='always')
def overload_is_object_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(StringIndexType, 'is_object', inline='always')
@overload_method(BinaryIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_numeric', inline='always')
@overload_method(RangeIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_object', inline='always')
def overload_is_methods_true(I):
    return lambda I: True


@overload_method(NumericIndexType, 'is_categorical', inline='always')
@overload_method(NumericIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_boolean', inline='always')
@overload_method(StringIndexType, 'is_floating', inline='always')
@overload_method(StringIndexType, 'is_categorical', inline='always')
@overload_method(StringIndexType, 'is_integer', inline='always')
@overload_method(StringIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_numeric', inline='always')
@overload_method(BinaryIndexType, 'is_boolean', inline='always')
@overload_method(BinaryIndexType, 'is_floating', inline='always')
@overload_method(BinaryIndexType, 'is_categorical', inline='always')
@overload_method(BinaryIndexType, 'is_integer', inline='always')
@overload_method(BinaryIndexType, 'is_interval', inline='always')
@overload_method(BinaryIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_boolean', inline='always')
@overload_method(DatetimeIndexType, 'is_floating', inline='always')
@overload_method(DatetimeIndexType, 'is_categorical', inline='always')
@overload_method(DatetimeIndexType, 'is_integer', inline='always')
@overload_method(DatetimeIndexType, 'is_interval', inline='always')
@overload_method(DatetimeIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_object', inline='always')
@overload_method(TimedeltaIndexType, 'is_boolean', inline='always')
@overload_method(TimedeltaIndexType, 'is_floating', inline='always')
@overload_method(TimedeltaIndexType, 'is_categorical', inline='always')
@overload_method(TimedeltaIndexType, 'is_integer', inline='always')
@overload_method(TimedeltaIndexType, 'is_interval', inline='always')
@overload_method(TimedeltaIndexType, 'is_numeric', inline='always')
@overload_method(TimedeltaIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_boolean', inline='always')
@overload_method(RangeIndexType, 'is_floating', inline='always')
@overload_method(RangeIndexType, 'is_categorical', inline='always')
@overload_method(RangeIndexType, 'is_interval', inline='always')
@overload_method(RangeIndexType, 'is_object', inline='always')
@overload_method(IntervalIndexType, 'is_boolean', inline='always')
@overload_method(IntervalIndexType, 'is_floating', inline='always')
@overload_method(IntervalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_integer', inline='always')
@overload_method(IntervalIndexType, 'is_numeric', inline='always')
@overload_method(IntervalIndexType, 'is_object', inline='always')
@overload_method(CategoricalIndexType, 'is_boolean', inline='always')
@overload_method(CategoricalIndexType, 'is_floating', inline='always')
@overload_method(CategoricalIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_interval', inline='always')
@overload_method(CategoricalIndexType, 'is_numeric', inline='always')
@overload_method(CategoricalIndexType, 'is_object', inline='always')
@overload_method(PeriodIndexType, 'is_boolean', inline='always')
@overload_method(PeriodIndexType, 'is_floating', inline='always')
@overload_method(PeriodIndexType, 'is_categorical', inline='always')
@overload_method(PeriodIndexType, 'is_integer', inline='always')
@overload_method(PeriodIndexType, 'is_interval', inline='always')
@overload_method(PeriodIndexType, 'is_numeric', inline='always')
@overload_method(PeriodIndexType, 'is_object', inline='always')
@overload_method(MultiIndexType, 'is_boolean', inline='always')
@overload_method(MultiIndexType, 'is_floating', inline='always')
@overload_method(MultiIndexType, 'is_categorical', inline='always')
@overload_method(MultiIndexType, 'is_integer', inline='always')
@overload_method(MultiIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_numeric', inline='always')
def overload_is_methods_false(I):
    return lambda I: False


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    if isinstance(ty.data, bodo.DatetimeArrayType):
        data = context.get_constant_generic(builder, ty.data, pyval.array)
    else:
        data = context.get_constant_generic(builder, types.Array(types.
            int64, 1, 'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    eeci__cvg = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, eeci__cvg])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    eeci__cvg = context.get_constant_null(types.DictType(types.int64, types
        .int64))
    return lir.Constant.literal_struct([data, name, eeci__cvg])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    eeci__cvg = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, eeci__cvg])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    fset__tbxz = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, fset__tbxz, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    eeci__cvg = context.get_constant_null(types.DictType(scalar_type, types
        .int64))
    return lir.Constant.literal_struct([data, name, eeci__cvg])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [oelv__nvve] = sig.args
    [index] = args
    rny__icgh = context.make_helper(builder, oelv__nvve, value=index)
    kuiru__tmn = context.make_helper(builder, sig.return_type)
    jffoj__xjfrr = cgutils.alloca_once_value(builder, rny__icgh.start)
    cyjyb__aiirl = context.get_constant(types.intp, 0)
    unz__luf = cgutils.alloca_once_value(builder, cyjyb__aiirl)
    kuiru__tmn.iter = jffoj__xjfrr
    kuiru__tmn.stop = rny__icgh.stop
    kuiru__tmn.step = rny__icgh.step
    kuiru__tmn.count = unz__luf
    zkco__micv = builder.sub(rny__icgh.stop, rny__icgh.start)
    twepx__apt = context.get_constant(types.intp, 1)
    mpv__rlqt = builder.icmp_signed('>', zkco__micv, cyjyb__aiirl)
    zzcb__eqy = builder.icmp_signed('>', rny__icgh.step, cyjyb__aiirl)
    wbnyj__ooxed = builder.not_(builder.xor(mpv__rlqt, zzcb__eqy))
    with builder.if_then(wbnyj__ooxed):
        kqnk__cdds = builder.srem(zkco__micv, rny__icgh.step)
        kqnk__cdds = builder.select(mpv__rlqt, kqnk__cdds, builder.neg(
            kqnk__cdds))
        qznot__uyd = builder.icmp_signed('>', kqnk__cdds, cyjyb__aiirl)
        wsc__mjlxl = builder.add(builder.sdiv(zkco__micv, rny__icgh.step),
            builder.select(qznot__uyd, twepx__apt, cyjyb__aiirl))
        builder.store(wsc__mjlxl, unz__luf)
    tmzaj__sft = kuiru__tmn._getvalue()
    wbvss__lzicu = impl_ret_new_ref(context, builder, sig.return_type,
        tmzaj__sft)
    return wbvss__lzicu


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(numba.np.arrayobj.getiter_array)


_install_index_getiter()
index_unsupported_methods = ['append', 'asof', 'asof_locs', 'astype',
    'delete', 'drop', 'droplevel', 'dropna', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert', 'is_',
    'is_mixed', 'is_type_compatible', 'item', 'join', 'memory_usage',
    'ravel', 'reindex', 'searchsorted', 'set_names', 'set_value', 'shift',
    'slice_indexer', 'slice_locs', 'sort', 'sortlevel', 'str',
    'to_flat_index', 'to_native_types', 'transpose', 'value_counts', 'view']
index_unsupported_atrs = ['array', 'asi8', 'has_duplicates', 'hasnans',
    'is_unique']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc', 'isin',
    'all', 'any', 'union', 'intersection', 'difference', 'symmetric_difference'
    ]
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing', 'dtype']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map',
    'isin', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_frame', 'to_list', 'tolist',
    'repeat', 'min', 'max']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map', 'isin',
    'unique', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_list', 'tolist', 'to_numpy',
    'repeat', 'min', 'max']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_localize', 'round', 'floor', 'ceil', 'to_period', 'to_perioddelta',
    'to_pydatetime', 'month_name', 'day_name', 'mean', 'indexer_at_time',
    'indexer_between', 'indexer_between_time', 'all', 'any']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean', 'all', 'any']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing', 'dtype']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp',
    'isin', 'unique', 'all', 'any', 'where', 'putmask', 'sort_values',
    'union', 'intersection', 'difference', 'symmetric_difference',
    'to_series', 'to_frame', 'to_numpy', 'to_list', 'tolist', 'repeat',
    'min', 'max']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_methods = ['min', 'max']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_methods = ['repeat', 'min', 'max']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for navx__cks in index_unsupported_methods:
        for jsylc__opm, typ in index_types:
            overload_method(typ, navx__cks, no_unliteral=True)(
                create_unsupported_overload(jsylc__opm.format(navx__cks +
                '()')))
    for ttj__xwefr in index_unsupported_atrs:
        for jsylc__opm, typ in index_types:
            overload_attribute(typ, ttj__xwefr, no_unliteral=True)(
                create_unsupported_overload(jsylc__opm.format(ttj__xwefr)))
    alci__gcza = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    ziz__lkawr = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, hdcr__bni in ziz__lkawr:
        jsylc__opm = idx_typ_to_format_str_map[typ]
        for yoxp__jcxpo in hdcr__bni:
            overload_method(typ, yoxp__jcxpo, no_unliteral=True)(
                create_unsupported_overload(jsylc__opm.format(yoxp__jcxpo +
                '()')))
    for typ, oef__pmv in alci__gcza:
        jsylc__opm = idx_typ_to_format_str_map[typ]
        for ttj__xwefr in oef__pmv:
            overload_attribute(typ, ttj__xwefr, no_unliteral=True)(
                create_unsupported_overload(jsylc__opm.format(ttj__xwefr)))


_install_index_unsupported()
