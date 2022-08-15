"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        if isinstance(obj_type, bodo.SeriesType):
            ojde__bnh = 'Series'
        else:
            ojde__bnh = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{ojde__bnh}.rolling()')
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wyvvz__dabmq = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, wyvvz__dabmq)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    lds__jwenp = dict(win_type=win_type, axis=axis, closed=closed)
    ndw__hllb = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', lds__jwenp, ndw__hllb,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    lds__jwenp = dict(win_type=win_type, axis=axis, closed=closed)
    ndw__hllb = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', lds__jwenp, ndw__hllb,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        npzru__qmxv, ntj__ddaxf, etg__zhdpz, uoef__vbaig, udjz__jit = args
        pdwko__pwfbq = signature.return_type
        ala__lpzus = cgutils.create_struct_proxy(pdwko__pwfbq)(context, builder
            )
        ala__lpzus.obj = npzru__qmxv
        ala__lpzus.window = ntj__ddaxf
        ala__lpzus.min_periods = etg__zhdpz
        ala__lpzus.center = uoef__vbaig
        context.nrt.incref(builder, signature.args[0], npzru__qmxv)
        context.nrt.incref(builder, signature.args[1], ntj__ddaxf)
        context.nrt.incref(builder, signature.args[2], etg__zhdpz)
        context.nrt.incref(builder, signature.args[3], uoef__vbaig)
        return ala__lpzus._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    pdwko__pwfbq = RollingType(obj_type, window_type, on, selection, False)
    return pdwko__pwfbq(obj_type, window_type, min_periods_type,
        center_type, on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    hwq__lvnni = not isinstance(rolling.window_type, types.Integer)
    nkz__xnz = 'variable' if hwq__lvnni else 'fixed'
    sgsgv__gzi = 'None'
    if hwq__lvnni:
        sgsgv__gzi = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    arxul__charb = []
    jnjm__ogzi = 'on_arr, ' if hwq__lvnni else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{nkz__xnz}(bodo.hiframes.pd_series_ext.get_series_data(df), {jnjm__ogzi}index_arr, window, minp, center, func, raw)'
            , sgsgv__gzi, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    nxtpl__zwump = rolling.obj_type.data
    out_cols = []
    for mau__bosj in rolling.selection:
        lny__agr = rolling.obj_type.columns.index(mau__bosj)
        if mau__bosj == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            cfdxf__fzn = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {lny__agr})'
                )
            out_cols.append(mau__bosj)
        else:
            if not isinstance(nxtpl__zwump[lny__agr].dtype, (types.Boolean,
                types.Number)):
                continue
            cfdxf__fzn = (
                f'bodo.hiframes.rolling.rolling_{nkz__xnz}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {lny__agr}), {jnjm__ogzi}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(mau__bosj)
        arxul__charb.append(cfdxf__fzn)
    return ', '.join(arxul__charb), sgsgv__gzi, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    lds__jwenp = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    ndw__hllb = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', lds__jwenp, ndw__hllb,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    lds__jwenp = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    ndw__hllb = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', lds__jwenp, ndw__hllb,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        tfq__kplo = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        wgz__lrl = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{mxv__inmp}'" if
                isinstance(mxv__inmp, str) else f'{mxv__inmp}' for
                mxv__inmp in rolling.selection if mxv__inmp != rolling.on))
        nyg__mplit = rny__naqmm = ''
        if fname == 'apply':
            nyg__mplit = 'func, raw, args, kwargs'
            rny__naqmm = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            nyg__mplit = rny__naqmm = 'other, pairwise'
        if fname == 'cov':
            nyg__mplit = rny__naqmm = 'other, pairwise, ddof'
        xamxx__ejo = (
            f'lambda df, window, minp, center, {nyg__mplit}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {wgz__lrl}){selection}.{fname}({rny__naqmm})'
            )
        tfq__kplo += f"""  return rolling.obj.apply({xamxx__ejo}, rolling.window, rolling.min_periods, rolling.center, {nyg__mplit})
"""
        ulc__njp = {}
        exec(tfq__kplo, {'bodo': bodo}, ulc__njp)
        impl = ulc__njp['impl']
        return impl
    afy__weaft = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if afy__weaft else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if afy__weaft else rolling.obj_type.columns
        other_cols = None if afy__weaft else other.columns
        arxul__charb, sgsgv__gzi = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        arxul__charb, sgsgv__gzi, out_cols = _gen_df_rolling_out_data(rolling)
    usdz__gyyga = afy__weaft or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    ylw__eew = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    ylw__eew += '  df = rolling.obj\n'
    ylw__eew += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if afy__weaft else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    ojde__bnh = 'None'
    if afy__weaft:
        ojde__bnh = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif usdz__gyyga:
        mau__bosj = (set(out_cols) - set([rolling.on])).pop()
        ojde__bnh = f"'{mau__bosj}'" if isinstance(mau__bosj, str) else str(
            mau__bosj)
    ylw__eew += f'  name = {ojde__bnh}\n'
    ylw__eew += '  window = rolling.window\n'
    ylw__eew += '  center = rolling.center\n'
    ylw__eew += '  minp = rolling.min_periods\n'
    ylw__eew += f'  on_arr = {sgsgv__gzi}\n'
    if fname == 'apply':
        ylw__eew += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        ylw__eew += f"  func = '{fname}'\n"
        ylw__eew += f'  index_arr = None\n'
        ylw__eew += f'  raw = False\n'
    if usdz__gyyga:
        ylw__eew += (
            f'  return bodo.hiframes.pd_series_ext.init_series({arxul__charb}, index, name)'
            )
        ulc__njp = {}
        cliis__rzx = {'bodo': bodo}
        exec(ylw__eew, cliis__rzx, ulc__njp)
        impl = ulc__njp['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(ylw__eew, out_cols,
        arxul__charb)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        cgzuf__rdyj = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(cgzuf__rdyj)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    kmk__edcmc = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(kmk__edcmc) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    hwq__lvnni = not isinstance(window_type, types.Integer)
    sgsgv__gzi = 'None'
    if hwq__lvnni:
        sgsgv__gzi = 'bodo.utils.conversion.index_to_array(index)'
    jnjm__ogzi = 'on_arr, ' if hwq__lvnni else ''
    arxul__charb = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {jnjm__ogzi}window, minp, center)'
            , sgsgv__gzi)
    for mau__bosj in out_cols:
        if mau__bosj in df_cols and mau__bosj in other_cols:
            kddj__sdcqh = df_cols.index(mau__bosj)
            hbv__utanp = other_cols.index(mau__bosj)
            cfdxf__fzn = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {kddj__sdcqh}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {hbv__utanp}), {jnjm__ogzi}window, minp, center)'
                )
        else:
            cfdxf__fzn = 'np.full(len(df), np.nan)'
        arxul__charb.append(cfdxf__fzn)
    return ', '.join(arxul__charb), sgsgv__gzi


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    mkq__ksf = {'pairwise': pairwise, 'ddof': ddof}
    gwhfz__uflt = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        mkq__ksf, gwhfz__uflt, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    mkq__ksf = {'ddof': ddof, 'pairwise': pairwise}
    gwhfz__uflt = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        mkq__ksf, gwhfz__uflt, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, wkggb__mrnvk = args
        if isinstance(rolling, RollingType):
            kmk__edcmc = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(wkggb__mrnvk, (tuple, list)):
                if len(set(wkggb__mrnvk).difference(set(kmk__edcmc))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(wkggb__mrnvk).difference(set(kmk__edcmc))))
                selection = list(wkggb__mrnvk)
            else:
                if wkggb__mrnvk not in kmk__edcmc:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(wkggb__mrnvk))
                selection = [wkggb__mrnvk]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            ytdr__xlp = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(ytdr__xlp, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        kmk__edcmc = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            kmk__edcmc = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            kmk__edcmc = rolling.obj_type.columns
        if attr in kmk__edcmc:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    nam__undnx = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    nxtpl__zwump = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in nam__undnx):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        nrzda__mggej = nxtpl__zwump[nam__undnx.index(get_literal_value(on))]
        if not isinstance(nrzda__mggej, types.Array
            ) or nrzda__mggej.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(kqln__egrdv.dtype, (types.Boolean, types.Number)) for
        kqln__egrdv in nxtpl__zwump):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
