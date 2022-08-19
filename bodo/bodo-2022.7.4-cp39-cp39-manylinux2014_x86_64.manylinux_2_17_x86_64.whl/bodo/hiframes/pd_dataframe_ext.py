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
from bodo.hiframes.time_ext import TimeArrayType
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
            ctg__qeel = f'{len(self.data)} columns of types {set(self.data)}'
            efh__jhmvt = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({ctg__qeel}, {self.index}, {efh__jhmvt}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {qxh__ikawm: i for i, qxh__ikawm in enumerate(self.columns)}

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
            zlsmb__rwez = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(lico__eswrn.unify(typingctx, iulf__lwut) if 
                lico__eswrn != iulf__lwut else lico__eswrn for lico__eswrn,
                iulf__lwut in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if zlsmb__rwez is not None and None not in data:
                return DataFrameType(data, zlsmb__rwez, self.columns, dist,
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
        return all(lico__eswrn.is_precise() for lico__eswrn in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        foct__vgqt = self.columns.index(col_name)
        mpl__myvv = tuple(list(self.data[:foct__vgqt]) + [new_type] + list(
            self.data[foct__vgqt + 1:]))
        return DataFrameType(mpl__myvv, self.index, self.columns, self.dist,
            self.is_table_format)


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
        edc__pcsc = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            edc__pcsc.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, edc__pcsc)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        edc__pcsc = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, edc__pcsc)


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
        qziv__dykw = 'n',
        dahfb__ygvkh = {'n': 5}
        ybwpz__oxg, ioml__dyd = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, qziv__dykw, dahfb__ygvkh)
        syytx__cyi = ioml__dyd[0]
        if not is_overload_int(syytx__cyi):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        wbp__wmj = df.copy()
        return wbp__wmj(*ioml__dyd).replace(pysig=ybwpz__oxg)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        dvmkp__tka = (df,) + args
        qziv__dykw = 'df', 'method', 'min_periods'
        dahfb__ygvkh = {'method': 'pearson', 'min_periods': 1}
        oeuz__vis = 'method',
        ybwpz__oxg, ioml__dyd = bodo.utils.typing.fold_typing_args(func_name,
            dvmkp__tka, kws, qziv__dykw, dahfb__ygvkh, oeuz__vis)
        eget__hpfc = ioml__dyd[2]
        if not is_overload_int(eget__hpfc):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        bqlq__scnne = []
        cjl__pkbe = []
        for qxh__ikawm, uha__ysmv in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(uha__ysmv.dtype):
                bqlq__scnne.append(qxh__ikawm)
                cjl__pkbe.append(types.Array(types.float64, 1, 'A'))
        if len(bqlq__scnne) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        cjl__pkbe = tuple(cjl__pkbe)
        bqlq__scnne = tuple(bqlq__scnne)
        index_typ = bodo.utils.typing.type_col_to_index(bqlq__scnne)
        wbp__wmj = DataFrameType(cjl__pkbe, index_typ, bqlq__scnne)
        return wbp__wmj(*ioml__dyd).replace(pysig=ybwpz__oxg)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        dgfil__rusfp = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        upiny__czru = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        uqwf__rllgb = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        kvreg__hpmiw = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        vwfoi__siuhn = dict(raw=upiny__czru, result_type=uqwf__rllgb)
        jvzqf__hcunb = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', vwfoi__siuhn,
            jvzqf__hcunb, package_name='pandas', module_name='DataFrame')
        dub__bgvh = True
        if types.unliteral(dgfil__rusfp) == types.unicode_type:
            if not is_overload_constant_str(dgfil__rusfp):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            dub__bgvh = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        xahms__exxf = get_overload_const_int(axis)
        if dub__bgvh and xahms__exxf != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif xahms__exxf not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        fusg__xeyj = []
        for arr_typ in df.data:
            csnl__oaytp = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            npxw__luv = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(csnl__oaytp), types.int64), {}).return_type
            fusg__xeyj.append(npxw__luv)
        hlb__jnhv = types.none
        idk__ppvj = HeterogeneousIndexType(types.BaseTuple.from_types(tuple
            (types.literal(qxh__ikawm) for qxh__ikawm in df.columns)), None)
        bwtar__nijae = types.BaseTuple.from_types(fusg__xeyj)
        tpxis__mwmp = types.Tuple([types.bool_] * len(bwtar__nijae))
        zoi__tftsy = bodo.NullableTupleType(bwtar__nijae, tpxis__mwmp)
        acdb__vbpz = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if acdb__vbpz == types.NPDatetime('ns'):
            acdb__vbpz = bodo.pd_timestamp_type
        if acdb__vbpz == types.NPTimedelta('ns'):
            acdb__vbpz = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(bwtar__nijae):
            pqtsg__atep = HeterogeneousSeriesType(zoi__tftsy, idk__ppvj,
                acdb__vbpz)
        else:
            pqtsg__atep = SeriesType(bwtar__nijae.dtype, zoi__tftsy,
                idk__ppvj, acdb__vbpz)
        czeh__shgn = pqtsg__atep,
        if kvreg__hpmiw is not None:
            czeh__shgn += tuple(kvreg__hpmiw.types)
        try:
            if not dub__bgvh:
                vvxo__rvse = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(dgfil__rusfp), self.context,
                    'DataFrame.apply', axis if xahms__exxf == 1 else None)
            else:
                vvxo__rvse = get_const_func_output_type(dgfil__rusfp,
                    czeh__shgn, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as nyw__htuh:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', nyw__htuh))
        if dub__bgvh:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(vvxo__rvse, (SeriesType, HeterogeneousSeriesType)
                ) and vvxo__rvse.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(vvxo__rvse, HeterogeneousSeriesType):
                woixh__ovf, pxiwv__rgr = vvxo__rvse.const_info
                if isinstance(vvxo__rvse.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    vczsx__sluen = vvxo__rvse.data.tuple_typ.types
                elif isinstance(vvxo__rvse.data, types.Tuple):
                    vczsx__sluen = vvxo__rvse.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                bljvh__sximo = tuple(to_nullable_type(dtype_to_array_type(
                    cou__sqza)) for cou__sqza in vczsx__sluen)
                awjvm__zrvu = DataFrameType(bljvh__sximo, df.index, pxiwv__rgr)
            elif isinstance(vvxo__rvse, SeriesType):
                hioko__oos, pxiwv__rgr = vvxo__rvse.const_info
                bljvh__sximo = tuple(to_nullable_type(dtype_to_array_type(
                    vvxo__rvse.dtype)) for woixh__ovf in range(hioko__oos))
                awjvm__zrvu = DataFrameType(bljvh__sximo, df.index, pxiwv__rgr)
            else:
                tvq__wksv = get_udf_out_arr_type(vvxo__rvse)
                awjvm__zrvu = SeriesType(tvq__wksv.dtype, tvq__wksv, df.
                    index, None)
        else:
            awjvm__zrvu = vvxo__rvse
        pwvgv__cjl = ', '.join("{} = ''".format(lico__eswrn) for
            lico__eswrn in kws.keys())
        pszuj__hnagz = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {pwvgv__cjl}):
"""
        pszuj__hnagz += '    pass\n'
        cutbe__thzim = {}
        exec(pszuj__hnagz, {}, cutbe__thzim)
        cjz__pyiio = cutbe__thzim['apply_stub']
        ybwpz__oxg = numba.core.utils.pysignature(cjz__pyiio)
        wzz__vben = (dgfil__rusfp, axis, upiny__czru, uqwf__rllgb, kvreg__hpmiw
            ) + tuple(kws.values())
        return signature(awjvm__zrvu, *wzz__vben).replace(pysig=ybwpz__oxg)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        qziv__dykw = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        dahfb__ygvkh = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        oeuz__vis = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        ybwpz__oxg, ioml__dyd = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, qziv__dykw, dahfb__ygvkh, oeuz__vis)
        ckxj__xgig = ioml__dyd[2]
        if not is_overload_constant_str(ckxj__xgig):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        ybgq__rlklr = ioml__dyd[0]
        if not is_overload_none(ybgq__rlklr) and not (is_overload_int(
            ybgq__rlklr) or is_overload_constant_str(ybgq__rlklr)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ybgq__rlklr):
            pvc__gwpd = get_overload_const_str(ybgq__rlklr)
            if pvc__gwpd not in df.columns:
                raise BodoError(f'{func_name}: {pvc__gwpd} column not found.')
        elif is_overload_int(ybgq__rlklr):
            oxaz__gqj = get_overload_const_int(ybgq__rlklr)
            if oxaz__gqj > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {oxaz__gqj} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ybgq__rlklr = df.columns[ybgq__rlklr]
        drm__caak = ioml__dyd[1]
        if not is_overload_none(drm__caak) and not (is_overload_int(
            drm__caak) or is_overload_constant_str(drm__caak)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(drm__caak):
            jmjv__yosd = get_overload_const_str(drm__caak)
            if jmjv__yosd not in df.columns:
                raise BodoError(f'{func_name}: {jmjv__yosd} column not found.')
        elif is_overload_int(drm__caak):
            hev__ptxer = get_overload_const_int(drm__caak)
            if hev__ptxer > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {hev__ptxer} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            drm__caak = df.columns[drm__caak]
        uaza__mhn = ioml__dyd[3]
        if not is_overload_none(uaza__mhn) and not is_tuple_like_type(uaza__mhn
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        rat__tmog = ioml__dyd[10]
        if not is_overload_none(rat__tmog) and not is_overload_constant_str(
            rat__tmog):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        zalil__byzz = ioml__dyd[12]
        if not is_overload_bool(zalil__byzz):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        isplj__gsp = ioml__dyd[17]
        if not is_overload_none(isplj__gsp) and not is_tuple_like_type(
            isplj__gsp):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        twiic__fxif = ioml__dyd[18]
        if not is_overload_none(twiic__fxif) and not is_tuple_like_type(
            twiic__fxif):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        qsntn__mrjt = ioml__dyd[22]
        if not is_overload_none(qsntn__mrjt) and not is_overload_int(
            qsntn__mrjt):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        nsw__wcsf = ioml__dyd[29]
        if not is_overload_none(nsw__wcsf) and not is_overload_constant_str(
            nsw__wcsf):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        arvf__ghxr = ioml__dyd[30]
        if not is_overload_none(arvf__ghxr) and not is_overload_constant_str(
            arvf__ghxr):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        ahplu__lfyr = types.List(types.mpl_line_2d_type)
        ckxj__xgig = get_overload_const_str(ckxj__xgig)
        if ckxj__xgig == 'scatter':
            if is_overload_none(ybgq__rlklr) and is_overload_none(drm__caak):
                raise BodoError(
                    f'{func_name}: {ckxj__xgig} requires an x and y column.')
            elif is_overload_none(ybgq__rlklr):
                raise BodoError(
                    f'{func_name}: {ckxj__xgig} x column is missing.')
            elif is_overload_none(drm__caak):
                raise BodoError(
                    f'{func_name}: {ckxj__xgig} y column is missing.')
            ahplu__lfyr = types.mpl_path_collection_type
        elif ckxj__xgig != 'line':
            raise BodoError(f'{func_name}: {ckxj__xgig} plot is not supported.'
                )
        return signature(ahplu__lfyr, *ioml__dyd).replace(pysig=ybwpz__oxg)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            tjryn__swcd = df.columns.index(attr)
            arr_typ = df.data[tjryn__swcd]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            jzxtg__mvz = []
            mpl__myvv = []
            jbw__rbl = False
            for i, lxf__kzpz in enumerate(df.columns):
                if lxf__kzpz[0] != attr:
                    continue
                jbw__rbl = True
                jzxtg__mvz.append(lxf__kzpz[1] if len(lxf__kzpz) == 2 else
                    lxf__kzpz[1:])
                mpl__myvv.append(df.data[i])
            if jbw__rbl:
                return DataFrameType(tuple(mpl__myvv), df.index, tuple(
                    jzxtg__mvz))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        jlrhi__pkkxm = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(jlrhi__pkkxm)
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
        hrpac__gdy = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], hrpac__gdy)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    rcpa__vgex = builder.module
    qgi__yth = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vevb__ezomz = cgutils.get_or_insert_function(rcpa__vgex, qgi__yth, name
        ='.dtor.df.{}'.format(df_type))
    if not vevb__ezomz.is_declaration:
        return vevb__ezomz
    vevb__ezomz.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vevb__ezomz.append_basic_block())
    blyf__wbboe = vevb__ezomz.args[0]
    ijc__blbu = context.get_value_type(payload_type).as_pointer()
    xbhw__veq = builder.bitcast(blyf__wbboe, ijc__blbu)
    payload = context.make_helper(builder, payload_type, ref=xbhw__veq)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        tdlq__zmpsd = context.get_python_api(builder)
        taxj__ovo = tdlq__zmpsd.gil_ensure()
        tdlq__zmpsd.decref(payload.parent)
        tdlq__zmpsd.gil_release(taxj__ovo)
    builder.ret_void()
    return vevb__ezomz


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    lvu__dtbjk = cgutils.create_struct_proxy(payload_type)(context, builder)
    lvu__dtbjk.data = data_tup
    lvu__dtbjk.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        lvu__dtbjk.columns = colnames
    thu__ikpr = context.get_value_type(payload_type)
    edmne__smo = context.get_abi_sizeof(thu__ikpr)
    jgja__mlhvj = define_df_dtor(context, builder, df_type, payload_type)
    iyctf__eerl = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, edmne__smo), jgja__mlhvj)
    wwsfn__swx = context.nrt.meminfo_data(builder, iyctf__eerl)
    suuqn__gtxtj = builder.bitcast(wwsfn__swx, thu__ikpr.as_pointer())
    qpc__tmvil = cgutils.create_struct_proxy(df_type)(context, builder)
    qpc__tmvil.meminfo = iyctf__eerl
    if parent is None:
        qpc__tmvil.parent = cgutils.get_null_value(qpc__tmvil.parent.type)
    else:
        qpc__tmvil.parent = parent
        lvu__dtbjk.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            tdlq__zmpsd = context.get_python_api(builder)
            taxj__ovo = tdlq__zmpsd.gil_ensure()
            tdlq__zmpsd.incref(parent)
            tdlq__zmpsd.gil_release(taxj__ovo)
    builder.store(lvu__dtbjk._getvalue(), suuqn__gtxtj)
    return qpc__tmvil._getvalue()


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
        lwz__kbird = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        lwz__kbird = [cou__sqza for cou__sqza in data_typ.dtype.arr_types]
    kvy__kusd = DataFrameType(tuple(lwz__kbird + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        twlrf__pgbly = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return twlrf__pgbly
    sig = signature(kvy__kusd, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    hioko__oos = len(data_tup_typ.types)
    if hioko__oos == 0:
        column_names = ()
    ihf__aase = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(ihf__aase, ColNamesMetaType) and isinstance(ihf__aase
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = ihf__aase.meta
    if hioko__oos == 1 and isinstance(data_tup_typ.types[0], TableType):
        hioko__oos = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == hioko__oos, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    jie__qix = data_tup_typ.types
    if hioko__oos != 0 and isinstance(data_tup_typ.types[0], TableType):
        jie__qix = data_tup_typ.types[0].arr_types
        is_table_format = True
    kvy__kusd = DataFrameType(jie__qix, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            ijtas__bryww = cgutils.create_struct_proxy(kvy__kusd.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = ijtas__bryww.parent
        twlrf__pgbly = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return twlrf__pgbly
    sig = signature(kvy__kusd, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        qpc__tmvil = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, qpc__tmvil.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        lvu__dtbjk = get_dataframe_payload(context, builder, df_typ, args[0])
        jvkj__uaxsu = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[jvkj__uaxsu]
        if df_typ.is_table_format:
            ijtas__bryww = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(lvu__dtbjk.data, 0))
            tbdsk__gzbn = df_typ.table_type.type_to_blk[arr_typ]
            oxbj__mxbwu = getattr(ijtas__bryww, f'block_{tbdsk__gzbn}')
            osku__zqjro = ListInstance(context, builder, types.List(arr_typ
                ), oxbj__mxbwu)
            wixw__ptfh = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[jvkj__uaxsu])
            hrpac__gdy = osku__zqjro.getitem(wixw__ptfh)
        else:
            hrpac__gdy = builder.extract_value(lvu__dtbjk.data, jvkj__uaxsu)
        cui__pytn = cgutils.alloca_once_value(builder, hrpac__gdy)
        glo__kkth = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, cui__pytn, glo__kkth)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    iyctf__eerl = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, iyctf__eerl)
    ijc__blbu = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, ijc__blbu)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    kvy__kusd = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        kvy__kusd = types.Tuple([TableType(df_typ.data)])
    sig = signature(kvy__kusd, df_typ)

    def codegen(context, builder, signature, args):
        lvu__dtbjk = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            lvu__dtbjk.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        lvu__dtbjk = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, lvu__dtbjk
            .index)
    kvy__kusd = df_typ.index
    sig = signature(kvy__kusd, df_typ)
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
        wbp__wmj = df.data[i]
        return wbp__wmj(*args)


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
        lvu__dtbjk = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(lvu__dtbjk.data, 0))
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
    ctad__moe = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{ctad__moe})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        wbp__wmj = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return wbp__wmj(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        lvu__dtbjk = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, lvu__dtbjk.columns)
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
    bwtar__nijae = self.typemap[data_tup.name]
    if any(is_tuple_like_type(cou__sqza) for cou__sqza in bwtar__nijae.types):
        return None
    if equiv_set.has_shape(data_tup):
        sutj__ftry = equiv_set.get_shape(data_tup)
        if len(sutj__ftry) > 1:
            equiv_set.insert_equiv(*sutj__ftry)
        if len(sutj__ftry) > 0:
            idk__ppvj = self.typemap[index.name]
            if not isinstance(idk__ppvj, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(sutj__ftry[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(sutj__ftry[0], len(
                sutj__ftry)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ocbpg__oihm = args[0]
    data_types = self.typemap[ocbpg__oihm.name].data
    if any(is_tuple_like_type(cou__sqza) for cou__sqza in data_types):
        return None
    if equiv_set.has_shape(ocbpg__oihm):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ocbpg__oihm)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    ocbpg__oihm = args[0]
    idk__ppvj = self.typemap[ocbpg__oihm.name].index
    if isinstance(idk__ppvj, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(ocbpg__oihm):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ocbpg__oihm)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ocbpg__oihm = args[0]
    if equiv_set.has_shape(ocbpg__oihm):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ocbpg__oihm), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ocbpg__oihm = args[0]
    if equiv_set.has_shape(ocbpg__oihm):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ocbpg__oihm)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    jvkj__uaxsu = get_overload_const_int(c_ind_typ)
    if df_typ.data[jvkj__uaxsu] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        hogao__ozoub, woixh__ovf, qgh__ddpfh = args
        lvu__dtbjk = get_dataframe_payload(context, builder, df_typ,
            hogao__ozoub)
        if df_typ.is_table_format:
            ijtas__bryww = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(lvu__dtbjk.data, 0))
            tbdsk__gzbn = df_typ.table_type.type_to_blk[arr_typ]
            oxbj__mxbwu = getattr(ijtas__bryww, f'block_{tbdsk__gzbn}')
            osku__zqjro = ListInstance(context, builder, types.List(arr_typ
                ), oxbj__mxbwu)
            wixw__ptfh = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[jvkj__uaxsu])
            osku__zqjro.setitem(wixw__ptfh, qgh__ddpfh, True)
        else:
            hrpac__gdy = builder.extract_value(lvu__dtbjk.data, jvkj__uaxsu)
            context.nrt.decref(builder, df_typ.data[jvkj__uaxsu], hrpac__gdy)
            lvu__dtbjk.data = builder.insert_value(lvu__dtbjk.data,
                qgh__ddpfh, jvkj__uaxsu)
            context.nrt.incref(builder, arr_typ, qgh__ddpfh)
        qpc__tmvil = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=hogao__ozoub)
        payload_type = DataFramePayloadType(df_typ)
        xbhw__veq = context.nrt.meminfo_data(builder, qpc__tmvil.meminfo)
        ijc__blbu = context.get_value_type(payload_type).as_pointer()
        xbhw__veq = builder.bitcast(xbhw__veq, ijc__blbu)
        builder.store(lvu__dtbjk._getvalue(), xbhw__veq)
        return impl_ret_borrowed(context, builder, df_typ, hogao__ozoub)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        jnnb__qra = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        ginrl__ehr = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=jnnb__qra)
        tqacs__ldmke = get_dataframe_payload(context, builder, df_typ,
            jnnb__qra)
        qpc__tmvil = construct_dataframe(context, builder, signature.
            return_type, tqacs__ldmke.data, index_val, ginrl__ehr.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), tqacs__ldmke.data)
        return qpc__tmvil
    kvy__kusd = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(kvy__kusd, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    hioko__oos = len(df_type.columns)
    xgs__okwcc = hioko__oos
    gmqzi__ycmnu = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    pked__zdd = col_name not in df_type.columns
    jvkj__uaxsu = hioko__oos
    if pked__zdd:
        gmqzi__ycmnu += arr_type,
        column_names += col_name,
        xgs__okwcc += 1
    else:
        jvkj__uaxsu = df_type.columns.index(col_name)
        gmqzi__ycmnu = tuple(arr_type if i == jvkj__uaxsu else gmqzi__ycmnu
            [i] for i in range(hioko__oos))

    def codegen(context, builder, signature, args):
        hogao__ozoub, woixh__ovf, qgh__ddpfh = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, hogao__ozoub)
        qbnd__yfbfy = cgutils.create_struct_proxy(df_type)(context, builder,
            value=hogao__ozoub)
        if df_type.is_table_format:
            fwxoi__mwbc = df_type.table_type
            prszb__eefp = builder.extract_value(in_dataframe_payload.data, 0)
            thts__ohp = TableType(gmqzi__ycmnu)
            yjqj__cuwx = set_table_data_codegen(context, builder,
                fwxoi__mwbc, prszb__eefp, thts__ohp, arr_type, qgh__ddpfh,
                jvkj__uaxsu, pked__zdd)
            data_tup = context.make_tuple(builder, types.Tuple([thts__ohp]),
                [yjqj__cuwx])
        else:
            jie__qix = [(builder.extract_value(in_dataframe_payload.data, i
                ) if i != jvkj__uaxsu else qgh__ddpfh) for i in range(
                hioko__oos)]
            if pked__zdd:
                jie__qix.append(qgh__ddpfh)
            for ocbpg__oihm, hezr__wsx in zip(jie__qix, gmqzi__ycmnu):
                context.nrt.incref(builder, hezr__wsx, ocbpg__oihm)
            data_tup = context.make_tuple(builder, types.Tuple(gmqzi__ycmnu
                ), jie__qix)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        rsv__thu = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, qbnd__yfbfy.parent, None)
        if not pked__zdd and arr_type == df_type.data[jvkj__uaxsu]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            xbhw__veq = context.nrt.meminfo_data(builder, qbnd__yfbfy.meminfo)
            ijc__blbu = context.get_value_type(payload_type).as_pointer()
            xbhw__veq = builder.bitcast(xbhw__veq, ijc__blbu)
            qqziq__vmth = get_dataframe_payload(context, builder, df_type,
                rsv__thu)
            builder.store(qqziq__vmth._getvalue(), xbhw__veq)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, thts__ohp, builder.
                    extract_value(data_tup, 0))
            else:
                for ocbpg__oihm, hezr__wsx in zip(jie__qix, gmqzi__ycmnu):
                    context.nrt.incref(builder, hezr__wsx, ocbpg__oihm)
        has_parent = cgutils.is_not_null(builder, qbnd__yfbfy.parent)
        with builder.if_then(has_parent):
            tdlq__zmpsd = context.get_python_api(builder)
            taxj__ovo = tdlq__zmpsd.gil_ensure()
            ewrgo__sgabs = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, qgh__ddpfh)
            qxh__ikawm = numba.core.pythonapi._BoxContext(context, builder,
                tdlq__zmpsd, ewrgo__sgabs)
            ysu__sayj = qxh__ikawm.pyapi.from_native_value(arr_type,
                qgh__ddpfh, qxh__ikawm.env_manager)
            if isinstance(col_name, str):
                vlf__sudg = context.insert_const_string(builder.module,
                    col_name)
                tqyuy__yjqt = tdlq__zmpsd.string_from_string(vlf__sudg)
            else:
                assert isinstance(col_name, int)
                tqyuy__yjqt = tdlq__zmpsd.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            tdlq__zmpsd.object_setitem(qbnd__yfbfy.parent, tqyuy__yjqt,
                ysu__sayj)
            tdlq__zmpsd.decref(ysu__sayj)
            tdlq__zmpsd.decref(tqyuy__yjqt)
            tdlq__zmpsd.gil_release(taxj__ovo)
        return rsv__thu
    kvy__kusd = DataFrameType(gmqzi__ycmnu, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(kvy__kusd, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    hioko__oos = len(pyval.columns)
    jie__qix = []
    for i in range(hioko__oos):
        olmsg__sani = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            ysu__sayj = olmsg__sani.array
        else:
            ysu__sayj = olmsg__sani.values
        jie__qix.append(ysu__sayj)
    jie__qix = tuple(jie__qix)
    if df_type.is_table_format:
        ijtas__bryww = context.get_constant_generic(builder, df_type.
            table_type, Table(jie__qix))
        data_tup = lir.Constant.literal_struct([ijtas__bryww])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], lxf__kzpz) for i,
            lxf__kzpz in enumerate(jie__qix)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    leuot__idjyj = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, leuot__idjyj])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    lnzh__ohrou = context.get_constant(types.int64, -1)
    avg__dmdd = context.get_constant_null(types.voidptr)
    iyctf__eerl = lir.Constant.literal_struct([lnzh__ohrou, avg__dmdd,
        avg__dmdd, payload, lnzh__ohrou])
    iyctf__eerl = cgutils.global_constant(builder, '.const.meminfo',
        iyctf__eerl).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([iyctf__eerl, leuot__idjyj])


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
        zlsmb__rwez = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        zlsmb__rwez = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, zlsmb__rwez)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        mpl__myvv = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                mpl__myvv)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), mpl__myvv)
    elif not fromty.is_table_format and toty.is_table_format:
        mpl__myvv = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        mpl__myvv = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        mpl__myvv = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        mpl__myvv = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, mpl__myvv,
        zlsmb__rwez, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    yukp__hxjy = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        fmbp__twoe = get_index_data_arr_types(toty.index)[0]
        vjpre__giyr = bodo.utils.transform.get_type_alloc_counts(fmbp__twoe
            ) - 1
        lehx__dlqox = ', '.join('0' for woixh__ovf in range(vjpre__giyr))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(lehx__dlqox, ', ' if vjpre__giyr == 1 else ''))
        yukp__hxjy['index_arr_type'] = fmbp__twoe
    eok__uimnx = []
    for i, arr_typ in enumerate(toty.data):
        vjpre__giyr = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        lehx__dlqox = ', '.join('0' for woixh__ovf in range(vjpre__giyr))
        qbjmx__mfhpn = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, lehx__dlqox, ', ' if vjpre__giyr == 1 else ''))
        eok__uimnx.append(qbjmx__mfhpn)
        yukp__hxjy[f'arr_type{i}'] = arr_typ
    eok__uimnx = ', '.join(eok__uimnx)
    pszuj__hnagz = 'def impl():\n'
    oryd__oxwzs = bodo.hiframes.dataframe_impl._gen_init_df(pszuj__hnagz,
        toty.columns, eok__uimnx, index, yukp__hxjy)
    df = context.compile_internal(builder, oryd__oxwzs, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    ukymz__djj = toty.table_type
    ijtas__bryww = cgutils.create_struct_proxy(ukymz__djj)(context, builder)
    ijtas__bryww.parent = in_dataframe_payload.parent
    for cou__sqza, tbdsk__gzbn in ukymz__djj.type_to_blk.items():
        dchz__xkm = context.get_constant(types.int64, len(ukymz__djj.
            block_to_arr_ind[tbdsk__gzbn]))
        woixh__ovf, fsbrg__msk = ListInstance.allocate_ex(context, builder,
            types.List(cou__sqza), dchz__xkm)
        fsbrg__msk.size = dchz__xkm
        setattr(ijtas__bryww, f'block_{tbdsk__gzbn}', fsbrg__msk.value)
    for i, cou__sqza in enumerate(fromty.data):
        xuoko__jpevb = toty.data[i]
        if cou__sqza != xuoko__jpevb:
            iojm__ggwjn = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*iojm__ggwjn)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        hrpac__gdy = builder.extract_value(in_dataframe_payload.data, i)
        if cou__sqza != xuoko__jpevb:
            hioof__hsmgm = context.cast(builder, hrpac__gdy, cou__sqza,
                xuoko__jpevb)
            wgjeu__yds = False
        else:
            hioof__hsmgm = hrpac__gdy
            wgjeu__yds = True
        tbdsk__gzbn = ukymz__djj.type_to_blk[cou__sqza]
        oxbj__mxbwu = getattr(ijtas__bryww, f'block_{tbdsk__gzbn}')
        osku__zqjro = ListInstance(context, builder, types.List(cou__sqza),
            oxbj__mxbwu)
        wixw__ptfh = context.get_constant(types.int64, ukymz__djj.
            block_offsets[i])
        osku__zqjro.setitem(wixw__ptfh, hioof__hsmgm, wgjeu__yds)
    data_tup = context.make_tuple(builder, types.Tuple([ukymz__djj]), [
        ijtas__bryww._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    jie__qix = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            iojm__ggwjn = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*iojm__ggwjn)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            hrpac__gdy = builder.extract_value(in_dataframe_payload.data, i)
            hioof__hsmgm = context.cast(builder, hrpac__gdy, fromty.data[i],
                toty.data[i])
            wgjeu__yds = False
        else:
            hioof__hsmgm = builder.extract_value(in_dataframe_payload.data, i)
            wgjeu__yds = True
        if wgjeu__yds:
            context.nrt.incref(builder, toty.data[i], hioof__hsmgm)
        jie__qix.append(hioof__hsmgm)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), jie__qix)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    fwxoi__mwbc = fromty.table_type
    prszb__eefp = cgutils.create_struct_proxy(fwxoi__mwbc)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    thts__ohp = toty.table_type
    yjqj__cuwx = cgutils.create_struct_proxy(thts__ohp)(context, builder)
    yjqj__cuwx.parent = in_dataframe_payload.parent
    for cou__sqza, tbdsk__gzbn in thts__ohp.type_to_blk.items():
        dchz__xkm = context.get_constant(types.int64, len(thts__ohp.
            block_to_arr_ind[tbdsk__gzbn]))
        woixh__ovf, fsbrg__msk = ListInstance.allocate_ex(context, builder,
            types.List(cou__sqza), dchz__xkm)
        fsbrg__msk.size = dchz__xkm
        setattr(yjqj__cuwx, f'block_{tbdsk__gzbn}', fsbrg__msk.value)
    for i in range(len(fromty.data)):
        valy__jhw = fromty.data[i]
        xuoko__jpevb = toty.data[i]
        if valy__jhw != xuoko__jpevb:
            iojm__ggwjn = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*iojm__ggwjn)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ibxnc__vnp = fwxoi__mwbc.type_to_blk[valy__jhw]
        gbus__qso = getattr(prszb__eefp, f'block_{ibxnc__vnp}')
        udsp__gandf = ListInstance(context, builder, types.List(valy__jhw),
            gbus__qso)
        pkdhe__mle = context.get_constant(types.int64, fwxoi__mwbc.
            block_offsets[i])
        hrpac__gdy = udsp__gandf.getitem(pkdhe__mle)
        if valy__jhw != xuoko__jpevb:
            hioof__hsmgm = context.cast(builder, hrpac__gdy, valy__jhw,
                xuoko__jpevb)
            wgjeu__yds = False
        else:
            hioof__hsmgm = hrpac__gdy
            wgjeu__yds = True
        zreq__kmhwt = thts__ohp.type_to_blk[cou__sqza]
        fsbrg__msk = getattr(yjqj__cuwx, f'block_{zreq__kmhwt}')
        zbsx__lwsrv = ListInstance(context, builder, types.List(
            xuoko__jpevb), fsbrg__msk)
        gdc__ngfou = context.get_constant(types.int64, thts__ohp.
            block_offsets[i])
        zbsx__lwsrv.setitem(gdc__ngfou, hioof__hsmgm, wgjeu__yds)
    data_tup = context.make_tuple(builder, types.Tuple([thts__ohp]), [
        yjqj__cuwx._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    ukymz__djj = fromty.table_type
    ijtas__bryww = cgutils.create_struct_proxy(ukymz__djj)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    jie__qix = []
    for i, cou__sqza in enumerate(toty.data):
        valy__jhw = fromty.data[i]
        if cou__sqza != valy__jhw:
            iojm__ggwjn = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*iojm__ggwjn)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        tbdsk__gzbn = ukymz__djj.type_to_blk[valy__jhw]
        oxbj__mxbwu = getattr(ijtas__bryww, f'block_{tbdsk__gzbn}')
        osku__zqjro = ListInstance(context, builder, types.List(valy__jhw),
            oxbj__mxbwu)
        wixw__ptfh = context.get_constant(types.int64, ukymz__djj.
            block_offsets[i])
        hrpac__gdy = osku__zqjro.getitem(wixw__ptfh)
        if cou__sqza != valy__jhw:
            hioof__hsmgm = context.cast(builder, hrpac__gdy, valy__jhw,
                cou__sqza)
        else:
            hioof__hsmgm = hrpac__gdy
            context.nrt.incref(builder, cou__sqza, hioof__hsmgm)
        jie__qix.append(hioof__hsmgm)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), jie__qix)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    pvme__bugp, eok__uimnx, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    lqj__ajc = ColNamesMetaType(tuple(pvme__bugp))
    pszuj__hnagz = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    pszuj__hnagz += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(eok__uimnx, index_arg))
    cutbe__thzim = {}
    exec(pszuj__hnagz, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': lqj__ajc}, cutbe__thzim)
    odunn__uika = cutbe__thzim['_init_df']
    return odunn__uika


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    kvy__kusd = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(kvy__kusd, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    kvy__kusd = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(kvy__kusd, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    haw__obk = ''
    if not is_overload_none(dtype):
        haw__obk = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        hioko__oos = (len(data.types) - 1) // 2
        xty__vgbla = [cou__sqza.literal_value for cou__sqza in data.types[1
            :hioko__oos + 1]]
        data_val_types = dict(zip(xty__vgbla, data.types[hioko__oos + 1:]))
        jie__qix = ['data[{}]'.format(i) for i in range(hioko__oos + 1, 2 *
            hioko__oos + 1)]
        data_dict = dict(zip(xty__vgbla, jie__qix))
        if is_overload_none(index):
            for i, cou__sqza in enumerate(data.types[hioko__oos + 1:]):
                if isinstance(cou__sqza, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(hioko__oos + 1 + i))
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
        pufn__iwzt = '.copy()' if copy else ''
        dfn__jlar = get_overload_const_list(columns)
        hioko__oos = len(dfn__jlar)
        data_val_types = {qxh__ikawm: data.copy(ndim=1) for qxh__ikawm in
            dfn__jlar}
        jie__qix = ['data[:,{}]{}'.format(i, pufn__iwzt) for i in range(
            hioko__oos)]
        data_dict = dict(zip(dfn__jlar, jie__qix))
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
    eok__uimnx = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[qxh__ikawm], df_len, haw__obk) for qxh__ikawm in
        col_names))
    if len(col_names) == 0:
        eok__uimnx = '()'
    return col_names, eok__uimnx, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for qxh__ikawm in col_names:
        if qxh__ikawm in data_dict and is_iterable_type(data_val_types[
            qxh__ikawm]):
            df_len = 'len({})'.format(data_dict[qxh__ikawm])
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
    if all(qxh__ikawm in data_dict for qxh__ikawm in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    yoc__gza = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for qxh__ikawm in col_names:
        if qxh__ikawm not in data_dict:
            data_dict[qxh__ikawm] = yoc__gza


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
            cou__sqza = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(cou__sqza)
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
        huthe__xby = idx.literal_value
        if isinstance(huthe__xby, int):
            wbp__wmj = tup.types[huthe__xby]
        elif isinstance(huthe__xby, slice):
            wbp__wmj = types.BaseTuple.from_types(tup.types[huthe__xby])
        return signature(wbp__wmj, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    nri__hqiw, idx = sig.args
    idx = idx.literal_value
    tup, woixh__ovf = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(nri__hqiw)
        if not 0 <= idx < len(nri__hqiw):
            raise IndexError('cannot index at %d in %s' % (idx, nri__hqiw))
        yjqq__ecj = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        ilylr__anfc = cgutils.unpack_tuple(builder, tup)[idx]
        yjqq__ecj = context.make_tuple(builder, sig.return_type, ilylr__anfc)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, yjqq__ecj)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, bltg__piqm, suffix_x,
            suffix_y, is_join, indicator, woixh__ovf, woixh__ovf) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        ilal__kzpr = {qxh__ikawm: i for i, qxh__ikawm in enumerate(left_on)}
        whbk__gna = {qxh__ikawm: i for i, qxh__ikawm in enumerate(right_on)}
        eiq__pwyct = set(left_on) & set(right_on)
        wcmjv__ostfc = set(left_df.columns) & set(right_df.columns)
        empu__njn = wcmjv__ostfc - eiq__pwyct
        birg__zqpjv = '$_bodo_index_' in left_on
        fsyw__mvr = '$_bodo_index_' in right_on
        how = get_overload_const_str(bltg__piqm)
        slfag__wzwmp = how in {'left', 'outer'}
        qpcan__vfrz = how in {'right', 'outer'}
        columns = []
        data = []
        if birg__zqpjv:
            xeygt__iya = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            xeygt__iya = left_df.data[left_df.column_index[left_on[0]]]
        if fsyw__mvr:
            nwvhi__wswng = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            nwvhi__wswng = right_df.data[right_df.column_index[right_on[0]]]
        if birg__zqpjv and not fsyw__mvr and not is_join.literal_value:
            tbo__wcnu = right_on[0]
            if tbo__wcnu in left_df.column_index:
                columns.append(tbo__wcnu)
                if (nwvhi__wswng == bodo.dict_str_arr_type and xeygt__iya ==
                    bodo.string_array_type):
                    juqbj__okhjp = bodo.string_array_type
                else:
                    juqbj__okhjp = nwvhi__wswng
                data.append(juqbj__okhjp)
        if fsyw__mvr and not birg__zqpjv and not is_join.literal_value:
            wak__wrwz = left_on[0]
            if wak__wrwz in right_df.column_index:
                columns.append(wak__wrwz)
                if (xeygt__iya == bodo.dict_str_arr_type and nwvhi__wswng ==
                    bodo.string_array_type):
                    juqbj__okhjp = bodo.string_array_type
                else:
                    juqbj__okhjp = xeygt__iya
                data.append(juqbj__okhjp)
        for valy__jhw, olmsg__sani in zip(left_df.data, left_df.columns):
            columns.append(str(olmsg__sani) + suffix_x.literal_value if 
                olmsg__sani in empu__njn else olmsg__sani)
            if olmsg__sani in eiq__pwyct:
                if valy__jhw == bodo.dict_str_arr_type:
                    valy__jhw = right_df.data[right_df.column_index[
                        olmsg__sani]]
                data.append(valy__jhw)
            else:
                if (valy__jhw == bodo.dict_str_arr_type and olmsg__sani in
                    ilal__kzpr):
                    if fsyw__mvr:
                        valy__jhw = nwvhi__wswng
                    else:
                        upun__oos = ilal__kzpr[olmsg__sani]
                        rzua__ujv = right_on[upun__oos]
                        valy__jhw = right_df.data[right_df.column_index[
                            rzua__ujv]]
                if qpcan__vfrz:
                    valy__jhw = to_nullable_type(valy__jhw)
                data.append(valy__jhw)
        for valy__jhw, olmsg__sani in zip(right_df.data, right_df.columns):
            if olmsg__sani not in eiq__pwyct:
                columns.append(str(olmsg__sani) + suffix_y.literal_value if
                    olmsg__sani in empu__njn else olmsg__sani)
                if (valy__jhw == bodo.dict_str_arr_type and olmsg__sani in
                    whbk__gna):
                    if birg__zqpjv:
                        valy__jhw = xeygt__iya
                    else:
                        upun__oos = whbk__gna[olmsg__sani]
                        abnoi__lyw = left_on[upun__oos]
                        valy__jhw = left_df.data[left_df.column_index[
                            abnoi__lyw]]
                if slfag__wzwmp:
                    valy__jhw = to_nullable_type(valy__jhw)
                data.append(valy__jhw)
        glw__fuwj = get_overload_const_bool(indicator)
        if glw__fuwj:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        pyd__loec = False
        if birg__zqpjv and fsyw__mvr and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            pyd__loec = True
        elif birg__zqpjv and not fsyw__mvr:
            index_typ = right_df.index
            pyd__loec = True
        elif fsyw__mvr and not birg__zqpjv:
            index_typ = left_df.index
            pyd__loec = True
        if pyd__loec and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        fct__byb = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(fct__byb, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    qpc__tmvil = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return qpc__tmvil._getvalue()


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
    vwfoi__siuhn = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    dahfb__ygvkh = dict(join='outer', join_axes=None, keys=None, levels=
        None, names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', vwfoi__siuhn, dahfb__ygvkh,
        package_name='pandas', module_name='General')
    pszuj__hnagz = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        fes__dtny = 0
        eok__uimnx = []
        names = []
        for i, vopf__uekt in enumerate(objs.types):
            assert isinstance(vopf__uekt, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(vopf__uekt, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                vopf__uekt, 'pandas.concat()')
            if isinstance(vopf__uekt, SeriesType):
                names.append(str(fes__dtny))
                fes__dtny += 1
                eok__uimnx.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(vopf__uekt.columns)
                for zomxp__mny in range(len(vopf__uekt.data)):
                    eok__uimnx.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, zomxp__mny))
        return bodo.hiframes.dataframe_impl._gen_init_df(pszuj__hnagz,
            names, ', '.join(eok__uimnx), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(cou__sqza, DataFrameType) for cou__sqza in
            objs.types)
        xtdxf__wlk = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            xtdxf__wlk.extend(df.columns)
        xtdxf__wlk = list(dict.fromkeys(xtdxf__wlk).keys())
        lwz__kbird = {}
        for fes__dtny, qxh__ikawm in enumerate(xtdxf__wlk):
            for i, df in enumerate(objs.types):
                if qxh__ikawm in df.column_index:
                    lwz__kbird[f'arr_typ{fes__dtny}'] = df.data[df.
                        column_index[qxh__ikawm]]
                    break
        assert len(lwz__kbird) == len(xtdxf__wlk)
        rcc__ibpl = []
        for fes__dtny, qxh__ikawm in enumerate(xtdxf__wlk):
            args = []
            for i, df in enumerate(objs.types):
                if qxh__ikawm in df.column_index:
                    jvkj__uaxsu = df.column_index[qxh__ikawm]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, jvkj__uaxsu))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, fes__dtny))
            pszuj__hnagz += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(fes__dtny, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(pszuj__hnagz,
            xtdxf__wlk, ', '.join('A{}'.format(i) for i in range(len(
            xtdxf__wlk))), index, lwz__kbird)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(cou__sqza, SeriesType) for cou__sqza in objs.
            types)
        pszuj__hnagz += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            pszuj__hnagz += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pszuj__hnagz += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        pszuj__hnagz += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        cutbe__thzim = {}
        exec(pszuj__hnagz, {'bodo': bodo, 'np': np, 'numba': numba},
            cutbe__thzim)
        return cutbe__thzim['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for fes__dtny, qxh__ikawm in enumerate(df_type.columns):
            pszuj__hnagz += '  arrs{} = []\n'.format(fes__dtny)
            pszuj__hnagz += '  for i in range(len(objs)):\n'
            pszuj__hnagz += '    df = objs[i]\n'
            pszuj__hnagz += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(fes__dtny))
            pszuj__hnagz += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(fes__dtny))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            pszuj__hnagz += '  arrs_index = []\n'
            pszuj__hnagz += '  for i in range(len(objs)):\n'
            pszuj__hnagz += '    df = objs[i]\n'
            pszuj__hnagz += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(pszuj__hnagz,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        pszuj__hnagz += '  arrs = []\n'
        pszuj__hnagz += '  for i in range(len(objs)):\n'
        pszuj__hnagz += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        pszuj__hnagz += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            pszuj__hnagz += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pszuj__hnagz += '  arrs_index = []\n'
            pszuj__hnagz += '  for i in range(len(objs)):\n'
            pszuj__hnagz += '    S = objs[i]\n'
            pszuj__hnagz += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            pszuj__hnagz += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        pszuj__hnagz += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        cutbe__thzim = {}
        exec(pszuj__hnagz, {'bodo': bodo, 'np': np, 'numba': numba},
            cutbe__thzim)
        return cutbe__thzim['impl']
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
        kvy__kusd = df.copy(index=index)
        return signature(kvy__kusd, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    ppg__cer = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ppg__cer._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    vwfoi__siuhn = dict(index=index, name=name)
    dahfb__ygvkh = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', vwfoi__siuhn,
        dahfb__ygvkh, package_name='pandas', module_name='DataFrame')

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
        lwz__kbird = (types.Array(types.int64, 1, 'C'),) + df.data
        vqiet__tlghn = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, lwz__kbird)
        return signature(vqiet__tlghn, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    ppg__cer = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ppg__cer._getvalue()


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
    ppg__cer = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ppg__cer._getvalue()


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
    ppg__cer = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ppg__cer._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    peii__nfnr = get_overload_const_bool(check_duplicates)
    wtqr__ldgu = not get_overload_const_bool(is_already_shuffled)
    ewi__xyqap = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    xveh__qqe = len(value_names) > 1
    affyf__mjqm = None
    imo__bgqz = None
    qwu__enlu = None
    fzgk__pqyo = None
    ftln__lgidr = isinstance(values_tup, types.UniTuple)
    if ftln__lgidr:
        ipem__uyjf = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        ipem__uyjf = [to_str_arr_if_dict_array(to_nullable_type(hezr__wsx)) for
            hezr__wsx in values_tup]
    pszuj__hnagz = 'def impl(\n'
    pszuj__hnagz += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    pszuj__hnagz += '):\n'
    pszuj__hnagz += (
        "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n")
    if wtqr__ldgu:
        pszuj__hnagz += '    if parallel:\n'
        pszuj__hnagz += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        zxqa__efvsa = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        pszuj__hnagz += f'        info_list = [{zxqa__efvsa}]\n'
        pszuj__hnagz += (
            '        cpp_table = arr_info_list_to_table(info_list)\n')
        pszuj__hnagz += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        cbzvd__yuh = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        pcnj__mdcs = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        cgj__yuvph = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        pszuj__hnagz += f'        index_tup = ({cbzvd__yuh},)\n'
        pszuj__hnagz += f'        columns_tup = ({pcnj__mdcs},)\n'
        pszuj__hnagz += f'        values_tup = ({cgj__yuvph},)\n'
        pszuj__hnagz += '        delete_table(cpp_table)\n'
        pszuj__hnagz += '        delete_table(out_cpp_table)\n'
        pszuj__hnagz += '        ev_shuffle.finalize()\n'
    pszuj__hnagz += '    columns_arr = columns_tup[0]\n'
    if ftln__lgidr:
        pszuj__hnagz += '    values_arrs = [arr for arr in values_tup]\n'
    pszuj__hnagz += """    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)
"""
    pszuj__hnagz += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    pszuj__hnagz += '        index_tup\n'
    pszuj__hnagz += '    )\n'
    pszuj__hnagz += '    n_rows = len(unique_index_arr_tup[0])\n'
    pszuj__hnagz += '    num_values_arrays = len(values_tup)\n'
    pszuj__hnagz += '    n_unique_pivots = len(pivot_values)\n'
    if ftln__lgidr:
        pszuj__hnagz += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        pszuj__hnagz += '    n_cols = n_unique_pivots\n'
    pszuj__hnagz += '    col_map = {}\n'
    pszuj__hnagz += '    for i in range(n_unique_pivots):\n'
    pszuj__hnagz += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    pszuj__hnagz += '            raise ValueError(\n'
    pszuj__hnagz += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    pszuj__hnagz += '            )\n'
    pszuj__hnagz += '        col_map[pivot_values[i]] = i\n'
    pszuj__hnagz += '    ev_unique.finalize()\n'
    pszuj__hnagz += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    nhrwd__jfl = False
    for i, ayzv__obgxf in enumerate(ipem__uyjf):
        if is_str_arr_type(ayzv__obgxf):
            nhrwd__jfl = True
            pszuj__hnagz += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            pszuj__hnagz += (
                f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n')
    if nhrwd__jfl:
        if peii__nfnr:
            pszuj__hnagz += '    nbytes = (n_rows + 7) >> 3\n'
            pszuj__hnagz += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        pszuj__hnagz += '    for i in range(len(columns_arr)):\n'
        pszuj__hnagz += '        col_name = columns_arr[i]\n'
        pszuj__hnagz += '        pivot_idx = col_map[col_name]\n'
        pszuj__hnagz += '        row_idx = row_vector[i]\n'
        if peii__nfnr:
            pszuj__hnagz += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            pszuj__hnagz += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            pszuj__hnagz += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            pszuj__hnagz += '        else:\n'
            pszuj__hnagz += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if ftln__lgidr:
            pszuj__hnagz += '        for j in range(num_values_arrays):\n'
            pszuj__hnagz += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            pszuj__hnagz += '            len_arr = len_arrs_0[col_idx]\n'
            pszuj__hnagz += '            values_arr = values_arrs[j]\n'
            pszuj__hnagz += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            pszuj__hnagz += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            pszuj__hnagz += '                len_arr[row_idx] = str_val_len\n'
            pszuj__hnagz += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, ayzv__obgxf in enumerate(ipem__uyjf):
                if is_str_arr_type(ayzv__obgxf):
                    pszuj__hnagz += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    pszuj__hnagz += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    pszuj__hnagz += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    pszuj__hnagz += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    pszuj__hnagz += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, ayzv__obgxf in enumerate(ipem__uyjf):
        if is_str_arr_type(ayzv__obgxf):
            pszuj__hnagz += f'    data_arrs_{i} = [\n'
            pszuj__hnagz += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            pszuj__hnagz += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            pszuj__hnagz += '        )\n'
            pszuj__hnagz += '        for i in range(n_cols)\n'
            pszuj__hnagz += '    ]\n'
            pszuj__hnagz += f'    if tracing.is_tracing():\n'
            pszuj__hnagz += '         for i in range(n_cols):'
            pszuj__hnagz += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            pszuj__hnagz += f'    data_arrs_{i} = [\n'
            pszuj__hnagz += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            pszuj__hnagz += '        for _ in range(n_cols)\n'
            pszuj__hnagz += '    ]\n'
    if not nhrwd__jfl and peii__nfnr:
        pszuj__hnagz += '    nbytes = (n_rows + 7) >> 3\n'
        pszuj__hnagz += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    pszuj__hnagz += '    ev_alloc.finalize()\n'
    pszuj__hnagz += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    pszuj__hnagz += '    for i in range(len(columns_arr)):\n'
    pszuj__hnagz += '        col_name = columns_arr[i]\n'
    pszuj__hnagz += '        pivot_idx = col_map[col_name]\n'
    pszuj__hnagz += '        row_idx = row_vector[i]\n'
    if not nhrwd__jfl and peii__nfnr:
        pszuj__hnagz += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        pszuj__hnagz += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        pszuj__hnagz += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        pszuj__hnagz += '        else:\n'
        pszuj__hnagz += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if ftln__lgidr:
        pszuj__hnagz += '        for j in range(num_values_arrays):\n'
        pszuj__hnagz += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        pszuj__hnagz += '            col_arr = data_arrs_0[col_idx]\n'
        pszuj__hnagz += '            values_arr = values_arrs[j]\n'
        pszuj__hnagz += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        pszuj__hnagz += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        pszuj__hnagz += '            else:\n'
        pszuj__hnagz += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, ayzv__obgxf in enumerate(ipem__uyjf):
            pszuj__hnagz += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            pszuj__hnagz += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            pszuj__hnagz += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            pszuj__hnagz += f'        else:\n'
            pszuj__hnagz += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        pszuj__hnagz += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        affyf__mjqm = index_names.meta[0]
    else:
        pszuj__hnagz += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        affyf__mjqm = tuple(index_names.meta)
    pszuj__hnagz += f'    if tracing.is_tracing():\n'
    pszuj__hnagz += f'        index_nbytes = index.nbytes\n'
    pszuj__hnagz += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not ewi__xyqap:
        qwu__enlu = columns_name.meta[0]
        if xveh__qqe:
            pszuj__hnagz += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            imo__bgqz = value_names.meta
            if all(isinstance(qxh__ikawm, str) for qxh__ikawm in imo__bgqz):
                imo__bgqz = pd.array(imo__bgqz, 'string')
            elif all(isinstance(qxh__ikawm, int) for qxh__ikawm in imo__bgqz):
                imo__bgqz = np.array(imo__bgqz, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(imo__bgqz.dtype, pd.StringDtype):
                pszuj__hnagz += '    total_chars = 0\n'
                pszuj__hnagz += f'    for i in range({len(value_names)}):\n'
                pszuj__hnagz += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                pszuj__hnagz += '        total_chars += value_name_str_len\n'
                pszuj__hnagz += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                pszuj__hnagz += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                pszuj__hnagz += '    total_chars = 0\n'
                pszuj__hnagz += '    for i in range(len(pivot_values)):\n'
                pszuj__hnagz += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                pszuj__hnagz += '        total_chars += pivot_val_str_len\n'
                pszuj__hnagz += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                pszuj__hnagz += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            pszuj__hnagz += f'    for i in range({len(value_names)}):\n'
            pszuj__hnagz += '        for j in range(len(pivot_values)):\n'
            pszuj__hnagz += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            pszuj__hnagz += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            pszuj__hnagz += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            pszuj__hnagz += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    pszuj__hnagz += '    ev_fill.finalize()\n'
    ukymz__djj = None
    if ewi__xyqap:
        if xveh__qqe:
            pldpg__mhnmo = []
            for ainn__qnji in _constant_pivot_values.meta:
                for daar__kdq in value_names.meta:
                    pldpg__mhnmo.append((ainn__qnji, daar__kdq))
            column_names = tuple(pldpg__mhnmo)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        fzgk__pqyo = ColNamesMetaType(column_names)
        zaiz__bkgme = []
        for hezr__wsx in ipem__uyjf:
            zaiz__bkgme.extend([hezr__wsx] * len(_constant_pivot_values))
        ukty__ntpnp = tuple(zaiz__bkgme)
        ukymz__djj = TableType(ukty__ntpnp)
        pszuj__hnagz += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        pszuj__hnagz += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, hezr__wsx in enumerate(ipem__uyjf):
            pszuj__hnagz += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {ukymz__djj.type_to_blk[hezr__wsx]})
"""
        pszuj__hnagz += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        pszuj__hnagz += '        (table,), index, columns_typ\n'
        pszuj__hnagz += '    )\n'
    else:
        ntay__rhf = ', '.join(f'data_arrs_{i}' for i in range(len(ipem__uyjf)))
        pszuj__hnagz += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({ntay__rhf},), n_rows)
"""
        pszuj__hnagz += """    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(
"""
        pszuj__hnagz += '        (table,), index, column_index\n'
        pszuj__hnagz += '    )\n'
    pszuj__hnagz += '    ev.finalize()\n'
    pszuj__hnagz += '    return result\n'
    cutbe__thzim = {}
    ivoy__ljvep = {f'data_arr_typ_{i}': ayzv__obgxf for i, ayzv__obgxf in
        enumerate(ipem__uyjf)}
    valu__jswac = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        ukymz__djj, 'columns_typ': fzgk__pqyo, 'index_names_lit':
        affyf__mjqm, 'value_names_lit': imo__bgqz, 'columns_name_lit':
        qwu__enlu, **ivoy__ljvep, 'tracing': tracing}
    exec(pszuj__hnagz, valu__jswac, cutbe__thzim)
    impl = cutbe__thzim['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    qwdxt__pau = {}
    qwdxt__pau['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, rjy__pnvnj in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        nux__cvg = None
        if isinstance(rjy__pnvnj, bodo.DatetimeArrayType):
            ffv__tlba = 'datetimetz'
            wxx__dnss = 'datetime64[ns]'
            if isinstance(rjy__pnvnj.tz, int):
                ycdaa__nxr = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(rjy__pnvnj.tz))
            else:
                ycdaa__nxr = pd.DatetimeTZDtype(tz=rjy__pnvnj.tz).tz
            nux__cvg = {'timezone': pa.lib.tzinfo_to_string(ycdaa__nxr)}
        elif isinstance(rjy__pnvnj, types.Array
            ) or rjy__pnvnj == boolean_array:
            ffv__tlba = wxx__dnss = rjy__pnvnj.dtype.name
            if wxx__dnss.startswith('datetime'):
                ffv__tlba = 'datetime'
        elif is_str_arr_type(rjy__pnvnj):
            ffv__tlba = 'unicode'
            wxx__dnss = 'object'
        elif rjy__pnvnj == binary_array_type:
            ffv__tlba = 'bytes'
            wxx__dnss = 'object'
        elif isinstance(rjy__pnvnj, DecimalArrayType):
            ffv__tlba = wxx__dnss = 'object'
        elif isinstance(rjy__pnvnj, IntegerArrayType):
            uqo__eio = rjy__pnvnj.dtype.name
            if uqo__eio.startswith('int'):
                ffv__tlba = 'Int' + uqo__eio[3:]
            elif uqo__eio.startswith('uint'):
                ffv__tlba = 'UInt' + uqo__eio[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, rjy__pnvnj))
            wxx__dnss = rjy__pnvnj.dtype.name
        elif rjy__pnvnj == datetime_date_array_type:
            ffv__tlba = 'datetime'
            wxx__dnss = 'object'
        elif isinstance(rjy__pnvnj, TimeArrayType):
            ffv__tlba = 'datetime'
            wxx__dnss = 'object'
        elif isinstance(rjy__pnvnj, (StructArrayType, ArrayItemArrayType)):
            ffv__tlba = 'object'
            wxx__dnss = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, rjy__pnvnj))
        uxr__cjp = {'name': col_name, 'field_name': col_name, 'pandas_type':
            ffv__tlba, 'numpy_type': wxx__dnss, 'metadata': nux__cvg}
        qwdxt__pau['columns'].append(uxr__cjp)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            ifim__odrl = '__index_level_0__'
            tyum__mgy = None
        else:
            ifim__odrl = '%s'
            tyum__mgy = '%s'
        qwdxt__pau['index_columns'] = [ifim__odrl]
        qwdxt__pau['columns'].append({'name': tyum__mgy, 'field_name':
            ifim__odrl, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        qwdxt__pau['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        qwdxt__pau['index_columns'] = []
    qwdxt__pau['pandas_version'] = pd.__version__
    return qwdxt__pau


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
        agf__iqpb = []
        for vem__penf in partition_cols:
            try:
                idx = df.columns.index(vem__penf)
            except ValueError as hekww__phcmz:
                raise BodoError(
                    f'Partition column {vem__penf} is not in dataframe')
            agf__iqpb.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    xgg__nrhs = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    qbunh__wnnpy = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not xgg__nrhs)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not xgg__nrhs or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and xgg__nrhs and not is_overload_true(_is_parallel)
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
        htcl__demku = df.runtime_data_types
        lulm__rrmsc = len(htcl__demku)
        nux__cvg = gen_pandas_parquet_metadata([''] * lulm__rrmsc,
            htcl__demku, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        mngpe__qxzk = nux__cvg['columns'][:lulm__rrmsc]
        nux__cvg['columns'] = nux__cvg['columns'][lulm__rrmsc:]
        mngpe__qxzk = [json.dumps(ybgq__rlklr).replace('""', '{0}') for
            ybgq__rlklr in mngpe__qxzk]
        ihfj__lttb = json.dumps(nux__cvg)
        ziec__ymxnr = '"columns": ['
        grnf__zqtv = ihfj__lttb.find(ziec__ymxnr)
        if grnf__zqtv == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        jhkev__wxtz = grnf__zqtv + len(ziec__ymxnr)
        gkccn__gwr = ihfj__lttb[:jhkev__wxtz]
        ihfj__lttb = ihfj__lttb[jhkev__wxtz:]
        aus__rqhap = len(nux__cvg['columns'])
    else:
        ihfj__lttb = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and xgg__nrhs:
        ihfj__lttb = ihfj__lttb.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            ihfj__lttb = ihfj__lttb.replace('"%s"', '%s')
    if not df.is_table_format:
        eok__uimnx = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    pszuj__hnagz = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        pszuj__hnagz += '    py_table = get_dataframe_table(df)\n'
        pszuj__hnagz += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        pszuj__hnagz += '    info_list = [{}]\n'.format(eok__uimnx)
        pszuj__hnagz += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pszuj__hnagz += '    columns_index = get_dataframe_column_names(df)\n'
        pszuj__hnagz += '    names_arr = index_to_array(columns_index)\n'
        pszuj__hnagz += '    col_names = array_to_info(names_arr)\n'
    else:
        pszuj__hnagz += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and qbunh__wnnpy:
        pszuj__hnagz += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        rvc__olwb = True
    else:
        pszuj__hnagz += '    index_col = array_to_info(np.empty(0))\n'
        rvc__olwb = False
    if df.has_runtime_cols:
        pszuj__hnagz += '    columns_lst = []\n'
        pszuj__hnagz += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            pszuj__hnagz += f'    for _ in range(len(py_table.block_{i})):\n'
            pszuj__hnagz += f"""        columns_lst.append({mngpe__qxzk[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            pszuj__hnagz += '        num_cols += 1\n'
        if aus__rqhap:
            pszuj__hnagz += "    columns_lst.append('')\n"
        pszuj__hnagz += '    columns_str = ", ".join(columns_lst)\n'
        pszuj__hnagz += ('    metadata = """' + gkccn__gwr +
            '""" + columns_str + """' + ihfj__lttb + '"""\n')
    else:
        pszuj__hnagz += '    metadata = """' + ihfj__lttb + '"""\n'
    pszuj__hnagz += '    if compression is None:\n'
    pszuj__hnagz += "        compression = 'none'\n"
    pszuj__hnagz += '    if df.index.name is not None:\n'
    pszuj__hnagz += '        name_ptr = df.index.name\n'
    pszuj__hnagz += '    else:\n'
    pszuj__hnagz += "        name_ptr = 'null'\n"
    pszuj__hnagz += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    guql__nfmnl = None
    if partition_cols:
        guql__nfmnl = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        bpvgn__mfm = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in agf__iqpb)
        if bpvgn__mfm:
            pszuj__hnagz += '    cat_info_list = [{}]\n'.format(bpvgn__mfm)
            pszuj__hnagz += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            pszuj__hnagz += '    cat_table = table\n'
        pszuj__hnagz += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        pszuj__hnagz += (
            f'    part_cols_idxs = np.array({agf__iqpb}, dtype=np.int32)\n')
        pszuj__hnagz += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        pszuj__hnagz += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        pszuj__hnagz += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        pszuj__hnagz += (
            '                            unicode_to_utf8(compression),\n')
        pszuj__hnagz += '                            _is_parallel,\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(bucket_region),\n')
        pszuj__hnagz += '                            row_group_size,\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pszuj__hnagz += '    delete_table_decref_arrays(table)\n'
        pszuj__hnagz += '    delete_info_decref_array(index_col)\n'
        pszuj__hnagz += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        pszuj__hnagz += '    delete_info_decref_array(col_names)\n'
        if bpvgn__mfm:
            pszuj__hnagz += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        pszuj__hnagz += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pszuj__hnagz += (
            '                            table, col_names, index_col,\n')
        pszuj__hnagz += '                            ' + str(rvc__olwb) + ',\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(metadata),\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(compression),\n')
        pszuj__hnagz += (
            '                            _is_parallel, 1, df.index.start,\n')
        pszuj__hnagz += (
            '                            df.index.stop, df.index.step,\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(name_ptr),\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(bucket_region),\n')
        pszuj__hnagz += '                            row_group_size,\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pszuj__hnagz += '    delete_table_decref_arrays(table)\n'
        pszuj__hnagz += '    delete_info_decref_array(index_col)\n'
        pszuj__hnagz += '    delete_info_decref_array(col_names)\n'
    else:
        pszuj__hnagz += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pszuj__hnagz += (
            '                            table, col_names, index_col,\n')
        pszuj__hnagz += '                            ' + str(rvc__olwb) + ',\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(metadata),\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(compression),\n')
        pszuj__hnagz += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(name_ptr),\n')
        pszuj__hnagz += (
            '                            unicode_to_utf8(bucket_region),\n')
        pszuj__hnagz += '                            row_group_size,\n'
        pszuj__hnagz += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pszuj__hnagz += '    delete_table_decref_arrays(table)\n'
        pszuj__hnagz += '    delete_info_decref_array(index_col)\n'
        pszuj__hnagz += '    delete_info_decref_array(col_names)\n'
    cutbe__thzim = {}
    if df.has_runtime_cols:
        asul__oav = None
    else:
        for olmsg__sani in df.columns:
            if not isinstance(olmsg__sani, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        asul__oav = pd.array(df.columns)
    exec(pszuj__hnagz, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': asul__oav,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': guql__nfmnl, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, cutbe__thzim)
    rbmhb__jmnbn = cutbe__thzim['df_to_parquet']
    return rbmhb__jmnbn


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    wwky__pmrvz = 'all_ok'
    jyo__sgolx, jqsg__ziiyk = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        hto__cmtw = 100
        if chunksize is None:
            lnslu__dxv = hto__cmtw
        else:
            lnslu__dxv = min(chunksize, hto__cmtw)
        if _is_table_create:
            df = df.iloc[:lnslu__dxv, :]
        else:
            df = df.iloc[lnslu__dxv:, :]
            if len(df) == 0:
                return wwky__pmrvz
    zkyr__ipsi = df.columns
    try:
        if jyo__sgolx == 'snowflake':
            if jqsg__ziiyk and con.count(jqsg__ziiyk) == 1:
                con = con.replace(jqsg__ziiyk, quote(jqsg__ziiyk))
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
                df.columns = [(qxh__ikawm.upper() if qxh__ikawm.islower() else
                    qxh__ikawm) for qxh__ikawm in df.columns]
            except ImportError as hekww__phcmz:
                wwky__pmrvz = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return wwky__pmrvz
        if jyo__sgolx == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            fuqrd__hvpmt = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            glqas__brxed = bodo.typeof(df)
            jhm__ncgl = {}
            for qxh__ikawm, ahos__ppbca in zip(glqas__brxed.columns,
                glqas__brxed.data):
                if df[qxh__ikawm].dtype == 'object':
                    if ahos__ppbca == datetime_date_array_type:
                        jhm__ncgl[qxh__ikawm] = sa.types.Date
                    elif ahos__ppbca in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not fuqrd__hvpmt or 
                        fuqrd__hvpmt == '0'):
                        jhm__ncgl[qxh__ikawm] = VARCHAR2(4000)
            dtype = jhm__ncgl
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as nyw__htuh:
            wwky__pmrvz = nyw__htuh.args[0]
            if jyo__sgolx == 'oracle' and 'ORA-12899' in wwky__pmrvz:
                wwky__pmrvz += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return wwky__pmrvz
    finally:
        df.columns = zkyr__ipsi


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
    pszuj__hnagz = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    pszuj__hnagz += f"    if con.startswith('iceberg'):\n"
    pszuj__hnagz += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    pszuj__hnagz += f'        if schema is None:\n'
    pszuj__hnagz += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    pszuj__hnagz += f'        if chunksize is not None:\n'
    pszuj__hnagz += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    pszuj__hnagz += f'        if index and bodo.get_rank() == 0:\n'
    pszuj__hnagz += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    pszuj__hnagz += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    pszuj__hnagz += f"""            warnings.warn('index_label is not supported for Iceberg tables.')
"""
    if df.is_table_format:
        pszuj__hnagz += f'        py_table = get_dataframe_table(df)\n'
        pszuj__hnagz += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        eok__uimnx = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        pszuj__hnagz += f'        info_list = [{eok__uimnx}]\n'
        pszuj__hnagz += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pszuj__hnagz += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        pszuj__hnagz += f'        names_arr = index_to_array(columns_index)\n'
        pszuj__hnagz += f'        col_names = array_to_info(names_arr)\n'
    else:
        pszuj__hnagz += f'        col_names = array_to_info(col_names_arr)\n'
    pszuj__hnagz += """        bodo.io.iceberg.iceberg_write(
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
    pszuj__hnagz += f'        delete_table_decref_arrays(table)\n'
    pszuj__hnagz += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        asul__oav = None
    else:
        for olmsg__sani in df.columns:
            if not isinstance(olmsg__sani, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        asul__oav = pd.array(df.columns)
    pszuj__hnagz += f'    else:\n'
    pszuj__hnagz += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    pszuj__hnagz += f"        err_msg = 'unset'\n"
    pszuj__hnagz += f'        if rank != 0:\n'
    pszuj__hnagz += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pszuj__hnagz += f'        elif rank == 0:\n'
    pszuj__hnagz += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pszuj__hnagz += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pszuj__hnagz += f'                          chunksize, dtype, method,\n'
    pszuj__hnagz += f'                          True, _is_parallel,\n'
    pszuj__hnagz += f'                      )\n'
    pszuj__hnagz += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pszuj__hnagz += f"        if_exists = 'append'\n"
    pszuj__hnagz += f"        if _is_parallel and err_msg == 'all_ok':\n"
    pszuj__hnagz += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pszuj__hnagz += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pszuj__hnagz += f'                          chunksize, dtype, method,\n'
    pszuj__hnagz += f'                          False, _is_parallel,\n'
    pszuj__hnagz += f'                      )\n'
    pszuj__hnagz += f"        if err_msg != 'all_ok':\n"
    pszuj__hnagz += f"            print('err_msg=', err_msg)\n"
    pszuj__hnagz += (
        f"            raise ValueError('error in to_sql() operation')\n")
    cutbe__thzim = {}
    exec(pszuj__hnagz, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': asul__oav, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, cutbe__thzim)
    _impl = cutbe__thzim['df_to_sql']
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
        hncj__fly = get_overload_const_str(path_or_buf)
        if hncj__fly.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        ottdh__awfel = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(ottdh__awfel), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(ottdh__awfel), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    tcooz__lfn = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    pkx__wssl = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', tcooz__lfn, pkx__wssl,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    pszuj__hnagz = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        rqmw__zhmwj = data.data.dtype.categories
        pszuj__hnagz += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        rqmw__zhmwj = data.dtype.categories
        pszuj__hnagz += '  data_values = data\n'
    hioko__oos = len(rqmw__zhmwj)
    pszuj__hnagz += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    pszuj__hnagz += '  numba.parfors.parfor.init_prange()\n'
    pszuj__hnagz += '  n = len(data_values)\n'
    for i in range(hioko__oos):
        pszuj__hnagz += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    pszuj__hnagz += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    pszuj__hnagz += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for zomxp__mny in range(hioko__oos):
        pszuj__hnagz += '          data_arr_{}[i] = 0\n'.format(zomxp__mny)
    pszuj__hnagz += '      else:\n'
    for tyoc__jnanv in range(hioko__oos):
        pszuj__hnagz += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            tyoc__jnanv)
    eok__uimnx = ', '.join(f'data_arr_{i}' for i in range(hioko__oos))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(rqmw__zhmwj[0], np.datetime64):
        rqmw__zhmwj = tuple(pd.Timestamp(qxh__ikawm) for qxh__ikawm in
            rqmw__zhmwj)
    elif isinstance(rqmw__zhmwj[0], np.timedelta64):
        rqmw__zhmwj = tuple(pd.Timedelta(qxh__ikawm) for qxh__ikawm in
            rqmw__zhmwj)
    return bodo.hiframes.dataframe_impl._gen_init_df(pszuj__hnagz,
        rqmw__zhmwj, eok__uimnx, index)


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
    for lutx__tetan in pd_unsupported:
        uzxfm__oulac = mod_name + '.' + lutx__tetan.__name__
        overload(lutx__tetan, no_unliteral=True)(create_unsupported_overload
            (uzxfm__oulac))


def _install_dataframe_unsupported():
    for ckx__nrai in dataframe_unsupported_attrs:
        xsjtn__nkzte = 'DataFrame.' + ckx__nrai
        overload_attribute(DataFrameType, ckx__nrai)(
            create_unsupported_overload(xsjtn__nkzte))
    for uzxfm__oulac in dataframe_unsupported:
        xsjtn__nkzte = 'DataFrame.' + uzxfm__oulac + '()'
        overload_method(DataFrameType, uzxfm__oulac)(
            create_unsupported_overload(xsjtn__nkzte))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
