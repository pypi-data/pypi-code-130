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
        mlq__zzppe = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, mlq__zzppe)


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
        qgrt__guo = args[0]
        bpr__tjbtq = signature.return_type
        weda__hvyj = cgutils.create_struct_proxy(bpr__tjbtq)(context, builder)
        weda__hvyj.obj = qgrt__guo
        context.nrt.incref(builder, signature.args[0], qgrt__guo)
        return weda__hvyj._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for tdt__ehxf in keys:
        selection.remove(tdt__ehxf)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        yeapn__nhq = get_overload_const_int(_num_shuffle_keys)
    else:
        yeapn__nhq = -1
    bpr__tjbtq = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=yeapn__nhq)
    return bpr__tjbtq(obj_type, by_type, as_index_type, dropna_type,
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
        grpby, piw__gfacm = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(piw__gfacm, (tuple, list)):
                if len(set(piw__gfacm).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(piw__gfacm).difference(set(grpby.
                        df_type.columns))))
                selection = piw__gfacm
            else:
                if piw__gfacm not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(piw__gfacm))
                selection = piw__gfacm,
                series_select = True
            lnot__cnabp = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(lnot__cnabp, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, piw__gfacm = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            piw__gfacm):
            lnot__cnabp = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(piw__gfacm)), {}).return_type
            return signature(lnot__cnabp, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    hkjye__tmokm = arr_type == ArrayItemArrayType(string_array_type)
    fxqmd__etdsl = arr_type.dtype
    if isinstance(fxqmd__etdsl, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {fxqmd__etdsl} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(fxqmd__etdsl, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {fxqmd__etdsl} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(
        fxqmd__etdsl, (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(fxqmd__etdsl, (types.Integer, types.Float, types.Boolean)
        ):
        if hkjye__tmokm or fxqmd__etdsl == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(fxqmd__etdsl, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not fxqmd__etdsl.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {fxqmd__etdsl} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(fxqmd__etdsl, types.Boolean) and func_name in {'cumsum',
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
    fxqmd__etdsl = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(fxqmd__etdsl, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(fxqmd__etdsl, types.Integer):
            return IntDtype(fxqmd__etdsl)
        return fxqmd__etdsl
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        slpr__euajc = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{slpr__euajc}'."
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
    for tdt__ehxf in grp.keys:
        if multi_level_names:
            xvj__iavok = tdt__ehxf, ''
        else:
            xvj__iavok = tdt__ehxf
        zzn__rrg = grp.df_type.column_index[tdt__ehxf]
        data = grp.df_type.data[zzn__rrg]
        out_columns.append(xvj__iavok)
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
        daxm__hqvs = tuple(grp.df_type.column_index[grp.keys[zhff__tfp]] for
            zhff__tfp in range(len(grp.keys)))
        wizf__yplnd = tuple(grp.df_type.data[zzn__rrg] for zzn__rrg in
            daxm__hqvs)
        index = MultiIndexType(wizf__yplnd, tuple(types.StringLiteral(
            tdt__ehxf) for tdt__ehxf in grp.keys))
    else:
        zzn__rrg = grp.df_type.column_index[grp.keys[0]]
        vrpyk__ovtay = grp.df_type.data[zzn__rrg]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(vrpyk__ovtay,
            types.StringLiteral(grp.keys[0]))
    aqsw__uclb = {}
    cgj__eqv = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        aqsw__uclb[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        aqsw__uclb[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        mfa__emj = dict(ascending=ascending)
        ecj__aevt = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', mfa__emj, ecj__aevt,
            package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for khiq__aoiy in columns:
            zzn__rrg = grp.df_type.column_index[khiq__aoiy]
            data = grp.df_type.data[zzn__rrg]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            cyyb__niw = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                cyyb__niw = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    yrs__xki = SeriesType(data.dtype, data, None, string_type)
                    mjefm__wpvaf = get_const_func_output_type(func, (
                        yrs__xki,), {}, typing_context, target_context)
                    if mjefm__wpvaf != ArrayItemArrayType(string_array_type):
                        mjefm__wpvaf = dtype_to_array_type(mjefm__wpvaf)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=khiq__aoiy, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    uaxj__hispq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    qrffv__cfwa = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    mfa__emj = dict(numeric_only=uaxj__hispq, min_count=
                        qrffv__cfwa)
                    ecj__aevt = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}', mfa__emj,
                        ecj__aevt, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    uaxj__hispq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    qrffv__cfwa = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    mfa__emj = dict(numeric_only=uaxj__hispq, min_count=
                        qrffv__cfwa)
                    ecj__aevt = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}', mfa__emj,
                        ecj__aevt, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    uaxj__hispq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    mfa__emj = dict(numeric_only=uaxj__hispq)
                    ecj__aevt = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}', mfa__emj,
                        ecj__aevt, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    wab__gwlvz = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    vakzb__rseye = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    mfa__emj = dict(axis=wab__gwlvz, skipna=vakzb__rseye)
                    ecj__aevt = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}', mfa__emj,
                        ecj__aevt, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    nahz__xzhce = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    mfa__emj = dict(ddof=nahz__xzhce)
                    ecj__aevt = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}', mfa__emj,
                        ecj__aevt, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                mjefm__wpvaf, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                mjefm__wpvaf = to_str_arr_if_dict_array(mjefm__wpvaf
                    ) if func_name in ('sum', 'cumsum') else mjefm__wpvaf
                out_data.append(mjefm__wpvaf)
                out_columns.append(khiq__aoiy)
                if func_name == 'agg':
                    awy__lseb = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    aqsw__uclb[khiq__aoiy, awy__lseb] = khiq__aoiy
                else:
                    aqsw__uclb[khiq__aoiy, func_name] = khiq__aoiy
                out_column_type.append(cyyb__niw)
            else:
                cgj__eqv.append(err_msg)
    if func_name == 'sum':
        cxek__blit = any([(quase__sgfd == ColumnType.NumericalColumn.value) for
            quase__sgfd in out_column_type])
        if cxek__blit:
            out_data = [quase__sgfd for quase__sgfd, jrnvv__kzer in zip(
                out_data, out_column_type) if jrnvv__kzer != ColumnType.
                NonNumericalColumn.value]
            out_columns = [quase__sgfd for quase__sgfd, jrnvv__kzer in zip(
                out_columns, out_column_type) if jrnvv__kzer != ColumnType.
                NonNumericalColumn.value]
            aqsw__uclb = {}
            for khiq__aoiy in out_columns:
                if grp.as_index is False and khiq__aoiy in grp.keys:
                    continue
                aqsw__uclb[khiq__aoiy, func_name] = khiq__aoiy
    auixz__psa = len(cgj__eqv)
    if len(out_data) == 0:
        if auixz__psa == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(auixz__psa, ' was' if auixz__psa == 1 else 's were',
                ','.join(cgj__eqv)))
    exu__odppv = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            snzj__jeq = IntDtype(out_data[0].dtype)
        else:
            snzj__jeq = out_data[0].dtype
        lwgb__mugq = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        exu__odppv = SeriesType(snzj__jeq, data=out_data[0], index=index,
            name_typ=lwgb__mugq)
    return signature(exu__odppv, *args), aqsw__uclb


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    ialq__ewi = True
    if isinstance(f_val, str):
        ialq__ewi = False
        tkkt__ttgw = f_val
    elif is_overload_constant_str(f_val):
        ialq__ewi = False
        tkkt__ttgw = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        ialq__ewi = False
        tkkt__ttgw = bodo.utils.typing.get_builtin_function_name(f_val)
    if not ialq__ewi:
        if tkkt__ttgw not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {tkkt__ttgw}')
        lnot__cnabp = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(lnot__cnabp, (), tkkt__ttgw, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            rpxyx__feb = types.functions.MakeFunctionLiteral(f_val)
        else:
            rpxyx__feb = f_val
        validate_udf('agg', rpxyx__feb)
        func = get_overload_const_func(rpxyx__feb, None)
        lgn__kraj = func.code if hasattr(func, 'code') else func.__code__
        tkkt__ttgw = lgn__kraj.co_name
        lnot__cnabp = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(lnot__cnabp, (), 'agg', typing_context,
            target_context, rpxyx__feb)[0].return_type
    return tkkt__ttgw, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    vws__ivf = kws and all(isinstance(dtezd__jumj, types.Tuple) and len(
        dtezd__jumj) == 2 for dtezd__jumj in kws.values())
    if is_overload_none(func) and not vws__ivf:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not vws__ivf:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    xhhp__tfbt = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if vws__ivf or is_overload_constant_dict(func):
        if vws__ivf:
            jyoei__rakuu = [get_literal_value(jgb__rbknj) for jgb__rbknj,
                sfhcg__dtrrb in kws.values()]
            hupak__nch = [get_literal_value(ctr__rrt) for sfhcg__dtrrb,
                ctr__rrt in kws.values()]
        else:
            dlvgl__exk = get_overload_constant_dict(func)
            jyoei__rakuu = tuple(dlvgl__exk.keys())
            hupak__nch = tuple(dlvgl__exk.values())
        for dtpzq__jkajg in ('head', 'ngroup'):
            if dtpzq__jkajg in hupak__nch:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {dtpzq__jkajg} cannot be mixed with other groupby operations.'
                    )
        if any(khiq__aoiy not in grp.selection and khiq__aoiy not in grp.
            keys for khiq__aoiy in jyoei__rakuu):
            raise_bodo_error(
                f'Selected column names {jyoei__rakuu} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            hupak__nch)
        if vws__ivf and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        aqsw__uclb = {}
        out_columns = []
        out_data = []
        out_column_type = []
        hmw__urmvf = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for xxl__dcf, f_val in zip(jyoei__rakuu, hupak__nch):
            if isinstance(f_val, (tuple, list)):
                xdcx__zrnbu = 0
                for rpxyx__feb in f_val:
                    tkkt__ttgw, out_tp = get_agg_funcname_and_outtyp(grp,
                        xxl__dcf, rpxyx__feb, typing_context, target_context)
                    xhhp__tfbt = tkkt__ttgw in list_cumulative
                    if tkkt__ttgw == '<lambda>' and len(f_val) > 1:
                        tkkt__ttgw = '<lambda_' + str(xdcx__zrnbu) + '>'
                        xdcx__zrnbu += 1
                    out_columns.append((xxl__dcf, tkkt__ttgw))
                    aqsw__uclb[xxl__dcf, tkkt__ttgw] = xxl__dcf, tkkt__ttgw
                    _append_out_type(grp, out_data, out_tp)
            else:
                tkkt__ttgw, out_tp = get_agg_funcname_and_outtyp(grp,
                    xxl__dcf, f_val, typing_context, target_context)
                xhhp__tfbt = tkkt__ttgw in list_cumulative
                if multi_level_names:
                    out_columns.append((xxl__dcf, tkkt__ttgw))
                    aqsw__uclb[xxl__dcf, tkkt__ttgw] = xxl__dcf, tkkt__ttgw
                elif not vws__ivf:
                    out_columns.append(xxl__dcf)
                    aqsw__uclb[xxl__dcf, tkkt__ttgw] = xxl__dcf
                elif vws__ivf:
                    hmw__urmvf.append(tkkt__ttgw)
                _append_out_type(grp, out_data, out_tp)
        if vws__ivf:
            for zhff__tfp, bjqwg__tqi in enumerate(kws.keys()):
                out_columns.append(bjqwg__tqi)
                aqsw__uclb[jyoei__rakuu[zhff__tfp], hmw__urmvf[zhff__tfp]
                    ] = bjqwg__tqi
        if xhhp__tfbt:
            index = grp.df_type.index
        else:
            index = out_tp.index
        exu__odppv = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(exu__odppv, *args), aqsw__uclb
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            vfaai__kohiw = get_overload_const_list(func)
        else:
            vfaai__kohiw = func.types
        if len(vfaai__kohiw) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        xdcx__zrnbu = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        aqsw__uclb = {}
        wcm__unq = grp.selection[0]
        for f_val in vfaai__kohiw:
            tkkt__ttgw, out_tp = get_agg_funcname_and_outtyp(grp, wcm__unq,
                f_val, typing_context, target_context)
            xhhp__tfbt = tkkt__ttgw in list_cumulative
            if tkkt__ttgw == '<lambda>' and len(vfaai__kohiw) > 1:
                tkkt__ttgw = '<lambda_' + str(xdcx__zrnbu) + '>'
                xdcx__zrnbu += 1
            out_columns.append(tkkt__ttgw)
            aqsw__uclb[wcm__unq, tkkt__ttgw] = tkkt__ttgw
            _append_out_type(grp, out_data, out_tp)
        if xhhp__tfbt:
            index = grp.df_type.index
        else:
            index = out_tp.index
        exu__odppv = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(exu__odppv, *args), aqsw__uclb
    tkkt__ttgw = ''
    if types.unliteral(func) == types.unicode_type:
        tkkt__ttgw = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        tkkt__ttgw = bodo.utils.typing.get_builtin_function_name(func)
    if tkkt__ttgw:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, tkkt__ttgw, typing_context, kws)
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
        wab__gwlvz = args[0] if len(args) > 0 else kws.pop('axis', 0)
        uaxj__hispq = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        vakzb__rseye = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        mfa__emj = dict(axis=wab__gwlvz, numeric_only=uaxj__hispq)
        ecj__aevt = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', mfa__emj,
            ecj__aevt, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        ynij__nfvg = args[0] if len(args) > 0 else kws.pop('periods', 1)
        nmt__kbtgb = args[1] if len(args) > 1 else kws.pop('freq', None)
        wab__gwlvz = args[2] if len(args) > 2 else kws.pop('axis', 0)
        ndddf__uwf = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        mfa__emj = dict(freq=nmt__kbtgb, axis=wab__gwlvz, fill_value=ndddf__uwf
            )
        ecj__aevt = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', mfa__emj,
            ecj__aevt, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        xocp__hja = args[0] if len(args) > 0 else kws.pop('func', None)
        tunp__qzk = kws.pop('engine', None)
        fbc__qyqgr = kws.pop('engine_kwargs', None)
        mfa__emj = dict(engine=tunp__qzk, engine_kwargs=fbc__qyqgr)
        ecj__aevt = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', mfa__emj, ecj__aevt,
            package_name='pandas', module_name='GroupBy')
    aqsw__uclb = {}
    for khiq__aoiy in grp.selection:
        out_columns.append(khiq__aoiy)
        aqsw__uclb[khiq__aoiy, name_operation] = khiq__aoiy
        zzn__rrg = grp.df_type.column_index[khiq__aoiy]
        data = grp.df_type.data[zzn__rrg]
        kfk__aam = (name_operation if name_operation != 'transform' else
            get_literal_value(xocp__hja))
        if kfk__aam in ('sum', 'cumsum'):
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
            mjefm__wpvaf, err_msg = get_groupby_output_dtype(data,
                get_literal_value(xocp__hja), grp.df_type.index)
            if err_msg == 'ok':
                data = mjefm__wpvaf
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    exu__odppv = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        exu__odppv = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(exu__odppv, *args), aqsw__uclb


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
        fjim__hmge = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        yfd__wjflm = isinstance(fjim__hmge, (SeriesType,
            HeterogeneousSeriesType)
            ) and fjim__hmge.const_info is not None or not isinstance(
            fjim__hmge, (SeriesType, DataFrameType))
        if yfd__wjflm:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                lfbco__nve = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                daxm__hqvs = tuple(grp.df_type.column_index[grp.keys[
                    zhff__tfp]] for zhff__tfp in range(len(grp.keys)))
                wizf__yplnd = tuple(grp.df_type.data[zzn__rrg] for zzn__rrg in
                    daxm__hqvs)
                lfbco__nve = MultiIndexType(wizf__yplnd, tuple(types.
                    literal(tdt__ehxf) for tdt__ehxf in grp.keys))
            else:
                zzn__rrg = grp.df_type.column_index[grp.keys[0]]
                vrpyk__ovtay = grp.df_type.data[zzn__rrg]
                lfbco__nve = bodo.hiframes.pd_index_ext.array_type_to_index(
                    vrpyk__ovtay, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            crid__ojnuo = tuple(grp.df_type.data[grp.df_type.column_index[
                khiq__aoiy]] for khiq__aoiy in grp.keys)
            jwy__rpcnt = tuple(types.literal(dtezd__jumj) for dtezd__jumj in
                grp.keys) + get_index_name_types(fjim__hmge.index)
            if not grp.as_index:
                crid__ojnuo = types.Array(types.int64, 1, 'C'),
                jwy__rpcnt = (types.none,) + get_index_name_types(fjim__hmge
                    .index)
            lfbco__nve = MultiIndexType(crid__ojnuo +
                get_index_data_arr_types(fjim__hmge.index), jwy__rpcnt)
        if yfd__wjflm:
            if isinstance(fjim__hmge, HeterogeneousSeriesType):
                sfhcg__dtrrb, drqkj__eka = fjim__hmge.const_info
                if isinstance(fjim__hmge.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    yil__cxp = fjim__hmge.data.tuple_typ.types
                elif isinstance(fjim__hmge.data, types.Tuple):
                    yil__cxp = fjim__hmge.data.types
                ght__rwj = tuple(to_nullable_type(dtype_to_array_type(
                    dst__qbna)) for dst__qbna in yil__cxp)
                twc__iaac = DataFrameType(out_data + ght__rwj, lfbco__nve, 
                    out_columns + drqkj__eka)
            elif isinstance(fjim__hmge, SeriesType):
                aqyq__njiw, drqkj__eka = fjim__hmge.const_info
                ght__rwj = tuple(to_nullable_type(dtype_to_array_type(
                    fjim__hmge.dtype)) for sfhcg__dtrrb in range(aqyq__njiw))
                twc__iaac = DataFrameType(out_data + ght__rwj, lfbco__nve, 
                    out_columns + drqkj__eka)
            else:
                meaid__uxz = get_udf_out_arr_type(fjim__hmge)
                if not grp.as_index:
                    twc__iaac = DataFrameType(out_data + (meaid__uxz,),
                        lfbco__nve, out_columns + ('',))
                else:
                    twc__iaac = SeriesType(meaid__uxz.dtype, meaid__uxz,
                        lfbco__nve, None)
        elif isinstance(fjim__hmge, SeriesType):
            twc__iaac = SeriesType(fjim__hmge.dtype, fjim__hmge.data,
                lfbco__nve, fjim__hmge.name_typ)
        else:
            twc__iaac = DataFrameType(fjim__hmge.data, lfbco__nve,
                fjim__hmge.columns)
        tow__pbye = gen_apply_pysig(len(f_args), kws.keys())
        kmpz__mueu = (func, *f_args) + tuple(kws.values())
        return signature(twc__iaac, *kmpz__mueu).replace(pysig=tow__pbye)

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
    rlrkz__yadw = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            xxl__dcf = grp.selection[0]
            meaid__uxz = rlrkz__yadw.data[rlrkz__yadw.column_index[xxl__dcf]]
            tuei__osjus = SeriesType(meaid__uxz.dtype, meaid__uxz,
                rlrkz__yadw.index, types.literal(xxl__dcf))
        else:
            jxt__aigia = tuple(rlrkz__yadw.data[rlrkz__yadw.column_index[
                khiq__aoiy]] for khiq__aoiy in grp.selection)
            tuei__osjus = DataFrameType(jxt__aigia, rlrkz__yadw.index,
                tuple(grp.selection))
    else:
        tuei__osjus = rlrkz__yadw
    qcr__vhtf = tuei__osjus,
    qcr__vhtf += tuple(f_args)
    try:
        fjim__hmge = get_const_func_output_type(func, qcr__vhtf, kws,
            typing_context, target_context)
    except Exception as eyoh__iqyrg:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', eyoh__iqyrg),
            getattr(eyoh__iqyrg, 'loc', None))
    return fjim__hmge


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    qcr__vhtf = (grp,) + f_args
    try:
        fjim__hmge = get_const_func_output_type(func, qcr__vhtf, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as eyoh__iqyrg:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()',
            eyoh__iqyrg), getattr(eyoh__iqyrg, 'loc', None))
    tow__pbye = gen_apply_pysig(len(f_args), kws.keys())
    kmpz__mueu = (func, *f_args) + tuple(kws.values())
    return signature(fjim__hmge, *kmpz__mueu).replace(pysig=tow__pbye)


def gen_apply_pysig(n_args, kws):
    unt__dxc = ', '.join(f'arg{zhff__tfp}' for zhff__tfp in range(n_args))
    unt__dxc = unt__dxc + ', ' if unt__dxc else ''
    gzcq__snx = ', '.join(f"{vuz__lduxy} = ''" for vuz__lduxy in kws)
    liol__poak = f'def apply_stub(func, {unt__dxc}{gzcq__snx}):\n'
    liol__poak += '    pass\n'
    vntm__mlc = {}
    exec(liol__poak, {}, vntm__mlc)
    isooa__bjl = vntm__mlc['apply_stub']
    return numba.core.utils.pysignature(isooa__bjl)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        tzekd__aobhu = types.Array(types.int64, 1, 'C')
        qifjp__cmitt = _pivot_values.meta
        brgcm__rzmd = len(qifjp__cmitt)
        ywzmp__emoz = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        zvxxi__aqgp = DataFrameType((tzekd__aobhu,) * brgcm__rzmd,
            ywzmp__emoz, tuple(qifjp__cmitt))
        return signature(zvxxi__aqgp, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    liol__poak = 'def impl(keys, dropna, _is_parallel):\n'
    liol__poak += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    liol__poak += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{zhff__tfp}])' for zhff__tfp in range(len(keys
        .types))))
    liol__poak += '    table = arr_info_list_to_table(info_list)\n'
    liol__poak += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    liol__poak += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    liol__poak += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    liol__poak += '    delete_table_decref_arrays(table)\n'
    liol__poak += '    ev.finalize()\n'
    liol__poak += '    return sort_idx, group_labels, ngroups\n'
    vntm__mlc = {}
    exec(liol__poak, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, vntm__mlc)
    xikcz__ftrld = vntm__mlc['impl']
    return xikcz__ftrld


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    srl__szdo = len(labels)
    ynivb__mxip = np.zeros(ngroups, dtype=np.int64)
    qeeg__cei = np.zeros(ngroups, dtype=np.int64)
    ajq__ifhl = 0
    eqj__mbrez = 0
    for zhff__tfp in range(srl__szdo):
        guj__ulek = labels[zhff__tfp]
        if guj__ulek < 0:
            ajq__ifhl += 1
        else:
            eqj__mbrez += 1
            if zhff__tfp == srl__szdo - 1 or guj__ulek != labels[zhff__tfp + 1
                ]:
                ynivb__mxip[guj__ulek] = ajq__ifhl
                qeeg__cei[guj__ulek] = ajq__ifhl + eqj__mbrez
                ajq__ifhl += eqj__mbrez
                eqj__mbrez = 0
    return ynivb__mxip, qeeg__cei


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    xikcz__ftrld, sfhcg__dtrrb = gen_shuffle_dataframe(df, keys, _is_parallel)
    return xikcz__ftrld


def gen_shuffle_dataframe(df, keys, _is_parallel):
    aqyq__njiw = len(df.columns)
    gqpdr__gyuo = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    liol__poak = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        liol__poak += '  return df, keys, get_null_shuffle_info()\n'
        vntm__mlc = {}
        exec(liol__poak, {'get_null_shuffle_info': get_null_shuffle_info},
            vntm__mlc)
        xikcz__ftrld = vntm__mlc['impl']
        return xikcz__ftrld
    for zhff__tfp in range(aqyq__njiw):
        liol__poak += f"""  in_arr{zhff__tfp} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {zhff__tfp})
"""
    liol__poak += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    liol__poak += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{zhff__tfp}])' for zhff__tfp in range(
        gqpdr__gyuo)), ', '.join(f'array_to_info(in_arr{zhff__tfp})' for
        zhff__tfp in range(aqyq__njiw)), 'array_to_info(in_index_arr)')
    liol__poak += '  table = arr_info_list_to_table(info_list)\n'
    liol__poak += (
        f'  out_table = shuffle_table(table, {gqpdr__gyuo}, _is_parallel, 1)\n'
        )
    for zhff__tfp in range(gqpdr__gyuo):
        liol__poak += f"""  out_key{zhff__tfp} = info_to_array(info_from_table(out_table, {zhff__tfp}), keys{zhff__tfp}_typ)
"""
    for zhff__tfp in range(aqyq__njiw):
        liol__poak += f"""  out_arr{zhff__tfp} = info_to_array(info_from_table(out_table, {zhff__tfp + gqpdr__gyuo}), in_arr{zhff__tfp}_typ)
"""
    liol__poak += f"""  out_arr_index = info_to_array(info_from_table(out_table, {gqpdr__gyuo + aqyq__njiw}), ind_arr_typ)
"""
    liol__poak += '  shuffle_info = get_shuffle_info(out_table)\n'
    liol__poak += '  delete_table(out_table)\n'
    liol__poak += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{zhff__tfp}' for zhff__tfp in range(
        aqyq__njiw))
    liol__poak += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    liol__poak += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    liol__poak += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{zhff__tfp}' for zhff__tfp in range(gqpdr__gyuo)))
    izwkm__cqal = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    izwkm__cqal.update({f'keys{zhff__tfp}_typ': keys.types[zhff__tfp] for
        zhff__tfp in range(gqpdr__gyuo)})
    izwkm__cqal.update({f'in_arr{zhff__tfp}_typ': df.data[zhff__tfp] for
        zhff__tfp in range(aqyq__njiw)})
    vntm__mlc = {}
    exec(liol__poak, izwkm__cqal, vntm__mlc)
    xikcz__ftrld = vntm__mlc['impl']
    return xikcz__ftrld, izwkm__cqal


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        pftk__fxlvx = len(data.array_types)
        liol__poak = 'def impl(data, shuffle_info):\n'
        liol__poak += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{zhff__tfp}])' for zhff__tfp in
            range(pftk__fxlvx)))
        liol__poak += '  table = arr_info_list_to_table(info_list)\n'
        liol__poak += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for zhff__tfp in range(pftk__fxlvx):
            liol__poak += f"""  out_arr{zhff__tfp} = info_to_array(info_from_table(out_table, {zhff__tfp}), data._data[{zhff__tfp}])
"""
        liol__poak += '  delete_table(out_table)\n'
        liol__poak += '  delete_table(table)\n'
        liol__poak += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{zhff__tfp}' for zhff__tfp in range(
            pftk__fxlvx))))
        vntm__mlc = {}
        exec(liol__poak, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, vntm__mlc)
        xikcz__ftrld = vntm__mlc['impl']
        return xikcz__ftrld
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            zmcev__cia = bodo.utils.conversion.index_to_array(data)
            zho__vzb = reverse_shuffle(zmcev__cia, shuffle_info)
            return bodo.utils.conversion.index_from_array(zho__vzb)
        return impl_index

    def impl_arr(data, shuffle_info):
        wjd__jmo = [array_to_info(data)]
        vbuy__xww = arr_info_list_to_table(wjd__jmo)
        ibgxv__zyvr = reverse_shuffle_table(vbuy__xww, shuffle_info)
        zho__vzb = info_to_array(info_from_table(ibgxv__zyvr, 0), data)
        delete_table(ibgxv__zyvr)
        delete_table(vbuy__xww)
        return zho__vzb
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    mfa__emj = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    ecj__aevt = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', mfa__emj, ecj__aevt,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    slhdo__gipwu = get_overload_const_bool(ascending)
    ndhpa__nbbpx = grp.selection[0]
    liol__poak = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    mvo__qwxsy = (
        f"lambda S: S.value_counts(ascending={slhdo__gipwu}, _index_name='{ndhpa__nbbpx}')"
        )
    liol__poak += f'    return grp.apply({mvo__qwxsy})\n'
    vntm__mlc = {}
    exec(liol__poak, {'bodo': bodo}, vntm__mlc)
    xikcz__ftrld = vntm__mlc['impl']
    return xikcz__ftrld


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
    for ajhke__qvuyw in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, ajhke__qvuyw, no_unliteral
            =True)(create_unsupported_overload(
            f'DataFrameGroupBy.{ajhke__qvuyw}'))
    for ajhke__qvuyw in groupby_unsupported:
        overload_method(DataFrameGroupByType, ajhke__qvuyw, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ajhke__qvuyw}'))
    for ajhke__qvuyw in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, ajhke__qvuyw, no_unliteral
            =True)(create_unsupported_overload(f'SeriesGroupBy.{ajhke__qvuyw}')
            )
    for ajhke__qvuyw in series_only_unsupported:
        overload_method(DataFrameGroupByType, ajhke__qvuyw, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{ajhke__qvuyw}'))
    for ajhke__qvuyw in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, ajhke__qvuyw, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ajhke__qvuyw}'))


_install_groupby_unsupported()
