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
        gns__zkx = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, gns__zkx)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    xuoip__fhq = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yjod__vex = c.pyapi.long_from_longlong(xuoip__fhq.year)
    islze__omlez = c.pyapi.long_from_longlong(xuoip__fhq.month)
    oxt__flcqo = c.pyapi.long_from_longlong(xuoip__fhq.day)
    gmsvn__ucoxw = c.pyapi.long_from_longlong(xuoip__fhq.hour)
    zvwgg__hqrod = c.pyapi.long_from_longlong(xuoip__fhq.minute)
    ltm__vhvi = c.pyapi.long_from_longlong(xuoip__fhq.second)
    jvwvq__paag = c.pyapi.long_from_longlong(xuoip__fhq.microsecond)
    fhv__mjqac = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    hga__zpb = c.pyapi.call_function_objargs(fhv__mjqac, (yjod__vex,
        islze__omlez, oxt__flcqo, gmsvn__ucoxw, zvwgg__hqrod, ltm__vhvi,
        jvwvq__paag))
    c.pyapi.decref(yjod__vex)
    c.pyapi.decref(islze__omlez)
    c.pyapi.decref(oxt__flcqo)
    c.pyapi.decref(gmsvn__ucoxw)
    c.pyapi.decref(zvwgg__hqrod)
    c.pyapi.decref(ltm__vhvi)
    c.pyapi.decref(jvwvq__paag)
    c.pyapi.decref(fhv__mjqac)
    return hga__zpb


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    yjod__vex = c.pyapi.object_getattr_string(val, 'year')
    islze__omlez = c.pyapi.object_getattr_string(val, 'month')
    oxt__flcqo = c.pyapi.object_getattr_string(val, 'day')
    gmsvn__ucoxw = c.pyapi.object_getattr_string(val, 'hour')
    zvwgg__hqrod = c.pyapi.object_getattr_string(val, 'minute')
    ltm__vhvi = c.pyapi.object_getattr_string(val, 'second')
    jvwvq__paag = c.pyapi.object_getattr_string(val, 'microsecond')
    xuoip__fhq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xuoip__fhq.year = c.pyapi.long_as_longlong(yjod__vex)
    xuoip__fhq.month = c.pyapi.long_as_longlong(islze__omlez)
    xuoip__fhq.day = c.pyapi.long_as_longlong(oxt__flcqo)
    xuoip__fhq.hour = c.pyapi.long_as_longlong(gmsvn__ucoxw)
    xuoip__fhq.minute = c.pyapi.long_as_longlong(zvwgg__hqrod)
    xuoip__fhq.second = c.pyapi.long_as_longlong(ltm__vhvi)
    xuoip__fhq.microsecond = c.pyapi.long_as_longlong(jvwvq__paag)
    c.pyapi.decref(yjod__vex)
    c.pyapi.decref(islze__omlez)
    c.pyapi.decref(oxt__flcqo)
    c.pyapi.decref(gmsvn__ucoxw)
    c.pyapi.decref(zvwgg__hqrod)
    c.pyapi.decref(ltm__vhvi)
    c.pyapi.decref(jvwvq__paag)
    gnf__fusb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xuoip__fhq._getvalue(), is_error=gnf__fusb)


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
        xuoip__fhq = cgutils.create_struct_proxy(typ)(context, builder)
        xuoip__fhq.year = args[0]
        xuoip__fhq.month = args[1]
        xuoip__fhq.day = args[2]
        xuoip__fhq.hour = args[3]
        xuoip__fhq.minute = args[4]
        xuoip__fhq.second = args[5]
        xuoip__fhq.microsecond = args[6]
        return xuoip__fhq._getvalue()
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
                y, ykn__drq = lhs.year, rhs.year
                plofg__nujt, xur__puvuf = lhs.month, rhs.month
                d, jzqp__xzpn = lhs.day, rhs.day
                ypnly__ewpo, bfa__vzgto = lhs.hour, rhs.hour
                mkpf__kcdc, knq__rinxw = lhs.minute, rhs.minute
                jnfb__bmptu, ygy__pfig = lhs.second, rhs.second
                rbtm__qduge, fcxgr__kfgn = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, plofg__nujt, d, ypnly__ewpo, mkpf__kcdc,
                    jnfb__bmptu, rbtm__qduge), (ykn__drq, xur__puvuf,
                    jzqp__xzpn, bfa__vzgto, knq__rinxw, ygy__pfig,
                    fcxgr__kfgn)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            rkyv__cnu = lhs.toordinal()
            dwp__waqm = rhs.toordinal()
            hsob__rma = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            edt__ewcjr = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            hbi__aua = datetime.timedelta(rkyv__cnu - dwp__waqm, hsob__rma -
                edt__ewcjr, lhs.microsecond - rhs.microsecond)
            return hbi__aua
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    ewgyn__pkkxg = context.make_helper(builder, fromty, value=val)
    toj__ram = cgutils.as_bool_bit(builder, ewgyn__pkkxg.valid)
    with builder.if_else(toj__ram) as (sqbts__vatr, mkygc__flrfs):
        with sqbts__vatr:
            chwz__yyqtw = context.cast(builder, ewgyn__pkkxg.data, fromty.
                type, toty)
            oois__kxf = builder.block
        with mkygc__flrfs:
            issj__lrtui = numba.np.npdatetime.NAT
            wkkie__awbe = builder.block
    hga__zpb = builder.phi(chwz__yyqtw.type)
    hga__zpb.add_incoming(chwz__yyqtw, oois__kxf)
    hga__zpb.add_incoming(issj__lrtui, wkkie__awbe)
    return hga__zpb
