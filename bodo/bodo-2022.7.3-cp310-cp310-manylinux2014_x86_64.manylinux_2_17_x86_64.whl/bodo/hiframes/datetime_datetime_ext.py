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
        bdffv__bnye = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, bdffv__bnye)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    gvlox__gwlq = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ffyx__ajrdp = c.pyapi.long_from_longlong(gvlox__gwlq.year)
    ruxo__xmef = c.pyapi.long_from_longlong(gvlox__gwlq.month)
    mkx__zpq = c.pyapi.long_from_longlong(gvlox__gwlq.day)
    ythu__ewhy = c.pyapi.long_from_longlong(gvlox__gwlq.hour)
    zsrn__ryiqp = c.pyapi.long_from_longlong(gvlox__gwlq.minute)
    kfjg__wpzkw = c.pyapi.long_from_longlong(gvlox__gwlq.second)
    url__cep = c.pyapi.long_from_longlong(gvlox__gwlq.microsecond)
    gpp__cic = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.datetime))
    kfbki__lea = c.pyapi.call_function_objargs(gpp__cic, (ffyx__ajrdp,
        ruxo__xmef, mkx__zpq, ythu__ewhy, zsrn__ryiqp, kfjg__wpzkw, url__cep))
    c.pyapi.decref(ffyx__ajrdp)
    c.pyapi.decref(ruxo__xmef)
    c.pyapi.decref(mkx__zpq)
    c.pyapi.decref(ythu__ewhy)
    c.pyapi.decref(zsrn__ryiqp)
    c.pyapi.decref(kfjg__wpzkw)
    c.pyapi.decref(url__cep)
    c.pyapi.decref(gpp__cic)
    return kfbki__lea


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    ffyx__ajrdp = c.pyapi.object_getattr_string(val, 'year')
    ruxo__xmef = c.pyapi.object_getattr_string(val, 'month')
    mkx__zpq = c.pyapi.object_getattr_string(val, 'day')
    ythu__ewhy = c.pyapi.object_getattr_string(val, 'hour')
    zsrn__ryiqp = c.pyapi.object_getattr_string(val, 'minute')
    kfjg__wpzkw = c.pyapi.object_getattr_string(val, 'second')
    url__cep = c.pyapi.object_getattr_string(val, 'microsecond')
    gvlox__gwlq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gvlox__gwlq.year = c.pyapi.long_as_longlong(ffyx__ajrdp)
    gvlox__gwlq.month = c.pyapi.long_as_longlong(ruxo__xmef)
    gvlox__gwlq.day = c.pyapi.long_as_longlong(mkx__zpq)
    gvlox__gwlq.hour = c.pyapi.long_as_longlong(ythu__ewhy)
    gvlox__gwlq.minute = c.pyapi.long_as_longlong(zsrn__ryiqp)
    gvlox__gwlq.second = c.pyapi.long_as_longlong(kfjg__wpzkw)
    gvlox__gwlq.microsecond = c.pyapi.long_as_longlong(url__cep)
    c.pyapi.decref(ffyx__ajrdp)
    c.pyapi.decref(ruxo__xmef)
    c.pyapi.decref(mkx__zpq)
    c.pyapi.decref(ythu__ewhy)
    c.pyapi.decref(zsrn__ryiqp)
    c.pyapi.decref(kfjg__wpzkw)
    c.pyapi.decref(url__cep)
    fhoo__afuq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gvlox__gwlq._getvalue(), is_error=fhoo__afuq)


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
        gvlox__gwlq = cgutils.create_struct_proxy(typ)(context, builder)
        gvlox__gwlq.year = args[0]
        gvlox__gwlq.month = args[1]
        gvlox__gwlq.day = args[2]
        gvlox__gwlq.hour = args[3]
        gvlox__gwlq.minute = args[4]
        gvlox__gwlq.second = args[5]
        gvlox__gwlq.microsecond = args[6]
        return gvlox__gwlq._getvalue()
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
                y, selz__cxegd = lhs.year, rhs.year
                wslan__xngc, zbi__clz = lhs.month, rhs.month
                d, ppj__zxef = lhs.day, rhs.day
                uhp__uvt, ujofj__bbvi = lhs.hour, rhs.hour
                ynq__cmahd, wds__kmaby = lhs.minute, rhs.minute
                qhut__bfab, wwk__sluz = lhs.second, rhs.second
                pwang__vks, idbjz__xfmu = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, wslan__xngc, d, uhp__uvt, ynq__cmahd,
                    qhut__bfab, pwang__vks), (selz__cxegd, zbi__clz,
                    ppj__zxef, ujofj__bbvi, wds__kmaby, wwk__sluz,
                    idbjz__xfmu)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            sjpt__qez = lhs.toordinal()
            psdl__npud = rhs.toordinal()
            xvtdg__lkf = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ztvln__ytab = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            oggmh__mswn = datetime.timedelta(sjpt__qez - psdl__npud, 
                xvtdg__lkf - ztvln__ytab, lhs.microsecond - rhs.microsecond)
            return oggmh__mswn
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    fvao__qqof = context.make_helper(builder, fromty, value=val)
    zhj__lmeu = cgutils.as_bool_bit(builder, fvao__qqof.valid)
    with builder.if_else(zhj__lmeu) as (cddow__aawt, zui__bygf):
        with cddow__aawt:
            awv__afx = context.cast(builder, fvao__qqof.data, fromty.type, toty
                )
            ozgx__aaq = builder.block
        with zui__bygf:
            hfsp__uzz = numba.np.npdatetime.NAT
            ojo__ymilt = builder.block
    kfbki__lea = builder.phi(awv__afx.type)
    kfbki__lea.add_incoming(awv__afx, ozgx__aaq)
    kfbki__lea.add_incoming(hfsp__uzz, ojo__ymilt)
    return kfbki__lea
