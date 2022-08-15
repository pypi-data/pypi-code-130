"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from functools import cached_property
from urllib.parse import quote
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, decode_if_dict_table, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import fix_arr_dtype, index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_str_arr_type, is_tuple_like_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr, types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format}, {self.has_runtime_cols})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            ipzu__dps = f'{len(self.data)} columns of types {set(self.data)}'
            iark__zfn = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({ipzu__dps}, {self.index}, {iark__zfn}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @cached_property
    def column_index(self):
        return {pcy__zpws: i for i, pcy__zpws in enumerate(self.columns)}

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def runtime_data_types(self):
        return self.data[:-1] if self.has_runtime_cols else self.data

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            rtlhm__soa = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(pqd__muvb.unify(typingctx, nlq__yrec) if pqd__muvb !=
                nlq__yrec else pqd__muvb for pqd__muvb, nlq__yrec in zip(
                self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if rtlhm__soa is not None and None not in data:
                return DataFrameType(data, rtlhm__soa, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(pqd__muvb.is_precise() for pqd__muvb in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        raqn__oyto = self.columns.index(col_name)
        mrvcb__qik = tuple(list(self.data[:raqn__oyto]) + [new_type] + list
            (self.data[raqn__oyto + 1:]))
        return DataFrameType(mrvcb__qik, self.index, self.columns, self.
            dist, self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        utcdi__cjkaw = [('data', data_typ), ('index', fe_type.df_type.index
            ), ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            utcdi__cjkaw.append(('columns', fe_type.df_type.
                runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, utcdi__cjkaw)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        utcdi__cjkaw = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, utcdi__cjkaw)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        til__aqgd = 'n',
        pjqc__cxodo = {'n': 5}
        rqa__qjn, wlqtp__sqgct = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, til__aqgd, pjqc__cxodo)
        ldy__mxed = wlqtp__sqgct[0]
        if not is_overload_int(ldy__mxed):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        bqf__lcfgl = df.copy()
        return bqf__lcfgl(*wlqtp__sqgct).replace(pysig=rqa__qjn)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        jjqr__sai = (df,) + args
        til__aqgd = 'df', 'method', 'min_periods'
        pjqc__cxodo = {'method': 'pearson', 'min_periods': 1}
        jjh__tabaw = 'method',
        rqa__qjn, wlqtp__sqgct = bodo.utils.typing.fold_typing_args(func_name,
            jjqr__sai, kws, til__aqgd, pjqc__cxodo, jjh__tabaw)
        gnz__xjclq = wlqtp__sqgct[2]
        if not is_overload_int(gnz__xjclq):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        knawa__ghypd = []
        wzkma__dsuv = []
        for pcy__zpws, iucc__ccgme in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(iucc__ccgme.dtype):
                knawa__ghypd.append(pcy__zpws)
                wzkma__dsuv.append(types.Array(types.float64, 1, 'A'))
        if len(knawa__ghypd) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        wzkma__dsuv = tuple(wzkma__dsuv)
        knawa__ghypd = tuple(knawa__ghypd)
        index_typ = bodo.utils.typing.type_col_to_index(knawa__ghypd)
        bqf__lcfgl = DataFrameType(wzkma__dsuv, index_typ, knawa__ghypd)
        return bqf__lcfgl(*wlqtp__sqgct).replace(pysig=rqa__qjn)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        eni__bxzrf = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        hzvkb__kli = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        csbw__lyo = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        syg__bwri = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        dfafg__jvr = dict(raw=hzvkb__kli, result_type=csbw__lyo)
        qyzx__lvcyn = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', dfafg__jvr, qyzx__lvcyn,
            package_name='pandas', module_name='DataFrame')
        muf__kts = True
        if types.unliteral(eni__bxzrf) == types.unicode_type:
            if not is_overload_constant_str(eni__bxzrf):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            muf__kts = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        cmsci__rrm = get_overload_const_int(axis)
        if muf__kts and cmsci__rrm != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif cmsci__rrm not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        nhzcu__xgois = []
        for arr_typ in df.data:
            moto__kzqx = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            oatjr__ecs = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(moto__kzqx), types.int64), {}
                ).return_type
            nhzcu__xgois.append(oatjr__ecs)
        dnrqc__imcbw = types.none
        hyzjr__wazq = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(pcy__zpws) for pcy__zpws in df.columns)), None)
        apvup__uaxsa = types.BaseTuple.from_types(nhzcu__xgois)
        lgidu__wcirz = types.Tuple([types.bool_] * len(apvup__uaxsa))
        lzfb__zef = bodo.NullableTupleType(apvup__uaxsa, lgidu__wcirz)
        bxa__wvb = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if bxa__wvb == types.NPDatetime('ns'):
            bxa__wvb = bodo.pd_timestamp_type
        if bxa__wvb == types.NPTimedelta('ns'):
            bxa__wvb = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(apvup__uaxsa):
            jhxo__bkcok = HeterogeneousSeriesType(lzfb__zef, hyzjr__wazq,
                bxa__wvb)
        else:
            jhxo__bkcok = SeriesType(apvup__uaxsa.dtype, lzfb__zef,
                hyzjr__wazq, bxa__wvb)
        lnrn__bth = jhxo__bkcok,
        if syg__bwri is not None:
            lnrn__bth += tuple(syg__bwri.types)
        try:
            if not muf__kts:
                xbct__ejbg = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(eni__bxzrf), self.context,
                    'DataFrame.apply', axis if cmsci__rrm == 1 else None)
            else:
                xbct__ejbg = get_const_func_output_type(eni__bxzrf,
                    lnrn__bth, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as bcwt__cin:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', bcwt__cin))
        if muf__kts:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(xbct__ejbg, (SeriesType, HeterogeneousSeriesType)
                ) and xbct__ejbg.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(xbct__ejbg, HeterogeneousSeriesType):
                shkwa__gaq, jsh__yzp = xbct__ejbg.const_info
                if isinstance(xbct__ejbg.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    blnmp__drlkp = xbct__ejbg.data.tuple_typ.types
                elif isinstance(xbct__ejbg.data, types.Tuple):
                    blnmp__drlkp = xbct__ejbg.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                lsxzt__oaf = tuple(to_nullable_type(dtype_to_array_type(
                    sqo__otub)) for sqo__otub in blnmp__drlkp)
                hbzp__cnnwa = DataFrameType(lsxzt__oaf, df.index, jsh__yzp)
            elif isinstance(xbct__ejbg, SeriesType):
                iof__undq, jsh__yzp = xbct__ejbg.const_info
                lsxzt__oaf = tuple(to_nullable_type(dtype_to_array_type(
                    xbct__ejbg.dtype)) for shkwa__gaq in range(iof__undq))
                hbzp__cnnwa = DataFrameType(lsxzt__oaf, df.index, jsh__yzp)
            else:
                gri__ewsco = get_udf_out_arr_type(xbct__ejbg)
                hbzp__cnnwa = SeriesType(gri__ewsco.dtype, gri__ewsco, df.
                    index, None)
        else:
            hbzp__cnnwa = xbct__ejbg
        ewwl__leu = ', '.join("{} = ''".format(pqd__muvb) for pqd__muvb in
            kws.keys())
        squsw__dsv = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {ewwl__leu}):
"""
        squsw__dsv += '    pass\n'
        bfki__pqs = {}
        exec(squsw__dsv, {}, bfki__pqs)
        ieypb__hoebq = bfki__pqs['apply_stub']
        rqa__qjn = numba.core.utils.pysignature(ieypb__hoebq)
        btv__kzar = (eni__bxzrf, axis, hzvkb__kli, csbw__lyo, syg__bwri
            ) + tuple(kws.values())
        return signature(hbzp__cnnwa, *btv__kzar).replace(pysig=rqa__qjn)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        til__aqgd = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        pjqc__cxodo = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        jjh__tabaw = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        rqa__qjn, wlqtp__sqgct = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, til__aqgd, pjqc__cxodo, jjh__tabaw)
        rre__jgq = wlqtp__sqgct[2]
        if not is_overload_constant_str(rre__jgq):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        anxj__hbnqm = wlqtp__sqgct[0]
        if not is_overload_none(anxj__hbnqm) and not (is_overload_int(
            anxj__hbnqm) or is_overload_constant_str(anxj__hbnqm)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(anxj__hbnqm):
            oea__cnkeu = get_overload_const_str(anxj__hbnqm)
            if oea__cnkeu not in df.columns:
                raise BodoError(f'{func_name}: {oea__cnkeu} column not found.')
        elif is_overload_int(anxj__hbnqm):
            pxw__kkahr = get_overload_const_int(anxj__hbnqm)
            if pxw__kkahr > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {pxw__kkahr} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            anxj__hbnqm = df.columns[anxj__hbnqm]
        uedm__jcb = wlqtp__sqgct[1]
        if not is_overload_none(uedm__jcb) and not (is_overload_int(
            uedm__jcb) or is_overload_constant_str(uedm__jcb)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(uedm__jcb):
            syrx__yzrnv = get_overload_const_str(uedm__jcb)
            if syrx__yzrnv not in df.columns:
                raise BodoError(f'{func_name}: {syrx__yzrnv} column not found.'
                    )
        elif is_overload_int(uedm__jcb):
            rppla__xcygh = get_overload_const_int(uedm__jcb)
            if rppla__xcygh > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {rppla__xcygh} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            uedm__jcb = df.columns[uedm__jcb]
        mhyyq__tbiq = wlqtp__sqgct[3]
        if not is_overload_none(mhyyq__tbiq) and not is_tuple_like_type(
            mhyyq__tbiq):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        tcwo__fho = wlqtp__sqgct[10]
        if not is_overload_none(tcwo__fho) and not is_overload_constant_str(
            tcwo__fho):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        pivbd__sdm = wlqtp__sqgct[12]
        if not is_overload_bool(pivbd__sdm):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        agst__alwv = wlqtp__sqgct[17]
        if not is_overload_none(agst__alwv) and not is_tuple_like_type(
            agst__alwv):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        vfxjm__zwg = wlqtp__sqgct[18]
        if not is_overload_none(vfxjm__zwg) and not is_tuple_like_type(
            vfxjm__zwg):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        psm__xlug = wlqtp__sqgct[22]
        if not is_overload_none(psm__xlug) and not is_overload_int(psm__xlug):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        jsw__mjjg = wlqtp__sqgct[29]
        if not is_overload_none(jsw__mjjg) and not is_overload_constant_str(
            jsw__mjjg):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        zkjf__dlnw = wlqtp__sqgct[30]
        if not is_overload_none(zkjf__dlnw) and not is_overload_constant_str(
            zkjf__dlnw):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        wkl__xnq = types.List(types.mpl_line_2d_type)
        rre__jgq = get_overload_const_str(rre__jgq)
        if rre__jgq == 'scatter':
            if is_overload_none(anxj__hbnqm) and is_overload_none(uedm__jcb):
                raise BodoError(
                    f'{func_name}: {rre__jgq} requires an x and y column.')
            elif is_overload_none(anxj__hbnqm):
                raise BodoError(f'{func_name}: {rre__jgq} x column is missing.'
                    )
            elif is_overload_none(uedm__jcb):
                raise BodoError(f'{func_name}: {rre__jgq} y column is missing.'
                    )
            wkl__xnq = types.mpl_path_collection_type
        elif rre__jgq != 'line':
            raise BodoError(f'{func_name}: {rre__jgq} plot is not supported.')
        return signature(wkl__xnq, *wlqtp__sqgct).replace(pysig=rqa__qjn)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            ufdfa__ciw = df.columns.index(attr)
            arr_typ = df.data[ufdfa__ciw]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            zzs__xxdg = []
            mrvcb__qik = []
            tptp__dhtim = False
            for i, rpwne__spyym in enumerate(df.columns):
                if rpwne__spyym[0] != attr:
                    continue
                tptp__dhtim = True
                zzs__xxdg.append(rpwne__spyym[1] if len(rpwne__spyym) == 2 else
                    rpwne__spyym[1:])
                mrvcb__qik.append(df.data[i])
            if tptp__dhtim:
                return DataFrameType(tuple(mrvcb__qik), df.index, tuple(
                    zzs__xxdg))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        aretc__ctg = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(aretc__ctg)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        rjuxg__jvn = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], rjuxg__jvn)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    fgsin__baoal = builder.module
    sburk__liywt = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    cmb__fuf = cgutils.get_or_insert_function(fgsin__baoal, sburk__liywt,
        name='.dtor.df.{}'.format(df_type))
    if not cmb__fuf.is_declaration:
        return cmb__fuf
    cmb__fuf.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(cmb__fuf.append_basic_block())
    zfnn__yktta = cmb__fuf.args[0]
    ystgy__gww = context.get_value_type(payload_type).as_pointer()
    sbknz__bgxdk = builder.bitcast(zfnn__yktta, ystgy__gww)
    payload = context.make_helper(builder, payload_type, ref=sbknz__bgxdk)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        ppvx__ivy = context.get_python_api(builder)
        xiebd__woej = ppvx__ivy.gil_ensure()
        ppvx__ivy.decref(payload.parent)
        ppvx__ivy.gil_release(xiebd__woej)
    builder.ret_void()
    return cmb__fuf


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    krt__amv = cgutils.create_struct_proxy(payload_type)(context, builder)
    krt__amv.data = data_tup
    krt__amv.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        krt__amv.columns = colnames
    jlnm__ibc = context.get_value_type(payload_type)
    hjvg__ilko = context.get_abi_sizeof(jlnm__ibc)
    cfelc__mlrm = define_df_dtor(context, builder, df_type, payload_type)
    kylj__fui = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, hjvg__ilko), cfelc__mlrm)
    ktefr__olaj = context.nrt.meminfo_data(builder, kylj__fui)
    yjp__slmx = builder.bitcast(ktefr__olaj, jlnm__ibc.as_pointer())
    pbxuv__xrrpb = cgutils.create_struct_proxy(df_type)(context, builder)
    pbxuv__xrrpb.meminfo = kylj__fui
    if parent is None:
        pbxuv__xrrpb.parent = cgutils.get_null_value(pbxuv__xrrpb.parent.type)
    else:
        pbxuv__xrrpb.parent = parent
        krt__amv.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            ppvx__ivy = context.get_python_api(builder)
            xiebd__woej = ppvx__ivy.gil_ensure()
            ppvx__ivy.incref(parent)
            ppvx__ivy.gil_release(xiebd__woej)
    builder.store(krt__amv._getvalue(), yjp__slmx)
    return pbxuv__xrrpb._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        udpd__wij = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        udpd__wij = [sqo__otub for sqo__otub in data_typ.dtype.arr_types]
    cudq__xhbeb = DataFrameType(tuple(udpd__wij + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        hgjwx__maqy = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return hgjwx__maqy
    sig = signature(cudq__xhbeb, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    iof__undq = len(data_tup_typ.types)
    if iof__undq == 0:
        column_names = ()
    btjs__ontkj = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(btjs__ontkj, ColNamesMetaType) and isinstance(btjs__ontkj
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = btjs__ontkj.meta
    if iof__undq == 1 and isinstance(data_tup_typ.types[0], TableType):
        iof__undq = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == iof__undq, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    yhyqv__jnmz = data_tup_typ.types
    if iof__undq != 0 and isinstance(data_tup_typ.types[0], TableType):
        yhyqv__jnmz = data_tup_typ.types[0].arr_types
        is_table_format = True
    cudq__xhbeb = DataFrameType(yhyqv__jnmz, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            npgf__rmxm = cgutils.create_struct_proxy(cudq__xhbeb.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = npgf__rmxm.parent
        hgjwx__maqy = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return hgjwx__maqy
    sig = signature(cudq__xhbeb, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        pbxuv__xrrpb = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, pbxuv__xrrpb.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        krt__amv = get_dataframe_payload(context, builder, df_typ, args[0])
        yrgey__jpyk = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[yrgey__jpyk]
        if df_typ.is_table_format:
            npgf__rmxm = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(krt__amv.data, 0))
            fiowv__nww = df_typ.table_type.type_to_blk[arr_typ]
            aqstg__mhhxg = getattr(npgf__rmxm, f'block_{fiowv__nww}')
            upni__xcvh = ListInstance(context, builder, types.List(arr_typ),
                aqstg__mhhxg)
            kdu__vvwic = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[yrgey__jpyk])
            rjuxg__jvn = upni__xcvh.getitem(kdu__vvwic)
        else:
            rjuxg__jvn = builder.extract_value(krt__amv.data, yrgey__jpyk)
        xlqy__szsm = cgutils.alloca_once_value(builder, rjuxg__jvn)
        dly__nply = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, xlqy__szsm, dly__nply)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    kylj__fui = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, kylj__fui)
    ystgy__gww = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, ystgy__gww)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    cudq__xhbeb = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        cudq__xhbeb = types.Tuple([TableType(df_typ.data)])
    sig = signature(cudq__xhbeb, df_typ)

    def codegen(context, builder, signature, args):
        krt__amv = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            krt__amv.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        krt__amv = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, krt__amv.index
            )
    cudq__xhbeb = df_typ.index
    sig = signature(cudq__xhbeb, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        bqf__lcfgl = df.data[i]
        return bqf__lcfgl(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        krt__amv = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(krt__amv.data, 0))
    return df_typ.table_type(df_typ), codegen


def get_dataframe_all_data(df):
    return df.data


def get_dataframe_all_data_impl(df):
    if df.is_table_format:

        def _impl(df):
            return get_dataframe_table(df)
        return _impl
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for i in
        range(len(df.columns)))
    hlu__prnl = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{hlu__prnl})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        bqf__lcfgl = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return bqf__lcfgl(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        krt__amv = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, krt__amv.columns)
    return df_typ.runtime_colname_typ(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_all_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    apvup__uaxsa = self.typemap[data_tup.name]
    if any(is_tuple_like_type(sqo__otub) for sqo__otub in apvup__uaxsa.types):
        return None
    if equiv_set.has_shape(data_tup):
        rlc__jnfsd = equiv_set.get_shape(data_tup)
        if len(rlc__jnfsd) > 1:
            equiv_set.insert_equiv(*rlc__jnfsd)
        if len(rlc__jnfsd) > 0:
            hyzjr__wazq = self.typemap[index.name]
            if not isinstance(hyzjr__wazq, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(rlc__jnfsd[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(rlc__jnfsd[0], len(
                rlc__jnfsd)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vgq__pfhsg = args[0]
    data_types = self.typemap[vgq__pfhsg.name].data
    if any(is_tuple_like_type(sqo__otub) for sqo__otub in data_types):
        return None
    if equiv_set.has_shape(vgq__pfhsg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            vgq__pfhsg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    vgq__pfhsg = args[0]
    hyzjr__wazq = self.typemap[vgq__pfhsg.name].index
    if isinstance(hyzjr__wazq, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(vgq__pfhsg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            vgq__pfhsg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    vgq__pfhsg = args[0]
    if equiv_set.has_shape(vgq__pfhsg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            vgq__pfhsg), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    vgq__pfhsg = args[0]
    if equiv_set.has_shape(vgq__pfhsg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            vgq__pfhsg)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    yrgey__jpyk = get_overload_const_int(c_ind_typ)
    if df_typ.data[yrgey__jpyk] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        mfudy__znlrt, shkwa__gaq, rjmp__mfxzd = args
        krt__amv = get_dataframe_payload(context, builder, df_typ, mfudy__znlrt
            )
        if df_typ.is_table_format:
            npgf__rmxm = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(krt__amv.data, 0))
            fiowv__nww = df_typ.table_type.type_to_blk[arr_typ]
            aqstg__mhhxg = getattr(npgf__rmxm, f'block_{fiowv__nww}')
            upni__xcvh = ListInstance(context, builder, types.List(arr_typ),
                aqstg__mhhxg)
            kdu__vvwic = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[yrgey__jpyk])
            upni__xcvh.setitem(kdu__vvwic, rjmp__mfxzd, True)
        else:
            rjuxg__jvn = builder.extract_value(krt__amv.data, yrgey__jpyk)
            context.nrt.decref(builder, df_typ.data[yrgey__jpyk], rjuxg__jvn)
            krt__amv.data = builder.insert_value(krt__amv.data, rjmp__mfxzd,
                yrgey__jpyk)
            context.nrt.incref(builder, arr_typ, rjmp__mfxzd)
        pbxuv__xrrpb = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=mfudy__znlrt)
        payload_type = DataFramePayloadType(df_typ)
        sbknz__bgxdk = context.nrt.meminfo_data(builder, pbxuv__xrrpb.meminfo)
        ystgy__gww = context.get_value_type(payload_type).as_pointer()
        sbknz__bgxdk = builder.bitcast(sbknz__bgxdk, ystgy__gww)
        builder.store(krt__amv._getvalue(), sbknz__bgxdk)
        return impl_ret_borrowed(context, builder, df_typ, mfudy__znlrt)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        xof__fbneu = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        hwhwa__irgjy = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=xof__fbneu)
        vmif__fzdc = get_dataframe_payload(context, builder, df_typ, xof__fbneu
            )
        pbxuv__xrrpb = construct_dataframe(context, builder, signature.
            return_type, vmif__fzdc.data, index_val, hwhwa__irgjy.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), vmif__fzdc.data)
        return pbxuv__xrrpb
    cudq__xhbeb = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(cudq__xhbeb, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    iof__undq = len(df_type.columns)
    unjvu__zkhgn = iof__undq
    sjzuk__ugax = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    pzch__tes = col_name not in df_type.columns
    yrgey__jpyk = iof__undq
    if pzch__tes:
        sjzuk__ugax += arr_type,
        column_names += col_name,
        unjvu__zkhgn += 1
    else:
        yrgey__jpyk = df_type.columns.index(col_name)
        sjzuk__ugax = tuple(arr_type if i == yrgey__jpyk else sjzuk__ugax[i
            ] for i in range(iof__undq))

    def codegen(context, builder, signature, args):
        mfudy__znlrt, shkwa__gaq, rjmp__mfxzd = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, mfudy__znlrt)
        dnfq__fftn = cgutils.create_struct_proxy(df_type)(context, builder,
            value=mfudy__znlrt)
        if df_type.is_table_format:
            psffe__rix = df_type.table_type
            klu__zchgy = builder.extract_value(in_dataframe_payload.data, 0)
            fcyf__egym = TableType(sjzuk__ugax)
            rvh__fhuvx = set_table_data_codegen(context, builder,
                psffe__rix, klu__zchgy, fcyf__egym, arr_type, rjmp__mfxzd,
                yrgey__jpyk, pzch__tes)
            data_tup = context.make_tuple(builder, types.Tuple([fcyf__egym]
                ), [rvh__fhuvx])
        else:
            yhyqv__jnmz = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != yrgey__jpyk else rjmp__mfxzd) for i in range(
                iof__undq)]
            if pzch__tes:
                yhyqv__jnmz.append(rjmp__mfxzd)
            for vgq__pfhsg, objpf__rxc in zip(yhyqv__jnmz, sjzuk__ugax):
                context.nrt.incref(builder, objpf__rxc, vgq__pfhsg)
            data_tup = context.make_tuple(builder, types.Tuple(sjzuk__ugax),
                yhyqv__jnmz)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        lkcx__vcynk = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, dnfq__fftn.parent, None)
        if not pzch__tes and arr_type == df_type.data[yrgey__jpyk]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            sbknz__bgxdk = context.nrt.meminfo_data(builder, dnfq__fftn.meminfo
                )
            ystgy__gww = context.get_value_type(payload_type).as_pointer()
            sbknz__bgxdk = builder.bitcast(sbknz__bgxdk, ystgy__gww)
            iuq__odqvy = get_dataframe_payload(context, builder, df_type,
                lkcx__vcynk)
            builder.store(iuq__odqvy._getvalue(), sbknz__bgxdk)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, fcyf__egym, builder.
                    extract_value(data_tup, 0))
            else:
                for vgq__pfhsg, objpf__rxc in zip(yhyqv__jnmz, sjzuk__ugax):
                    context.nrt.incref(builder, objpf__rxc, vgq__pfhsg)
        has_parent = cgutils.is_not_null(builder, dnfq__fftn.parent)
        with builder.if_then(has_parent):
            ppvx__ivy = context.get_python_api(builder)
            xiebd__woej = ppvx__ivy.gil_ensure()
            fiy__bmh = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, rjmp__mfxzd)
            pcy__zpws = numba.core.pythonapi._BoxContext(context, builder,
                ppvx__ivy, fiy__bmh)
            ifye__uygw = pcy__zpws.pyapi.from_native_value(arr_type,
                rjmp__mfxzd, pcy__zpws.env_manager)
            if isinstance(col_name, str):
                rxysa__rkebc = context.insert_const_string(builder.module,
                    col_name)
                mvjuy__yavtv = ppvx__ivy.string_from_string(rxysa__rkebc)
            else:
                assert isinstance(col_name, int)
                mvjuy__yavtv = ppvx__ivy.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            ppvx__ivy.object_setitem(dnfq__fftn.parent, mvjuy__yavtv,
                ifye__uygw)
            ppvx__ivy.decref(ifye__uygw)
            ppvx__ivy.decref(mvjuy__yavtv)
            ppvx__ivy.gil_release(xiebd__woej)
        return lkcx__vcynk
    cudq__xhbeb = DataFrameType(sjzuk__ugax, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(cudq__xhbeb, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    iof__undq = len(pyval.columns)
    yhyqv__jnmz = []
    for i in range(iof__undq):
        cnio__puw = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            ifye__uygw = cnio__puw.array
        else:
            ifye__uygw = cnio__puw.values
        yhyqv__jnmz.append(ifye__uygw)
    yhyqv__jnmz = tuple(yhyqv__jnmz)
    if df_type.is_table_format:
        npgf__rmxm = context.get_constant_generic(builder, df_type.
            table_type, Table(yhyqv__jnmz))
        data_tup = lir.Constant.literal_struct([npgf__rmxm])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], rpwne__spyym) for
            i, rpwne__spyym in enumerate(yhyqv__jnmz)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    dnq__maswo = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, dnq__maswo])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    ufrz__byvi = context.get_constant(types.int64, -1)
    mjhc__qtam = context.get_constant_null(types.voidptr)
    kylj__fui = lir.Constant.literal_struct([ufrz__byvi, mjhc__qtam,
        mjhc__qtam, payload, ufrz__byvi])
    kylj__fui = cgutils.global_constant(builder, '.const.meminfo', kylj__fui
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([kylj__fui, dnq__maswo])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if len(fromty.data) != len(toty.data) or fromty.data != toty.data and any(
        context.typing_context.unify_pairs(fromty.data[i], toty.data[i]) is
        None for i in range(len(fromty.data))
        ) or fromty.has_runtime_cols != toty.has_runtime_cols:
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        rtlhm__soa = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        rtlhm__soa = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, rtlhm__soa)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        mrvcb__qik = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                mrvcb__qik)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), mrvcb__qik)
    elif not fromty.is_table_format and toty.is_table_format:
        mrvcb__qik = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        mrvcb__qik = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        mrvcb__qik = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        mrvcb__qik = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, mrvcb__qik,
        rtlhm__soa, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    vast__gsrwh = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        umh__urvcf = get_index_data_arr_types(toty.index)[0]
        ozq__cjxv = bodo.utils.transform.get_type_alloc_counts(umh__urvcf) - 1
        msli__jotax = ', '.join('0' for shkwa__gaq in range(ozq__cjxv))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(msli__jotax, ', ' if ozq__cjxv == 1 else ''))
        vast__gsrwh['index_arr_type'] = umh__urvcf
    aqi__yzkbt = []
    for i, arr_typ in enumerate(toty.data):
        ozq__cjxv = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        msli__jotax = ', '.join('0' for shkwa__gaq in range(ozq__cjxv))
        malxo__jwt = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, msli__jotax, ', ' if ozq__cjxv == 1 else ''))
        aqi__yzkbt.append(malxo__jwt)
        vast__gsrwh[f'arr_type{i}'] = arr_typ
    aqi__yzkbt = ', '.join(aqi__yzkbt)
    squsw__dsv = 'def impl():\n'
    iqndh__ikfnd = bodo.hiframes.dataframe_impl._gen_init_df(squsw__dsv,
        toty.columns, aqi__yzkbt, index, vast__gsrwh)
    df = context.compile_internal(builder, iqndh__ikfnd, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    vqmev__axu = toty.table_type
    npgf__rmxm = cgutils.create_struct_proxy(vqmev__axu)(context, builder)
    npgf__rmxm.parent = in_dataframe_payload.parent
    for sqo__otub, fiowv__nww in vqmev__axu.type_to_blk.items():
        wjo__fvi = context.get_constant(types.int64, len(vqmev__axu.
            block_to_arr_ind[fiowv__nww]))
        shkwa__gaq, wqh__nztb = ListInstance.allocate_ex(context, builder,
            types.List(sqo__otub), wjo__fvi)
        wqh__nztb.size = wjo__fvi
        setattr(npgf__rmxm, f'block_{fiowv__nww}', wqh__nztb.value)
    for i, sqo__otub in enumerate(fromty.data):
        ynv__qdbm = toty.data[i]
        if sqo__otub != ynv__qdbm:
            qnjc__xrt = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qnjc__xrt)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        rjuxg__jvn = builder.extract_value(in_dataframe_payload.data, i)
        if sqo__otub != ynv__qdbm:
            auw__vas = context.cast(builder, rjuxg__jvn, sqo__otub, ynv__qdbm)
            mgf__nyrn = False
        else:
            auw__vas = rjuxg__jvn
            mgf__nyrn = True
        fiowv__nww = vqmev__axu.type_to_blk[sqo__otub]
        aqstg__mhhxg = getattr(npgf__rmxm, f'block_{fiowv__nww}')
        upni__xcvh = ListInstance(context, builder, types.List(sqo__otub),
            aqstg__mhhxg)
        kdu__vvwic = context.get_constant(types.int64, vqmev__axu.
            block_offsets[i])
        upni__xcvh.setitem(kdu__vvwic, auw__vas, mgf__nyrn)
    data_tup = context.make_tuple(builder, types.Tuple([vqmev__axu]), [
        npgf__rmxm._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    yhyqv__jnmz = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            qnjc__xrt = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qnjc__xrt)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            rjuxg__jvn = builder.extract_value(in_dataframe_payload.data, i)
            auw__vas = context.cast(builder, rjuxg__jvn, fromty.data[i],
                toty.data[i])
            mgf__nyrn = False
        else:
            auw__vas = builder.extract_value(in_dataframe_payload.data, i)
            mgf__nyrn = True
        if mgf__nyrn:
            context.nrt.incref(builder, toty.data[i], auw__vas)
        yhyqv__jnmz.append(auw__vas)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), yhyqv__jnmz)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    psffe__rix = fromty.table_type
    klu__zchgy = cgutils.create_struct_proxy(psffe__rix)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    fcyf__egym = toty.table_type
    rvh__fhuvx = cgutils.create_struct_proxy(fcyf__egym)(context, builder)
    rvh__fhuvx.parent = in_dataframe_payload.parent
    for sqo__otub, fiowv__nww in fcyf__egym.type_to_blk.items():
        wjo__fvi = context.get_constant(types.int64, len(fcyf__egym.
            block_to_arr_ind[fiowv__nww]))
        shkwa__gaq, wqh__nztb = ListInstance.allocate_ex(context, builder,
            types.List(sqo__otub), wjo__fvi)
        wqh__nztb.size = wjo__fvi
        setattr(rvh__fhuvx, f'block_{fiowv__nww}', wqh__nztb.value)
    for i in range(len(fromty.data)):
        cyulm__kdr = fromty.data[i]
        ynv__qdbm = toty.data[i]
        if cyulm__kdr != ynv__qdbm:
            qnjc__xrt = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qnjc__xrt)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        vve__mfq = psffe__rix.type_to_blk[cyulm__kdr]
        rwgs__wrctm = getattr(klu__zchgy, f'block_{vve__mfq}')
        vbo__puaef = ListInstance(context, builder, types.List(cyulm__kdr),
            rwgs__wrctm)
        adea__ophwe = context.get_constant(types.int64, psffe__rix.
            block_offsets[i])
        rjuxg__jvn = vbo__puaef.getitem(adea__ophwe)
        if cyulm__kdr != ynv__qdbm:
            auw__vas = context.cast(builder, rjuxg__jvn, cyulm__kdr, ynv__qdbm)
            mgf__nyrn = False
        else:
            auw__vas = rjuxg__jvn
            mgf__nyrn = True
        brz__yckg = fcyf__egym.type_to_blk[sqo__otub]
        wqh__nztb = getattr(rvh__fhuvx, f'block_{brz__yckg}')
        khpbd__xxly = ListInstance(context, builder, types.List(ynv__qdbm),
            wqh__nztb)
        yqv__cerbi = context.get_constant(types.int64, fcyf__egym.
            block_offsets[i])
        khpbd__xxly.setitem(yqv__cerbi, auw__vas, mgf__nyrn)
    data_tup = context.make_tuple(builder, types.Tuple([fcyf__egym]), [
        rvh__fhuvx._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    vqmev__axu = fromty.table_type
    npgf__rmxm = cgutils.create_struct_proxy(vqmev__axu)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    yhyqv__jnmz = []
    for i, sqo__otub in enumerate(toty.data):
        cyulm__kdr = fromty.data[i]
        if sqo__otub != cyulm__kdr:
            qnjc__xrt = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qnjc__xrt)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        fiowv__nww = vqmev__axu.type_to_blk[sqo__otub]
        aqstg__mhhxg = getattr(npgf__rmxm, f'block_{fiowv__nww}')
        upni__xcvh = ListInstance(context, builder, types.List(sqo__otub),
            aqstg__mhhxg)
        kdu__vvwic = context.get_constant(types.int64, vqmev__axu.
            block_offsets[i])
        rjuxg__jvn = upni__xcvh.getitem(kdu__vvwic)
        if sqo__otub != cyulm__kdr:
            auw__vas = context.cast(builder, rjuxg__jvn, cyulm__kdr, sqo__otub)
            mgf__nyrn = False
        else:
            auw__vas = rjuxg__jvn
            mgf__nyrn = True
        if mgf__nyrn:
            context.nrt.incref(builder, sqo__otub, auw__vas)
        yhyqv__jnmz.append(auw__vas)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), yhyqv__jnmz)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    vbcya__whfy, aqi__yzkbt, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    mbi__ywh = ColNamesMetaType(tuple(vbcya__whfy))
    squsw__dsv = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    squsw__dsv += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(aqi__yzkbt, index_arg))
    bfki__pqs = {}
    exec(squsw__dsv, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': mbi__ywh}, bfki__pqs)
    ivs__tom = bfki__pqs['_init_df']
    return ivs__tom


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    cudq__xhbeb = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(cudq__xhbeb, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    cudq__xhbeb = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(cudq__xhbeb, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    esam__jqj = ''
    if not is_overload_none(dtype):
        esam__jqj = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        iof__undq = (len(data.types) - 1) // 2
        fcmq__nut = [sqo__otub.literal_value for sqo__otub in data.types[1:
            iof__undq + 1]]
        data_val_types = dict(zip(fcmq__nut, data.types[iof__undq + 1:]))
        yhyqv__jnmz = ['data[{}]'.format(i) for i in range(iof__undq + 1, 2 *
            iof__undq + 1)]
        data_dict = dict(zip(fcmq__nut, yhyqv__jnmz))
        if is_overload_none(index):
            for i, sqo__otub in enumerate(data.types[iof__undq + 1:]):
                if isinstance(sqo__otub, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(iof__undq + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        cmo__zjwz = '.copy()' if copy else ''
        lylif__yyy = get_overload_const_list(columns)
        iof__undq = len(lylif__yyy)
        data_val_types = {pcy__zpws: data.copy(ndim=1) for pcy__zpws in
            lylif__yyy}
        yhyqv__jnmz = ['data[:,{}]{}'.format(i, cmo__zjwz) for i in range(
            iof__undq)]
        data_dict = dict(zip(lylif__yyy, yhyqv__jnmz))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    aqi__yzkbt = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[pcy__zpws], df_len, esam__jqj) for pcy__zpws in
        col_names))
    if len(col_names) == 0:
        aqi__yzkbt = '()'
    return col_names, aqi__yzkbt, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for pcy__zpws in col_names:
        if pcy__zpws in data_dict and is_iterable_type(data_val_types[
            pcy__zpws]):
            df_len = 'len({})'.format(data_dict[pcy__zpws])
            break
    if df_len == '0':
        if not index_is_none:
            df_len = f'len({index_arg})'
        elif data_dict:
            raise BodoError(
                'Internal Error: Unable to determine length of DataFrame Index. If this is unexpected, please try passing an index value.'
                )
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(pcy__zpws in data_dict for pcy__zpws in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    jjpyx__uqd = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for pcy__zpws in col_names:
        if pcy__zpws not in data_dict:
            data_dict[pcy__zpws] = jjpyx__uqd


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            sqo__otub = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(sqo__otub)
        return impl
    if len(df.columns) == 0:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
        return impl

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        hiiki__raybj = idx.literal_value
        if isinstance(hiiki__raybj, int):
            bqf__lcfgl = tup.types[hiiki__raybj]
        elif isinstance(hiiki__raybj, slice):
            bqf__lcfgl = types.BaseTuple.from_types(tup.types[hiiki__raybj])
        return signature(bqf__lcfgl, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    swaom__jnz, idx = sig.args
    idx = idx.literal_value
    tup, shkwa__gaq = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(swaom__jnz)
        if not 0 <= idx < len(swaom__jnz):
            raise IndexError('cannot index at %d in %s' % (idx, swaom__jnz))
        whwkf__dkzh = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        shksh__utfuf = cgutils.unpack_tuple(builder, tup)[idx]
        whwkf__dkzh = context.make_tuple(builder, sig.return_type, shksh__utfuf
            )
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, whwkf__dkzh)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, dryvp__nwo, suffix_x,
            suffix_y, is_join, indicator, shkwa__gaq, shkwa__gaq) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        cqmsn__ynw = {pcy__zpws: i for i, pcy__zpws in enumerate(left_on)}
        drm__krjpa = {pcy__zpws: i for i, pcy__zpws in enumerate(right_on)}
        smha__ytjj = set(left_on) & set(right_on)
        ekih__icmoy = set(left_df.columns) & set(right_df.columns)
        gjaub__ioq = ekih__icmoy - smha__ytjj
        lmbdu__dqww = '$_bodo_index_' in left_on
        dedxr__mxj = '$_bodo_index_' in right_on
        how = get_overload_const_str(dryvp__nwo)
        yse__hmnws = how in {'left', 'outer'}
        vnsl__upc = how in {'right', 'outer'}
        columns = []
        data = []
        if lmbdu__dqww:
            manli__bfn = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            manli__bfn = left_df.data[left_df.column_index[left_on[0]]]
        if dedxr__mxj:
            iyrnq__fbrdk = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            iyrnq__fbrdk = right_df.data[right_df.column_index[right_on[0]]]
        if lmbdu__dqww and not dedxr__mxj and not is_join.literal_value:
            zmyy__zyan = right_on[0]
            if zmyy__zyan in left_df.column_index:
                columns.append(zmyy__zyan)
                if (iyrnq__fbrdk == bodo.dict_str_arr_type and manli__bfn ==
                    bodo.string_array_type):
                    lfoe__slmot = bodo.string_array_type
                else:
                    lfoe__slmot = iyrnq__fbrdk
                data.append(lfoe__slmot)
        if dedxr__mxj and not lmbdu__dqww and not is_join.literal_value:
            jbb__plug = left_on[0]
            if jbb__plug in right_df.column_index:
                columns.append(jbb__plug)
                if (manli__bfn == bodo.dict_str_arr_type and iyrnq__fbrdk ==
                    bodo.string_array_type):
                    lfoe__slmot = bodo.string_array_type
                else:
                    lfoe__slmot = manli__bfn
                data.append(lfoe__slmot)
        for cyulm__kdr, cnio__puw in zip(left_df.data, left_df.columns):
            columns.append(str(cnio__puw) + suffix_x.literal_value if 
                cnio__puw in gjaub__ioq else cnio__puw)
            if cnio__puw in smha__ytjj:
                if cyulm__kdr == bodo.dict_str_arr_type:
                    cyulm__kdr = right_df.data[right_df.column_index[cnio__puw]
                        ]
                data.append(cyulm__kdr)
            else:
                if (cyulm__kdr == bodo.dict_str_arr_type and cnio__puw in
                    cqmsn__ynw):
                    if dedxr__mxj:
                        cyulm__kdr = iyrnq__fbrdk
                    else:
                        rjy__wwhx = cqmsn__ynw[cnio__puw]
                        get__gpj = right_on[rjy__wwhx]
                        cyulm__kdr = right_df.data[right_df.column_index[
                            get__gpj]]
                if vnsl__upc:
                    cyulm__kdr = to_nullable_type(cyulm__kdr)
                data.append(cyulm__kdr)
        for cyulm__kdr, cnio__puw in zip(right_df.data, right_df.columns):
            if cnio__puw not in smha__ytjj:
                columns.append(str(cnio__puw) + suffix_y.literal_value if 
                    cnio__puw in gjaub__ioq else cnio__puw)
                if (cyulm__kdr == bodo.dict_str_arr_type and cnio__puw in
                    drm__krjpa):
                    if lmbdu__dqww:
                        cyulm__kdr = manli__bfn
                    else:
                        rjy__wwhx = drm__krjpa[cnio__puw]
                        jiou__izglb = left_on[rjy__wwhx]
                        cyulm__kdr = left_df.data[left_df.column_index[
                            jiou__izglb]]
                if yse__hmnws:
                    cyulm__kdr = to_nullable_type(cyulm__kdr)
                data.append(cyulm__kdr)
        ggo__uhv = get_overload_const_bool(indicator)
        if ggo__uhv:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        ebg__fgp = False
        if lmbdu__dqww and dedxr__mxj and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            ebg__fgp = True
        elif lmbdu__dqww and not dedxr__mxj:
            index_typ = right_df.index
            ebg__fgp = True
        elif dedxr__mxj and not lmbdu__dqww:
            index_typ = left_df.index
            ebg__fgp = True
        if ebg__fgp and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        apq__kjs = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(apq__kjs, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    pbxuv__xrrpb = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return pbxuv__xrrpb._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    dfafg__jvr = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    pjqc__cxodo = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', dfafg__jvr, pjqc__cxodo,
        package_name='pandas', module_name='General')
    squsw__dsv = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        mdme__tnpll = 0
        aqi__yzkbt = []
        names = []
        for i, jtbtv__xbxw in enumerate(objs.types):
            assert isinstance(jtbtv__xbxw, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(jtbtv__xbxw, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                jtbtv__xbxw, 'pandas.concat()')
            if isinstance(jtbtv__xbxw, SeriesType):
                names.append(str(mdme__tnpll))
                mdme__tnpll += 1
                aqi__yzkbt.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(jtbtv__xbxw.columns)
                for hsi__ppkyj in range(len(jtbtv__xbxw.data)):
                    aqi__yzkbt.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, hsi__ppkyj))
        return bodo.hiframes.dataframe_impl._gen_init_df(squsw__dsv, names,
            ', '.join(aqi__yzkbt), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(sqo__otub, DataFrameType) for sqo__otub in
            objs.types)
        srk__xuuu = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            srk__xuuu.extend(df.columns)
        srk__xuuu = list(dict.fromkeys(srk__xuuu).keys())
        udpd__wij = {}
        for mdme__tnpll, pcy__zpws in enumerate(srk__xuuu):
            for i, df in enumerate(objs.types):
                if pcy__zpws in df.column_index:
                    udpd__wij[f'arr_typ{mdme__tnpll}'] = df.data[df.
                        column_index[pcy__zpws]]
                    break
        assert len(udpd__wij) == len(srk__xuuu)
        snn__oqdpy = []
        for mdme__tnpll, pcy__zpws in enumerate(srk__xuuu):
            args = []
            for i, df in enumerate(objs.types):
                if pcy__zpws in df.column_index:
                    yrgey__jpyk = df.column_index[pcy__zpws]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, yrgey__jpyk))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, mdme__tnpll))
            squsw__dsv += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(mdme__tnpll, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(squsw__dsv,
            srk__xuuu, ', '.join('A{}'.format(i) for i in range(len(
            srk__xuuu))), index, udpd__wij)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(sqo__otub, SeriesType) for sqo__otub in objs.
            types)
        squsw__dsv += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            squsw__dsv += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            squsw__dsv += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        squsw__dsv += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        bfki__pqs = {}
        exec(squsw__dsv, {'bodo': bodo, 'np': np, 'numba': numba}, bfki__pqs)
        return bfki__pqs['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for mdme__tnpll, pcy__zpws in enumerate(df_type.columns):
            squsw__dsv += '  arrs{} = []\n'.format(mdme__tnpll)
            squsw__dsv += '  for i in range(len(objs)):\n'
            squsw__dsv += '    df = objs[i]\n'
            squsw__dsv += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(mdme__tnpll))
            squsw__dsv += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(mdme__tnpll))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            squsw__dsv += '  arrs_index = []\n'
            squsw__dsv += '  for i in range(len(objs)):\n'
            squsw__dsv += '    df = objs[i]\n'
            squsw__dsv += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(squsw__dsv,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        squsw__dsv += '  arrs = []\n'
        squsw__dsv += '  for i in range(len(objs)):\n'
        squsw__dsv += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        squsw__dsv += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            squsw__dsv += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            squsw__dsv += '  arrs_index = []\n'
            squsw__dsv += '  for i in range(len(objs)):\n'
            squsw__dsv += '    S = objs[i]\n'
            squsw__dsv += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            squsw__dsv += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        squsw__dsv += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        bfki__pqs = {}
        exec(squsw__dsv, {'bodo': bodo, 'np': np, 'numba': numba}, bfki__pqs)
        return bfki__pqs['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        cudq__xhbeb = df.copy(index=index)
        return signature(cudq__xhbeb, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    hnog__oux = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hnog__oux._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    dfafg__jvr = dict(index=index, name=name)
    pjqc__cxodo = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', dfafg__jvr, pjqc__cxodo,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        udpd__wij = (types.Array(types.int64, 1, 'C'),) + df.data
        bhivf__osb = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, udpd__wij)
        return signature(bhivf__osb, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    hnog__oux = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hnog__oux._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    hnog__oux = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hnog__oux._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    hnog__oux = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return hnog__oux._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    mpt__lbca = get_overload_const_bool(check_duplicates)
    kly__lciew = not get_overload_const_bool(is_already_shuffled)
    yihr__ppm = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    wan__ohz = len(value_names) > 1
    ejfdi__ltw = None
    bns__apr = None
    axhx__xwlf = None
    ewlcc__pcpbm = None
    psvjw__laalt = isinstance(values_tup, types.UniTuple)
    if psvjw__laalt:
        ifnvj__frgb = [to_str_arr_if_dict_array(to_nullable_type(values_tup
            .dtype))]
    else:
        ifnvj__frgb = [to_str_arr_if_dict_array(to_nullable_type(objpf__rxc
            )) for objpf__rxc in values_tup]
    squsw__dsv = 'def impl(\n'
    squsw__dsv += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    squsw__dsv += '):\n'
    squsw__dsv += (
        "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n")
    if kly__lciew:
        squsw__dsv += '    if parallel:\n'
        squsw__dsv += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        the__kzxe = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        squsw__dsv += f'        info_list = [{the__kzxe}]\n'
        squsw__dsv += '        cpp_table = arr_info_list_to_table(info_list)\n'
        squsw__dsv += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        svx__tpxq = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        kzvwd__ffcw = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        dzqg__yhe = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        squsw__dsv += f'        index_tup = ({svx__tpxq},)\n'
        squsw__dsv += f'        columns_tup = ({kzvwd__ffcw},)\n'
        squsw__dsv += f'        values_tup = ({dzqg__yhe},)\n'
        squsw__dsv += '        delete_table(cpp_table)\n'
        squsw__dsv += '        delete_table(out_cpp_table)\n'
        squsw__dsv += '        ev_shuffle.finalize()\n'
    squsw__dsv += '    columns_arr = columns_tup[0]\n'
    if psvjw__laalt:
        squsw__dsv += '    values_arrs = [arr for arr in values_tup]\n'
    squsw__dsv += (
        "    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)\n"
        )
    squsw__dsv += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    squsw__dsv += '        index_tup\n'
    squsw__dsv += '    )\n'
    squsw__dsv += '    n_rows = len(unique_index_arr_tup[0])\n'
    squsw__dsv += '    num_values_arrays = len(values_tup)\n'
    squsw__dsv += '    n_unique_pivots = len(pivot_values)\n'
    if psvjw__laalt:
        squsw__dsv += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        squsw__dsv += '    n_cols = n_unique_pivots\n'
    squsw__dsv += '    col_map = {}\n'
    squsw__dsv += '    for i in range(n_unique_pivots):\n'
    squsw__dsv += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    squsw__dsv += '            raise ValueError(\n'
    squsw__dsv += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    squsw__dsv += '            )\n'
    squsw__dsv += '        col_map[pivot_values[i]] = i\n'
    squsw__dsv += '    ev_unique.finalize()\n'
    squsw__dsv += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    enty__eea = False
    for i, udpe__rcoo in enumerate(ifnvj__frgb):
        if is_str_arr_type(udpe__rcoo):
            enty__eea = True
            squsw__dsv += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            squsw__dsv += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if enty__eea:
        if mpt__lbca:
            squsw__dsv += '    nbytes = (n_rows + 7) >> 3\n'
            squsw__dsv += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        squsw__dsv += '    for i in range(len(columns_arr)):\n'
        squsw__dsv += '        col_name = columns_arr[i]\n'
        squsw__dsv += '        pivot_idx = col_map[col_name]\n'
        squsw__dsv += '        row_idx = row_vector[i]\n'
        if mpt__lbca:
            squsw__dsv += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            squsw__dsv += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            squsw__dsv += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            squsw__dsv += '        else:\n'
            squsw__dsv += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if psvjw__laalt:
            squsw__dsv += '        for j in range(num_values_arrays):\n'
            squsw__dsv += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            squsw__dsv += '            len_arr = len_arrs_0[col_idx]\n'
            squsw__dsv += '            values_arr = values_arrs[j]\n'
            squsw__dsv += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            squsw__dsv += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            squsw__dsv += '                len_arr[row_idx] = str_val_len\n'
            squsw__dsv += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, udpe__rcoo in enumerate(ifnvj__frgb):
                if is_str_arr_type(udpe__rcoo):
                    squsw__dsv += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    squsw__dsv += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    squsw__dsv += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    squsw__dsv += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    squsw__dsv += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, udpe__rcoo in enumerate(ifnvj__frgb):
        if is_str_arr_type(udpe__rcoo):
            squsw__dsv += f'    data_arrs_{i} = [\n'
            squsw__dsv += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            squsw__dsv += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            squsw__dsv += '        )\n'
            squsw__dsv += '        for i in range(n_cols)\n'
            squsw__dsv += '    ]\n'
            squsw__dsv += f'    if tracing.is_tracing():\n'
            squsw__dsv += '         for i in range(n_cols):'
            squsw__dsv += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            squsw__dsv += f'    data_arrs_{i} = [\n'
            squsw__dsv += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            squsw__dsv += '        for _ in range(n_cols)\n'
            squsw__dsv += '    ]\n'
    if not enty__eea and mpt__lbca:
        squsw__dsv += '    nbytes = (n_rows + 7) >> 3\n'
        squsw__dsv += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    squsw__dsv += '    ev_alloc.finalize()\n'
    squsw__dsv += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    squsw__dsv += '    for i in range(len(columns_arr)):\n'
    squsw__dsv += '        col_name = columns_arr[i]\n'
    squsw__dsv += '        pivot_idx = col_map[col_name]\n'
    squsw__dsv += '        row_idx = row_vector[i]\n'
    if not enty__eea and mpt__lbca:
        squsw__dsv += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        squsw__dsv += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        squsw__dsv += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        squsw__dsv += '        else:\n'
        squsw__dsv += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if psvjw__laalt:
        squsw__dsv += '        for j in range(num_values_arrays):\n'
        squsw__dsv += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        squsw__dsv += '            col_arr = data_arrs_0[col_idx]\n'
        squsw__dsv += '            values_arr = values_arrs[j]\n'
        squsw__dsv += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        squsw__dsv += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        squsw__dsv += '            else:\n'
        squsw__dsv += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, udpe__rcoo in enumerate(ifnvj__frgb):
            squsw__dsv += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            squsw__dsv += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            squsw__dsv += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            squsw__dsv += f'        else:\n'
            squsw__dsv += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        squsw__dsv += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        ejfdi__ltw = index_names.meta[0]
    else:
        squsw__dsv += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        ejfdi__ltw = tuple(index_names.meta)
    squsw__dsv += f'    if tracing.is_tracing():\n'
    squsw__dsv += f'        index_nbytes = index.nbytes\n'
    squsw__dsv += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not yihr__ppm:
        axhx__xwlf = columns_name.meta[0]
        if wan__ohz:
            squsw__dsv += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            bns__apr = value_names.meta
            if all(isinstance(pcy__zpws, str) for pcy__zpws in bns__apr):
                bns__apr = pd.array(bns__apr, 'string')
            elif all(isinstance(pcy__zpws, int) for pcy__zpws in bns__apr):
                bns__apr = np.array(bns__apr, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(bns__apr.dtype, pd.StringDtype):
                squsw__dsv += '    total_chars = 0\n'
                squsw__dsv += f'    for i in range({len(value_names)}):\n'
                squsw__dsv += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                squsw__dsv += '        total_chars += value_name_str_len\n'
                squsw__dsv += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                squsw__dsv += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                squsw__dsv += '    total_chars = 0\n'
                squsw__dsv += '    for i in range(len(pivot_values)):\n'
                squsw__dsv += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                squsw__dsv += '        total_chars += pivot_val_str_len\n'
                squsw__dsv += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                squsw__dsv += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            squsw__dsv += f'    for i in range({len(value_names)}):\n'
            squsw__dsv += '        for j in range(len(pivot_values)):\n'
            squsw__dsv += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            squsw__dsv += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            squsw__dsv += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            squsw__dsv += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    squsw__dsv += '    ev_fill.finalize()\n'
    vqmev__axu = None
    if yihr__ppm:
        if wan__ohz:
            qwxau__tix = []
            for azo__qbf in _constant_pivot_values.meta:
                for hza__vcx in value_names.meta:
                    qwxau__tix.append((azo__qbf, hza__vcx))
            column_names = tuple(qwxau__tix)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        ewlcc__pcpbm = ColNamesMetaType(column_names)
        euihr__qimo = []
        for objpf__rxc in ifnvj__frgb:
            euihr__qimo.extend([objpf__rxc] * len(_constant_pivot_values))
        omb__ikf = tuple(euihr__qimo)
        vqmev__axu = TableType(omb__ikf)
        squsw__dsv += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        squsw__dsv += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, objpf__rxc in enumerate(ifnvj__frgb):
            squsw__dsv += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {vqmev__axu.type_to_blk[objpf__rxc]})
"""
        squsw__dsv += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        squsw__dsv += '        (table,), index, columns_typ\n'
        squsw__dsv += '    )\n'
    else:
        wqn__nrpc = ', '.join(f'data_arrs_{i}' for i in range(len(ifnvj__frgb))
            )
        squsw__dsv += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({wqn__nrpc},), n_rows)
"""
        squsw__dsv += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        squsw__dsv += '        (table,), index, column_index\n'
        squsw__dsv += '    )\n'
    squsw__dsv += '    ev.finalize()\n'
    squsw__dsv += '    return result\n'
    bfki__pqs = {}
    kbc__suqcv = {f'data_arr_typ_{i}': udpe__rcoo for i, udpe__rcoo in
        enumerate(ifnvj__frgb)}
    vkv__vgah = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        vqmev__axu, 'columns_typ': ewlcc__pcpbm, 'index_names_lit':
        ejfdi__ltw, 'value_names_lit': bns__apr, 'columns_name_lit':
        axhx__xwlf, **kbc__suqcv, 'tracing': tracing}
    exec(squsw__dsv, vkv__vgah, bfki__pqs)
    impl = bfki__pqs['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    lanu__iecul = {}
    lanu__iecul['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, hga__rvd in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        ljy__jta = None
        if isinstance(hga__rvd, bodo.DatetimeArrayType):
            mgy__keuht = 'datetimetz'
            tqfy__mdxu = 'datetime64[ns]'
            if isinstance(hga__rvd.tz, int):
                nlo__mhrwi = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(hga__rvd.tz))
            else:
                nlo__mhrwi = pd.DatetimeTZDtype(tz=hga__rvd.tz).tz
            ljy__jta = {'timezone': pa.lib.tzinfo_to_string(nlo__mhrwi)}
        elif isinstance(hga__rvd, types.Array) or hga__rvd == boolean_array:
            mgy__keuht = tqfy__mdxu = hga__rvd.dtype.name
            if tqfy__mdxu.startswith('datetime'):
                mgy__keuht = 'datetime'
        elif is_str_arr_type(hga__rvd):
            mgy__keuht = 'unicode'
            tqfy__mdxu = 'object'
        elif hga__rvd == binary_array_type:
            mgy__keuht = 'bytes'
            tqfy__mdxu = 'object'
        elif isinstance(hga__rvd, DecimalArrayType):
            mgy__keuht = tqfy__mdxu = 'object'
        elif isinstance(hga__rvd, IntegerArrayType):
            ywj__atyh = hga__rvd.dtype.name
            if ywj__atyh.startswith('int'):
                mgy__keuht = 'Int' + ywj__atyh[3:]
            elif ywj__atyh.startswith('uint'):
                mgy__keuht = 'UInt' + ywj__atyh[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, hga__rvd))
            tqfy__mdxu = hga__rvd.dtype.name
        elif hga__rvd == datetime_date_array_type:
            mgy__keuht = 'datetime'
            tqfy__mdxu = 'object'
        elif isinstance(hga__rvd, (StructArrayType, ArrayItemArrayType)):
            mgy__keuht = 'object'
            tqfy__mdxu = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, hga__rvd))
        kgbs__yojwo = {'name': col_name, 'field_name': col_name,
            'pandas_type': mgy__keuht, 'numpy_type': tqfy__mdxu, 'metadata':
            ljy__jta}
        lanu__iecul['columns'].append(kgbs__yojwo)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            opneb__jeikb = '__index_level_0__'
            sjftr__vppwg = None
        else:
            opneb__jeikb = '%s'
            sjftr__vppwg = '%s'
        lanu__iecul['index_columns'] = [opneb__jeikb]
        lanu__iecul['columns'].append({'name': sjftr__vppwg, 'field_name':
            opneb__jeikb, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        lanu__iecul['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        lanu__iecul['index_columns'] = []
    lanu__iecul['pandas_version'] = pd.__version__
    return lanu__iecul


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, path, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, row_group_size=-
    1, _bodo_file_prefix='part-', _is_parallel=False):
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if df.has_runtime_cols and not is_overload_none(partition_cols):
        raise BodoError(
            f"DataFrame.to_parquet(): Providing 'partition_cols' on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information."
            )
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        mzuns__aftk = []
        for zezma__nzgop in partition_cols:
            try:
                idx = df.columns.index(zezma__nzgop)
            except ValueError as fkmhs__wkn:
                raise BodoError(
                    f'Partition column {zezma__nzgop} is not in dataframe')
            mzuns__aftk.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    tyjj__qvco = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    etrb__aufxm = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not tyjj__qvco)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not tyjj__qvco or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and tyjj__qvco and not is_overload_true(_is_parallel)
    if df.has_runtime_cols:
        if isinstance(df.runtime_colname_typ, MultiIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): Not supported with MultiIndex runtime column names. Please return the DataFrame to regular Python to update typing information.'
                )
        if not isinstance(df.runtime_colname_typ, bodo.hiframes.
            pd_index_ext.StringIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): parquet must have string column names. Please return the DataFrame with runtime column names to regular Python to modify column names.'
                )
        oike__cgbbc = df.runtime_data_types
        khdx__rsd = len(oike__cgbbc)
        ljy__jta = gen_pandas_parquet_metadata([''] * khdx__rsd,
            oike__cgbbc, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        cibfe__uda = ljy__jta['columns'][:khdx__rsd]
        ljy__jta['columns'] = ljy__jta['columns'][khdx__rsd:]
        cibfe__uda = [json.dumps(anxj__hbnqm).replace('""', '{0}') for
            anxj__hbnqm in cibfe__uda]
        tjy__jenxv = json.dumps(ljy__jta)
        kkru__wing = '"columns": ['
        fahuo__gfz = tjy__jenxv.find(kkru__wing)
        if fahuo__gfz == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        zthii__ecvz = fahuo__gfz + len(kkru__wing)
        jorl__lkewr = tjy__jenxv[:zthii__ecvz]
        tjy__jenxv = tjy__jenxv[zthii__ecvz:]
        ovd__qsx = len(ljy__jta['columns'])
    else:
        tjy__jenxv = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and tyjj__qvco:
        tjy__jenxv = tjy__jenxv.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            tjy__jenxv = tjy__jenxv.replace('"%s"', '%s')
    if not df.is_table_format:
        aqi__yzkbt = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    squsw__dsv = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        squsw__dsv += '    py_table = get_dataframe_table(df)\n'
        squsw__dsv += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        squsw__dsv += '    info_list = [{}]\n'.format(aqi__yzkbt)
        squsw__dsv += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        squsw__dsv += '    columns_index = get_dataframe_column_names(df)\n'
        squsw__dsv += '    names_arr = index_to_array(columns_index)\n'
        squsw__dsv += '    col_names = array_to_info(names_arr)\n'
    else:
        squsw__dsv += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and etrb__aufxm:
        squsw__dsv += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        shubv__teruz = True
    else:
        squsw__dsv += '    index_col = array_to_info(np.empty(0))\n'
        shubv__teruz = False
    if df.has_runtime_cols:
        squsw__dsv += '    columns_lst = []\n'
        squsw__dsv += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            squsw__dsv += f'    for _ in range(len(py_table.block_{i})):\n'
            squsw__dsv += f"""        columns_lst.append({cibfe__uda[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            squsw__dsv += '        num_cols += 1\n'
        if ovd__qsx:
            squsw__dsv += "    columns_lst.append('')\n"
        squsw__dsv += '    columns_str = ", ".join(columns_lst)\n'
        squsw__dsv += ('    metadata = """' + jorl__lkewr +
            '""" + columns_str + """' + tjy__jenxv + '"""\n')
    else:
        squsw__dsv += '    metadata = """' + tjy__jenxv + '"""\n'
    squsw__dsv += '    if compression is None:\n'
    squsw__dsv += "        compression = 'none'\n"
    squsw__dsv += '    if df.index.name is not None:\n'
    squsw__dsv += '        name_ptr = df.index.name\n'
    squsw__dsv += '    else:\n'
    squsw__dsv += "        name_ptr = 'null'\n"
    squsw__dsv += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    geq__orbs = None
    if partition_cols:
        geq__orbs = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        gepw__ujzj = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in mzuns__aftk)
        if gepw__ujzj:
            squsw__dsv += '    cat_info_list = [{}]\n'.format(gepw__ujzj)
            squsw__dsv += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            squsw__dsv += '    cat_table = table\n'
        squsw__dsv += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        squsw__dsv += (
            f'    part_cols_idxs = np.array({mzuns__aftk}, dtype=np.int32)\n')
        squsw__dsv += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        squsw__dsv += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        squsw__dsv += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        squsw__dsv += (
            '                            unicode_to_utf8(compression),\n')
        squsw__dsv += '                            _is_parallel,\n'
        squsw__dsv += (
            '                            unicode_to_utf8(bucket_region),\n')
        squsw__dsv += '                            row_group_size,\n'
        squsw__dsv += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        squsw__dsv += '    delete_table_decref_arrays(table)\n'
        squsw__dsv += '    delete_info_decref_array(index_col)\n'
        squsw__dsv += '    delete_info_decref_array(col_names_no_partitions)\n'
        squsw__dsv += '    delete_info_decref_array(col_names)\n'
        if gepw__ujzj:
            squsw__dsv += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        squsw__dsv += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        squsw__dsv += (
            '                            table, col_names, index_col,\n')
        squsw__dsv += '                            ' + str(shubv__teruz
            ) + ',\n'
        squsw__dsv += (
            '                            unicode_to_utf8(metadata),\n')
        squsw__dsv += (
            '                            unicode_to_utf8(compression),\n')
        squsw__dsv += (
            '                            _is_parallel, 1, df.index.start,\n')
        squsw__dsv += (
            '                            df.index.stop, df.index.step,\n')
        squsw__dsv += (
            '                            unicode_to_utf8(name_ptr),\n')
        squsw__dsv += (
            '                            unicode_to_utf8(bucket_region),\n')
        squsw__dsv += '                            row_group_size,\n'
        squsw__dsv += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        squsw__dsv += '    delete_table_decref_arrays(table)\n'
        squsw__dsv += '    delete_info_decref_array(index_col)\n'
        squsw__dsv += '    delete_info_decref_array(col_names)\n'
    else:
        squsw__dsv += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        squsw__dsv += (
            '                            table, col_names, index_col,\n')
        squsw__dsv += '                            ' + str(shubv__teruz
            ) + ',\n'
        squsw__dsv += (
            '                            unicode_to_utf8(metadata),\n')
        squsw__dsv += (
            '                            unicode_to_utf8(compression),\n')
        squsw__dsv += '                            _is_parallel, 0, 0, 0, 0,\n'
        squsw__dsv += (
            '                            unicode_to_utf8(name_ptr),\n')
        squsw__dsv += (
            '                            unicode_to_utf8(bucket_region),\n')
        squsw__dsv += '                            row_group_size,\n'
        squsw__dsv += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        squsw__dsv += '    delete_table_decref_arrays(table)\n'
        squsw__dsv += '    delete_info_decref_array(index_col)\n'
        squsw__dsv += '    delete_info_decref_array(col_names)\n'
    bfki__pqs = {}
    if df.has_runtime_cols:
        rzmdl__cudwi = None
    else:
        for cnio__puw in df.columns:
            if not isinstance(cnio__puw, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        rzmdl__cudwi = pd.array(df.columns)
    exec(squsw__dsv, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': rzmdl__cudwi,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': geq__orbs, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, bfki__pqs)
    pphto__rav = bfki__pqs['df_to_parquet']
    return pphto__rav


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    karuu__ramdc = 'all_ok'
    hsup__blanq, yllto__rtn = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        hotk__jrfoj = 100
        if chunksize is None:
            glup__pxj = hotk__jrfoj
        else:
            glup__pxj = min(chunksize, hotk__jrfoj)
        if _is_table_create:
            df = df.iloc[:glup__pxj, :]
        else:
            df = df.iloc[glup__pxj:, :]
            if len(df) == 0:
                return karuu__ramdc
    uju__tlaop = df.columns
    try:
        if hsup__blanq == 'snowflake':
            if yllto__rtn and con.count(yllto__rtn) == 1:
                con = con.replace(yllto__rtn, quote(yllto__rtn))
            try:
                from snowflake.connector.pandas_tools import pd_writer
                from bodo import snowflake_sqlalchemy_compat
                if method is not None and _is_table_create and bodo.get_rank(
                    ) == 0:
                    import warnings
                    from bodo.utils.typing import BodoWarning
                    warnings.warn(BodoWarning(
                        'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                        ))
                method = pd_writer
                df.columns = [(pcy__zpws.upper() if pcy__zpws.islower() else
                    pcy__zpws) for pcy__zpws in df.columns]
            except ImportError as fkmhs__wkn:
                karuu__ramdc = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return karuu__ramdc
        if hsup__blanq == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            myxi__tshyn = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            xfigq__szh = bodo.typeof(df)
            guuoi__jpq = {}
            for pcy__zpws, dyr__dht in zip(xfigq__szh.columns, xfigq__szh.data
                ):
                if df[pcy__zpws].dtype == 'object':
                    if dyr__dht == datetime_date_array_type:
                        guuoi__jpq[pcy__zpws] = sa.types.Date
                    elif dyr__dht in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not myxi__tshyn or 
                        myxi__tshyn == '0'):
                        guuoi__jpq[pcy__zpws] = VARCHAR2(4000)
            dtype = guuoi__jpq
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as bcwt__cin:
            karuu__ramdc = bcwt__cin.args[0]
            if hsup__blanq == 'oracle' and 'ORA-12899' in karuu__ramdc:
                karuu__ramdc += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return karuu__ramdc
    finally:
        df.columns = uju__tlaop


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    import warnings
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    df: DataFrameType = df
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues when writing the table.'
                ))
    if not (is_overload_none(chunksize) or isinstance(chunksize, types.Integer)
        ):
        raise BodoError(
            "DataFrame.to_sql(): 'chunksize' argument must be an integer if provided."
            )
    squsw__dsv = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    squsw__dsv += f"    if con.startswith('iceberg'):\n"
    squsw__dsv += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    squsw__dsv += f'        if schema is None:\n'
    squsw__dsv += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    squsw__dsv += f'        if chunksize is not None:\n'
    squsw__dsv += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    squsw__dsv += f'        if index and bodo.get_rank() == 0:\n'
    squsw__dsv += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    squsw__dsv += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    squsw__dsv += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        squsw__dsv += f'        py_table = get_dataframe_table(df)\n'
        squsw__dsv += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        aqi__yzkbt = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        squsw__dsv += f'        info_list = [{aqi__yzkbt}]\n'
        squsw__dsv += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        squsw__dsv += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        squsw__dsv += f'        names_arr = index_to_array(columns_index)\n'
        squsw__dsv += f'        col_names = array_to_info(names_arr)\n'
    else:
        squsw__dsv += f'        col_names = array_to_info(col_names_arr)\n'
    squsw__dsv += """        bodo.io.iceberg.iceberg_write(
            name,
            con_str,
            schema,
            table,
            col_names,
            if_exists,
            _is_parallel,
            pyarrow_table_schema,
        )
"""
    squsw__dsv += f'        delete_table_decref_arrays(table)\n'
    squsw__dsv += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        rzmdl__cudwi = None
    else:
        for cnio__puw in df.columns:
            if not isinstance(cnio__puw, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        rzmdl__cudwi = pd.array(df.columns)
    squsw__dsv += f'    else:\n'
    squsw__dsv += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    squsw__dsv += f"        err_msg = 'unset'\n"
    squsw__dsv += f'        if rank != 0:\n'
    squsw__dsv += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    squsw__dsv += f'        elif rank == 0:\n'
    squsw__dsv += f'            err_msg = to_sql_exception_guard_encaps(\n'
    squsw__dsv += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    squsw__dsv += f'                          chunksize, dtype, method,\n'
    squsw__dsv += f'                          True, _is_parallel,\n'
    squsw__dsv += f'                      )\n'
    squsw__dsv += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    squsw__dsv += f"        if_exists = 'append'\n"
    squsw__dsv += f"        if _is_parallel and err_msg == 'all_ok':\n"
    squsw__dsv += f'            err_msg = to_sql_exception_guard_encaps(\n'
    squsw__dsv += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    squsw__dsv += f'                          chunksize, dtype, method,\n'
    squsw__dsv += f'                          False, _is_parallel,\n'
    squsw__dsv += f'                      )\n'
    squsw__dsv += f"        if err_msg != 'all_ok':\n"
    squsw__dsv += f"            print('err_msg=', err_msg)\n"
    squsw__dsv += (
        f"            raise ValueError('error in to_sql() operation')\n")
    bfki__pqs = {}
    exec(squsw__dsv, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': rzmdl__cudwi, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, bfki__pqs)
    _impl = bfki__pqs['df_to_sql']
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=
    None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        ffeg__shic = get_overload_const_str(path_or_buf)
        if ffeg__shic.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if not (is_overload_none(columns) or isinstance(columns, (types.List,
        types.Tuple))):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must be list a or tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None, _bodo_file_prefix=
            'part-'):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D, _bodo_file_prefix)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='records', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=True, compression='infer', index=True,
    indent=None, storage_options=None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='records', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=True, compression='infer', index=
            True, indent=None, storage_options=None, _bodo_file_prefix='part-'
            ):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='records', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=True, compression='infer', index=True,
        indent=None, storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        gftz__fit = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(gftz__fit), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(gftz__fit), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    otr__ann = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    rlbv__cteqg = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', otr__ann, rlbv__cteqg,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    squsw__dsv = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        ixz__wpll = data.data.dtype.categories
        squsw__dsv += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        ixz__wpll = data.dtype.categories
        squsw__dsv += '  data_values = data\n'
    iof__undq = len(ixz__wpll)
    squsw__dsv += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    squsw__dsv += '  numba.parfors.parfor.init_prange()\n'
    squsw__dsv += '  n = len(data_values)\n'
    for i in range(iof__undq):
        squsw__dsv += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    squsw__dsv += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    squsw__dsv += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for hsi__ppkyj in range(iof__undq):
        squsw__dsv += '          data_arr_{}[i] = 0\n'.format(hsi__ppkyj)
    squsw__dsv += '      else:\n'
    for kiwue__osvh in range(iof__undq):
        squsw__dsv += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            kiwue__osvh)
    aqi__yzkbt = ', '.join(f'data_arr_{i}' for i in range(iof__undq))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(ixz__wpll[0], np.datetime64):
        ixz__wpll = tuple(pd.Timestamp(pcy__zpws) for pcy__zpws in ixz__wpll)
    elif isinstance(ixz__wpll[0], np.timedelta64):
        ixz__wpll = tuple(pd.Timedelta(pcy__zpws) for pcy__zpws in ixz__wpll)
    return bodo.hiframes.dataframe_impl._gen_init_df(squsw__dsv, ixz__wpll,
        aqi__yzkbt, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_query, pd.read_gbq, pd.read_stata, pd.ExcelWriter, pd.
    json_normalize, pd.merge_ordered, pd.factorize, pd.wide_to_long, pd.
    bdate_range, pd.period_range, pd.infer_freq, pd.interval_range, pd.eval,
    pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'round',
    'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix', 'align',
    'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'squeeze',
    'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq', 'asof',
    'slice_shift', 'tshift', 'first_valid_index', 'last_valid_index',
    'resample', 'to_period', 'to_timestamp', 'tz_convert', 'tz_localize',
    'boxplot', 'hist', 'from_dict', 'from_records', 'to_pickle', 'to_hdf',
    'to_dict', 'to_excel', 'to_html', 'to_feather', 'to_latex', 'to_stata',
    'to_gbq', 'to_records', 'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for nsrb__yuhtx in pd_unsupported:
        yxggk__rhr = mod_name + '.' + nsrb__yuhtx.__name__
        overload(nsrb__yuhtx, no_unliteral=True)(create_unsupported_overload
            (yxggk__rhr))


def _install_dataframe_unsupported():
    for icwq__ggvwv in dataframe_unsupported_attrs:
        xxg__btcyp = 'DataFrame.' + icwq__ggvwv
        overload_attribute(DataFrameType, icwq__ggvwv)(
            create_unsupported_overload(xxg__btcyp))
    for yxggk__rhr in dataframe_unsupported:
        xxg__btcyp = 'DataFrame.' + yxggk__rhr + '()'
        overload_method(DataFrameType, yxggk__rhr)(create_unsupported_overload
            (xxg__btcyp))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
