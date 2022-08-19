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
        zmivd__eza = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(zmivd__eza)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zhlc__qtrj = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, zhlc__qtrj)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ipjj__lbxkj, = args
        omff__cvrsy = signature.return_type
        ewvv__iht = cgutils.create_struct_proxy(omff__cvrsy)(context, builder)
        ewvv__iht.obj = ipjj__lbxkj
        context.nrt.incref(builder, signature.args[0], ipjj__lbxkj)
        return ewvv__iht._getvalue()
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
        sldt__eludp = 'def impl(S_dt):\n'
        sldt__eludp += '    S = S_dt._obj\n'
        sldt__eludp += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        sldt__eludp += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        sldt__eludp += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        sldt__eludp += '    numba.parfors.parfor.init_prange()\n'
        sldt__eludp += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            sldt__eludp += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            sldt__eludp += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        sldt__eludp += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        sldt__eludp += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        sldt__eludp += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        sldt__eludp += '            continue\n'
        sldt__eludp += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            sldt__eludp += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                sldt__eludp += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            sldt__eludp += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            wwl__lvhcj = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            sldt__eludp += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            sldt__eludp += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            sldt__eludp += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(wwl__lvhcj[field]))
        elif field == 'is_leap_year':
            sldt__eludp += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            sldt__eludp += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            wwl__lvhcj = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            sldt__eludp += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            sldt__eludp += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            sldt__eludp += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(wwl__lvhcj[field]))
        else:
            sldt__eludp += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            sldt__eludp += '        out_arr[i] = ts.' + field + '\n'
        sldt__eludp += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        wokfk__cwu = {}
        exec(sldt__eludp, {'bodo': bodo, 'numba': numba, 'np': np}, wokfk__cwu)
        impl = wokfk__cwu['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        kcvq__gfv = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(kcvq__gfv)


_install_date_fields()


def create_date_method_overload(method):
    vcm__ggpc = method in ['day_name', 'month_name']
    if vcm__ggpc:
        sldt__eludp = 'def overload_method(S_dt, locale=None):\n'
        sldt__eludp += '    unsupported_args = dict(locale=locale)\n'
        sldt__eludp += '    arg_defaults = dict(locale=None)\n'
        sldt__eludp += '    bodo.utils.typing.check_unsupported_args(\n'
        sldt__eludp += f"        'Series.dt.{method}',\n"
        sldt__eludp += '        unsupported_args,\n'
        sldt__eludp += '        arg_defaults,\n'
        sldt__eludp += "        package_name='pandas',\n"
        sldt__eludp += "        module_name='Series',\n"
        sldt__eludp += '    )\n'
    else:
        sldt__eludp = 'def overload_method(S_dt):\n'
        sldt__eludp += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    sldt__eludp += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    sldt__eludp += '        return\n'
    if vcm__ggpc:
        sldt__eludp += '    def impl(S_dt, locale=None):\n'
    else:
        sldt__eludp += '    def impl(S_dt):\n'
    sldt__eludp += '        S = S_dt._obj\n'
    sldt__eludp += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    sldt__eludp += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    sldt__eludp += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    sldt__eludp += '        numba.parfors.parfor.init_prange()\n'
    sldt__eludp += '        n = len(arr)\n'
    if vcm__ggpc:
        sldt__eludp += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        sldt__eludp += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    sldt__eludp += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    sldt__eludp += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    sldt__eludp += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    sldt__eludp += '                continue\n'
    sldt__eludp += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    sldt__eludp += f'            method_val = ts.{method}()\n'
    if vcm__ggpc:
        sldt__eludp += '            out_arr[i] = method_val\n'
    else:
        sldt__eludp += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    sldt__eludp += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    sldt__eludp += '    return impl\n'
    wokfk__cwu = {}
    exec(sldt__eludp, {'bodo': bodo, 'numba': numba, 'np': np}, wokfk__cwu)
    overload_method = wokfk__cwu['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        kcvq__gfv = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kcvq__gfv)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        rbozw__hkv = S_dt._obj
        yzynt__ariq = bodo.hiframes.pd_series_ext.get_series_data(rbozw__hkv)
        fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rbozw__hkv)
        zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rbozw__hkv)
        numba.parfors.parfor.init_prange()
        eeix__qrmup = len(yzynt__ariq)
        vkk__cxocs = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            eeix__qrmup)
        for lmmh__tdgt in numba.parfors.parfor.internal_prange(eeix__qrmup):
            miqj__znco = yzynt__ariq[lmmh__tdgt]
            ncke__uxro = bodo.utils.conversion.box_if_dt64(miqj__znco)
            vkk__cxocs[lmmh__tdgt] = datetime.date(ncke__uxro.year,
                ncke__uxro.month, ncke__uxro.day)
        return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
            fwf__mkmop, zmivd__eza)
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
            yidl__pbor = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            tim__uwfvn = 'convert_numpy_timedelta64_to_pd_timedelta'
            uvru__kemzo = 'np.empty(n, np.int64)'
            ppxxg__jsy = attr
        elif attr == 'isocalendar':
            yidl__pbor = ['year', 'week', 'day']
            tim__uwfvn = 'convert_datetime64_to_timestamp'
            uvru__kemzo = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            ppxxg__jsy = attr + '()'
        sldt__eludp = 'def impl(S_dt):\n'
        sldt__eludp += '    S = S_dt._obj\n'
        sldt__eludp += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        sldt__eludp += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        sldt__eludp += '    numba.parfors.parfor.init_prange()\n'
        sldt__eludp += '    n = len(arr)\n'
        for field in yidl__pbor:
            sldt__eludp += '    {} = {}\n'.format(field, uvru__kemzo)
        sldt__eludp += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        sldt__eludp += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in yidl__pbor:
            sldt__eludp += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        sldt__eludp += '            continue\n'
        lzey__gsl = '(' + '[i], '.join(yidl__pbor) + '[i])'
        sldt__eludp += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(lzey__gsl, tim__uwfvn, ppxxg__jsy))
        ofs__usxv = '(' + ', '.join(yidl__pbor) + ')'
        sldt__eludp += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(ofs__usxv))
        wokfk__cwu = {}
        exec(sldt__eludp, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(yidl__pbor))}, wokfk__cwu)
        impl = wokfk__cwu['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    hgzhm__pnun = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, nrloi__ncao in hgzhm__pnun:
        kcvq__gfv = create_series_dt_df_output_overload(attr)
        nrloi__ncao(SeriesDatetimePropertiesType, attr, inline='always')(
            kcvq__gfv)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        sldt__eludp = 'def impl(S_dt):\n'
        sldt__eludp += '    S = S_dt._obj\n'
        sldt__eludp += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        sldt__eludp += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        sldt__eludp += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        sldt__eludp += '    numba.parfors.parfor.init_prange()\n'
        sldt__eludp += '    n = len(A)\n'
        sldt__eludp += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        sldt__eludp += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        sldt__eludp += '        if bodo.libs.array_kernels.isna(A, i):\n'
        sldt__eludp += '            bodo.libs.array_kernels.setna(B, i)\n'
        sldt__eludp += '            continue\n'
        sldt__eludp += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            sldt__eludp += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            sldt__eludp += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            sldt__eludp += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            sldt__eludp += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        sldt__eludp += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        wokfk__cwu = {}
        exec(sldt__eludp, {'numba': numba, 'np': np, 'bodo': bodo}, wokfk__cwu)
        impl = wokfk__cwu['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        sldt__eludp = 'def impl(S_dt):\n'
        sldt__eludp += '    S = S_dt._obj\n'
        sldt__eludp += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        sldt__eludp += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        sldt__eludp += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        sldt__eludp += '    numba.parfors.parfor.init_prange()\n'
        sldt__eludp += '    n = len(A)\n'
        if method == 'total_seconds':
            sldt__eludp += '    B = np.empty(n, np.float64)\n'
        else:
            sldt__eludp += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        sldt__eludp += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        sldt__eludp += '        if bodo.libs.array_kernels.isna(A, i):\n'
        sldt__eludp += '            bodo.libs.array_kernels.setna(B, i)\n'
        sldt__eludp += '            continue\n'
        sldt__eludp += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            sldt__eludp += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            sldt__eludp += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            sldt__eludp += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            sldt__eludp += '    return B\n'
        wokfk__cwu = {}
        exec(sldt__eludp, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, wokfk__cwu)
        impl = wokfk__cwu['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        kcvq__gfv = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(kcvq__gfv)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        kcvq__gfv = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kcvq__gfv)


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
        rbozw__hkv = S_dt._obj
        umz__dyu = bodo.hiframes.pd_series_ext.get_series_data(rbozw__hkv)
        fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rbozw__hkv)
        zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rbozw__hkv)
        numba.parfors.parfor.init_prange()
        eeix__qrmup = len(umz__dyu)
        qpvl__ofhsf = bodo.libs.str_arr_ext.pre_alloc_string_array(eeix__qrmup,
            -1)
        for kex__ajq in numba.parfors.parfor.internal_prange(eeix__qrmup):
            if bodo.libs.array_kernels.isna(umz__dyu, kex__ajq):
                bodo.libs.array_kernels.setna(qpvl__ofhsf, kex__ajq)
                continue
            qpvl__ofhsf[kex__ajq] = bodo.utils.conversion.box_if_dt64(umz__dyu
                [kex__ajq]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(qpvl__ofhsf,
            fwf__mkmop, zmivd__eza)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        rbozw__hkv = S_dt._obj
        zpeqe__hyfm = get_series_data(rbozw__hkv).tz_convert(tz)
        fwf__mkmop = get_series_index(rbozw__hkv)
        zmivd__eza = get_series_name(rbozw__hkv)
        return init_series(zpeqe__hyfm, fwf__mkmop, zmivd__eza)
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
        quq__mhm = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        fjvq__ktmk = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', quq__mhm, fjvq__ktmk,
            package_name='pandas', module_name='Series')
        sldt__eludp = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        sldt__eludp += '    S = S_dt._obj\n'
        sldt__eludp += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        sldt__eludp += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        sldt__eludp += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        sldt__eludp += '    numba.parfors.parfor.init_prange()\n'
        sldt__eludp += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            sldt__eludp += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            sldt__eludp += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        sldt__eludp += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        sldt__eludp += '        if bodo.libs.array_kernels.isna(A, i):\n'
        sldt__eludp += '            bodo.libs.array_kernels.setna(B, i)\n'
        sldt__eludp += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            ikv__cksa = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            xza__komd = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            ikv__cksa = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            xza__komd = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        sldt__eludp += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            xza__komd, ikv__cksa, method)
        sldt__eludp += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        wokfk__cwu = {}
        exec(sldt__eludp, {'numba': numba, 'np': np, 'bodo': bodo}, wokfk__cwu)
        impl = wokfk__cwu['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    tvo__oueog = ['ceil', 'floor', 'round']
    for method in tvo__oueog:
        kcvq__gfv = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kcvq__gfv)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                jwtna__zkucq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qecka__yvrjx = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    jwtna__zkucq)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                zujxg__rlza = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                quu__tfw = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    zujxg__rlza)
                eeix__qrmup = len(qecka__yvrjx)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    ssc__sqpr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qecka__yvrjx[lmmh__tdgt])
                    kpcc__chi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        quu__tfw[lmmh__tdgt])
                    if ssc__sqpr == cvya__ezvuk or kpcc__chi == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(ssc__sqpr, kpcc__chi)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                quu__tfw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, dt64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    lly__pns = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(quu__tfw[lmmh__tdgt]))
                    if cli__qpy == cvya__ezvuk or lly__pns == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, lly__pns)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                quu__tfw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, dt64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    lly__pns = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(quu__tfw[lmmh__tdgt]))
                    if cli__qpy == cvya__ezvuk or lly__pns == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, lly__pns)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                goveo__yrv = rhs.value
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if cli__qpy == cvya__ezvuk or goveo__yrv == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, goveo__yrv)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                goveo__yrv = lhs.value
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if goveo__yrv == cvya__ezvuk or cli__qpy == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(goveo__yrv, cli__qpy)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, dt64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                zbv__cxgxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                lly__pns = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(zbv__cxgxe))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if cli__qpy == cvya__ezvuk or lly__pns == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, lly__pns)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, dt64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                zbv__cxgxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                lly__pns = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(zbv__cxgxe))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if cli__qpy == cvya__ezvuk or lly__pns == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, lly__pns)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                oupsi__bwjq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    oupsi__bwjq)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    ffrjn__fyoq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if ffrjn__fyoq == cvya__ezvuk or cli__qpy == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(ffrjn__fyoq, cli__qpy)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                oupsi__bwjq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                cli__qpy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    oupsi__bwjq)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    ffrjn__fyoq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if cli__qpy == cvya__ezvuk or ffrjn__fyoq == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(cli__qpy, ffrjn__fyoq)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jqygf__pmr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yzynt__ariq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jqygf__pmr))
                zbv__cxgxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                lly__pns = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(zbv__cxgxe))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    hagt__wpj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if lly__pns == cvya__ezvuk or hagt__wpj == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(hagt__wpj, lly__pns)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jqygf__pmr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yzynt__ariq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                rbozw__hkv = np.empty(eeix__qrmup, timedelta64_dtype)
                cvya__ezvuk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jqygf__pmr))
                zbv__cxgxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                lly__pns = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(zbv__cxgxe))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    hagt__wpj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if lly__pns == cvya__ezvuk or hagt__wpj == cvya__ezvuk:
                        xlw__ruf = cvya__ezvuk
                    else:
                        xlw__ruf = op(lly__pns, hagt__wpj)
                    rbozw__hkv[lmmh__tdgt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        xlw__ruf)
                return bodo.hiframes.pd_series_ext.init_series(rbozw__hkv,
                    fwf__mkmop, zmivd__eza)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            ebrcm__sgkvy = True
        else:
            ebrcm__sgkvy = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jqygf__pmr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yzynt__ariq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jqygf__pmr))
                pfo__lbazy = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                yldh__sfpy = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pfo__lbazy))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    qszz__qwb = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if qszz__qwb == cvya__ezvuk or yldh__sfpy == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(qszz__qwb, yldh__sfpy)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jqygf__pmr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yzynt__ariq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jqygf__pmr))
                xcj__xcg = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                qszz__qwb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(xcj__xcg))
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    yldh__sfpy = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if qszz__qwb == cvya__ezvuk or yldh__sfpy == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(qszz__qwb, yldh__sfpy)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    qszz__qwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if qszz__qwb == cvya__ezvuk or rhs.value == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(qszz__qwb, rhs.value)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    yldh__sfpy = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if yldh__sfpy == cvya__ezvuk or lhs.value == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(lhs.value, yldh__sfpy)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                frs__igq = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                ijug__fyf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    frs__igq)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    qszz__qwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yzynt__ariq[lmmh__tdgt])
                    if qszz__qwb == cvya__ezvuk or ijug__fyf == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(qszz__qwb, ijug__fyf)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            jqygf__pmr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                mnm__fqlme = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzynt__ariq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    mnm__fqlme)
                fwf__mkmop = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zmivd__eza = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                eeix__qrmup = len(yzynt__ariq)
                vkk__cxocs = bodo.libs.bool_arr_ext.alloc_bool_array(
                    eeix__qrmup)
                cvya__ezvuk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jqygf__pmr)
                frs__igq = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                ijug__fyf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    frs__igq)
                for lmmh__tdgt in numba.parfors.parfor.internal_prange(
                    eeix__qrmup):
                    oupsi__bwjq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yzynt__ariq[lmmh__tdgt]))
                    if oupsi__bwjq == cvya__ezvuk or ijug__fyf == cvya__ezvuk:
                        xlw__ruf = ebrcm__sgkvy
                    else:
                        xlw__ruf = op(ijug__fyf, oupsi__bwjq)
                    vkk__cxocs[lmmh__tdgt] = xlw__ruf
                return bodo.hiframes.pd_series_ext.init_series(vkk__cxocs,
                    fwf__mkmop, zmivd__eza)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for uxod__moyml in series_dt_unsupported_attrs:
        hwb__obqt = 'Series.dt.' + uxod__moyml
        overload_attribute(SeriesDatetimePropertiesType, uxod__moyml)(
            create_unsupported_overload(hwb__obqt))
    for hly__mdtk in series_dt_unsupported_methods:
        hwb__obqt = 'Series.dt.' + hly__mdtk
        overload_method(SeriesDatetimePropertiesType, hly__mdtk,
            no_unliteral=True)(create_unsupported_overload(hwb__obqt))


_install_series_dt_unsupported()
