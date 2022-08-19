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
            himum__rndb = 'Series'
        else:
            himum__rndb = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{himum__rndb}.rolling()')
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
        hajbc__zno = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, hajbc__zno)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    juky__izmt = dict(win_type=win_type, axis=axis, closed=closed)
    bosa__eyxx = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', juky__izmt, bosa__eyxx,
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
    juky__izmt = dict(win_type=win_type, axis=axis, closed=closed)
    bosa__eyxx = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', juky__izmt, bosa__eyxx,
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
        dqs__zrz, tftu__dcu, mgdk__oxamd, rrthg__ubbuy, awlgs__olxt = args
        zya__zjt = signature.return_type
        igvsd__khzk = cgutils.create_struct_proxy(zya__zjt)(context, builder)
        igvsd__khzk.obj = dqs__zrz
        igvsd__khzk.window = tftu__dcu
        igvsd__khzk.min_periods = mgdk__oxamd
        igvsd__khzk.center = rrthg__ubbuy
        context.nrt.incref(builder, signature.args[0], dqs__zrz)
        context.nrt.incref(builder, signature.args[1], tftu__dcu)
        context.nrt.incref(builder, signature.args[2], mgdk__oxamd)
        context.nrt.incref(builder, signature.args[3], rrthg__ubbuy)
        return igvsd__khzk._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    zya__zjt = RollingType(obj_type, window_type, on, selection, False)
    return zya__zjt(obj_type, window_type, min_periods_type, center_type,
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
    ali__pnf = not isinstance(rolling.window_type, types.Integer)
    ero__pmtmr = 'variable' if ali__pnf else 'fixed'
    kccs__nwad = 'None'
    if ali__pnf:
        kccs__nwad = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    fsw__ctw = []
    ujp__enc = 'on_arr, ' if ali__pnf else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{ero__pmtmr}(bodo.hiframes.pd_series_ext.get_series_data(df), {ujp__enc}index_arr, window, minp, center, func, raw)'
            , kccs__nwad, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    lir__ticg = rolling.obj_type.data
    out_cols = []
    for ihp__aqnnu in rolling.selection:
        ttwdr__ojd = rolling.obj_type.columns.index(ihp__aqnnu)
        if ihp__aqnnu == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            bjx__rmy = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ttwdr__ojd})'
                )
            out_cols.append(ihp__aqnnu)
        else:
            if not isinstance(lir__ticg[ttwdr__ojd].dtype, (types.Boolean,
                types.Number)):
                continue
            bjx__rmy = (
                f'bodo.hiframes.rolling.rolling_{ero__pmtmr}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ttwdr__ojd}), {ujp__enc}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(ihp__aqnnu)
        fsw__ctw.append(bjx__rmy)
    return ', '.join(fsw__ctw), kccs__nwad, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    juky__izmt = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    bosa__eyxx = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', juky__izmt, bosa__eyxx,
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
    juky__izmt = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    bosa__eyxx = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', juky__izmt, bosa__eyxx,
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
        makl__lrgpu = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        bqisl__womaw = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{xxbyx__cxgzg}'" if
                isinstance(xxbyx__cxgzg, str) else f'{xxbyx__cxgzg}' for
                xxbyx__cxgzg in rolling.selection if xxbyx__cxgzg !=
                rolling.on))
        iwrip__dhmn = bvih__rdsvp = ''
        if fname == 'apply':
            iwrip__dhmn = 'func, raw, args, kwargs'
            bvih__rdsvp = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            iwrip__dhmn = bvih__rdsvp = 'other, pairwise'
        if fname == 'cov':
            iwrip__dhmn = bvih__rdsvp = 'other, pairwise, ddof'
        swkyd__dkiud = (
            f'lambda df, window, minp, center, {iwrip__dhmn}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {bqisl__womaw}){selection}.{fname}({bvih__rdsvp})'
            )
        makl__lrgpu += f"""  return rolling.obj.apply({swkyd__dkiud}, rolling.window, rolling.min_periods, rolling.center, {iwrip__dhmn})
"""
        jidg__ensaq = {}
        exec(makl__lrgpu, {'bodo': bodo}, jidg__ensaq)
        impl = jidg__ensaq['impl']
        return impl
    vzzni__lcuf = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if vzzni__lcuf else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if vzzni__lcuf else rolling.obj_type.columns
        other_cols = None if vzzni__lcuf else other.columns
        fsw__ctw, kccs__nwad = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        fsw__ctw, kccs__nwad, out_cols = _gen_df_rolling_out_data(rolling)
    tutpa__smxi = vzzni__lcuf or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    qba__lansz = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    qba__lansz += '  df = rolling.obj\n'
    qba__lansz += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if vzzni__lcuf else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    himum__rndb = 'None'
    if vzzni__lcuf:
        himum__rndb = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif tutpa__smxi:
        ihp__aqnnu = (set(out_cols) - set([rolling.on])).pop()
        himum__rndb = f"'{ihp__aqnnu}'" if isinstance(ihp__aqnnu, str
            ) else str(ihp__aqnnu)
    qba__lansz += f'  name = {himum__rndb}\n'
    qba__lansz += '  window = rolling.window\n'
    qba__lansz += '  center = rolling.center\n'
    qba__lansz += '  minp = rolling.min_periods\n'
    qba__lansz += f'  on_arr = {kccs__nwad}\n'
    if fname == 'apply':
        qba__lansz += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        qba__lansz += f"  func = '{fname}'\n"
        qba__lansz += f'  index_arr = None\n'
        qba__lansz += f'  raw = False\n'
    if tutpa__smxi:
        qba__lansz += (
            f'  return bodo.hiframes.pd_series_ext.init_series({fsw__ctw}, index, name)'
            )
        jidg__ensaq = {}
        phwx__iyyy = {'bodo': bodo}
        exec(qba__lansz, phwx__iyyy, jidg__ensaq)
        impl = jidg__ensaq['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(qba__lansz, out_cols,
        fsw__ctw)


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
        lkvwa__bnzg = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(lkvwa__bnzg)


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
    nmz__qgcs = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(nmz__qgcs) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    ali__pnf = not isinstance(window_type, types.Integer)
    kccs__nwad = 'None'
    if ali__pnf:
        kccs__nwad = 'bodo.utils.conversion.index_to_array(index)'
    ujp__enc = 'on_arr, ' if ali__pnf else ''
    fsw__ctw = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {ujp__enc}window, minp, center)'
            , kccs__nwad)
    for ihp__aqnnu in out_cols:
        if ihp__aqnnu in df_cols and ihp__aqnnu in other_cols:
            ccjzs__tcuk = df_cols.index(ihp__aqnnu)
            qcmsp__oxyfr = other_cols.index(ihp__aqnnu)
            bjx__rmy = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ccjzs__tcuk}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {qcmsp__oxyfr}), {ujp__enc}window, minp, center)'
                )
        else:
            bjx__rmy = 'np.full(len(df), np.nan)'
        fsw__ctw.append(bjx__rmy)
    return ', '.join(fsw__ctw), kccs__nwad


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    yrncd__pzhok = {'pairwise': pairwise, 'ddof': ddof}
    lgleb__owb = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        yrncd__pzhok, lgleb__owb, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    yrncd__pzhok = {'ddof': ddof, 'pairwise': pairwise}
    lgleb__owb = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        yrncd__pzhok, lgleb__owb, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, icrt__tldsn = args
        if isinstance(rolling, RollingType):
            nmz__qgcs = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(icrt__tldsn, (tuple, list)):
                if len(set(icrt__tldsn).difference(set(nmz__qgcs))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(icrt__tldsn).difference(set(nmz__qgcs))))
                selection = list(icrt__tldsn)
            else:
                if icrt__tldsn not in nmz__qgcs:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(icrt__tldsn))
                selection = [icrt__tldsn]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            xlk__nucw = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(xlk__nucw, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        nmz__qgcs = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            nmz__qgcs = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            nmz__qgcs = rolling.obj_type.columns
        if attr in nmz__qgcs:
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
    eupue__rkwop = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    lir__ticg = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in eupue__rkwop):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        lli__oogoy = lir__ticg[eupue__rkwop.index(get_literal_value(on))]
        if not isinstance(lli__oogoy, types.Array
            ) or lli__oogoy.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(ggeee__bvd.dtype, (types.Boolean, types.Number)) for
        ggeee__bvd in lir__ticg):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
