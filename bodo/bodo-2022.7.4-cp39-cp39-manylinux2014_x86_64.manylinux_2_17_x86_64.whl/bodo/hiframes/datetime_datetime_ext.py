import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vgvxy__typjq = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, vgvxy__typjq)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    epan__pfhpw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    vwc__lfpa = c.pyapi.long_from_longlong(epan__pfhpw.year)
    ihc__xgep = c.pyapi.long_from_longlong(epan__pfhpw.month)
    nrtq__vytrj = c.pyapi.long_from_longlong(epan__pfhpw.day)
    qpzb__phg = c.pyapi.long_from_longlong(epan__pfhpw.hour)
    uijh__ojzzh = c.pyapi.long_from_longlong(epan__pfhpw.minute)
    bwn__rqpgn = c.pyapi.long_from_longlong(epan__pfhpw.second)
    idur__olc = c.pyapi.long_from_longlong(epan__pfhpw.microsecond)
    tyudc__ppq = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    qgxn__lzga = c.pyapi.call_function_objargs(tyudc__ppq, (vwc__lfpa,
        ihc__xgep, nrtq__vytrj, qpzb__phg, uijh__ojzzh, bwn__rqpgn, idur__olc))
    c.pyapi.decref(vwc__lfpa)
    c.pyapi.decref(ihc__xgep)
    c.pyapi.decref(nrtq__vytrj)
    c.pyapi.decref(qpzb__phg)
    c.pyapi.decref(uijh__ojzzh)
    c.pyapi.decref(bwn__rqpgn)
    c.pyapi.decref(idur__olc)
    c.pyapi.decref(tyudc__ppq)
    return qgxn__lzga


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    vwc__lfpa = c.pyapi.object_getattr_string(val, 'year')
    ihc__xgep = c.pyapi.object_getattr_string(val, 'month')
    nrtq__vytrj = c.pyapi.object_getattr_string(val, 'day')
    qpzb__phg = c.pyapi.object_getattr_string(val, 'hour')
    uijh__ojzzh = c.pyapi.object_getattr_string(val, 'minute')
    bwn__rqpgn = c.pyapi.object_getattr_string(val, 'second')
    idur__olc = c.pyapi.object_getattr_string(val, 'microsecond')
    epan__pfhpw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    epan__pfhpw.year = c.pyapi.long_as_longlong(vwc__lfpa)
    epan__pfhpw.month = c.pyapi.long_as_longlong(ihc__xgep)
    epan__pfhpw.day = c.pyapi.long_as_longlong(nrtq__vytrj)
    epan__pfhpw.hour = c.pyapi.long_as_longlong(qpzb__phg)
    epan__pfhpw.minute = c.pyapi.long_as_longlong(uijh__ojzzh)
    epan__pfhpw.second = c.pyapi.long_as_longlong(bwn__rqpgn)
    epan__pfhpw.microsecond = c.pyapi.long_as_longlong(idur__olc)
    c.pyapi.decref(vwc__lfpa)
    c.pyapi.decref(ihc__xgep)
    c.pyapi.decref(nrtq__vytrj)
    c.pyapi.decref(qpzb__phg)
    c.pyapi.decref(uijh__ojzzh)
    c.pyapi.decref(bwn__rqpgn)
    c.pyapi.decref(idur__olc)
    kkwh__vmh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(epan__pfhpw._getvalue(), is_error=kkwh__vmh)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        epan__pfhpw = cgutils.create_struct_proxy(typ)(context, builder)
        epan__pfhpw.year = args[0]
        epan__pfhpw.month = args[1]
        epan__pfhpw.day = args[2]
        epan__pfhpw.hour = args[3]
        epan__pfhpw.minute = args[4]
        epan__pfhpw.second = args[5]
        epan__pfhpw.microsecond = args[6]
        return epan__pfhpw._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, dhm__fme = lhs.year, rhs.year
                vqq__yxm, hefh__vefcv = lhs.month, rhs.month
                d, mgahz__yvog = lhs.day, rhs.day
                shm__cxz, egbq__swfb = lhs.hour, rhs.hour
                vfssn__hyb, oqyd__tmsx = lhs.minute, rhs.minute
                rzp__yqr, rwcs__jrqw = lhs.second, rhs.second
                qcdu__mtwxy, mzgre__nrca = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, vqq__yxm, d, shm__cxz, vfssn__hyb,
                    rzp__yqr, qcdu__mtwxy), (dhm__fme, hefh__vefcv,
                    mgahz__yvog, egbq__swfb, oqyd__tmsx, rwcs__jrqw,
                    mzgre__nrca)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            lixg__ergtd = lhs.toordinal()
            wuf__vespa = rhs.toordinal()
            rhy__mdooe = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            kemew__mvkfe = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            okw__xbtxi = datetime.timedelta(lixg__ergtd - wuf__vespa, 
                rhy__mdooe - kemew__mvkfe, lhs.microsecond - rhs.microsecond)
            return okw__xbtxi
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    vxcoc__jiub = context.make_helper(builder, fromty, value=val)
    datwo__lxt = cgutils.as_bool_bit(builder, vxcoc__jiub.valid)
    with builder.if_else(datwo__lxt) as (bfoqc__jodo, iidly__nbzjx):
        with bfoqc__jodo:
            rncm__nwn = context.cast(builder, vxcoc__jiub.data, fromty.type,
                toty)
            tfte__noe = builder.block
        with iidly__nbzjx:
            rckm__akxwi = numba.np.npdatetime.NAT
            vis__wvccw = builder.block
    qgxn__lzga = builder.phi(rncm__nwn.type)
    qgxn__lzga.add_incoming(rncm__nwn, tfte__noe)
    qgxn__lzga.add_incoming(rckm__akxwi, vis__wvccw)
    return qgxn__lzga
