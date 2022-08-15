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
        pog__xfibx = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, pog__xfibx)


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
        kailm__bgit = args[0]
        woivm__ttwv = signature.return_type
        ivkh__iicc = cgutils.create_struct_proxy(woivm__ttwv)(context, builder)
        ivkh__iicc.obj = kailm__bgit
        context.nrt.incref(builder, signature.args[0], kailm__bgit)
        return ivkh__iicc._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for ikfnj__gzlt in keys:
        selection.remove(ikfnj__gzlt)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        sbku__zyfu = get_overload_const_int(_num_shuffle_keys)
    else:
        sbku__zyfu = -1
    woivm__ttwv = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=sbku__zyfu)
    return woivm__ttwv(obj_type, by_type, as_index_type, dropna_type,
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
        grpby, skaod__nszqz = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(skaod__nszqz, (tuple, list)):
                if len(set(skaod__nszqz).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(skaod__nszqz).difference(set(grpby.
                        df_type.columns))))
                selection = skaod__nszqz
            else:
                if skaod__nszqz not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(skaod__nszqz))
                selection = skaod__nszqz,
                series_select = True
            vwubm__gfrzi = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(vwubm__gfrzi, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, skaod__nszqz = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            skaod__nszqz):
            vwubm__gfrzi = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(skaod__nszqz)), {}).return_type
            return signature(vwubm__gfrzi, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    ydj__gasrh = arr_type == ArrayItemArrayType(string_array_type)
    lbw__voup = arr_type.dtype
    if isinstance(lbw__voup, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {lbw__voup} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(lbw__voup, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {lbw__voup} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(lbw__voup,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(lbw__voup, (types.Integer, types.Float, types.Boolean)):
        if ydj__gasrh or lbw__voup == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(lbw__voup, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not lbw__voup.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {lbw__voup} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(lbw__voup, types.Boolean) and func_name in {'cumsum',
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
    lbw__voup = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(lbw__voup, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(lbw__voup, types.Integer):
            return IntDtype(lbw__voup)
        return lbw__voup
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        jxzco__jazuh = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{jxzco__jazuh}'."
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
    for ikfnj__gzlt in grp.keys:
        if multi_level_names:
            nocdh__irb = ikfnj__gzlt, ''
        else:
            nocdh__irb = ikfnj__gzlt
        hyitj__cthti = grp.df_type.column_index[ikfnj__gzlt]
        data = grp.df_type.data[hyitj__cthti]
        out_columns.append(nocdh__irb)
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
        wnw__dgpzx = tuple(grp.df_type.column_index[grp.keys[witb__qzlvx]] for
            witb__qzlvx in range(len(grp.keys)))
        pahz__awd = tuple(grp.df_type.data[hyitj__cthti] for hyitj__cthti in
            wnw__dgpzx)
        index = MultiIndexType(pahz__awd, tuple(types.StringLiteral(
            ikfnj__gzlt) for ikfnj__gzlt in grp.keys))
    else:
        hyitj__cthti = grp.df_type.column_index[grp.keys[0]]
        zjsvi__zojb = grp.df_type.data[hyitj__cthti]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(zjsvi__zojb,
            types.StringLiteral(grp.keys[0]))
    aeyox__gwu = {}
    ojvss__yopdi = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        aeyox__gwu[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        aeyox__gwu[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        xdpl__hdjzl = dict(ascending=ascending)
        isvj__wscq = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', xdpl__hdjzl,
            isvj__wscq, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for pbvb__yeo in columns:
            hyitj__cthti = grp.df_type.column_index[pbvb__yeo]
            data = grp.df_type.data[hyitj__cthti]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            rccdm__cmy = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                rccdm__cmy = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    mph__jgos = SeriesType(data.dtype, data, None, string_type)
                    kgfb__yky = get_const_func_output_type(func, (mph__jgos
                        ,), {}, typing_context, target_context)
                    if kgfb__yky != ArrayItemArrayType(string_array_type):
                        kgfb__yky = dtype_to_array_type(kgfb__yky)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=pbvb__yeo, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    hdoy__ghd = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    baflt__buce = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    xdpl__hdjzl = dict(numeric_only=hdoy__ghd, min_count=
                        baflt__buce)
                    isvj__wscq = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xdpl__hdjzl, isvj__wscq, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    hdoy__ghd = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    baflt__buce = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    xdpl__hdjzl = dict(numeric_only=hdoy__ghd, min_count=
                        baflt__buce)
                    isvj__wscq = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xdpl__hdjzl, isvj__wscq, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    hdoy__ghd = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    xdpl__hdjzl = dict(numeric_only=hdoy__ghd)
                    isvj__wscq = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xdpl__hdjzl, isvj__wscq, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    cpqs__ofujv = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    hrh__ftc = args[1] if len(args) > 1 else kws.pop('skipna',
                        True)
                    xdpl__hdjzl = dict(axis=cpqs__ofujv, skipna=hrh__ftc)
                    isvj__wscq = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xdpl__hdjzl, isvj__wscq, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    dpr__qyjbw = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    xdpl__hdjzl = dict(ddof=dpr__qyjbw)
                    isvj__wscq = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        xdpl__hdjzl, isvj__wscq, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                kgfb__yky, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                kgfb__yky = to_str_arr_if_dict_array(kgfb__yky
                    ) if func_name in ('sum', 'cumsum') else kgfb__yky
                out_data.append(kgfb__yky)
                out_columns.append(pbvb__yeo)
                if func_name == 'agg':
                    vfno__habif = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    aeyox__gwu[pbvb__yeo, vfno__habif] = pbvb__yeo
                else:
                    aeyox__gwu[pbvb__yeo, func_name] = pbvb__yeo
                out_column_type.append(rccdm__cmy)
            else:
                ojvss__yopdi.append(err_msg)
    if func_name == 'sum':
        gxzt__qwnu = any([(ydwad__mkqbh == ColumnType.NumericalColumn.value
            ) for ydwad__mkqbh in out_column_type])
        if gxzt__qwnu:
            out_data = [ydwad__mkqbh for ydwad__mkqbh, pbxg__bylw in zip(
                out_data, out_column_type) if pbxg__bylw != ColumnType.
                NonNumericalColumn.value]
            out_columns = [ydwad__mkqbh for ydwad__mkqbh, pbxg__bylw in zip
                (out_columns, out_column_type) if pbxg__bylw != ColumnType.
                NonNumericalColumn.value]
            aeyox__gwu = {}
            for pbvb__yeo in out_columns:
                if grp.as_index is False and pbvb__yeo in grp.keys:
                    continue
                aeyox__gwu[pbvb__yeo, func_name] = pbvb__yeo
    gvqty__tbn = len(ojvss__yopdi)
    if len(out_data) == 0:
        if gvqty__tbn == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(gvqty__tbn, ' was' if gvqty__tbn == 1 else 's were',
                ','.join(ojvss__yopdi)))
    vay__vjxh = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            hctsh__tllfe = IntDtype(out_data[0].dtype)
        else:
            hctsh__tllfe = out_data[0].dtype
        kci__jvyej = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        vay__vjxh = SeriesType(hctsh__tllfe, data=out_data[0], index=index,
            name_typ=kci__jvyej)
    return signature(vay__vjxh, *args), aeyox__gwu


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    pwhqj__ukyf = True
    if isinstance(f_val, str):
        pwhqj__ukyf = False
        mbpi__tqumx = f_val
    elif is_overload_constant_str(f_val):
        pwhqj__ukyf = False
        mbpi__tqumx = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        pwhqj__ukyf = False
        mbpi__tqumx = bodo.utils.typing.get_builtin_function_name(f_val)
    if not pwhqj__ukyf:
        if mbpi__tqumx not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {mbpi__tqumx}')
        vwubm__gfrzi = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(vwubm__gfrzi, (), mbpi__tqumx, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            qgc__qflrd = types.functions.MakeFunctionLiteral(f_val)
        else:
            qgc__qflrd = f_val
        validate_udf('agg', qgc__qflrd)
        func = get_overload_const_func(qgc__qflrd, None)
        klq__fctm = func.code if hasattr(func, 'code') else func.__code__
        mbpi__tqumx = klq__fctm.co_name
        vwubm__gfrzi = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(vwubm__gfrzi, (), 'agg', typing_context,
            target_context, qgc__qflrd)[0].return_type
    return mbpi__tqumx, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    dbfam__dnum = kws and all(isinstance(jkqay__yeds, types.Tuple) and len(
        jkqay__yeds) == 2 for jkqay__yeds in kws.values())
    if is_overload_none(func) and not dbfam__dnum:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not dbfam__dnum:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    zewj__rwc = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if dbfam__dnum or is_overload_constant_dict(func):
        if dbfam__dnum:
            rbowo__nqcz = [get_literal_value(plm__tbxeq) for plm__tbxeq,
                yebtz__fsasq in kws.values()]
            llrl__ndkxi = [get_literal_value(mioy__pktxx) for yebtz__fsasq,
                mioy__pktxx in kws.values()]
        else:
            koeud__vomv = get_overload_constant_dict(func)
            rbowo__nqcz = tuple(koeud__vomv.keys())
            llrl__ndkxi = tuple(koeud__vomv.values())
        for puir__ynzk in ('head', 'ngroup'):
            if puir__ynzk in llrl__ndkxi:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {puir__ynzk} cannot be mixed with other groupby operations.'
                    )
        if any(pbvb__yeo not in grp.selection and pbvb__yeo not in grp.keys for
            pbvb__yeo in rbowo__nqcz):
            raise_bodo_error(
                f'Selected column names {rbowo__nqcz} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            llrl__ndkxi)
        if dbfam__dnum and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        aeyox__gwu = {}
        out_columns = []
        out_data = []
        out_column_type = []
        nsiz__ddf = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for ybyjm__mpqut, f_val in zip(rbowo__nqcz, llrl__ndkxi):
            if isinstance(f_val, (tuple, list)):
                mshx__hlfnw = 0
                for qgc__qflrd in f_val:
                    mbpi__tqumx, out_tp = get_agg_funcname_and_outtyp(grp,
                        ybyjm__mpqut, qgc__qflrd, typing_context,
                        target_context)
                    zewj__rwc = mbpi__tqumx in list_cumulative
                    if mbpi__tqumx == '<lambda>' and len(f_val) > 1:
                        mbpi__tqumx = '<lambda_' + str(mshx__hlfnw) + '>'
                        mshx__hlfnw += 1
                    out_columns.append((ybyjm__mpqut, mbpi__tqumx))
                    aeyox__gwu[ybyjm__mpqut, mbpi__tqumx
                        ] = ybyjm__mpqut, mbpi__tqumx
                    _append_out_type(grp, out_data, out_tp)
            else:
                mbpi__tqumx, out_tp = get_agg_funcname_and_outtyp(grp,
                    ybyjm__mpqut, f_val, typing_context, target_context)
                zewj__rwc = mbpi__tqumx in list_cumulative
                if multi_level_names:
                    out_columns.append((ybyjm__mpqut, mbpi__tqumx))
                    aeyox__gwu[ybyjm__mpqut, mbpi__tqumx
                        ] = ybyjm__mpqut, mbpi__tqumx
                elif not dbfam__dnum:
                    out_columns.append(ybyjm__mpqut)
                    aeyox__gwu[ybyjm__mpqut, mbpi__tqumx] = ybyjm__mpqut
                elif dbfam__dnum:
                    nsiz__ddf.append(mbpi__tqumx)
                _append_out_type(grp, out_data, out_tp)
        if dbfam__dnum:
            for witb__qzlvx, dzzbr__mhl in enumerate(kws.keys()):
                out_columns.append(dzzbr__mhl)
                aeyox__gwu[rbowo__nqcz[witb__qzlvx], nsiz__ddf[witb__qzlvx]
                    ] = dzzbr__mhl
        if zewj__rwc:
            index = grp.df_type.index
        else:
            index = out_tp.index
        vay__vjxh = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(vay__vjxh, *args), aeyox__gwu
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            haqul__yqpbo = get_overload_const_list(func)
        else:
            haqul__yqpbo = func.types
        if len(haqul__yqpbo) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        mshx__hlfnw = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        aeyox__gwu = {}
        fzk__jiai = grp.selection[0]
        for f_val in haqul__yqpbo:
            mbpi__tqumx, out_tp = get_agg_funcname_and_outtyp(grp,
                fzk__jiai, f_val, typing_context, target_context)
            zewj__rwc = mbpi__tqumx in list_cumulative
            if mbpi__tqumx == '<lambda>' and len(haqul__yqpbo) > 1:
                mbpi__tqumx = '<lambda_' + str(mshx__hlfnw) + '>'
                mshx__hlfnw += 1
            out_columns.append(mbpi__tqumx)
            aeyox__gwu[fzk__jiai, mbpi__tqumx] = mbpi__tqumx
            _append_out_type(grp, out_data, out_tp)
        if zewj__rwc:
            index = grp.df_type.index
        else:
            index = out_tp.index
        vay__vjxh = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(vay__vjxh, *args), aeyox__gwu
    mbpi__tqumx = ''
    if types.unliteral(func) == types.unicode_type:
        mbpi__tqumx = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        mbpi__tqumx = bodo.utils.typing.get_builtin_function_name(func)
    if mbpi__tqumx:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, mbpi__tqumx, typing_context, kws)
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
        cpqs__ofujv = args[0] if len(args) > 0 else kws.pop('axis', 0)
        hdoy__ghd = args[1] if len(args) > 1 else kws.pop('numeric_only', False
            )
        hrh__ftc = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        xdpl__hdjzl = dict(axis=cpqs__ofujv, numeric_only=hdoy__ghd)
        isvj__wscq = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', xdpl__hdjzl,
            isvj__wscq, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        fxb__fhwol = args[0] if len(args) > 0 else kws.pop('periods', 1)
        fmdyw__foznp = args[1] if len(args) > 1 else kws.pop('freq', None)
        cpqs__ofujv = args[2] if len(args) > 2 else kws.pop('axis', 0)
        ojz__wgwwb = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        xdpl__hdjzl = dict(freq=fmdyw__foznp, axis=cpqs__ofujv, fill_value=
            ojz__wgwwb)
        isvj__wscq = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', xdpl__hdjzl,
            isvj__wscq, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        izwg__jvsau = args[0] if len(args) > 0 else kws.pop('func', None)
        rwc__inis = kws.pop('engine', None)
        gndye__hdes = kws.pop('engine_kwargs', None)
        xdpl__hdjzl = dict(engine=rwc__inis, engine_kwargs=gndye__hdes)
        isvj__wscq = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', xdpl__hdjzl,
            isvj__wscq, package_name='pandas', module_name='GroupBy')
    aeyox__gwu = {}
    for pbvb__yeo in grp.selection:
        out_columns.append(pbvb__yeo)
        aeyox__gwu[pbvb__yeo, name_operation] = pbvb__yeo
        hyitj__cthti = grp.df_type.column_index[pbvb__yeo]
        data = grp.df_type.data[hyitj__cthti]
        mlz__mxme = (name_operation if name_operation != 'transform' else
            get_literal_value(izwg__jvsau))
        if mlz__mxme in ('sum', 'cumsum'):
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
            kgfb__yky, err_msg = get_groupby_output_dtype(data,
                get_literal_value(izwg__jvsau), grp.df_type.index)
            if err_msg == 'ok':
                data = kgfb__yky
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    vay__vjxh = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        vay__vjxh = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(vay__vjxh, *args), aeyox__gwu


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
        hlmx__nbhi = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        wtrj__thi = isinstance(hlmx__nbhi, (SeriesType,
            HeterogeneousSeriesType)
            ) and hlmx__nbhi.const_info is not None or not isinstance(
            hlmx__nbhi, (SeriesType, DataFrameType))
        if wtrj__thi:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                oyept__adkcf = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                wnw__dgpzx = tuple(grp.df_type.column_index[grp.keys[
                    witb__qzlvx]] for witb__qzlvx in range(len(grp.keys)))
                pahz__awd = tuple(grp.df_type.data[hyitj__cthti] for
                    hyitj__cthti in wnw__dgpzx)
                oyept__adkcf = MultiIndexType(pahz__awd, tuple(types.
                    literal(ikfnj__gzlt) for ikfnj__gzlt in grp.keys))
            else:
                hyitj__cthti = grp.df_type.column_index[grp.keys[0]]
                zjsvi__zojb = grp.df_type.data[hyitj__cthti]
                oyept__adkcf = bodo.hiframes.pd_index_ext.array_type_to_index(
                    zjsvi__zojb, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            qgibd__dxg = tuple(grp.df_type.data[grp.df_type.column_index[
                pbvb__yeo]] for pbvb__yeo in grp.keys)
            galvw__tlr = tuple(types.literal(jkqay__yeds) for jkqay__yeds in
                grp.keys) + get_index_name_types(hlmx__nbhi.index)
            if not grp.as_index:
                qgibd__dxg = types.Array(types.int64, 1, 'C'),
                galvw__tlr = (types.none,) + get_index_name_types(hlmx__nbhi
                    .index)
            oyept__adkcf = MultiIndexType(qgibd__dxg +
                get_index_data_arr_types(hlmx__nbhi.index), galvw__tlr)
        if wtrj__thi:
            if isinstance(hlmx__nbhi, HeterogeneousSeriesType):
                yebtz__fsasq, gyusx__ivyfw = hlmx__nbhi.const_info
                if isinstance(hlmx__nbhi.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    agod__wfn = hlmx__nbhi.data.tuple_typ.types
                elif isinstance(hlmx__nbhi.data, types.Tuple):
                    agod__wfn = hlmx__nbhi.data.types
                idu__pia = tuple(to_nullable_type(dtype_to_array_type(
                    srz__ccmn)) for srz__ccmn in agod__wfn)
                mivwf__ypd = DataFrameType(out_data + idu__pia,
                    oyept__adkcf, out_columns + gyusx__ivyfw)
            elif isinstance(hlmx__nbhi, SeriesType):
                rou__jkycl, gyusx__ivyfw = hlmx__nbhi.const_info
                idu__pia = tuple(to_nullable_type(dtype_to_array_type(
                    hlmx__nbhi.dtype)) for yebtz__fsasq in range(rou__jkycl))
                mivwf__ypd = DataFrameType(out_data + idu__pia,
                    oyept__adkcf, out_columns + gyusx__ivyfw)
            else:
                oui__wrg = get_udf_out_arr_type(hlmx__nbhi)
                if not grp.as_index:
                    mivwf__ypd = DataFrameType(out_data + (oui__wrg,),
                        oyept__adkcf, out_columns + ('',))
                else:
                    mivwf__ypd = SeriesType(oui__wrg.dtype, oui__wrg,
                        oyept__adkcf, None)
        elif isinstance(hlmx__nbhi, SeriesType):
            mivwf__ypd = SeriesType(hlmx__nbhi.dtype, hlmx__nbhi.data,
                oyept__adkcf, hlmx__nbhi.name_typ)
        else:
            mivwf__ypd = DataFrameType(hlmx__nbhi.data, oyept__adkcf,
                hlmx__nbhi.columns)
        cwhta__zzwz = gen_apply_pysig(len(f_args), kws.keys())
        owta__ctsdf = (func, *f_args) + tuple(kws.values())
        return signature(mivwf__ypd, *owta__ctsdf).replace(pysig=cwhta__zzwz)

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
    cylc__dkcbq = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            ybyjm__mpqut = grp.selection[0]
            oui__wrg = cylc__dkcbq.data[cylc__dkcbq.column_index[ybyjm__mpqut]]
            ihot__pjoe = SeriesType(oui__wrg.dtype, oui__wrg, cylc__dkcbq.
                index, types.literal(ybyjm__mpqut))
        else:
            ivaa__twhmo = tuple(cylc__dkcbq.data[cylc__dkcbq.column_index[
                pbvb__yeo]] for pbvb__yeo in grp.selection)
            ihot__pjoe = DataFrameType(ivaa__twhmo, cylc__dkcbq.index,
                tuple(grp.selection))
    else:
        ihot__pjoe = cylc__dkcbq
    ewuxl__alom = ihot__pjoe,
    ewuxl__alom += tuple(f_args)
    try:
        hlmx__nbhi = get_const_func_output_type(func, ewuxl__alom, kws,
            typing_context, target_context)
    except Exception as ugek__eycah:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', ugek__eycah),
            getattr(ugek__eycah, 'loc', None))
    return hlmx__nbhi


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    ewuxl__alom = (grp,) + f_args
    try:
        hlmx__nbhi = get_const_func_output_type(func, ewuxl__alom, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as ugek__eycah:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()',
            ugek__eycah), getattr(ugek__eycah, 'loc', None))
    cwhta__zzwz = gen_apply_pysig(len(f_args), kws.keys())
    owta__ctsdf = (func, *f_args) + tuple(kws.values())
    return signature(hlmx__nbhi, *owta__ctsdf).replace(pysig=cwhta__zzwz)


def gen_apply_pysig(n_args, kws):
    aefa__ekwe = ', '.join(f'arg{witb__qzlvx}' for witb__qzlvx in range(n_args)
        )
    aefa__ekwe = aefa__ekwe + ', ' if aefa__ekwe else ''
    mknac__azh = ', '.join(f"{xtqyo__sbdey} = ''" for xtqyo__sbdey in kws)
    kbo__jtxvh = f'def apply_stub(func, {aefa__ekwe}{mknac__azh}):\n'
    kbo__jtxvh += '    pass\n'
    syypd__nlk = {}
    exec(kbo__jtxvh, {}, syypd__nlk)
    svavt__qfg = syypd__nlk['apply_stub']
    return numba.core.utils.pysignature(svavt__qfg)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        tprjq__agkl = types.Array(types.int64, 1, 'C')
        ndoz__uqvtz = _pivot_values.meta
        cord__ktda = len(ndoz__uqvtz)
        idb__dbglk = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        quab__myfu = DataFrameType((tprjq__agkl,) * cord__ktda, idb__dbglk,
            tuple(ndoz__uqvtz))
        return signature(quab__myfu, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    kbo__jtxvh = 'def impl(keys, dropna, _is_parallel):\n'
    kbo__jtxvh += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    kbo__jtxvh += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{witb__qzlvx}])' for witb__qzlvx in range(len(
        keys.types))))
    kbo__jtxvh += '    table = arr_info_list_to_table(info_list)\n'
    kbo__jtxvh += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    kbo__jtxvh += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    kbo__jtxvh += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    kbo__jtxvh += '    delete_table_decref_arrays(table)\n'
    kbo__jtxvh += '    ev.finalize()\n'
    kbo__jtxvh += '    return sort_idx, group_labels, ngroups\n'
    syypd__nlk = {}
    exec(kbo__jtxvh, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, syypd__nlk)
    mcfpj__cjs = syypd__nlk['impl']
    return mcfpj__cjs


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    khg__ade = len(labels)
    qmpal__lhga = np.zeros(ngroups, dtype=np.int64)
    mxr__paicl = np.zeros(ngroups, dtype=np.int64)
    iiz__wlqfz = 0
    ejxy__phrh = 0
    for witb__qzlvx in range(khg__ade):
        jmo__xmdl = labels[witb__qzlvx]
        if jmo__xmdl < 0:
            iiz__wlqfz += 1
        else:
            ejxy__phrh += 1
            if witb__qzlvx == khg__ade - 1 or jmo__xmdl != labels[
                witb__qzlvx + 1]:
                qmpal__lhga[jmo__xmdl] = iiz__wlqfz
                mxr__paicl[jmo__xmdl] = iiz__wlqfz + ejxy__phrh
                iiz__wlqfz += ejxy__phrh
                ejxy__phrh = 0
    return qmpal__lhga, mxr__paicl


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    mcfpj__cjs, yebtz__fsasq = gen_shuffle_dataframe(df, keys, _is_parallel)
    return mcfpj__cjs


def gen_shuffle_dataframe(df, keys, _is_parallel):
    rou__jkycl = len(df.columns)
    mkaay__ets = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    kbo__jtxvh = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        kbo__jtxvh += '  return df, keys, get_null_shuffle_info()\n'
        syypd__nlk = {}
        exec(kbo__jtxvh, {'get_null_shuffle_info': get_null_shuffle_info},
            syypd__nlk)
        mcfpj__cjs = syypd__nlk['impl']
        return mcfpj__cjs
    for witb__qzlvx in range(rou__jkycl):
        kbo__jtxvh += f"""  in_arr{witb__qzlvx} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {witb__qzlvx})
"""
    kbo__jtxvh += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    kbo__jtxvh += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{witb__qzlvx}])' for witb__qzlvx in range(
        mkaay__ets)), ', '.join(f'array_to_info(in_arr{witb__qzlvx})' for
        witb__qzlvx in range(rou__jkycl)), 'array_to_info(in_index_arr)')
    kbo__jtxvh += '  table = arr_info_list_to_table(info_list)\n'
    kbo__jtxvh += (
        f'  out_table = shuffle_table(table, {mkaay__ets}, _is_parallel, 1)\n')
    for witb__qzlvx in range(mkaay__ets):
        kbo__jtxvh += f"""  out_key{witb__qzlvx} = info_to_array(info_from_table(out_table, {witb__qzlvx}), keys{witb__qzlvx}_typ)
"""
    for witb__qzlvx in range(rou__jkycl):
        kbo__jtxvh += f"""  out_arr{witb__qzlvx} = info_to_array(info_from_table(out_table, {witb__qzlvx + mkaay__ets}), in_arr{witb__qzlvx}_typ)
"""
    kbo__jtxvh += f"""  out_arr_index = info_to_array(info_from_table(out_table, {mkaay__ets + rou__jkycl}), ind_arr_typ)
"""
    kbo__jtxvh += '  shuffle_info = get_shuffle_info(out_table)\n'
    kbo__jtxvh += '  delete_table(out_table)\n'
    kbo__jtxvh += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{witb__qzlvx}' for witb__qzlvx in range(
        rou__jkycl))
    kbo__jtxvh += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    kbo__jtxvh += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    kbo__jtxvh += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{witb__qzlvx}' for witb__qzlvx in range(mkaay__ets)))
    vaa__mnlqe = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    vaa__mnlqe.update({f'keys{witb__qzlvx}_typ': keys.types[witb__qzlvx] for
        witb__qzlvx in range(mkaay__ets)})
    vaa__mnlqe.update({f'in_arr{witb__qzlvx}_typ': df.data[witb__qzlvx] for
        witb__qzlvx in range(rou__jkycl)})
    syypd__nlk = {}
    exec(kbo__jtxvh, vaa__mnlqe, syypd__nlk)
    mcfpj__cjs = syypd__nlk['impl']
    return mcfpj__cjs, vaa__mnlqe


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        uxirk__mqpjm = len(data.array_types)
        kbo__jtxvh = 'def impl(data, shuffle_info):\n'
        kbo__jtxvh += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{witb__qzlvx}])' for witb__qzlvx in
            range(uxirk__mqpjm)))
        kbo__jtxvh += '  table = arr_info_list_to_table(info_list)\n'
        kbo__jtxvh += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for witb__qzlvx in range(uxirk__mqpjm):
            kbo__jtxvh += f"""  out_arr{witb__qzlvx} = info_to_array(info_from_table(out_table, {witb__qzlvx}), data._data[{witb__qzlvx}])
"""
        kbo__jtxvh += '  delete_table(out_table)\n'
        kbo__jtxvh += '  delete_table(table)\n'
        kbo__jtxvh += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{witb__qzlvx}' for witb__qzlvx in
            range(uxirk__mqpjm))))
        syypd__nlk = {}
        exec(kbo__jtxvh, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, syypd__nlk)
        mcfpj__cjs = syypd__nlk['impl']
        return mcfpj__cjs
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            idh__klhcy = bodo.utils.conversion.index_to_array(data)
            cmm__yrp = reverse_shuffle(idh__klhcy, shuffle_info)
            return bodo.utils.conversion.index_from_array(cmm__yrp)
        return impl_index

    def impl_arr(data, shuffle_info):
        vgpk__mbe = [array_to_info(data)]
        groje__ktntu = arr_info_list_to_table(vgpk__mbe)
        pnkd__nmus = reverse_shuffle_table(groje__ktntu, shuffle_info)
        cmm__yrp = info_to_array(info_from_table(pnkd__nmus, 0), data)
        delete_table(pnkd__nmus)
        delete_table(groje__ktntu)
        return cmm__yrp
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    xdpl__hdjzl = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna
        )
    isvj__wscq = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', xdpl__hdjzl, isvj__wscq,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    ufjr__gbzl = get_overload_const_bool(ascending)
    qateb__yjhbx = grp.selection[0]
    kbo__jtxvh = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    ynq__dkxtg = (
        f"lambda S: S.value_counts(ascending={ufjr__gbzl}, _index_name='{qateb__yjhbx}')"
        )
    kbo__jtxvh += f'    return grp.apply({ynq__dkxtg})\n'
    syypd__nlk = {}
    exec(kbo__jtxvh, {'bodo': bodo}, syypd__nlk)
    mcfpj__cjs = syypd__nlk['impl']
    return mcfpj__cjs


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
    for zaoo__okxi in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, zaoo__okxi, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{zaoo__okxi}'))
    for zaoo__okxi in groupby_unsupported:
        overload_method(DataFrameGroupByType, zaoo__okxi, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{zaoo__okxi}'))
    for zaoo__okxi in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, zaoo__okxi, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{zaoo__okxi}'))
    for zaoo__okxi in series_only_unsupported:
        overload_method(DataFrameGroupByType, zaoo__okxi, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{zaoo__okxi}'))
    for zaoo__okxi in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, zaoo__okxi, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{zaoo__okxi}'))


_install_groupby_unsupported()
