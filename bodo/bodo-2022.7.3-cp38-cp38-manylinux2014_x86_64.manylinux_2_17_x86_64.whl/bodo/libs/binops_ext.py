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
        gudq__xoy = lhs.data if isinstance(lhs, SeriesType) else lhs
        kbit__zis = rhs.data if isinstance(rhs, SeriesType) else rhs
        if gudq__xoy in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and kbit__zis.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            gudq__xoy = kbit__zis.dtype
        elif kbit__zis in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and gudq__xoy.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            kbit__zis = gudq__xoy.dtype
        xkog__durk = gudq__xoy, kbit__zis
        tblgt__njekr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            soi__tnq = self.context.resolve_function_type(self.key,
                xkog__durk, {}).return_type
        except Exception as iyb__uha:
            raise BodoError(tblgt__njekr)
        if is_overload_bool(soi__tnq):
            raise BodoError(tblgt__njekr)
        yfiix__zapyw = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        ubpp__uifa = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        uitfx__lzo = types.bool_
        fbqtm__trqco = SeriesType(uitfx__lzo, soi__tnq, yfiix__zapyw,
            ubpp__uifa)
        return fbqtm__trqco(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        par__lmu = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if par__lmu is None:
            par__lmu = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, par__lmu, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        gudq__xoy = lhs.data if isinstance(lhs, SeriesType) else lhs
        kbit__zis = rhs.data if isinstance(rhs, SeriesType) else rhs
        xkog__durk = gudq__xoy, kbit__zis
        tblgt__njekr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            soi__tnq = self.context.resolve_function_type(self.key,
                xkog__durk, {}).return_type
        except Exception as vunya__kxu:
            raise BodoError(tblgt__njekr)
        yfiix__zapyw = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        ubpp__uifa = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        uitfx__lzo = soi__tnq.dtype
        fbqtm__trqco = SeriesType(uitfx__lzo, soi__tnq, yfiix__zapyw,
            ubpp__uifa)
        return fbqtm__trqco(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        par__lmu = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if par__lmu is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                par__lmu = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, par__lmu, sig, args)
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
            par__lmu = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return par__lmu(lhs, rhs)
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
            par__lmu = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return par__lmu(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    tjdx__kuln = lhs == datetime_timedelta_type and rhs == datetime_date_type
    uyxf__vaong = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return tjdx__kuln or uyxf__vaong


def add_timestamp(lhs, rhs):
    dncwl__lagp = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    tuw__jca = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return dncwl__lagp or tuw__jca


def add_datetime_and_timedeltas(lhs, rhs):
    iupr__egbpq = [datetime_timedelta_type, pd_timedelta_type]
    mnk__hle = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    umgg__gng = lhs in iupr__egbpq and rhs in iupr__egbpq
    msgqe__kcfb = (lhs == datetime_datetime_type and rhs in iupr__egbpq or 
        rhs == datetime_datetime_type and lhs in iupr__egbpq)
    return umgg__gng or msgqe__kcfb


def mul_string_arr_and_int(lhs, rhs):
    kbit__zis = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    gudq__xoy = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return kbit__zis or gudq__xoy


def mul_timedelta_and_int(lhs, rhs):
    tjdx__kuln = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    uyxf__vaong = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return tjdx__kuln or uyxf__vaong


def mul_date_offset_and_int(lhs, rhs):
    fcjc__oynz = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    ibjl__lmq = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return fcjc__oynz or ibjl__lmq


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    pnfz__nbgt = [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ]
    ppk__anomj = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in ppk__anomj and lhs in pnfz__nbgt


def sub_dt_index_and_timestamp(lhs, rhs):
    orjnr__gecqc = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    rchjs__ksh = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return orjnr__gecqc or rchjs__ksh


def sub_dt_or_td(lhs, rhs):
    gsn__ioveq = lhs == datetime_date_type and rhs == datetime_timedelta_type
    cipp__ggg = lhs == datetime_date_type and rhs == datetime_date_type
    jlc__auzbs = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return gsn__ioveq or cipp__ggg or jlc__auzbs


def sub_datetime_and_timedeltas(lhs, rhs):
    vcpa__ifo = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    ddcb__wdjw = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return vcpa__ifo or ddcb__wdjw


def div_timedelta_and_int(lhs, rhs):
    umgg__gng = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    sry__dzmyu = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return umgg__gng or sry__dzmyu


def div_datetime_timedelta(lhs, rhs):
    umgg__gng = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    sry__dzmyu = lhs == datetime_timedelta_type and rhs == types.int64
    return umgg__gng or sry__dzmyu


def mod_timedeltas(lhs, rhs):
    nmi__iwk = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    bpl__uxatl = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return nmi__iwk or bpl__uxatl


def cmp_dt_index_to_string(lhs, rhs):
    orjnr__gecqc = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    rchjs__ksh = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return orjnr__gecqc or rchjs__ksh


def cmp_timestamp_or_date(lhs, rhs):
    kgldu__hkfj = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    prkp__eazq = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    xgr__wewrf = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    oab__jfakf = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    ywj__jtryt = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return kgldu__hkfj or prkp__eazq or xgr__wewrf or oab__jfakf or ywj__jtryt


def cmp_timeseries(lhs, rhs):
    vqes__kecr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    amb__kgeq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    mucn__kgff = vqes__kecr or amb__kgeq
    ukv__qde = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    gbiug__hwvbe = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    wctvr__ogtc = ukv__qde or gbiug__hwvbe
    return mucn__kgff or wctvr__ogtc


def cmp_timedeltas(lhs, rhs):
    umgg__gng = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in umgg__gng and rhs in umgg__gng


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    rnisd__dwssw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return rnisd__dwssw


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    gakxl__sfq = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    teh__flx = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    vssva__raix = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    rqwrk__hlxqq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return gakxl__sfq or teh__flx or vssva__raix or rqwrk__hlxqq


def args_td_and_int_array(lhs, rhs):
    yazx__pqew = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    zwyvu__otv = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return yazx__pqew and zwyvu__otv


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        uyxf__vaong = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        tjdx__kuln = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        hdc__oaj = uyxf__vaong or tjdx__kuln
        xjw__qjhaq = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        dsfg__lbkz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        wlk__yek = xjw__qjhaq or dsfg__lbkz
        kjee__qmhx = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        poetg__gnh = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        optx__ftix = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        liab__yvyjx = kjee__qmhx or poetg__gnh or optx__ftix
        gdlin__hptbi = isinstance(lhs, types.List) and isinstance(rhs,
            types.Integer) or isinstance(lhs, types.Integer) and isinstance(rhs
            , types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        xkxb__mqh = isinstance(lhs, tys) or isinstance(rhs, tys)
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (hdc__oaj or wlk__yek or liab__yvyjx or gdlin__hptbi or
            xkxb__mqh or gqz__gje)
    if op == operator.pow:
        zvz__jic = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        kpyr__hfmv = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        optx__ftix = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return zvz__jic or kpyr__hfmv or optx__ftix or gqz__gje
    if op == operator.floordiv:
        poetg__gnh = lhs in types.real_domain and rhs in types.real_domain
        kjee__qmhx = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        noi__dyrka = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        umgg__gng = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return poetg__gnh or kjee__qmhx or noi__dyrka or umgg__gng or gqz__gje
    if op == operator.truediv:
        rwvvt__yry = lhs in machine_ints and rhs in machine_ints
        poetg__gnh = lhs in types.real_domain and rhs in types.real_domain
        optx__ftix = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        kjee__qmhx = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        noi__dyrka = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        marog__uveso = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        umgg__gng = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (rwvvt__yry or poetg__gnh or optx__ftix or kjee__qmhx or
            noi__dyrka or marog__uveso or umgg__gng or gqz__gje)
    if op == operator.mod:
        rwvvt__yry = lhs in machine_ints and rhs in machine_ints
        poetg__gnh = lhs in types.real_domain and rhs in types.real_domain
        kjee__qmhx = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        noi__dyrka = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return rwvvt__yry or poetg__gnh or kjee__qmhx or noi__dyrka or gqz__gje
    if op == operator.add or op == operator.sub:
        hdc__oaj = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        hyao__sone = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        quv__dzv = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        sohn__ladd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        kjee__qmhx = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        poetg__gnh = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        optx__ftix = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        liab__yvyjx = kjee__qmhx or poetg__gnh or optx__ftix
        gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        nldz__zun = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        gdlin__hptbi = isinstance(lhs, types.List) and isinstance(rhs,
            types.List)
        etoq__svgj = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        fcrz__rou = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        hbpuc__gwbi = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        xpsp__sgqmb = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        ldcme__wdn = etoq__svgj or fcrz__rou or hbpuc__gwbi or xpsp__sgqmb
        wlk__yek = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        kngam__vkij = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        rya__ldhsv = wlk__yek or kngam__vkij
        qvth__rcwro = lhs == types.NPTimedelta and rhs == types.NPDatetime
        oxk__rukax = (nldz__zun or gdlin__hptbi or ldcme__wdn or rya__ldhsv or
            qvth__rcwro)
        bji__vatb = op == operator.add and oxk__rukax
        return (hdc__oaj or hyao__sone or quv__dzv or sohn__ladd or
            liab__yvyjx or gqz__gje or bji__vatb)


def cmp_op_supported_by_numba(lhs, rhs):
    gqz__gje = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    gdlin__hptbi = isinstance(lhs, types.ListType) and isinstance(rhs,
        types.ListType)
    hdc__oaj = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, types
        .NPTimedelta)
    pbvrb__ejkq = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    wlk__yek = isinstance(lhs, unicode_types) and isinstance(rhs, unicode_types
        )
    nldz__zun = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types.
        BaseTuple)
    sohn__ladd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    liab__yvyjx = isinstance(lhs, types.Number) and isinstance(rhs, types.
        Number)
    zwmp__fmeef = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    xnsnr__gtfe = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    kdq__oilca = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    lfx__euj = isinstance(lhs, types.EnumMember) and isinstance(rhs, types.
        EnumMember)
    xoo__wniyp = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (gdlin__hptbi or hdc__oaj or pbvrb__ejkq or wlk__yek or
        nldz__zun or sohn__ladd or liab__yvyjx or zwmp__fmeef or
        xnsnr__gtfe or kdq__oilca or gqz__gje or lfx__euj or xoo__wniyp)


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
        pzr__aabvb = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(pzr__aabvb)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        pzr__aabvb = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(pzr__aabvb)


install_arith_ops()
