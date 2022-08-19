"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, to_nullable_type, to_numeric_index_if_range_index, to_str_arr_if_dict_array
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False, _num_shuffle_keys=-1):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df_type,
            'pandas.groupby()')
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        self._num_shuffle_keys = _num_shuffle_keys
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select}, {_num_shuffle_keys})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select, self._num_shuffle_keys)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iycjp__izdpj = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, iycjp__izdpj)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_bodo_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type, dropna_type,
    _num_shuffle_keys):

    def codegen(context, builder, signature, args):
        soz__aacwj = args[0]
        ups__ifves = signature.return_type
        kew__mfc = cgutils.create_struct_proxy(ups__ifves)(context, builder)
        kew__mfc.obj = soz__aacwj
        context.nrt.incref(builder, signature.args[0], soz__aacwj)
        return kew__mfc._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for nmq__avexk in keys:
        selection.remove(nmq__avexk)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        zpa__reg = get_overload_const_int(_num_shuffle_keys)
    else:
        zpa__reg = -1
    ups__ifves = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=zpa__reg)
    return ups__ifves(obj_type, by_type, as_index_type, dropna_type,
        _num_shuffle_keys), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, kayv__mbdb = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(kayv__mbdb, (tuple, list)):
                if len(set(kayv__mbdb).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(kayv__mbdb).difference(set(grpby.
                        df_type.columns))))
                selection = kayv__mbdb
            else:
                if kayv__mbdb not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(kayv__mbdb))
                selection = kayv__mbdb,
                series_select = True
            dvpa__hwpok = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(dvpa__hwpok, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, kayv__mbdb = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            kayv__mbdb):
            dvpa__hwpok = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(kayv__mbdb)), {}).return_type
            return signature(dvpa__hwpok, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    orwra__kwkb = arr_type == ArrayItemArrayType(string_array_type)
    chpt__wyfn = arr_type.dtype
    if isinstance(chpt__wyfn, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {chpt__wyfn} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(chpt__wyfn, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {chpt__wyfn} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(chpt__wyfn,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(chpt__wyfn, (types.Integer, types.Float, types.Boolean)):
        if orwra__kwkb or chpt__wyfn == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(chpt__wyfn, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not chpt__wyfn.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {chpt__wyfn} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(chpt__wyfn, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    chpt__wyfn = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(chpt__wyfn, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(chpt__wyfn, types.Integer):
            return IntDtype(chpt__wyfn)
        return chpt__wyfn
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        qfbfa__npig = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{qfbfa__npig}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for nmq__avexk in grp.keys:
        if multi_level_names:
            qtzs__ctpke = nmq__avexk, ''
        else:
            qtzs__ctpke = nmq__avexk
        xrwmn__flqk = grp.df_type.column_index[nmq__avexk]
        data = grp.df_type.data[xrwmn__flqk]
        out_columns.append(qtzs__ctpke)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name in ('head', 'ngroup'):
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name in ('head', 'ngroup'):
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        aofps__bsuey = tuple(grp.df_type.column_index[grp.keys[twpe__ilog]] for
            twpe__ilog in range(len(grp.keys)))
        cks__ucl = tuple(grp.df_type.data[xrwmn__flqk] for xrwmn__flqk in
            aofps__bsuey)
        index = MultiIndexType(cks__ucl, tuple(types.StringLiteral(
            nmq__avexk) for nmq__avexk in grp.keys))
    else:
        xrwmn__flqk = grp.df_type.column_index[grp.keys[0]]
        wmuoa__pzzp = grp.df_type.data[xrwmn__flqk]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(wmuoa__pzzp,
            types.StringLiteral(grp.keys[0]))
    ntmdn__rvayg = {}
    nbtz__pddt = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        ntmdn__rvayg[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        ntmdn__rvayg[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        htznu__dwbau = dict(ascending=ascending)
        diizi__kfx = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', htznu__dwbau,
            diizi__kfx, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for tdow__wgaj in columns:
            xrwmn__flqk = grp.df_type.column_index[tdow__wgaj]
            data = grp.df_type.data[xrwmn__flqk]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            vvdj__dncfj = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                vvdj__dncfj = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    kgzpn__tnjf = SeriesType(data.dtype, data, None,
                        string_type)
                    tivk__qsgnx = get_const_func_output_type(func, (
                        kgzpn__tnjf,), {}, typing_context, target_context)
                    if tivk__qsgnx != ArrayItemArrayType(string_array_type):
                        tivk__qsgnx = dtype_to_array_type(tivk__qsgnx)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=tdow__wgaj, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    mzajf__ymwk = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    trrdb__mhty = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    htznu__dwbau = dict(numeric_only=mzajf__ymwk, min_count
                        =trrdb__mhty)
                    diizi__kfx = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        htznu__dwbau, diizi__kfx, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    mzajf__ymwk = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    trrdb__mhty = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    htznu__dwbau = dict(numeric_only=mzajf__ymwk, min_count
                        =trrdb__mhty)
                    diizi__kfx = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        htznu__dwbau, diizi__kfx, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    mzajf__ymwk = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    htznu__dwbau = dict(numeric_only=mzajf__ymwk)
                    diizi__kfx = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        htznu__dwbau, diizi__kfx, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    ziy__ntpm = args[0] if len(args) > 0 else kws.pop('axis', 0
                        )
                    pvc__xsxiu = args[1] if len(args) > 1 else kws.pop('skipna'
                        , True)
                    htznu__dwbau = dict(axis=ziy__ntpm, skipna=pvc__xsxiu)
                    diizi__kfx = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        htznu__dwbau, diizi__kfx, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    rojrn__nzt = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    htznu__dwbau = dict(ddof=rojrn__nzt)
                    diizi__kfx = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        htznu__dwbau, diizi__kfx, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                tivk__qsgnx, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                tivk__qsgnx = to_str_arr_if_dict_array(tivk__qsgnx
                    ) if func_name in ('sum', 'cumsum') else tivk__qsgnx
                out_data.append(tivk__qsgnx)
                out_columns.append(tdow__wgaj)
                if func_name == 'agg':
                    avxtk__szluc = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    ntmdn__rvayg[tdow__wgaj, avxtk__szluc] = tdow__wgaj
                else:
                    ntmdn__rvayg[tdow__wgaj, func_name] = tdow__wgaj
                out_column_type.append(vvdj__dncfj)
            else:
                nbtz__pddt.append(err_msg)
    if func_name == 'sum':
        uxau__ooxnm = any([(cgqr__tgt == ColumnType.NumericalColumn.value) for
            cgqr__tgt in out_column_type])
        if uxau__ooxnm:
            out_data = [cgqr__tgt for cgqr__tgt, awnr__gqhyt in zip(
                out_data, out_column_type) if awnr__gqhyt != ColumnType.
                NonNumericalColumn.value]
            out_columns = [cgqr__tgt for cgqr__tgt, awnr__gqhyt in zip(
                out_columns, out_column_type) if awnr__gqhyt != ColumnType.
                NonNumericalColumn.value]
            ntmdn__rvayg = {}
            for tdow__wgaj in out_columns:
                if grp.as_index is False and tdow__wgaj in grp.keys:
                    continue
                ntmdn__rvayg[tdow__wgaj, func_name] = tdow__wgaj
    hqabx__hgfs = len(nbtz__pddt)
    if len(out_data) == 0:
        if hqabx__hgfs == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(hqabx__hgfs, ' was' if hqabx__hgfs == 1 else
                's were', ','.join(nbtz__pddt)))
    gfh__sknm = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            sacwc__ihrw = IntDtype(out_data[0].dtype)
        else:
            sacwc__ihrw = out_data[0].dtype
        fjyuz__qpqgx = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        gfh__sknm = SeriesType(sacwc__ihrw, data=out_data[0], index=index,
            name_typ=fjyuz__qpqgx)
    return signature(gfh__sknm, *args), ntmdn__rvayg


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    ezci__yvuq = True
    if isinstance(f_val, str):
        ezci__yvuq = False
        exwyh__oib = f_val
    elif is_overload_constant_str(f_val):
        ezci__yvuq = False
        exwyh__oib = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        ezci__yvuq = False
        exwyh__oib = bodo.utils.typing.get_builtin_function_name(f_val)
    if not ezci__yvuq:
        if exwyh__oib not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {exwyh__oib}')
        dvpa__hwpok = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(dvpa__hwpok, (), exwyh__oib, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            ksk__eng = types.functions.MakeFunctionLiteral(f_val)
        else:
            ksk__eng = f_val
        validate_udf('agg', ksk__eng)
        func = get_overload_const_func(ksk__eng, None)
        snz__opgl = func.code if hasattr(func, 'code') else func.__code__
        exwyh__oib = snz__opgl.co_name
        dvpa__hwpok = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(dvpa__hwpok, (), 'agg', typing_context,
            target_context, ksk__eng)[0].return_type
    return exwyh__oib, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    dwjz__qot = kws and all(isinstance(kebty__fcv, types.Tuple) and len(
        kebty__fcv) == 2 for kebty__fcv in kws.values())
    if is_overload_none(func) and not dwjz__qot:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not dwjz__qot:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    ouhh__yeqs = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if dwjz__qot or is_overload_constant_dict(func):
        if dwjz__qot:
            krezl__kzlu = [get_literal_value(mbtl__nef) for mbtl__nef,
                nuxyk__fzvet in kws.values()]
            jvv__kcc = [get_literal_value(fsb__omdbx) for nuxyk__fzvet,
                fsb__omdbx in kws.values()]
        else:
            nfja__jsfx = get_overload_constant_dict(func)
            krezl__kzlu = tuple(nfja__jsfx.keys())
            jvv__kcc = tuple(nfja__jsfx.values())
        for qets__bsd in ('head', 'ngroup'):
            if qets__bsd in jvv__kcc:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {qets__bsd} cannot be mixed with other groupby operations.'
                    )
        if any(tdow__wgaj not in grp.selection and tdow__wgaj not in grp.
            keys for tdow__wgaj in krezl__kzlu):
            raise_bodo_error(
                f'Selected column names {krezl__kzlu} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            jvv__kcc)
        if dwjz__qot and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        ntmdn__rvayg = {}
        out_columns = []
        out_data = []
        out_column_type = []
        pxecw__fezz = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for tddex__qfgf, f_val in zip(krezl__kzlu, jvv__kcc):
            if isinstance(f_val, (tuple, list)):
                zxr__crwq = 0
                for ksk__eng in f_val:
                    exwyh__oib, out_tp = get_agg_funcname_and_outtyp(grp,
                        tddex__qfgf, ksk__eng, typing_context, target_context)
                    ouhh__yeqs = exwyh__oib in list_cumulative
                    if exwyh__oib == '<lambda>' and len(f_val) > 1:
                        exwyh__oib = '<lambda_' + str(zxr__crwq) + '>'
                        zxr__crwq += 1
                    out_columns.append((tddex__qfgf, exwyh__oib))
                    ntmdn__rvayg[tddex__qfgf, exwyh__oib
                        ] = tddex__qfgf, exwyh__oib
                    _append_out_type(grp, out_data, out_tp)
            else:
                exwyh__oib, out_tp = get_agg_funcname_and_outtyp(grp,
                    tddex__qfgf, f_val, typing_context, target_context)
                ouhh__yeqs = exwyh__oib in list_cumulative
                if multi_level_names:
                    out_columns.append((tddex__qfgf, exwyh__oib))
                    ntmdn__rvayg[tddex__qfgf, exwyh__oib
                        ] = tddex__qfgf, exwyh__oib
                elif not dwjz__qot:
                    out_columns.append(tddex__qfgf)
                    ntmdn__rvayg[tddex__qfgf, exwyh__oib] = tddex__qfgf
                elif dwjz__qot:
                    pxecw__fezz.append(exwyh__oib)
                _append_out_type(grp, out_data, out_tp)
        if dwjz__qot:
            for twpe__ilog, mpszm__zonao in enumerate(kws.keys()):
                out_columns.append(mpszm__zonao)
                ntmdn__rvayg[krezl__kzlu[twpe__ilog], pxecw__fezz[twpe__ilog]
                    ] = mpszm__zonao
        if ouhh__yeqs:
            index = grp.df_type.index
        else:
            index = out_tp.index
        gfh__sknm = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(gfh__sknm, *args), ntmdn__rvayg
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            mayn__ifqne = get_overload_const_list(func)
        else:
            mayn__ifqne = func.types
        if len(mayn__ifqne) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        zxr__crwq = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        ntmdn__rvayg = {}
        edqjl__yyqzb = grp.selection[0]
        for f_val in mayn__ifqne:
            exwyh__oib, out_tp = get_agg_funcname_and_outtyp(grp,
                edqjl__yyqzb, f_val, typing_context, target_context)
            ouhh__yeqs = exwyh__oib in list_cumulative
            if exwyh__oib == '<lambda>' and len(mayn__ifqne) > 1:
                exwyh__oib = '<lambda_' + str(zxr__crwq) + '>'
                zxr__crwq += 1
            out_columns.append(exwyh__oib)
            ntmdn__rvayg[edqjl__yyqzb, exwyh__oib] = exwyh__oib
            _append_out_type(grp, out_data, out_tp)
        if ouhh__yeqs:
            index = grp.df_type.index
        else:
            index = out_tp.index
        gfh__sknm = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(gfh__sknm, *args), ntmdn__rvayg
    exwyh__oib = ''
    if types.unliteral(func) == types.unicode_type:
        exwyh__oib = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        exwyh__oib = bodo.utils.typing.get_builtin_function_name(func)
    if exwyh__oib:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, exwyh__oib, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = to_numeric_index_if_range_index(grp.df_type.index)
    if isinstance(index, MultiIndexType):
        raise_bodo_error(
            f'Groupby.{name_operation}: MultiIndex input not supported for groupby operations that use input Index'
            )
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        ziy__ntpm = args[0] if len(args) > 0 else kws.pop('axis', 0)
        mzajf__ymwk = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        pvc__xsxiu = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        htznu__dwbau = dict(axis=ziy__ntpm, numeric_only=mzajf__ymwk)
        diizi__kfx = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', htznu__dwbau,
            diizi__kfx, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        pycsh__obp = args[0] if len(args) > 0 else kws.pop('periods', 1)
        jtul__ixi = args[1] if len(args) > 1 else kws.pop('freq', None)
        ziy__ntpm = args[2] if len(args) > 2 else kws.pop('axis', 0)
        fdapn__aeiid = args[3] if len(args) > 3 else kws.pop('fill_value', None
            )
        htznu__dwbau = dict(freq=jtul__ixi, axis=ziy__ntpm, fill_value=
            fdapn__aeiid)
        diizi__kfx = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', htznu__dwbau,
            diizi__kfx, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        xpaxb__mfo = args[0] if len(args) > 0 else kws.pop('func', None)
        jcuun__fzqpm = kws.pop('engine', None)
        hnbm__akm = kws.pop('engine_kwargs', None)
        htznu__dwbau = dict(engine=jcuun__fzqpm, engine_kwargs=hnbm__akm)
        diizi__kfx = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', htznu__dwbau,
            diizi__kfx, package_name='pandas', module_name='GroupBy')
    ntmdn__rvayg = {}
    for tdow__wgaj in grp.selection:
        out_columns.append(tdow__wgaj)
        ntmdn__rvayg[tdow__wgaj, name_operation] = tdow__wgaj
        xrwmn__flqk = grp.df_type.column_index[tdow__wgaj]
        data = grp.df_type.data[xrwmn__flqk]
        jngga__xjuy = (name_operation if name_operation != 'transform' else
            get_literal_value(xpaxb__mfo))
        if jngga__xjuy in ('sum', 'cumsum'):
            data = to_str_arr_if_dict_array(data)
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            tivk__qsgnx, err_msg = get_groupby_output_dtype(data,
                get_literal_value(xpaxb__mfo), grp.df_type.index)
            if err_msg == 'ok':
                data = tivk__qsgnx
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    gfh__sknm = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        gfh__sknm = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(gfh__sknm, *args), ntmdn__rvayg


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.ngroup', no_unliteral=True)
    def resolve_ngroup(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'ngroup', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        ptm__duyk = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        mwa__qra = isinstance(ptm__duyk, (SeriesType, HeterogeneousSeriesType)
            ) and ptm__duyk.const_info is not None or not isinstance(ptm__duyk,
            (SeriesType, DataFrameType))
        if mwa__qra:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                grhaj__qdn = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                aofps__bsuey = tuple(grp.df_type.column_index[grp.keys[
                    twpe__ilog]] for twpe__ilog in range(len(grp.keys)))
                cks__ucl = tuple(grp.df_type.data[xrwmn__flqk] for
                    xrwmn__flqk in aofps__bsuey)
                grhaj__qdn = MultiIndexType(cks__ucl, tuple(types.literal(
                    nmq__avexk) for nmq__avexk in grp.keys))
            else:
                xrwmn__flqk = grp.df_type.column_index[grp.keys[0]]
                wmuoa__pzzp = grp.df_type.data[xrwmn__flqk]
                grhaj__qdn = bodo.hiframes.pd_index_ext.array_type_to_index(
                    wmuoa__pzzp, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            kttek__oak = tuple(grp.df_type.data[grp.df_type.column_index[
                tdow__wgaj]] for tdow__wgaj in grp.keys)
            wmv__qfmqc = tuple(types.literal(kebty__fcv) for kebty__fcv in
                grp.keys) + get_index_name_types(ptm__duyk.index)
            if not grp.as_index:
                kttek__oak = types.Array(types.int64, 1, 'C'),
                wmv__qfmqc = (types.none,) + get_index_name_types(ptm__duyk
                    .index)
            grhaj__qdn = MultiIndexType(kttek__oak +
                get_index_data_arr_types(ptm__duyk.index), wmv__qfmqc)
        if mwa__qra:
            if isinstance(ptm__duyk, HeterogeneousSeriesType):
                nuxyk__fzvet, mpyiv__snon = ptm__duyk.const_info
                if isinstance(ptm__duyk.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    psj__tyqxq = ptm__duyk.data.tuple_typ.types
                elif isinstance(ptm__duyk.data, types.Tuple):
                    psj__tyqxq = ptm__duyk.data.types
                xhyu__dirrn = tuple(to_nullable_type(dtype_to_array_type(
                    pgwr__bkpd)) for pgwr__bkpd in psj__tyqxq)
                dbg__zfugf = DataFrameType(out_data + xhyu__dirrn,
                    grhaj__qdn, out_columns + mpyiv__snon)
            elif isinstance(ptm__duyk, SeriesType):
                brz__ocwdh, mpyiv__snon = ptm__duyk.const_info
                xhyu__dirrn = tuple(to_nullable_type(dtype_to_array_type(
                    ptm__duyk.dtype)) for nuxyk__fzvet in range(brz__ocwdh))
                dbg__zfugf = DataFrameType(out_data + xhyu__dirrn,
                    grhaj__qdn, out_columns + mpyiv__snon)
            else:
                dytq__bpifz = get_udf_out_arr_type(ptm__duyk)
                if not grp.as_index:
                    dbg__zfugf = DataFrameType(out_data + (dytq__bpifz,),
                        grhaj__qdn, out_columns + ('',))
                else:
                    dbg__zfugf = SeriesType(dytq__bpifz.dtype, dytq__bpifz,
                        grhaj__qdn, None)
        elif isinstance(ptm__duyk, SeriesType):
            dbg__zfugf = SeriesType(ptm__duyk.dtype, ptm__duyk.data,
                grhaj__qdn, ptm__duyk.name_typ)
        else:
            dbg__zfugf = DataFrameType(ptm__duyk.data, grhaj__qdn,
                ptm__duyk.columns)
        zgnm__svddq = gen_apply_pysig(len(f_args), kws.keys())
        wec__gljj = (func, *f_args) + tuple(kws.values())
        return signature(dbg__zfugf, *wec__gljj).replace(pysig=zgnm__svddq)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_bodo_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True, _num_shuffle_keys=
            grpby._num_shuffle_keys)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    vjxh__uuqhu = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            tddex__qfgf = grp.selection[0]
            dytq__bpifz = vjxh__uuqhu.data[vjxh__uuqhu.column_index[
                tddex__qfgf]]
            aqp__nrt = SeriesType(dytq__bpifz.dtype, dytq__bpifz,
                vjxh__uuqhu.index, types.literal(tddex__qfgf))
        else:
            hqsyl__kaxfe = tuple(vjxh__uuqhu.data[vjxh__uuqhu.column_index[
                tdow__wgaj]] for tdow__wgaj in grp.selection)
            aqp__nrt = DataFrameType(hqsyl__kaxfe, vjxh__uuqhu.index, tuple
                (grp.selection))
    else:
        aqp__nrt = vjxh__uuqhu
    xztkj__gyxz = aqp__nrt,
    xztkj__gyxz += tuple(f_args)
    try:
        ptm__duyk = get_const_func_output_type(func, xztkj__gyxz, kws,
            typing_context, target_context)
    except Exception as verb__bxc:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', verb__bxc),
            getattr(verb__bxc, 'loc', None))
    return ptm__duyk


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    xztkj__gyxz = (grp,) + f_args
    try:
        ptm__duyk = get_const_func_output_type(func, xztkj__gyxz, kws, self
            .context, numba.core.registry.cpu_target.target_context, False)
    except Exception as verb__bxc:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', verb__bxc),
            getattr(verb__bxc, 'loc', None))
    zgnm__svddq = gen_apply_pysig(len(f_args), kws.keys())
    wec__gljj = (func, *f_args) + tuple(kws.values())
    return signature(ptm__duyk, *wec__gljj).replace(pysig=zgnm__svddq)


def gen_apply_pysig(n_args, kws):
    aule__nwg = ', '.join(f'arg{twpe__ilog}' for twpe__ilog in range(n_args))
    aule__nwg = aule__nwg + ', ' if aule__nwg else ''
    hohy__sjob = ', '.join(f"{yhq__ibgn} = ''" for yhq__ibgn in kws)
    zpihp__mcspz = f'def apply_stub(func, {aule__nwg}{hohy__sjob}):\n'
    zpihp__mcspz += '    pass\n'
    zbs__fdbsu = {}
    exec(zpihp__mcspz, {}, zbs__fdbsu)
    olz__dgr = zbs__fdbsu['apply_stub']
    return numba.core.utils.pysignature(olz__dgr)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        hdknl__pbcb = types.Array(types.int64, 1, 'C')
        uknc__djp = _pivot_values.meta
        akb__ilpx = len(uknc__djp)
        whgxq__zqody = bodo.hiframes.pd_index_ext.array_type_to_index(index
            .data, types.StringLiteral('index'))
        xdwif__sqq = DataFrameType((hdknl__pbcb,) * akb__ilpx, whgxq__zqody,
            tuple(uknc__djp))
        return signature(xdwif__sqq, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    zpihp__mcspz = 'def impl(keys, dropna, _is_parallel):\n'
    zpihp__mcspz += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    zpihp__mcspz += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{twpe__ilog}])' for twpe__ilog in range(len(
        keys.types))))
    zpihp__mcspz += '    table = arr_info_list_to_table(info_list)\n'
    zpihp__mcspz += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    zpihp__mcspz += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    zpihp__mcspz += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    zpihp__mcspz += '    delete_table_decref_arrays(table)\n'
    zpihp__mcspz += '    ev.finalize()\n'
    zpihp__mcspz += '    return sort_idx, group_labels, ngroups\n'
    zbs__fdbsu = {}
    exec(zpihp__mcspz, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, zbs__fdbsu)
    teli__sezr = zbs__fdbsu['impl']
    return teli__sezr


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    lli__ughxu = len(labels)
    blw__dsumo = np.zeros(ngroups, dtype=np.int64)
    gaqfc__dygp = np.zeros(ngroups, dtype=np.int64)
    jelk__zgd = 0
    dfvg__gjq = 0
    for twpe__ilog in range(lli__ughxu):
        onzfw__mnf = labels[twpe__ilog]
        if onzfw__mnf < 0:
            jelk__zgd += 1
        else:
            dfvg__gjq += 1
            if twpe__ilog == lli__ughxu - 1 or onzfw__mnf != labels[
                twpe__ilog + 1]:
                blw__dsumo[onzfw__mnf] = jelk__zgd
                gaqfc__dygp[onzfw__mnf] = jelk__zgd + dfvg__gjq
                jelk__zgd += dfvg__gjq
                dfvg__gjq = 0
    return blw__dsumo, gaqfc__dygp


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    teli__sezr, nuxyk__fzvet = gen_shuffle_dataframe(df, keys, _is_parallel)
    return teli__sezr


def gen_shuffle_dataframe(df, keys, _is_parallel):
    brz__ocwdh = len(df.columns)
    tspk__jrzlc = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    zpihp__mcspz = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        zpihp__mcspz += '  return df, keys, get_null_shuffle_info()\n'
        zbs__fdbsu = {}
        exec(zpihp__mcspz, {'get_null_shuffle_info': get_null_shuffle_info},
            zbs__fdbsu)
        teli__sezr = zbs__fdbsu['impl']
        return teli__sezr
    for twpe__ilog in range(brz__ocwdh):
        zpihp__mcspz += f"""  in_arr{twpe__ilog} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {twpe__ilog})
"""
    zpihp__mcspz += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    zpihp__mcspz += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{twpe__ilog}])' for twpe__ilog in range(
        tspk__jrzlc)), ', '.join(f'array_to_info(in_arr{twpe__ilog})' for
        twpe__ilog in range(brz__ocwdh)), 'array_to_info(in_index_arr)')
    zpihp__mcspz += '  table = arr_info_list_to_table(info_list)\n'
    zpihp__mcspz += (
        f'  out_table = shuffle_table(table, {tspk__jrzlc}, _is_parallel, 1)\n'
        )
    for twpe__ilog in range(tspk__jrzlc):
        zpihp__mcspz += f"""  out_key{twpe__ilog} = info_to_array(info_from_table(out_table, {twpe__ilog}), keys{twpe__ilog}_typ)
"""
    for twpe__ilog in range(brz__ocwdh):
        zpihp__mcspz += f"""  out_arr{twpe__ilog} = info_to_array(info_from_table(out_table, {twpe__ilog + tspk__jrzlc}), in_arr{twpe__ilog}_typ)
"""
    zpihp__mcspz += f"""  out_arr_index = info_to_array(info_from_table(out_table, {tspk__jrzlc + brz__ocwdh}), ind_arr_typ)
"""
    zpihp__mcspz += '  shuffle_info = get_shuffle_info(out_table)\n'
    zpihp__mcspz += '  delete_table(out_table)\n'
    zpihp__mcspz += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{twpe__ilog}' for twpe__ilog in range(
        brz__ocwdh))
    zpihp__mcspz += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    zpihp__mcspz += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    zpihp__mcspz += '  return out_df, ({},), shuffle_info\n'.format(', '.
        join(f'out_key{twpe__ilog}' for twpe__ilog in range(tspk__jrzlc)))
    wti__jqcpp = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    wti__jqcpp.update({f'keys{twpe__ilog}_typ': keys.types[twpe__ilog] for
        twpe__ilog in range(tspk__jrzlc)})
    wti__jqcpp.update({f'in_arr{twpe__ilog}_typ': df.data[twpe__ilog] for
        twpe__ilog in range(brz__ocwdh)})
    zbs__fdbsu = {}
    exec(zpihp__mcspz, wti__jqcpp, zbs__fdbsu)
    teli__sezr = zbs__fdbsu['impl']
    return teli__sezr, wti__jqcpp


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        quk__igdub = len(data.array_types)
        zpihp__mcspz = 'def impl(data, shuffle_info):\n'
        zpihp__mcspz += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{twpe__ilog}])' for twpe__ilog in
            range(quk__igdub)))
        zpihp__mcspz += '  table = arr_info_list_to_table(info_list)\n'
        zpihp__mcspz += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for twpe__ilog in range(quk__igdub):
            zpihp__mcspz += f"""  out_arr{twpe__ilog} = info_to_array(info_from_table(out_table, {twpe__ilog}), data._data[{twpe__ilog}])
"""
        zpihp__mcspz += '  delete_table(out_table)\n'
        zpihp__mcspz += '  delete_table(table)\n'
        zpihp__mcspz += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{twpe__ilog}' for twpe__ilog in range
            (quk__igdub))))
        zbs__fdbsu = {}
        exec(zpihp__mcspz, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, zbs__fdbsu)
        teli__sezr = zbs__fdbsu['impl']
        return teli__sezr
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            dtxy__poi = bodo.utils.conversion.index_to_array(data)
            rnx__opq = reverse_shuffle(dtxy__poi, shuffle_info)
            return bodo.utils.conversion.index_from_array(rnx__opq)
        return impl_index

    def impl_arr(data, shuffle_info):
        hhdv__uga = [array_to_info(data)]
        pqd__leq = arr_info_list_to_table(hhdv__uga)
        mnpwc__vnnuo = reverse_shuffle_table(pqd__leq, shuffle_info)
        rnx__opq = info_to_array(info_from_table(mnpwc__vnnuo, 0), data)
        delete_table(mnpwc__vnnuo)
        delete_table(pqd__leq)
        return rnx__opq
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    htznu__dwbau = dict(normalize=normalize, sort=sort, bins=bins, dropna=
        dropna)
    diizi__kfx = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', htznu__dwbau, diizi__kfx,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    wttu__fza = get_overload_const_bool(ascending)
    kxgeo__rud = grp.selection[0]
    zpihp__mcspz = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    pem__jgw = (
        f"lambda S: S.value_counts(ascending={wttu__fza}, _index_name='{kxgeo__rud}')"
        )
    zpihp__mcspz += f'    return grp.apply({pem__jgw})\n'
    zbs__fdbsu = {}
    exec(zpihp__mcspz, {'bodo': bodo}, zbs__fdbsu)
    teli__sezr = zbs__fdbsu['impl']
    return teli__sezr


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill', 'nth',
    'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail', 'corr', 'cov',
    'describe', 'diff', 'fillna', 'filter', 'hist', 'mad', 'plot',
    'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupby_unsupported():
    for lgj__ptqsx in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, lgj__ptqsx, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{lgj__ptqsx}'))
    for lgj__ptqsx in groupby_unsupported:
        overload_method(DataFrameGroupByType, lgj__ptqsx, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{lgj__ptqsx}'))
    for lgj__ptqsx in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, lgj__ptqsx, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{lgj__ptqsx}'))
    for lgj__ptqsx in series_only_unsupported:
        overload_method(DataFrameGroupByType, lgj__ptqsx, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{lgj__ptqsx}'))
    for lgj__ptqsx in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, lgj__ptqsx, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{lgj__ptqsx}'))


_install_groupby_unsupported()
