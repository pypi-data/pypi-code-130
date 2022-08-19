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
            gcjr__spdii = 'Series'
        else:
            gcjr__spdii = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{gcjr__spdii}.rolling()')
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
        txryi__qgu = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, txryi__qgu)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    pwwkn__iwb = dict(win_type=win_type, axis=axis, closed=closed)
    geq__nrhzi = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', pwwkn__iwb, geq__nrhzi,
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
    pwwkn__iwb = dict(win_type=win_type, axis=axis, closed=closed)
    geq__nrhzi = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', pwwkn__iwb, geq__nrhzi,
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
        clxb__zskw, lbb__rkaxw, sne__btgf, oijog__cnv, wegyj__jcg = args
        cmhpu__rjlw = signature.return_type
        ydlzx__wlf = cgutils.create_struct_proxy(cmhpu__rjlw)(context, builder)
        ydlzx__wlf.obj = clxb__zskw
        ydlzx__wlf.window = lbb__rkaxw
        ydlzx__wlf.min_periods = sne__btgf
        ydlzx__wlf.center = oijog__cnv
        context.nrt.incref(builder, signature.args[0], clxb__zskw)
        context.nrt.incref(builder, signature.args[1], lbb__rkaxw)
        context.nrt.incref(builder, signature.args[2], sne__btgf)
        context.nrt.incref(builder, signature.args[3], oijog__cnv)
        return ydlzx__wlf._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    cmhpu__rjlw = RollingType(obj_type, window_type, on, selection, False)
    return cmhpu__rjlw(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


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
    mcuv__mfun = not isinstance(rolling.window_type, types.Integer)
    ksgyn__agw = 'variable' if mcuv__mfun else 'fixed'
    tla__qhr = 'None'
    if mcuv__mfun:
        tla__qhr = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    ayq__blv = []
    wicb__cycoy = 'on_arr, ' if mcuv__mfun else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{ksgyn__agw}(bodo.hiframes.pd_series_ext.get_series_data(df), {wicb__cycoy}index_arr, window, minp, center, func, raw)'
            , tla__qhr, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    txwrw__ehgdy = rolling.obj_type.data
    out_cols = []
    for aiscv__qffub in rolling.selection:
        vyqat__xhivv = rolling.obj_type.columns.index(aiscv__qffub)
        if aiscv__qffub == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            byg__hjukl = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {vyqat__xhivv})'
                )
            out_cols.append(aiscv__qffub)
        else:
            if not isinstance(txwrw__ehgdy[vyqat__xhivv].dtype, (types.
                Boolean, types.Number)):
                continue
            byg__hjukl = (
                f'bodo.hiframes.rolling.rolling_{ksgyn__agw}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {vyqat__xhivv}), {wicb__cycoy}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(aiscv__qffub)
        ayq__blv.append(byg__hjukl)
    return ', '.join(ayq__blv), tla__qhr, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    pwwkn__iwb = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    geq__nrhzi = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', pwwkn__iwb, geq__nrhzi,
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
    pwwkn__iwb = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    geq__nrhzi = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', pwwkn__iwb, geq__nrhzi,
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
        ioxho__qqfvk = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        keaxb__plz = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{ltzy__zeve}'" if
                isinstance(ltzy__zeve, str) else f'{ltzy__zeve}' for
                ltzy__zeve in rolling.selection if ltzy__zeve != rolling.on))
        hxnjm__ykhk = rdx__ijgw = ''
        if fname == 'apply':
            hxnjm__ykhk = 'func, raw, args, kwargs'
            rdx__ijgw = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            hxnjm__ykhk = rdx__ijgw = 'other, pairwise'
        if fname == 'cov':
            hxnjm__ykhk = rdx__ijgw = 'other, pairwise, ddof'
        ljgy__kczn = (
            f'lambda df, window, minp, center, {hxnjm__ykhk}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {keaxb__plz}){selection}.{fname}({rdx__ijgw})'
            )
        ioxho__qqfvk += f"""  return rolling.obj.apply({ljgy__kczn}, rolling.window, rolling.min_periods, rolling.center, {hxnjm__ykhk})
"""
        rpcg__yzma = {}
        exec(ioxho__qqfvk, {'bodo': bodo}, rpcg__yzma)
        impl = rpcg__yzma['impl']
        return impl
    rsna__ttfz = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if rsna__ttfz else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if rsna__ttfz else rolling.obj_type.columns
        other_cols = None if rsna__ttfz else other.columns
        ayq__blv, tla__qhr = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        ayq__blv, tla__qhr, out_cols = _gen_df_rolling_out_data(rolling)
    yuozb__wxsjs = rsna__ttfz or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    wxbp__grua = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    wxbp__grua += '  df = rolling.obj\n'
    wxbp__grua += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if rsna__ttfz else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    gcjr__spdii = 'None'
    if rsna__ttfz:
        gcjr__spdii = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif yuozb__wxsjs:
        aiscv__qffub = (set(out_cols) - set([rolling.on])).pop()
        gcjr__spdii = f"'{aiscv__qffub}'" if isinstance(aiscv__qffub, str
            ) else str(aiscv__qffub)
    wxbp__grua += f'  name = {gcjr__spdii}\n'
    wxbp__grua += '  window = rolling.window\n'
    wxbp__grua += '  center = rolling.center\n'
    wxbp__grua += '  minp = rolling.min_periods\n'
    wxbp__grua += f'  on_arr = {tla__qhr}\n'
    if fname == 'apply':
        wxbp__grua += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        wxbp__grua += f"  func = '{fname}'\n"
        wxbp__grua += f'  index_arr = None\n'
        wxbp__grua += f'  raw = False\n'
    if yuozb__wxsjs:
        wxbp__grua += (
            f'  return bodo.hiframes.pd_series_ext.init_series({ayq__blv}, index, name)'
            )
        rpcg__yzma = {}
        rsids__yqral = {'bodo': bodo}
        exec(wxbp__grua, rsids__yqral, rpcg__yzma)
        impl = rpcg__yzma['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(wxbp__grua, out_cols,
        ayq__blv)


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
        ypxle__mciwf = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(ypxle__mciwf)


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
    iyssm__sjp = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(iyssm__sjp) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    mcuv__mfun = not isinstance(window_type, types.Integer)
    tla__qhr = 'None'
    if mcuv__mfun:
        tla__qhr = 'bodo.utils.conversion.index_to_array(index)'
    wicb__cycoy = 'on_arr, ' if mcuv__mfun else ''
    ayq__blv = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {wicb__cycoy}window, minp, center)'
            , tla__qhr)
    for aiscv__qffub in out_cols:
        if aiscv__qffub in df_cols and aiscv__qffub in other_cols:
            opbm__mfwpf = df_cols.index(aiscv__qffub)
            wvsqs__vjys = other_cols.index(aiscv__qffub)
            byg__hjukl = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {opbm__mfwpf}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {wvsqs__vjys}), {wicb__cycoy}window, minp, center)'
                )
        else:
            byg__hjukl = 'np.full(len(df), np.nan)'
        ayq__blv.append(byg__hjukl)
    return ', '.join(ayq__blv), tla__qhr


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    xgt__owq = {'pairwise': pairwise, 'ddof': ddof}
    oawq__hmv = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        xgt__owq, oawq__hmv, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    xgt__owq = {'ddof': ddof, 'pairwise': pairwise}
    oawq__hmv = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        xgt__owq, oawq__hmv, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, mszl__mis = args
        if isinstance(rolling, RollingType):
            iyssm__sjp = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(mszl__mis, (tuple, list)):
                if len(set(mszl__mis).difference(set(iyssm__sjp))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(mszl__mis).difference(set(iyssm__sjp))))
                selection = list(mszl__mis)
            else:
                if mszl__mis not in iyssm__sjp:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(mszl__mis))
                selection = [mszl__mis]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            omxba__mhhtl = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(omxba__mhhtl, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        iyssm__sjp = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            iyssm__sjp = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            iyssm__sjp = rolling.obj_type.columns
        if attr in iyssm__sjp:
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
    avt__dzf = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    txwrw__ehgdy = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in avt__dzf):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        apl__tvpv = txwrw__ehgdy[avt__dzf.index(get_literal_value(on))]
        if not isinstance(apl__tvpv, types.Array
            ) or apl__tvpv.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(pus__sfb.dtype, (types.Boolean, types.Number)) for
        pus__sfb in txwrw__ehgdy):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
