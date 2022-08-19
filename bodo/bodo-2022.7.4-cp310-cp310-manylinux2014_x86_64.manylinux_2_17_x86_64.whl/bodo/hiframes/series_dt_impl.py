"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType, get_series_data, get_series_index, get_series_name, init_series
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        kpop__ngly = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(kpop__ngly)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        spor__nlxys = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, spor__nlxys)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kmo__glsq, = args
        fretn__gsr = signature.return_type
        axq__gru = cgutils.create_struct_proxy(fretn__gsr)(context, builder)
        axq__gru.obj = kmo__glsq
        context.nrt.incref(builder, signature.args[0], kmo__glsq)
        return axq__gru._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if S_dt.stype.dtype != types.NPDatetime('ns') and not isinstance(S_dt
            .stype.dtype, PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{field}')
        piru__xgiz = 'def impl(S_dt):\n'
        piru__xgiz += '    S = S_dt._obj\n'
        piru__xgiz += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        piru__xgiz += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        piru__xgiz += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        piru__xgiz += '    numba.parfors.parfor.init_prange()\n'
        piru__xgiz += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            piru__xgiz += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            piru__xgiz += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        piru__xgiz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        piru__xgiz += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        piru__xgiz += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        piru__xgiz += '            continue\n'
        piru__xgiz += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            piru__xgiz += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                piru__xgiz += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            piru__xgiz += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            sqki__ufir = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            piru__xgiz += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            piru__xgiz += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            piru__xgiz += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(sqki__ufir[field]))
        elif field == 'is_leap_year':
            piru__xgiz += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            piru__xgiz += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            sqki__ufir = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            piru__xgiz += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            piru__xgiz += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            piru__xgiz += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(sqki__ufir[field]))
        else:
            piru__xgiz += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            piru__xgiz += '        out_arr[i] = ts.' + field + '\n'
        piru__xgiz += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        hyvj__hfm = {}
        exec(piru__xgiz, {'bodo': bodo, 'numba': numba, 'np': np}, hyvj__hfm)
        impl = hyvj__hfm['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        vgx__awfb = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vgx__awfb)


_install_date_fields()


def create_date_method_overload(method):
    omw__pviqu = method in ['day_name', 'month_name']
    if omw__pviqu:
        piru__xgiz = 'def overload_method(S_dt, locale=None):\n'
        piru__xgiz += '    unsupported_args = dict(locale=locale)\n'
        piru__xgiz += '    arg_defaults = dict(locale=None)\n'
        piru__xgiz += '    bodo.utils.typing.check_unsupported_args(\n'
        piru__xgiz += f"        'Series.dt.{method}',\n"
        piru__xgiz += '        unsupported_args,\n'
        piru__xgiz += '        arg_defaults,\n'
        piru__xgiz += "        package_name='pandas',\n"
        piru__xgiz += "        module_name='Series',\n"
        piru__xgiz += '    )\n'
    else:
        piru__xgiz = 'def overload_method(S_dt):\n'
        piru__xgiz += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    piru__xgiz += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    piru__xgiz += '        return\n'
    if omw__pviqu:
        piru__xgiz += '    def impl(S_dt, locale=None):\n'
    else:
        piru__xgiz += '    def impl(S_dt):\n'
    piru__xgiz += '        S = S_dt._obj\n'
    piru__xgiz += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    piru__xgiz += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    piru__xgiz += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    piru__xgiz += '        numba.parfors.parfor.init_prange()\n'
    piru__xgiz += '        n = len(arr)\n'
    if omw__pviqu:
        piru__xgiz += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        piru__xgiz += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    piru__xgiz += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    piru__xgiz += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    piru__xgiz += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    piru__xgiz += '                continue\n'
    piru__xgiz += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    piru__xgiz += f'            method_val = ts.{method}()\n'
    if omw__pviqu:
        piru__xgiz += '            out_arr[i] = method_val\n'
    else:
        piru__xgiz += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    piru__xgiz += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    piru__xgiz += '    return impl\n'
    hyvj__hfm = {}
    exec(piru__xgiz, {'bodo': bodo, 'numba': numba, 'np': np}, hyvj__hfm)
    overload_method = hyvj__hfm['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        vgx__awfb = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vgx__awfb)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        ymb__hbjoc = S_dt._obj
        ubv__vyws = bodo.hiframes.pd_series_ext.get_series_data(ymb__hbjoc)
        pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(ymb__hbjoc)
        kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(ymb__hbjoc)
        numba.parfors.parfor.init_prange()
        lilpd__bwwn = len(ubv__vyws)
        bppsx__etw = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            lilpd__bwwn)
        for uymr__aey in numba.parfors.parfor.internal_prange(lilpd__bwwn):
            mpcv__gvuar = ubv__vyws[uymr__aey]
            prd__iyzg = bodo.utils.conversion.box_if_dt64(mpcv__gvuar)
            bppsx__etw[uymr__aey] = datetime.date(prd__iyzg.year, prd__iyzg
                .month, prd__iyzg.day)
        return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
            pwbu__bmjtl, kpop__ngly)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and (S_dt.stype.
            dtype == types.NPDatetime('ns') or isinstance(S_dt.stype.dtype,
            PandasDatetimeTZDtype))):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{attr}')
        if attr == 'components':
            urejy__goaj = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            aciqp__xyrz = 'convert_numpy_timedelta64_to_pd_timedelta'
            kpnot__pnjh = 'np.empty(n, np.int64)'
            vpqrr__csb = attr
        elif attr == 'isocalendar':
            urejy__goaj = ['year', 'week', 'day']
            aciqp__xyrz = 'convert_datetime64_to_timestamp'
            kpnot__pnjh = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            vpqrr__csb = attr + '()'
        piru__xgiz = 'def impl(S_dt):\n'
        piru__xgiz += '    S = S_dt._obj\n'
        piru__xgiz += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        piru__xgiz += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        piru__xgiz += '    numba.parfors.parfor.init_prange()\n'
        piru__xgiz += '    n = len(arr)\n'
        for field in urejy__goaj:
            piru__xgiz += '    {} = {}\n'.format(field, kpnot__pnjh)
        piru__xgiz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        piru__xgiz += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in urejy__goaj:
            piru__xgiz += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        piru__xgiz += '            continue\n'
        rrbdi__xtx = '(' + '[i], '.join(urejy__goaj) + '[i])'
        piru__xgiz += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(rrbdi__xtx, aciqp__xyrz, vpqrr__csb))
        odt__sxiho = '(' + ', '.join(urejy__goaj) + ')'
        piru__xgiz += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(odt__sxiho))
        hyvj__hfm = {}
        exec(piru__xgiz, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(urejy__goaj))}, hyvj__hfm)
        impl = hyvj__hfm['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    ouok__regeu = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, pphv__wxp in ouok__regeu:
        vgx__awfb = create_series_dt_df_output_overload(attr)
        pphv__wxp(SeriesDatetimePropertiesType, attr, inline='always')(
            vgx__awfb)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        piru__xgiz = 'def impl(S_dt):\n'
        piru__xgiz += '    S = S_dt._obj\n'
        piru__xgiz += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        piru__xgiz += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        piru__xgiz += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        piru__xgiz += '    numba.parfors.parfor.init_prange()\n'
        piru__xgiz += '    n = len(A)\n'
        piru__xgiz += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        piru__xgiz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        piru__xgiz += '        if bodo.libs.array_kernels.isna(A, i):\n'
        piru__xgiz += '            bodo.libs.array_kernels.setna(B, i)\n'
        piru__xgiz += '            continue\n'
        piru__xgiz += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            piru__xgiz += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            piru__xgiz += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            piru__xgiz += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            piru__xgiz += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        piru__xgiz += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        hyvj__hfm = {}
        exec(piru__xgiz, {'numba': numba, 'np': np, 'bodo': bodo}, hyvj__hfm)
        impl = hyvj__hfm['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        piru__xgiz = 'def impl(S_dt):\n'
        piru__xgiz += '    S = S_dt._obj\n'
        piru__xgiz += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        piru__xgiz += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        piru__xgiz += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        piru__xgiz += '    numba.parfors.parfor.init_prange()\n'
        piru__xgiz += '    n = len(A)\n'
        if method == 'total_seconds':
            piru__xgiz += '    B = np.empty(n, np.float64)\n'
        else:
            piru__xgiz += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        piru__xgiz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        piru__xgiz += '        if bodo.libs.array_kernels.isna(A, i):\n'
        piru__xgiz += '            bodo.libs.array_kernels.setna(B, i)\n'
        piru__xgiz += '            continue\n'
        piru__xgiz += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            piru__xgiz += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            piru__xgiz += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            piru__xgiz += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            piru__xgiz += '    return B\n'
        hyvj__hfm = {}
        exec(piru__xgiz, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, hyvj__hfm)
        impl = hyvj__hfm['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        vgx__awfb = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vgx__awfb)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        vgx__awfb = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vgx__awfb)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        ymb__hbjoc = S_dt._obj
        mlc__cieuv = bodo.hiframes.pd_series_ext.get_series_data(ymb__hbjoc)
        pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(ymb__hbjoc)
        kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(ymb__hbjoc)
        numba.parfors.parfor.init_prange()
        lilpd__bwwn = len(mlc__cieuv)
        olkyt__dzs = bodo.libs.str_arr_ext.pre_alloc_string_array(lilpd__bwwn,
            -1)
        for wbf__ylpv in numba.parfors.parfor.internal_prange(lilpd__bwwn):
            if bodo.libs.array_kernels.isna(mlc__cieuv, wbf__ylpv):
                bodo.libs.array_kernels.setna(olkyt__dzs, wbf__ylpv)
                continue
            olkyt__dzs[wbf__ylpv] = bodo.utils.conversion.box_if_dt64(
                mlc__cieuv[wbf__ylpv]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(olkyt__dzs,
            pwbu__bmjtl, kpop__ngly)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        ymb__hbjoc = S_dt._obj
        mxr__xujyr = get_series_data(ymb__hbjoc).tz_convert(tz)
        pwbu__bmjtl = get_series_index(ymb__hbjoc)
        kpop__ngly = get_series_name(ymb__hbjoc)
        return init_series(mxr__xujyr, pwbu__bmjtl, kpop__ngly)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'
            ) and not isinstance(S_dt.stype.dtype, bodo.libs.
            pd_datetime_arr_ext.PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{method}()')
        rkzwy__ruur = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        syn__fjk = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', rkzwy__ruur, syn__fjk,
            package_name='pandas', module_name='Series')
        piru__xgiz = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        piru__xgiz += '    S = S_dt._obj\n'
        piru__xgiz += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        piru__xgiz += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        piru__xgiz += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        piru__xgiz += '    numba.parfors.parfor.init_prange()\n'
        piru__xgiz += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            piru__xgiz += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            piru__xgiz += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        piru__xgiz += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        piru__xgiz += '        if bodo.libs.array_kernels.isna(A, i):\n'
        piru__xgiz += '            bodo.libs.array_kernels.setna(B, i)\n'
        piru__xgiz += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            ioy__ypzlc = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            bpq__tczo = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            ioy__ypzlc = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            bpq__tczo = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        piru__xgiz += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            bpq__tczo, ioy__ypzlc, method)
        piru__xgiz += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        hyvj__hfm = {}
        exec(piru__xgiz, {'numba': numba, 'np': np, 'bodo': bodo}, hyvj__hfm)
        impl = hyvj__hfm['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    wrbba__tpis = ['ceil', 'floor', 'round']
    for method in wrbba__tpis:
        vgx__awfb = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vgx__awfb)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                psg__zzn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                satdx__ywrqi = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    psg__zzn)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                owk__vsxp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lwjb__yfz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    owk__vsxp)
                lilpd__bwwn = len(satdx__ywrqi)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    hgfxv__lirme = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(satdx__ywrqi[uymr__aey]))
                    wpo__xcy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        lwjb__yfz[uymr__aey])
                    if hgfxv__lirme == uiaox__tnv or wpo__xcy == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(hgfxv__lirme, wpo__xcy)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lwjb__yfz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, dt64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(lwjb__yfz[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or oulog__yeu == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, oulog__yeu)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lwjb__yfz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, dt64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(lwjb__yfz[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or oulog__yeu == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, oulog__yeu)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                hxfl__owed = rhs.value
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or hxfl__owed == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, hxfl__owed)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                hxfl__owed = lhs.value
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if hxfl__owed == uiaox__tnv or iyo__ypzsb == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(hxfl__owed, iyo__ypzsb)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, dt64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                ethxg__dwnnp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ethxg__dwnnp))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or oulog__yeu == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, oulog__yeu)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, dt64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                ethxg__dwnnp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ethxg__dwnnp))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    iyo__ypzsb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or oulog__yeu == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, oulog__yeu)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                cco__ruk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                iyo__ypzsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    cco__ruk)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    lrlx__wdqtx = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if lrlx__wdqtx == uiaox__tnv or iyo__ypzsb == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(lrlx__wdqtx, iyo__ypzsb)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                cco__ruk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                iyo__ypzsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    cco__ruk)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    lrlx__wdqtx = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if iyo__ypzsb == uiaox__tnv or lrlx__wdqtx == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(iyo__ypzsb, lrlx__wdqtx)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            vjghh__zuqn = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ubv__vyws = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(vjghh__zuqn))
                ethxg__dwnnp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ethxg__dwnnp))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    rxuua__jgyr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ubv__vyws[uymr__aey]))
                    if oulog__yeu == uiaox__tnv or rxuua__jgyr == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(rxuua__jgyr, oulog__yeu)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            vjghh__zuqn = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ubv__vyws = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                ymb__hbjoc = np.empty(lilpd__bwwn, timedelta64_dtype)
                uiaox__tnv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(vjghh__zuqn))
                ethxg__dwnnp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                oulog__yeu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ethxg__dwnnp))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    rxuua__jgyr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ubv__vyws[uymr__aey]))
                    if oulog__yeu == uiaox__tnv or rxuua__jgyr == uiaox__tnv:
                        waszk__qps = uiaox__tnv
                    else:
                        waszk__qps = op(oulog__yeu, rxuua__jgyr)
                    ymb__hbjoc[uymr__aey
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        waszk__qps)
                return bodo.hiframes.pd_series_ext.init_series(ymb__hbjoc,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            ajv__ahkog = True
        else:
            ajv__ahkog = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            vjghh__zuqn = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ubv__vyws = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(vjghh__zuqn))
                awqn__glp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ips__cjol = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(awqn__glp))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    fwhc__wdudk = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ubv__vyws[uymr__aey]))
                    if fwhc__wdudk == uiaox__tnv or ips__cjol == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(fwhc__wdudk, ips__cjol)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            vjghh__zuqn = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ubv__vyws = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(vjghh__zuqn))
                sqo__cjc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                fwhc__wdudk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(sqo__cjc))
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    ips__cjol = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ubv__vyws[uymr__aey]))
                    if fwhc__wdudk == uiaox__tnv or ips__cjol == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(fwhc__wdudk, ips__cjol)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    fwhc__wdudk = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if fwhc__wdudk == uiaox__tnv or rhs.value == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(fwhc__wdudk, rhs.value)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    ips__cjol = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ubv__vyws[uymr__aey])
                    if ips__cjol == uiaox__tnv or lhs.value == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(lhs.value, ips__cjol)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                jwrzp__stj = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                amjjv__wgh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jwrzp__stj)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    fwhc__wdudk = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ubv__vyws[uymr__aey]))
                    if fwhc__wdudk == uiaox__tnv or amjjv__wgh == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(fwhc__wdudk, amjjv__wgh)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            vjghh__zuqn = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                iby__opixe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ubv__vyws = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    iby__opixe)
                pwbu__bmjtl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                kpop__ngly = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                lilpd__bwwn = len(ubv__vyws)
                bppsx__etw = bodo.libs.bool_arr_ext.alloc_bool_array(
                    lilpd__bwwn)
                uiaox__tnv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vjghh__zuqn)
                jwrzp__stj = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                amjjv__wgh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jwrzp__stj)
                for uymr__aey in numba.parfors.parfor.internal_prange(
                    lilpd__bwwn):
                    cco__ruk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ubv__vyws[uymr__aey])
                    if cco__ruk == uiaox__tnv or amjjv__wgh == uiaox__tnv:
                        waszk__qps = ajv__ahkog
                    else:
                        waszk__qps = op(amjjv__wgh, cco__ruk)
                    bppsx__etw[uymr__aey] = waszk__qps
                return bodo.hiframes.pd_series_ext.init_series(bppsx__etw,
                    pwbu__bmjtl, kpop__ngly)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for tutht__xokwi in series_dt_unsupported_attrs:
        kzbix__ygmm = 'Series.dt.' + tutht__xokwi
        overload_attribute(SeriesDatetimePropertiesType, tutht__xokwi)(
            create_unsupported_overload(kzbix__ygmm))
    for tggkn__gvzv in series_dt_unsupported_methods:
        kzbix__ygmm = 'Series.dt.' + tggkn__gvzv
        overload_method(SeriesDatetimePropertiesType, tggkn__gvzv,
            no_unliteral=True)(create_unsupported_overload(kzbix__ygmm))


_install_series_dt_unsupported()
