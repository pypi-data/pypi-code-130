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
        zsii__xjb = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(zsii__xjb)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qnqac__migkd = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, qnqac__migkd)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        bkov__gyxy, = args
        hslj__purul = signature.return_type
        zzdx__rvcda = cgutils.create_struct_proxy(hslj__purul)(context, builder
            )
        zzdx__rvcda.obj = bkov__gyxy
        context.nrt.incref(builder, signature.args[0], bkov__gyxy)
        return zzdx__rvcda._getvalue()
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
        csiyi__emnae = 'def impl(S_dt):\n'
        csiyi__emnae += '    S = S_dt._obj\n'
        csiyi__emnae += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        csiyi__emnae += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        csiyi__emnae += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        csiyi__emnae += '    numba.parfors.parfor.init_prange()\n'
        csiyi__emnae += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            csiyi__emnae += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            csiyi__emnae += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        csiyi__emnae += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        csiyi__emnae += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        csiyi__emnae += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        csiyi__emnae += '            continue\n'
        csiyi__emnae += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            csiyi__emnae += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                csiyi__emnae += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            csiyi__emnae += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            fpgxe__ykttf = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            csiyi__emnae += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            csiyi__emnae += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            csiyi__emnae += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(fpgxe__ykttf[field]))
        elif field == 'is_leap_year':
            csiyi__emnae += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            csiyi__emnae += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            fpgxe__ykttf = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            csiyi__emnae += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            csiyi__emnae += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            csiyi__emnae += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(fpgxe__ykttf[field]))
        else:
            csiyi__emnae += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            csiyi__emnae += '        out_arr[i] = ts.' + field + '\n'
        csiyi__emnae += """    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
        yqgxx__aqegu = {}
        exec(csiyi__emnae, {'bodo': bodo, 'numba': numba, 'np': np},
            yqgxx__aqegu)
        impl = yqgxx__aqegu['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        sifw__nzk = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(sifw__nzk)


_install_date_fields()


def create_date_method_overload(method):
    cyawb__dbxyg = method in ['day_name', 'month_name']
    if cyawb__dbxyg:
        csiyi__emnae = 'def overload_method(S_dt, locale=None):\n'
        csiyi__emnae += '    unsupported_args = dict(locale=locale)\n'
        csiyi__emnae += '    arg_defaults = dict(locale=None)\n'
        csiyi__emnae += '    bodo.utils.typing.check_unsupported_args(\n'
        csiyi__emnae += f"        'Series.dt.{method}',\n"
        csiyi__emnae += '        unsupported_args,\n'
        csiyi__emnae += '        arg_defaults,\n'
        csiyi__emnae += "        package_name='pandas',\n"
        csiyi__emnae += "        module_name='Series',\n"
        csiyi__emnae += '    )\n'
    else:
        csiyi__emnae = 'def overload_method(S_dt):\n'
        csiyi__emnae += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    csiyi__emnae += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    csiyi__emnae += '        return\n'
    if cyawb__dbxyg:
        csiyi__emnae += '    def impl(S_dt, locale=None):\n'
    else:
        csiyi__emnae += '    def impl(S_dt):\n'
    csiyi__emnae += '        S = S_dt._obj\n'
    csiyi__emnae += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    csiyi__emnae += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    csiyi__emnae += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    csiyi__emnae += '        numba.parfors.parfor.init_prange()\n'
    csiyi__emnae += '        n = len(arr)\n'
    if cyawb__dbxyg:
        csiyi__emnae += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        csiyi__emnae += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    csiyi__emnae += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    csiyi__emnae += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    csiyi__emnae += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    csiyi__emnae += '                continue\n'
    csiyi__emnae += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    csiyi__emnae += f'            method_val = ts.{method}()\n'
    if cyawb__dbxyg:
        csiyi__emnae += '            out_arr[i] = method_val\n'
    else:
        csiyi__emnae += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    csiyi__emnae += """        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    csiyi__emnae += '    return impl\n'
    yqgxx__aqegu = {}
    exec(csiyi__emnae, {'bodo': bodo, 'numba': numba, 'np': np}, yqgxx__aqegu)
    overload_method = yqgxx__aqegu['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        sifw__nzk = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            sifw__nzk)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        wldqu__srwlf = S_dt._obj
        ecbb__qgbk = bodo.hiframes.pd_series_ext.get_series_data(wldqu__srwlf)
        gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(wldqu__srwlf)
        zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(wldqu__srwlf)
        numba.parfors.parfor.init_prange()
        tzzdx__kontz = len(ecbb__qgbk)
        iuti__zca = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            tzzdx__kontz)
        for zml__rygx in numba.parfors.parfor.internal_prange(tzzdx__kontz):
            vqukb__ksysa = ecbb__qgbk[zml__rygx]
            fxu__lcul = bodo.utils.conversion.box_if_dt64(vqukb__ksysa)
            iuti__zca[zml__rygx] = datetime.date(fxu__lcul.year, fxu__lcul.
                month, fxu__lcul.day)
        return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
            gpjd__rvfr, zsii__xjb)
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
            jje__buwcf = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            vhq__kkr = 'convert_numpy_timedelta64_to_pd_timedelta'
            crr__nyfb = 'np.empty(n, np.int64)'
            pixhn__bfppn = attr
        elif attr == 'isocalendar':
            jje__buwcf = ['year', 'week', 'day']
            vhq__kkr = 'convert_datetime64_to_timestamp'
            crr__nyfb = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            pixhn__bfppn = attr + '()'
        csiyi__emnae = 'def impl(S_dt):\n'
        csiyi__emnae += '    S = S_dt._obj\n'
        csiyi__emnae += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        csiyi__emnae += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        csiyi__emnae += '    numba.parfors.parfor.init_prange()\n'
        csiyi__emnae += '    n = len(arr)\n'
        for field in jje__buwcf:
            csiyi__emnae += '    {} = {}\n'.format(field, crr__nyfb)
        csiyi__emnae += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        csiyi__emnae += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in jje__buwcf:
            csiyi__emnae += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        csiyi__emnae += '            continue\n'
        zggx__oftpt = '(' + '[i], '.join(jje__buwcf) + '[i])'
        csiyi__emnae += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(zggx__oftpt, vhq__kkr, pixhn__bfppn))
        eznu__gun = '(' + ', '.join(jje__buwcf) + ')'
        csiyi__emnae += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(eznu__gun))
        yqgxx__aqegu = {}
        exec(csiyi__emnae, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(jje__buwcf))}, yqgxx__aqegu)
        impl = yqgxx__aqegu['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    naan__lmn = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, ojamn__icttd in naan__lmn:
        sifw__nzk = create_series_dt_df_output_overload(attr)
        ojamn__icttd(SeriesDatetimePropertiesType, attr, inline='always')(
            sifw__nzk)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        csiyi__emnae = 'def impl(S_dt):\n'
        csiyi__emnae += '    S = S_dt._obj\n'
        csiyi__emnae += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        csiyi__emnae += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        csiyi__emnae += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        csiyi__emnae += '    numba.parfors.parfor.init_prange()\n'
        csiyi__emnae += '    n = len(A)\n'
        csiyi__emnae += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        csiyi__emnae += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        csiyi__emnae += '        if bodo.libs.array_kernels.isna(A, i):\n'
        csiyi__emnae += '            bodo.libs.array_kernels.setna(B, i)\n'
        csiyi__emnae += '            continue\n'
        csiyi__emnae += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            csiyi__emnae += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            csiyi__emnae += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            csiyi__emnae += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            csiyi__emnae += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        csiyi__emnae += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        yqgxx__aqegu = {}
        exec(csiyi__emnae, {'numba': numba, 'np': np, 'bodo': bodo},
            yqgxx__aqegu)
        impl = yqgxx__aqegu['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        csiyi__emnae = 'def impl(S_dt):\n'
        csiyi__emnae += '    S = S_dt._obj\n'
        csiyi__emnae += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        csiyi__emnae += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        csiyi__emnae += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        csiyi__emnae += '    numba.parfors.parfor.init_prange()\n'
        csiyi__emnae += '    n = len(A)\n'
        if method == 'total_seconds':
            csiyi__emnae += '    B = np.empty(n, np.float64)\n'
        else:
            csiyi__emnae += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        csiyi__emnae += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        csiyi__emnae += '        if bodo.libs.array_kernels.isna(A, i):\n'
        csiyi__emnae += '            bodo.libs.array_kernels.setna(B, i)\n'
        csiyi__emnae += '            continue\n'
        csiyi__emnae += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            csiyi__emnae += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            csiyi__emnae += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            csiyi__emnae += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            csiyi__emnae += '    return B\n'
        yqgxx__aqegu = {}
        exec(csiyi__emnae, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, yqgxx__aqegu)
        impl = yqgxx__aqegu['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        sifw__nzk = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(sifw__nzk)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        sifw__nzk = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            sifw__nzk)


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
        wldqu__srwlf = S_dt._obj
        ezgo__eyc = bodo.hiframes.pd_series_ext.get_series_data(wldqu__srwlf)
        gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(wldqu__srwlf)
        zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(wldqu__srwlf)
        numba.parfors.parfor.init_prange()
        tzzdx__kontz = len(ezgo__eyc)
        ocqg__zcx = bodo.libs.str_arr_ext.pre_alloc_string_array(tzzdx__kontz,
            -1)
        for lhbjd__jufm in numba.parfors.parfor.internal_prange(tzzdx__kontz):
            if bodo.libs.array_kernels.isna(ezgo__eyc, lhbjd__jufm):
                bodo.libs.array_kernels.setna(ocqg__zcx, lhbjd__jufm)
                continue
            ocqg__zcx[lhbjd__jufm] = bodo.utils.conversion.box_if_dt64(
                ezgo__eyc[lhbjd__jufm]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(ocqg__zcx,
            gpjd__rvfr, zsii__xjb)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        wldqu__srwlf = S_dt._obj
        tid__dxix = get_series_data(wldqu__srwlf).tz_convert(tz)
        gpjd__rvfr = get_series_index(wldqu__srwlf)
        zsii__xjb = get_series_name(wldqu__srwlf)
        return init_series(tid__dxix, gpjd__rvfr, zsii__xjb)
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
        wnzal__mqww = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        vrrtg__jwnvq = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', wnzal__mqww,
            vrrtg__jwnvq, package_name='pandas', module_name='Series')
        csiyi__emnae = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        csiyi__emnae += '    S = S_dt._obj\n'
        csiyi__emnae += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        csiyi__emnae += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        csiyi__emnae += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        csiyi__emnae += '    numba.parfors.parfor.init_prange()\n'
        csiyi__emnae += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            csiyi__emnae += (
                "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n")
        else:
            csiyi__emnae += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        csiyi__emnae += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        csiyi__emnae += '        if bodo.libs.array_kernels.isna(A, i):\n'
        csiyi__emnae += '            bodo.libs.array_kernels.setna(B, i)\n'
        csiyi__emnae += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            uabi__bya = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            wxobj__sdm = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            uabi__bya = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            wxobj__sdm = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        csiyi__emnae += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            wxobj__sdm, uabi__bya, method)
        csiyi__emnae += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        yqgxx__aqegu = {}
        exec(csiyi__emnae, {'numba': numba, 'np': np, 'bodo': bodo},
            yqgxx__aqegu)
        impl = yqgxx__aqegu['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    enrr__havz = ['ceil', 'floor', 'round']
    for method in enrr__havz:
        sifw__nzk = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            sifw__nzk)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dhri__bareq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                wqcjy__omf = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dhri__bareq)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                qxxak__sjywe = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pbrr__hytmh = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    qxxak__sjywe)
                tzzdx__kontz = len(wqcjy__omf)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    dcy__ujood = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wqcjy__omf[zml__rygx]))
                    gpilr__jsh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(pbrr__hytmh[zml__rygx]))
                    if dcy__ujood == hquyq__uwu or gpilr__jsh == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(dcy__ujood, gpilr__jsh)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                pbrr__hytmh = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, dt64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pbrr__hytmh[zml__rygx]))
                    if bxnyr__teft == hquyq__uwu or kkxao__njqq == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, kkxao__njqq)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                pbrr__hytmh = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, dt64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pbrr__hytmh[zml__rygx]))
                    if bxnyr__teft == hquyq__uwu or kkxao__njqq == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, kkxao__njqq)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                kwqd__jcera = rhs.value
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if bxnyr__teft == hquyq__uwu or kwqd__jcera == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, kwqd__jcera)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                kwqd__jcera = lhs.value
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if kwqd__jcera == hquyq__uwu or bxnyr__teft == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(kwqd__jcera, bxnyr__teft)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, dt64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                btuk__mvbp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(btuk__mvbp))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if bxnyr__teft == hquyq__uwu or kkxao__njqq == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, kkxao__njqq)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, dt64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                btuk__mvbp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(btuk__mvbp))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    bxnyr__teft = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if bxnyr__teft == hquyq__uwu or kkxao__njqq == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, kkxao__njqq)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                cedl__xpwlk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                bxnyr__teft = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    cedl__xpwlk)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    evyu__bic = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ecbb__qgbk[zml__rygx])
                    if evyu__bic == hquyq__uwu or bxnyr__teft == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(evyu__bic, bxnyr__teft)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                cedl__xpwlk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                bxnyr__teft = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    cedl__xpwlk)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    evyu__bic = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ecbb__qgbk[zml__rygx])
                    if bxnyr__teft == hquyq__uwu or evyu__bic == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(bxnyr__teft, evyu__bic)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tbrk__oasq = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ecbb__qgbk = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tbrk__oasq))
                btuk__mvbp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(btuk__mvbp))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    rcbcy__xlbpw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ecbb__qgbk[zml__rygx]))
                    if kkxao__njqq == hquyq__uwu or rcbcy__xlbpw == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(rcbcy__xlbpw, kkxao__njqq)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tbrk__oasq = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ecbb__qgbk = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                wldqu__srwlf = np.empty(tzzdx__kontz, timedelta64_dtype)
                hquyq__uwu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tbrk__oasq))
                btuk__mvbp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kkxao__njqq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(btuk__mvbp))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    rcbcy__xlbpw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ecbb__qgbk[zml__rygx]))
                    if kkxao__njqq == hquyq__uwu or rcbcy__xlbpw == hquyq__uwu:
                        qjye__ntsj = hquyq__uwu
                    else:
                        qjye__ntsj = op(kkxao__njqq, rcbcy__xlbpw)
                    wldqu__srwlf[zml__rygx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        qjye__ntsj)
                return bodo.hiframes.pd_series_ext.init_series(wldqu__srwlf,
                    gpjd__rvfr, zsii__xjb)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            jbmmb__iegpc = True
        else:
            jbmmb__iegpc = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tbrk__oasq = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ecbb__qgbk = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tbrk__oasq))
                jwt__ora = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ssxt__oxptq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jwt__ora))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    tmotx__mofnm = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ecbb__qgbk[zml__rygx]))
                    if tmotx__mofnm == hquyq__uwu or ssxt__oxptq == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(tmotx__mofnm, ssxt__oxptq)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tbrk__oasq = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ecbb__qgbk = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tbrk__oasq))
                ntvhu__ddih = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                tmotx__mofnm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ntvhu__ddih))
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    ssxt__oxptq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ecbb__qgbk[zml__rygx]))
                    if tmotx__mofnm == hquyq__uwu or ssxt__oxptq == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(tmotx__mofnm, ssxt__oxptq)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    tmotx__mofnm = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if tmotx__mofnm == hquyq__uwu or rhs.value == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(tmotx__mofnm, rhs.value)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    ssxt__oxptq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if ssxt__oxptq == hquyq__uwu or lhs.value == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(lhs.value, ssxt__oxptq)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                aom__ffv = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                ajucu__ftf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    aom__ffv)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    tmotx__mofnm = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if tmotx__mofnm == hquyq__uwu or ajucu__ftf == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(tmotx__mofnm, ajucu__ftf)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            tbrk__oasq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                ifv__krd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ecbb__qgbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifv__krd)
                gpjd__rvfr = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zsii__xjb = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                tzzdx__kontz = len(ecbb__qgbk)
                iuti__zca = bodo.libs.bool_arr_ext.alloc_bool_array(
                    tzzdx__kontz)
                hquyq__uwu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tbrk__oasq)
                aom__ffv = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                ajucu__ftf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    aom__ffv)
                for zml__rygx in numba.parfors.parfor.internal_prange(
                    tzzdx__kontz):
                    cedl__xpwlk = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ecbb__qgbk[zml__rygx]))
                    if cedl__xpwlk == hquyq__uwu or ajucu__ftf == hquyq__uwu:
                        qjye__ntsj = jbmmb__iegpc
                    else:
                        qjye__ntsj = op(ajucu__ftf, cedl__xpwlk)
                    iuti__zca[zml__rygx] = qjye__ntsj
                return bodo.hiframes.pd_series_ext.init_series(iuti__zca,
                    gpjd__rvfr, zsii__xjb)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for ilz__yrnkv in series_dt_unsupported_attrs:
        xnzwz__pfz = 'Series.dt.' + ilz__yrnkv
        overload_attribute(SeriesDatetimePropertiesType, ilz__yrnkv)(
            create_unsupported_overload(xnzwz__pfz))
    for bbuj__lywaf in series_dt_unsupported_methods:
        xnzwz__pfz = 'Series.dt.' + bbuj__lywaf
        overload_method(SeriesDatetimePropertiesType, bbuj__lywaf,
            no_unliteral=True)(create_unsupported_overload(xnzwz__pfz))


_install_series_dt_unsupported()
