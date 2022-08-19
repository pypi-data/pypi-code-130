""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.time_ext import TimeType
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_str_arr_type, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        xqx__fgqqd = lhs.data if isinstance(lhs, SeriesType) else lhs
        lokk__tpl = rhs.data if isinstance(rhs, SeriesType) else rhs
        if xqx__fgqqd in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and lokk__tpl.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            xqx__fgqqd = lokk__tpl.dtype
        elif lokk__tpl in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and xqx__fgqqd.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            lokk__tpl = xqx__fgqqd.dtype
        gwmk__exzp = xqx__fgqqd, lokk__tpl
        wdnr__xmkw = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            tjudy__zdhl = self.context.resolve_function_type(self.key,
                gwmk__exzp, {}).return_type
        except Exception as exdgt__cldr:
            raise BodoError(wdnr__xmkw)
        if is_overload_bool(tjudy__zdhl):
            raise BodoError(wdnr__xmkw)
        hfqs__tbnkp = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        vku__hbgqj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        tzmo__gsj = types.bool_
        ghxhh__vcwxm = SeriesType(tzmo__gsj, tjudy__zdhl, hfqs__tbnkp,
            vku__hbgqj)
        return ghxhh__vcwxm(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        jbj__swyqc = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if jbj__swyqc is None:
            jbj__swyqc = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, jbj__swyqc, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        xqx__fgqqd = lhs.data if isinstance(lhs, SeriesType) else lhs
        lokk__tpl = rhs.data if isinstance(rhs, SeriesType) else rhs
        gwmk__exzp = xqx__fgqqd, lokk__tpl
        wdnr__xmkw = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            tjudy__zdhl = self.context.resolve_function_type(self.key,
                gwmk__exzp, {}).return_type
        except Exception as rtdyz__eradj:
            raise BodoError(wdnr__xmkw)
        hfqs__tbnkp = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        vku__hbgqj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        tzmo__gsj = tjudy__zdhl.dtype
        ghxhh__vcwxm = SeriesType(tzmo__gsj, tjudy__zdhl, hfqs__tbnkp,
            vku__hbgqj)
        return ghxhh__vcwxm(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        jbj__swyqc = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if jbj__swyqc is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                jbj__swyqc = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, jbj__swyqc, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (is_str_arr_type(lhs) or types.unliteral(
            lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
                f'{op} operator')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
                f'{op} operator')
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            jbj__swyqc = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return jbj__swyqc(lhs, rhs)
        if is_str_arr_type(lhs) or is_str_arr_type(rhs):
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if isinstance(lhs, TimeType) and isinstance(rhs, TimeType):
            return bodo.hiframes.time_ext.create_cmp_op_overload(op)(lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            jbj__swyqc = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return jbj__swyqc(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    fxy__flkr = lhs == datetime_timedelta_type and rhs == datetime_date_type
    peg__vktg = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return fxy__flkr or peg__vktg


def add_timestamp(lhs, rhs):
    yvv__thf = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    gdw__cbkep = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return yvv__thf or gdw__cbkep


def add_datetime_and_timedeltas(lhs, rhs):
    nfm__sbab = [datetime_timedelta_type, pd_timedelta_type]
    moskc__vqr = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    duq__ewn = lhs in nfm__sbab and rhs in nfm__sbab
    uoom__zabm = (lhs == datetime_datetime_type and rhs in nfm__sbab or rhs ==
        datetime_datetime_type and lhs in nfm__sbab)
    return duq__ewn or uoom__zabm


def mul_string_arr_and_int(lhs, rhs):
    lokk__tpl = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    xqx__fgqqd = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return lokk__tpl or xqx__fgqqd


def mul_timedelta_and_int(lhs, rhs):
    fxy__flkr = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    peg__vktg = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return fxy__flkr or peg__vktg


def mul_date_offset_and_int(lhs, rhs):
    vrs__amam = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    watm__oupv = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return vrs__amam or watm__oupv


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    cdsiy__jcgwj = [datetime_datetime_type, pd_timestamp_type,
        datetime_date_type]
    brqf__jnje = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in brqf__jnje and lhs in cdsiy__jcgwj


def sub_dt_index_and_timestamp(lhs, rhs):
    ncsh__ujtco = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    gssu__jlv = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return ncsh__ujtco or gssu__jlv


def sub_dt_or_td(lhs, rhs):
    qskfo__xaj = lhs == datetime_date_type and rhs == datetime_timedelta_type
    rpplo__ikqdy = lhs == datetime_date_type and rhs == datetime_date_type
    thd__zlfh = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return qskfo__xaj or rpplo__ikqdy or thd__zlfh


def sub_datetime_and_timedeltas(lhs, rhs):
    wawc__bjzxv = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    yach__cuco = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return wawc__bjzxv or yach__cuco


def div_timedelta_and_int(lhs, rhs):
    duq__ewn = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    hiyp__mly = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return duq__ewn or hiyp__mly


def div_datetime_timedelta(lhs, rhs):
    duq__ewn = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    hiyp__mly = lhs == datetime_timedelta_type and rhs == types.int64
    return duq__ewn or hiyp__mly


def mod_timedeltas(lhs, rhs):
    shli__iwfcw = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    bmv__ldcs = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return shli__iwfcw or bmv__ldcs


def cmp_dt_index_to_string(lhs, rhs):
    ncsh__ujtco = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    gssu__jlv = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return ncsh__ujtco or gssu__jlv


def cmp_timestamp_or_date(lhs, rhs):
    eva__oda = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    mdseg__kbt = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    knhbx__xrfaa = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    xiwcc__iljl = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    pdyg__muft = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return eva__oda or mdseg__kbt or knhbx__xrfaa or xiwcc__iljl or pdyg__muft


def cmp_timeseries(lhs, rhs):
    wmil__fkm = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    qgxt__gez = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    kbb__ndkt = wmil__fkm or qgxt__gez
    eyw__daxk = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    iei__szqsb = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    bkt__cma = eyw__daxk or iei__szqsb
    return kbb__ndkt or bkt__cma


def cmp_timedeltas(lhs, rhs):
    duq__ewn = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in duq__ewn and rhs in duq__ewn


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    nowmx__vraxr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return nowmx__vraxr


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    gyvyf__cpkrq = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    qcjs__tcfjn = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    zfdxx__tpdi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    ueqov__vxijt = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return gyvyf__cpkrq or qcjs__tcfjn or zfdxx__tpdi or ueqov__vxijt


def args_td_and_int_array(lhs, rhs):
    wlei__ajqgj = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    slsa__hlol = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return wlei__ajqgj and slsa__hlol


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        peg__vktg = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        fxy__flkr = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        tkbr__ydt = peg__vktg or fxy__flkr
        xsmr__dhx = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        eso__zfubv = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        jrglu__jya = xsmr__dhx or eso__zfubv
        ncrp__eun = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        gfnc__xgz = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        grsnt__momer = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ppdp__pkka = ncrp__eun or gfnc__xgz or grsnt__momer
        pxsqf__qwl = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        hxm__uww = isinstance(lhs, tys) or isinstance(rhs, tys)
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (tkbr__ydt or jrglu__jya or ppdp__pkka or pxsqf__qwl or
            hxm__uww or myf__secv)
    if op == operator.pow:
        zrr__ylx = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        ldqs__tpxys = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        grsnt__momer = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return zrr__ylx or ldqs__tpxys or grsnt__momer or myf__secv
    if op == operator.floordiv:
        gfnc__xgz = lhs in types.real_domain and rhs in types.real_domain
        ncrp__eun = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        hof__ohsp = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        duq__ewn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return gfnc__xgz or ncrp__eun or hof__ohsp or duq__ewn or myf__secv
    if op == operator.truediv:
        ovv__tsjvf = lhs in machine_ints and rhs in machine_ints
        gfnc__xgz = lhs in types.real_domain and rhs in types.real_domain
        grsnt__momer = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        ncrp__eun = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        hof__ohsp = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        gap__coevy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        duq__ewn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (ovv__tsjvf or gfnc__xgz or grsnt__momer or ncrp__eun or
            hof__ohsp or gap__coevy or duq__ewn or myf__secv)
    if op == operator.mod:
        ovv__tsjvf = lhs in machine_ints and rhs in machine_ints
        gfnc__xgz = lhs in types.real_domain and rhs in types.real_domain
        ncrp__eun = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        hof__ohsp = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return ovv__tsjvf or gfnc__xgz or ncrp__eun or hof__ohsp or myf__secv
    if op == operator.add or op == operator.sub:
        tkbr__ydt = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        oafj__ntzs = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        lgh__tlui = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        zbt__qcgdm = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        ncrp__eun = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        gfnc__xgz = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        grsnt__momer = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ppdp__pkka = ncrp__eun or gfnc__xgz or grsnt__momer
        myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        hlykz__egsis = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        pxsqf__qwl = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        zpril__zyo = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        bfkf__kqykh = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        mwrz__jprg = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        kyeh__guo = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        nfox__gkyt = zpril__zyo or bfkf__kqykh or mwrz__jprg or kyeh__guo
        jrglu__jya = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        rjho__jmzy = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        vah__acb = jrglu__jya or rjho__jmzy
        qxx__vqq = lhs == types.NPTimedelta and rhs == types.NPDatetime
        kfvg__myqr = (hlykz__egsis or pxsqf__qwl or nfox__gkyt or vah__acb or
            qxx__vqq)
        ztjaf__gbzg = op == operator.add and kfvg__myqr
        return (tkbr__ydt or oafj__ntzs or lgh__tlui or zbt__qcgdm or
            ppdp__pkka or myf__secv or ztjaf__gbzg)


def cmp_op_supported_by_numba(lhs, rhs):
    myf__secv = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    pxsqf__qwl = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    tkbr__ydt = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    rqy__ylr = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types.
        NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    jrglu__jya = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    hlykz__egsis = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    zbt__qcgdm = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    ppdp__pkka = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    oxt__rdwgg = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    lmmoh__gvhzf = isinstance(lhs, types.NoneType) or isinstance(rhs, types
        .NoneType)
    bngge__vgguf = isinstance(lhs, types.DictType) and isinstance(rhs,
        types.DictType)
    vjlss__nylr = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    vrfji__ansln = isinstance(lhs, types.Literal) and isinstance(rhs, types
        .Literal)
    return (pxsqf__qwl or tkbr__ydt or rqy__ylr or jrglu__jya or
        hlykz__egsis or zbt__qcgdm or ppdp__pkka or oxt__rdwgg or
        lmmoh__gvhzf or bngge__vgguf or myf__secv or vjlss__nylr or
        vrfji__ansln)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        ecwi__ybogz = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(ecwi__ybogz)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        ecwi__ybogz = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(ecwi__ybogz)


install_arith_ops()
