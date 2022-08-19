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
        hchov__hxmhm = lhs.data if isinstance(lhs, SeriesType) else lhs
        ghhc__pqie = rhs.data if isinstance(rhs, SeriesType) else rhs
        if hchov__hxmhm in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and ghhc__pqie.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            hchov__hxmhm = ghhc__pqie.dtype
        elif ghhc__pqie in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and hchov__hxmhm.dtype in (bodo.datetime64ns, bodo.timedelta64ns
            ):
            ghhc__pqie = hchov__hxmhm.dtype
        fnywf__ake = hchov__hxmhm, ghhc__pqie
        ssnzz__tpdv = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            xdi__pcss = self.context.resolve_function_type(self.key,
                fnywf__ake, {}).return_type
        except Exception as vdhg__txtef:
            raise BodoError(ssnzz__tpdv)
        if is_overload_bool(xdi__pcss):
            raise BodoError(ssnzz__tpdv)
        qbqg__nyyh = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        cdar__oruuk = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vrf__yaavg = types.bool_
        mcu__srxyq = SeriesType(vrf__yaavg, xdi__pcss, qbqg__nyyh, cdar__oruuk)
        return mcu__srxyq(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        aetv__yzdk = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if aetv__yzdk is None:
            aetv__yzdk = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, aetv__yzdk, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        hchov__hxmhm = lhs.data if isinstance(lhs, SeriesType) else lhs
        ghhc__pqie = rhs.data if isinstance(rhs, SeriesType) else rhs
        fnywf__ake = hchov__hxmhm, ghhc__pqie
        ssnzz__tpdv = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            xdi__pcss = self.context.resolve_function_type(self.key,
                fnywf__ake, {}).return_type
        except Exception as nbony__wfel:
            raise BodoError(ssnzz__tpdv)
        qbqg__nyyh = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        cdar__oruuk = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vrf__yaavg = xdi__pcss.dtype
        mcu__srxyq = SeriesType(vrf__yaavg, xdi__pcss, qbqg__nyyh, cdar__oruuk)
        return mcu__srxyq(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        aetv__yzdk = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if aetv__yzdk is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                aetv__yzdk = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, aetv__yzdk, sig, args)
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
            aetv__yzdk = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return aetv__yzdk(lhs, rhs)
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
            aetv__yzdk = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return aetv__yzdk(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    vdr__qlo = lhs == datetime_timedelta_type and rhs == datetime_date_type
    rsvs__kyga = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return vdr__qlo or rsvs__kyga


def add_timestamp(lhs, rhs):
    jqh__eyczb = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    ucnr__ndc = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return jqh__eyczb or ucnr__ndc


def add_datetime_and_timedeltas(lhs, rhs):
    jwit__zno = [datetime_timedelta_type, pd_timedelta_type]
    ygex__ngyuu = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    xsdpc__vnaf = lhs in jwit__zno and rhs in jwit__zno
    eim__hccpl = (lhs == datetime_datetime_type and rhs in jwit__zno or rhs ==
        datetime_datetime_type and lhs in jwit__zno)
    return xsdpc__vnaf or eim__hccpl


def mul_string_arr_and_int(lhs, rhs):
    ghhc__pqie = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    hchov__hxmhm = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return ghhc__pqie or hchov__hxmhm


def mul_timedelta_and_int(lhs, rhs):
    vdr__qlo = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    rsvs__kyga = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return vdr__qlo or rsvs__kyga


def mul_date_offset_and_int(lhs, rhs):
    xcj__toct = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    nrmvf__mnxxx = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return xcj__toct or nrmvf__mnxxx


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    qkfz__ldp = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    pff__bjon = [date_offset_type, month_begin_type, month_end_type, week_type]
    return rhs in pff__bjon and lhs in qkfz__ldp


def sub_dt_index_and_timestamp(lhs, rhs):
    izd__fhhp = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    klawo__uwynn = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return izd__fhhp or klawo__uwynn


def sub_dt_or_td(lhs, rhs):
    hmcfj__yxazn = lhs == datetime_date_type and rhs == datetime_timedelta_type
    rmyy__dkro = lhs == datetime_date_type and rhs == datetime_date_type
    ynnmx__gkck = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return hmcfj__yxazn or rmyy__dkro or ynnmx__gkck


def sub_datetime_and_timedeltas(lhs, rhs):
    vwbaq__ufkwm = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    zupn__sji = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return vwbaq__ufkwm or zupn__sji


def div_timedelta_and_int(lhs, rhs):
    xsdpc__vnaf = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    sjwv__ufnx = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return xsdpc__vnaf or sjwv__ufnx


def div_datetime_timedelta(lhs, rhs):
    xsdpc__vnaf = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    sjwv__ufnx = lhs == datetime_timedelta_type and rhs == types.int64
    return xsdpc__vnaf or sjwv__ufnx


def mod_timedeltas(lhs, rhs):
    fxn__jwlws = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    mrnnj__fkgga = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return fxn__jwlws or mrnnj__fkgga


def cmp_dt_index_to_string(lhs, rhs):
    izd__fhhp = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    klawo__uwynn = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return izd__fhhp or klawo__uwynn


def cmp_timestamp_or_date(lhs, rhs):
    grccc__cua = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    lbykv__kssbd = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    cbzce__sir = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    roirr__nydvy = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    ovaep__enl = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (grccc__cua or lbykv__kssbd or cbzce__sir or roirr__nydvy or
        ovaep__enl)


def cmp_timeseries(lhs, rhs):
    wydh__jjm = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    ypnv__zoqho = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    qjuxx__xtn = wydh__jjm or ypnv__zoqho
    tuzck__hgy = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    fcy__dfeyn = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    rrp__mrc = tuzck__hgy or fcy__dfeyn
    return qjuxx__xtn or rrp__mrc


def cmp_timedeltas(lhs, rhs):
    xsdpc__vnaf = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in xsdpc__vnaf and rhs in xsdpc__vnaf


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    fwjld__sizml = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return fwjld__sizml


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    ggzz__hparj = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    nycfz__dmbry = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    tba__eskv = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    pawk__yjgaf = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return ggzz__hparj or nycfz__dmbry or tba__eskv or pawk__yjgaf


def args_td_and_int_array(lhs, rhs):
    wdr__pkt = (isinstance(lhs, IntegerArrayType) or isinstance(lhs, types.
        Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance(rhs,
        IntegerArrayType) or isinstance(rhs, types.Array) and isinstance(
        rhs.dtype, types.Integer))
    pjyu__mcudn = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return wdr__pkt and pjyu__mcudn


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        rsvs__kyga = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        vdr__qlo = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        luyqv__hcw = rsvs__kyga or vdr__qlo
        ghp__iog = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        imr__ooqj = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        jifpk__jfkbo = ghp__iog or imr__ooqj
        ovxv__ronv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        vfxn__rlouf = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        lmcnu__ccrbb = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ujfno__fkc = ovxv__ronv or vfxn__rlouf or lmcnu__ccrbb
        fwio__xwdf = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        tocj__cxv = isinstance(lhs, tys) or isinstance(rhs, tys)
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (luyqv__hcw or jifpk__jfkbo or ujfno__fkc or fwio__xwdf or
            tocj__cxv or smsa__mvwl)
    if op == operator.pow:
        tbsbn__katm = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        ffya__hcanl = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        lmcnu__ccrbb = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return tbsbn__katm or ffya__hcanl or lmcnu__ccrbb or smsa__mvwl
    if op == operator.floordiv:
        vfxn__rlouf = lhs in types.real_domain and rhs in types.real_domain
        ovxv__ronv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        vpbv__nxrg = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        xsdpc__vnaf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (vfxn__rlouf or ovxv__ronv or vpbv__nxrg or xsdpc__vnaf or
            smsa__mvwl)
    if op == operator.truediv:
        kgthl__rdguv = lhs in machine_ints and rhs in machine_ints
        vfxn__rlouf = lhs in types.real_domain and rhs in types.real_domain
        lmcnu__ccrbb = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        ovxv__ronv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        vpbv__nxrg = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        ritn__cwpyo = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        xsdpc__vnaf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (kgthl__rdguv or vfxn__rlouf or lmcnu__ccrbb or ovxv__ronv or
            vpbv__nxrg or ritn__cwpyo or xsdpc__vnaf or smsa__mvwl)
    if op == operator.mod:
        kgthl__rdguv = lhs in machine_ints and rhs in machine_ints
        vfxn__rlouf = lhs in types.real_domain and rhs in types.real_domain
        ovxv__ronv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        vpbv__nxrg = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (kgthl__rdguv or vfxn__rlouf or ovxv__ronv or vpbv__nxrg or
            smsa__mvwl)
    if op == operator.add or op == operator.sub:
        luyqv__hcw = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        zpzt__xux = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        llmnc__fyyxt = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        edjfr__aebd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        ovxv__ronv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        vfxn__rlouf = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        lmcnu__ccrbb = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ujfno__fkc = ovxv__ronv or vfxn__rlouf or lmcnu__ccrbb
        smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        vea__qeq = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        fwio__xwdf = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        siz__xydh = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        znhq__pev = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        sbk__utugv = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        iik__yvyf = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        yfc__aiw = siz__xydh or znhq__pev or sbk__utugv or iik__yvyf
        jifpk__jfkbo = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        ltq__pcwtt = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        sas__nygtj = jifpk__jfkbo or ltq__pcwtt
        qttc__vcyz = lhs == types.NPTimedelta and rhs == types.NPDatetime
        xzrqf__ohwy = (vea__qeq or fwio__xwdf or yfc__aiw or sas__nygtj or
            qttc__vcyz)
        pww__hhre = op == operator.add and xzrqf__ohwy
        return (luyqv__hcw or zpzt__xux or llmnc__fyyxt or edjfr__aebd or
            ujfno__fkc or smsa__mvwl or pww__hhre)


def cmp_op_supported_by_numba(lhs, rhs):
    smsa__mvwl = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    fwio__xwdf = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    luyqv__hcw = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    vixa__lxq = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types
        .NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    jifpk__jfkbo = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    vea__qeq = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types.
        BaseTuple)
    edjfr__aebd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    ujfno__fkc = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    mgct__adqhe = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    pbes__bur = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    jru__rger = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    arply__sxy = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    xquo__fji = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (fwio__xwdf or luyqv__hcw or vixa__lxq or jifpk__jfkbo or
        vea__qeq or edjfr__aebd or ujfno__fkc or mgct__adqhe or pbes__bur or
        jru__rger or smsa__mvwl or arply__sxy or xquo__fji)


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
        tmtef__pxesz = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(tmtef__pxesz)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        tmtef__pxesz = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(tmtef__pxesz)


install_arith_ops()
