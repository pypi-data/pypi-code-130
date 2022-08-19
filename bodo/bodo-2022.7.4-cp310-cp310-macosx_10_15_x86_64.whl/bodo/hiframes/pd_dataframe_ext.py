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
            acwnu__kex = f'{len(self.data)} columns of types {set(self.data)}'
            clisw__ecgj = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({acwnu__kex}, {self.index}, {clisw__ecgj}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {rzdcq__fqboi: i for i, rzdcq__fqboi in enumerate(self.columns)}

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
            eog__yqhll = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(ayob__iodio.unify(typingctx, esw__awgzh) if 
                ayob__iodio != esw__awgzh else ayob__iodio for ayob__iodio,
                esw__awgzh in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if eog__yqhll is not None and None not in data:
                return DataFrameType(data, eog__yqhll, self.columns, dist,
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
        return all(ayob__iodio.is_precise() for ayob__iodio in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        ocl__ftb = self.columns.index(col_name)
        qalm__hpzqu = tuple(list(self.data[:ocl__ftb]) + [new_type] + list(
            self.data[ocl__ftb + 1:]))
        return DataFrameType(qalm__hpzqu, self.index, self.columns, self.
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
        hutfm__scp = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            hutfm__scp.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, hutfm__scp)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        hutfm__scp = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, hutfm__scp)


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
        ncph__grd = 'n',
        gtq__lkjp = {'n': 5}
        ijj__pnce, xuv__eyvmo = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ncph__grd, gtq__lkjp)
        cpy__yfse = xuv__eyvmo[0]
        if not is_overload_int(cpy__yfse):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        snrqi__qczpb = df.copy()
        return snrqi__qczpb(*xuv__eyvmo).replace(pysig=ijj__pnce)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        gdayj__rkp = (df,) + args
        ncph__grd = 'df', 'method', 'min_periods'
        gtq__lkjp = {'method': 'pearson', 'min_periods': 1}
        dko__jkkb = 'method',
        ijj__pnce, xuv__eyvmo = bodo.utils.typing.fold_typing_args(func_name,
            gdayj__rkp, kws, ncph__grd, gtq__lkjp, dko__jkkb)
        pmqa__ldbj = xuv__eyvmo[2]
        if not is_overload_int(pmqa__ldbj):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        fhj__ymfr = []
        mvgow__ddg = []
        for rzdcq__fqboi, gozqv__qwo in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(gozqv__qwo.dtype):
                fhj__ymfr.append(rzdcq__fqboi)
                mvgow__ddg.append(types.Array(types.float64, 1, 'A'))
        if len(fhj__ymfr) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        mvgow__ddg = tuple(mvgow__ddg)
        fhj__ymfr = tuple(fhj__ymfr)
        index_typ = bodo.utils.typing.type_col_to_index(fhj__ymfr)
        snrqi__qczpb = DataFrameType(mvgow__ddg, index_typ, fhj__ymfr)
        return snrqi__qczpb(*xuv__eyvmo).replace(pysig=ijj__pnce)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        bdqn__qmuqw = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        pljtr__mqn = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        kwb__umi = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        ofhdd__gsma = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        cyqtp__rcmw = dict(raw=pljtr__mqn, result_type=kwb__umi)
        uzc__clzun = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', cyqtp__rcmw, uzc__clzun,
            package_name='pandas', module_name='DataFrame')
        mcp__zuz = True
        if types.unliteral(bdqn__qmuqw) == types.unicode_type:
            if not is_overload_constant_str(bdqn__qmuqw):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            mcp__zuz = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        tjt__pdz = get_overload_const_int(axis)
        if mcp__zuz and tjt__pdz != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif tjt__pdz not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        amhp__doif = []
        for arr_typ in df.data:
            sapm__ije = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            vqabc__gprqw = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(sapm__ije), types.int64), {}
                ).return_type
            amhp__doif.append(vqabc__gprqw)
        ywr__ept = types.none
        thh__flue = HeterogeneousIndexType(types.BaseTuple.from_types(tuple
            (types.literal(rzdcq__fqboi) for rzdcq__fqboi in df.columns)), None
            )
        uupt__eua = types.BaseTuple.from_types(amhp__doif)
        tkx__aim = types.Tuple([types.bool_] * len(uupt__eua))
        ttvx__owhzy = bodo.NullableTupleType(uupt__eua, tkx__aim)
        worzu__tdv = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if worzu__tdv == types.NPDatetime('ns'):
            worzu__tdv = bodo.pd_timestamp_type
        if worzu__tdv == types.NPTimedelta('ns'):
            worzu__tdv = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(uupt__eua):
            llo__ndenu = HeterogeneousSeriesType(ttvx__owhzy, thh__flue,
                worzu__tdv)
        else:
            llo__ndenu = SeriesType(uupt__eua.dtype, ttvx__owhzy, thh__flue,
                worzu__tdv)
        noxv__jmaa = llo__ndenu,
        if ofhdd__gsma is not None:
            noxv__jmaa += tuple(ofhdd__gsma.types)
        try:
            if not mcp__zuz:
                oypy__vjdb = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(bdqn__qmuqw), self.context,
                    'DataFrame.apply', axis if tjt__pdz == 1 else None)
            else:
                oypy__vjdb = get_const_func_output_type(bdqn__qmuqw,
                    noxv__jmaa, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as uhk__jidjp:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', uhk__jidjp)
                )
        if mcp__zuz:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(oypy__vjdb, (SeriesType, HeterogeneousSeriesType)
                ) and oypy__vjdb.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(oypy__vjdb, HeterogeneousSeriesType):
                qwjia__bzf, foof__gzam = oypy__vjdb.const_info
                if isinstance(oypy__vjdb.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    ynnda__xia = oypy__vjdb.data.tuple_typ.types
                elif isinstance(oypy__vjdb.data, types.Tuple):
                    ynnda__xia = oypy__vjdb.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                iba__bzccr = tuple(to_nullable_type(dtype_to_array_type(
                    qfo__xtvjj)) for qfo__xtvjj in ynnda__xia)
                kqgz__cqng = DataFrameType(iba__bzccr, df.index, foof__gzam)
            elif isinstance(oypy__vjdb, SeriesType):
                tgbyd__zjoo, foof__gzam = oypy__vjdb.const_info
                iba__bzccr = tuple(to_nullable_type(dtype_to_array_type(
                    oypy__vjdb.dtype)) for qwjia__bzf in range(tgbyd__zjoo))
                kqgz__cqng = DataFrameType(iba__bzccr, df.index, foof__gzam)
            else:
                uxcbe__zbfjs = get_udf_out_arr_type(oypy__vjdb)
                kqgz__cqng = SeriesType(uxcbe__zbfjs.dtype, uxcbe__zbfjs,
                    df.index, None)
        else:
            kqgz__cqng = oypy__vjdb
        ygdo__munys = ', '.join("{} = ''".format(ayob__iodio) for
            ayob__iodio in kws.keys())
        lbk__tltl = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {ygdo__munys}):
"""
        lbk__tltl += '    pass\n'
        nrm__sused = {}
        exec(lbk__tltl, {}, nrm__sused)
        wro__ytw = nrm__sused['apply_stub']
        ijj__pnce = numba.core.utils.pysignature(wro__ytw)
        xmc__lsr = (bdqn__qmuqw, axis, pljtr__mqn, kwb__umi, ofhdd__gsma
            ) + tuple(kws.values())
        return signature(kqgz__cqng, *xmc__lsr).replace(pysig=ijj__pnce)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ncph__grd = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        gtq__lkjp = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        dko__jkkb = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        ijj__pnce, xuv__eyvmo = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ncph__grd, gtq__lkjp, dko__jkkb)
        rfx__nyekb = xuv__eyvmo[2]
        if not is_overload_constant_str(rfx__nyekb):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        judhb__telgy = xuv__eyvmo[0]
        if not is_overload_none(judhb__telgy) and not (is_overload_int(
            judhb__telgy) or is_overload_constant_str(judhb__telgy)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(judhb__telgy):
            aram__ddtpu = get_overload_const_str(judhb__telgy)
            if aram__ddtpu not in df.columns:
                raise BodoError(f'{func_name}: {aram__ddtpu} column not found.'
                    )
        elif is_overload_int(judhb__telgy):
            wsxj__deg = get_overload_const_int(judhb__telgy)
            if wsxj__deg > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {wsxj__deg} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            judhb__telgy = df.columns[judhb__telgy]
        kpet__vpw = xuv__eyvmo[1]
        if not is_overload_none(kpet__vpw) and not (is_overload_int(
            kpet__vpw) or is_overload_constant_str(kpet__vpw)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(kpet__vpw):
            qkpb__yzga = get_overload_const_str(kpet__vpw)
            if qkpb__yzga not in df.columns:
                raise BodoError(f'{func_name}: {qkpb__yzga} column not found.')
        elif is_overload_int(kpet__vpw):
            ciaps__enrq = get_overload_const_int(kpet__vpw)
            if ciaps__enrq > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {ciaps__enrq} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            kpet__vpw = df.columns[kpet__vpw]
        qxub__hcq = xuv__eyvmo[3]
        if not is_overload_none(qxub__hcq) and not is_tuple_like_type(qxub__hcq
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        oalfm__jvfyu = xuv__eyvmo[10]
        if not is_overload_none(oalfm__jvfyu) and not is_overload_constant_str(
            oalfm__jvfyu):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        wgtf__ipmof = xuv__eyvmo[12]
        if not is_overload_bool(wgtf__ipmof):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        bdws__jsrlc = xuv__eyvmo[17]
        if not is_overload_none(bdws__jsrlc) and not is_tuple_like_type(
            bdws__jsrlc):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        suluf__avdeq = xuv__eyvmo[18]
        if not is_overload_none(suluf__avdeq) and not is_tuple_like_type(
            suluf__avdeq):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        kdn__byt = xuv__eyvmo[22]
        if not is_overload_none(kdn__byt) and not is_overload_int(kdn__byt):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        usl__kqup = xuv__eyvmo[29]
        if not is_overload_none(usl__kqup) and not is_overload_constant_str(
            usl__kqup):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        pgve__aox = xuv__eyvmo[30]
        if not is_overload_none(pgve__aox) and not is_overload_constant_str(
            pgve__aox):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        cxyz__czkh = types.List(types.mpl_line_2d_type)
        rfx__nyekb = get_overload_const_str(rfx__nyekb)
        if rfx__nyekb == 'scatter':
            if is_overload_none(judhb__telgy) and is_overload_none(kpet__vpw):
                raise BodoError(
                    f'{func_name}: {rfx__nyekb} requires an x and y column.')
            elif is_overload_none(judhb__telgy):
                raise BodoError(
                    f'{func_name}: {rfx__nyekb} x column is missing.')
            elif is_overload_none(kpet__vpw):
                raise BodoError(
                    f'{func_name}: {rfx__nyekb} y column is missing.')
            cxyz__czkh = types.mpl_path_collection_type
        elif rfx__nyekb != 'line':
            raise BodoError(f'{func_name}: {rfx__nyekb} plot is not supported.'
                )
        return signature(cxyz__czkh, *xuv__eyvmo).replace(pysig=ijj__pnce)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            bzaqh__aunoi = df.columns.index(attr)
            arr_typ = df.data[bzaqh__aunoi]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            bjaed__fepim = []
            qalm__hpzqu = []
            gem__itnsi = False
            for i, wbxf__aoz in enumerate(df.columns):
                if wbxf__aoz[0] != attr:
                    continue
                gem__itnsi = True
                bjaed__fepim.append(wbxf__aoz[1] if len(wbxf__aoz) == 2 else
                    wbxf__aoz[1:])
                qalm__hpzqu.append(df.data[i])
            if gem__itnsi:
                return DataFrameType(tuple(qalm__hpzqu), df.index, tuple(
                    bjaed__fepim))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        nkps__cmtxc = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(nkps__cmtxc)
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
        pnp__oqw = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], pnp__oqw)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    oifa__rsj = builder.module
    bnn__dembi = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    wwjai__blnv = cgutils.get_or_insert_function(oifa__rsj, bnn__dembi,
        name='.dtor.df.{}'.format(df_type))
    if not wwjai__blnv.is_declaration:
        return wwjai__blnv
    wwjai__blnv.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(wwjai__blnv.append_basic_block())
    jxz__rrw = wwjai__blnv.args[0]
    aqz__pyl = context.get_value_type(payload_type).as_pointer()
    enf__mjo = builder.bitcast(jxz__rrw, aqz__pyl)
    payload = context.make_helper(builder, payload_type, ref=enf__mjo)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        taedu__ekh = context.get_python_api(builder)
        khrf__gffw = taedu__ekh.gil_ensure()
        taedu__ekh.decref(payload.parent)
        taedu__ekh.gil_release(khrf__gffw)
    builder.ret_void()
    return wwjai__blnv


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    ubcdb__kqoji = cgutils.create_struct_proxy(payload_type)(context, builder)
    ubcdb__kqoji.data = data_tup
    ubcdb__kqoji.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        ubcdb__kqoji.columns = colnames
    yclru__xmj = context.get_value_type(payload_type)
    edr__jqwl = context.get_abi_sizeof(yclru__xmj)
    agsse__nekmz = define_df_dtor(context, builder, df_type, payload_type)
    hzk__apow = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, edr__jqwl), agsse__nekmz)
    mks__xhwg = context.nrt.meminfo_data(builder, hzk__apow)
    bqpag__mcbt = builder.bitcast(mks__xhwg, yclru__xmj.as_pointer())
    fql__clkn = cgutils.create_struct_proxy(df_type)(context, builder)
    fql__clkn.meminfo = hzk__apow
    if parent is None:
        fql__clkn.parent = cgutils.get_null_value(fql__clkn.parent.type)
    else:
        fql__clkn.parent = parent
        ubcdb__kqoji.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            taedu__ekh = context.get_python_api(builder)
            khrf__gffw = taedu__ekh.gil_ensure()
            taedu__ekh.incref(parent)
            taedu__ekh.gil_release(khrf__gffw)
    builder.store(ubcdb__kqoji._getvalue(), bqpag__mcbt)
    return fql__clkn._getvalue()


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
        tul__tysm = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        tul__tysm = [qfo__xtvjj for qfo__xtvjj in data_typ.dtype.arr_types]
    thl__nqon = DataFrameType(tuple(tul__tysm + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        mxqa__acf = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return mxqa__acf
    sig = signature(thl__nqon, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    tgbyd__zjoo = len(data_tup_typ.types)
    if tgbyd__zjoo == 0:
        column_names = ()
    zgyt__bhj = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(zgyt__bhj, ColNamesMetaType) and isinstance(zgyt__bhj
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = zgyt__bhj.meta
    if tgbyd__zjoo == 1 and isinstance(data_tup_typ.types[0], TableType):
        tgbyd__zjoo = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == tgbyd__zjoo, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    rmn__swp = data_tup_typ.types
    if tgbyd__zjoo != 0 and isinstance(data_tup_typ.types[0], TableType):
        rmn__swp = data_tup_typ.types[0].arr_types
        is_table_format = True
    thl__nqon = DataFrameType(rmn__swp, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            qal__ikr = cgutils.create_struct_proxy(thl__nqon.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = qal__ikr.parent
        mxqa__acf = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return mxqa__acf
    sig = signature(thl__nqon, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        fql__clkn = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, fql__clkn.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        ubcdb__kqoji = get_dataframe_payload(context, builder, df_typ, args[0])
        kegn__opv = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[kegn__opv]
        if df_typ.is_table_format:
            qal__ikr = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(ubcdb__kqoji.data, 0))
            gieip__avga = df_typ.table_type.type_to_blk[arr_typ]
            ccn__gfdi = getattr(qal__ikr, f'block_{gieip__avga}')
            lerbe__wfgv = ListInstance(context, builder, types.List(arr_typ
                ), ccn__gfdi)
            eyo__wnt = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[kegn__opv])
            pnp__oqw = lerbe__wfgv.getitem(eyo__wnt)
        else:
            pnp__oqw = builder.extract_value(ubcdb__kqoji.data, kegn__opv)
        slds__mkpwp = cgutils.alloca_once_value(builder, pnp__oqw)
        mrawa__jrc = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, slds__mkpwp, mrawa__jrc)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    hzk__apow = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, hzk__apow)
    aqz__pyl = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, aqz__pyl)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    thl__nqon = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        thl__nqon = types.Tuple([TableType(df_typ.data)])
    sig = signature(thl__nqon, df_typ)

    def codegen(context, builder, signature, args):
        ubcdb__kqoji = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            ubcdb__kqoji.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        ubcdb__kqoji = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index,
            ubcdb__kqoji.index)
    thl__nqon = df_typ.index
    sig = signature(thl__nqon, df_typ)
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
        snrqi__qczpb = df.data[i]
        return snrqi__qczpb(*args)


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
        ubcdb__kqoji = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(ubcdb__kqoji.data, 0))
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
    orx__fhmv = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{orx__fhmv})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        snrqi__qczpb = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return snrqi__qczpb(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        ubcdb__kqoji = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, ubcdb__kqoji.columns)
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
    uupt__eua = self.typemap[data_tup.name]
    if any(is_tuple_like_type(qfo__xtvjj) for qfo__xtvjj in uupt__eua.types):
        return None
    if equiv_set.has_shape(data_tup):
        uyxet__qhs = equiv_set.get_shape(data_tup)
        if len(uyxet__qhs) > 1:
            equiv_set.insert_equiv(*uyxet__qhs)
        if len(uyxet__qhs) > 0:
            thh__flue = self.typemap[index.name]
            if not isinstance(thh__flue, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(uyxet__qhs[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(uyxet__qhs[0], len(
                uyxet__qhs)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    uyb__upj = args[0]
    data_types = self.typemap[uyb__upj.name].data
    if any(is_tuple_like_type(qfo__xtvjj) for qfo__xtvjj in data_types):
        return None
    if equiv_set.has_shape(uyb__upj):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            uyb__upj)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    uyb__upj = args[0]
    thh__flue = self.typemap[uyb__upj.name].index
    if isinstance(thh__flue, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(uyb__upj):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            uyb__upj)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    uyb__upj = args[0]
    if equiv_set.has_shape(uyb__upj):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            uyb__upj), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    uyb__upj = args[0]
    if equiv_set.has_shape(uyb__upj):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            uyb__upj)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    kegn__opv = get_overload_const_int(c_ind_typ)
    if df_typ.data[kegn__opv] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        zooj__ieqre, qwjia__bzf, tels__bwae = args
        ubcdb__kqoji = get_dataframe_payload(context, builder, df_typ,
            zooj__ieqre)
        if df_typ.is_table_format:
            qal__ikr = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(ubcdb__kqoji.data, 0))
            gieip__avga = df_typ.table_type.type_to_blk[arr_typ]
            ccn__gfdi = getattr(qal__ikr, f'block_{gieip__avga}')
            lerbe__wfgv = ListInstance(context, builder, types.List(arr_typ
                ), ccn__gfdi)
            eyo__wnt = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[kegn__opv])
            lerbe__wfgv.setitem(eyo__wnt, tels__bwae, True)
        else:
            pnp__oqw = builder.extract_value(ubcdb__kqoji.data, kegn__opv)
            context.nrt.decref(builder, df_typ.data[kegn__opv], pnp__oqw)
            ubcdb__kqoji.data = builder.insert_value(ubcdb__kqoji.data,
                tels__bwae, kegn__opv)
            context.nrt.incref(builder, arr_typ, tels__bwae)
        fql__clkn = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=zooj__ieqre)
        payload_type = DataFramePayloadType(df_typ)
        enf__mjo = context.nrt.meminfo_data(builder, fql__clkn.meminfo)
        aqz__pyl = context.get_value_type(payload_type).as_pointer()
        enf__mjo = builder.bitcast(enf__mjo, aqz__pyl)
        builder.store(ubcdb__kqoji._getvalue(), enf__mjo)
        return impl_ret_borrowed(context, builder, df_typ, zooj__ieqre)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        vlrce__ifv = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        fkh__ffz = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=vlrce__ifv)
        pqdqz__jys = get_dataframe_payload(context, builder, df_typ, vlrce__ifv
            )
        fql__clkn = construct_dataframe(context, builder, signature.
            return_type, pqdqz__jys.data, index_val, fkh__ffz.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), pqdqz__jys.data)
        return fql__clkn
    thl__nqon = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(thl__nqon, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    tgbyd__zjoo = len(df_type.columns)
    ogbh__rqh = tgbyd__zjoo
    luwcn__vggdv = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    okzzf__xtcg = col_name not in df_type.columns
    kegn__opv = tgbyd__zjoo
    if okzzf__xtcg:
        luwcn__vggdv += arr_type,
        column_names += col_name,
        ogbh__rqh += 1
    else:
        kegn__opv = df_type.columns.index(col_name)
        luwcn__vggdv = tuple(arr_type if i == kegn__opv else luwcn__vggdv[i
            ] for i in range(tgbyd__zjoo))

    def codegen(context, builder, signature, args):
        zooj__ieqre, qwjia__bzf, tels__bwae = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, zooj__ieqre)
        vftxx__ydblv = cgutils.create_struct_proxy(df_type)(context,
            builder, value=zooj__ieqre)
        if df_type.is_table_format:
            ycgv__uri = df_type.table_type
            ohda__wawu = builder.extract_value(in_dataframe_payload.data, 0)
            yxznx__plv = TableType(luwcn__vggdv)
            zxbie__qelud = set_table_data_codegen(context, builder,
                ycgv__uri, ohda__wawu, yxznx__plv, arr_type, tels__bwae,
                kegn__opv, okzzf__xtcg)
            data_tup = context.make_tuple(builder, types.Tuple([yxznx__plv]
                ), [zxbie__qelud])
        else:
            rmn__swp = [(builder.extract_value(in_dataframe_payload.data, i
                ) if i != kegn__opv else tels__bwae) for i in range(
                tgbyd__zjoo)]
            if okzzf__xtcg:
                rmn__swp.append(tels__bwae)
            for uyb__upj, qze__amct in zip(rmn__swp, luwcn__vggdv):
                context.nrt.incref(builder, qze__amct, uyb__upj)
            data_tup = context.make_tuple(builder, types.Tuple(luwcn__vggdv
                ), rmn__swp)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        qar__rze = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, vftxx__ydblv.parent, None)
        if not okzzf__xtcg and arr_type == df_type.data[kegn__opv]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            enf__mjo = context.nrt.meminfo_data(builder, vftxx__ydblv.meminfo)
            aqz__pyl = context.get_value_type(payload_type).as_pointer()
            enf__mjo = builder.bitcast(enf__mjo, aqz__pyl)
            rpuir__xtc = get_dataframe_payload(context, builder, df_type,
                qar__rze)
            builder.store(rpuir__xtc._getvalue(), enf__mjo)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, yxznx__plv, builder.
                    extract_value(data_tup, 0))
            else:
                for uyb__upj, qze__amct in zip(rmn__swp, luwcn__vggdv):
                    context.nrt.incref(builder, qze__amct, uyb__upj)
        has_parent = cgutils.is_not_null(builder, vftxx__ydblv.parent)
        with builder.if_then(has_parent):
            taedu__ekh = context.get_python_api(builder)
            khrf__gffw = taedu__ekh.gil_ensure()
            xyih__lfv = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, tels__bwae)
            rzdcq__fqboi = numba.core.pythonapi._BoxContext(context,
                builder, taedu__ekh, xyih__lfv)
            gxl__fnt = rzdcq__fqboi.pyapi.from_native_value(arr_type,
                tels__bwae, rzdcq__fqboi.env_manager)
            if isinstance(col_name, str):
                zkabi__kql = context.insert_const_string(builder.module,
                    col_name)
                accd__gmbxy = taedu__ekh.string_from_string(zkabi__kql)
            else:
                assert isinstance(col_name, int)
                accd__gmbxy = taedu__ekh.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            taedu__ekh.object_setitem(vftxx__ydblv.parent, accd__gmbxy,
                gxl__fnt)
            taedu__ekh.decref(gxl__fnt)
            taedu__ekh.decref(accd__gmbxy)
            taedu__ekh.gil_release(khrf__gffw)
        return qar__rze
    thl__nqon = DataFrameType(luwcn__vggdv, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(thl__nqon, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    tgbyd__zjoo = len(pyval.columns)
    rmn__swp = []
    for i in range(tgbyd__zjoo):
        yftos__fbwp = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            gxl__fnt = yftos__fbwp.array
        else:
            gxl__fnt = yftos__fbwp.values
        rmn__swp.append(gxl__fnt)
    rmn__swp = tuple(rmn__swp)
    if df_type.is_table_format:
        qal__ikr = context.get_constant_generic(builder, df_type.table_type,
            Table(rmn__swp))
        data_tup = lir.Constant.literal_struct([qal__ikr])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], wbxf__aoz) for i,
            wbxf__aoz in enumerate(rmn__swp)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    wjht__sqf = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, wjht__sqf])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    tkw__gmw = context.get_constant(types.int64, -1)
    dyx__cqo = context.get_constant_null(types.voidptr)
    hzk__apow = lir.Constant.literal_struct([tkw__gmw, dyx__cqo, dyx__cqo,
        payload, tkw__gmw])
    hzk__apow = cgutils.global_constant(builder, '.const.meminfo', hzk__apow
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([hzk__apow, wjht__sqf])


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
        eog__yqhll = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        eog__yqhll = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, eog__yqhll)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        qalm__hpzqu = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                qalm__hpzqu)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), qalm__hpzqu)
    elif not fromty.is_table_format and toty.is_table_format:
        qalm__hpzqu = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        qalm__hpzqu = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        qalm__hpzqu = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        qalm__hpzqu = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, qalm__hpzqu,
        eog__yqhll, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    bwro__aidf = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        ruyb__fwmub = get_index_data_arr_types(toty.index)[0]
        tly__ola = bodo.utils.transform.get_type_alloc_counts(ruyb__fwmub) - 1
        mus__fbxri = ', '.join('0' for qwjia__bzf in range(tly__ola))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(mus__fbxri, ', ' if tly__ola == 1 else ''))
        bwro__aidf['index_arr_type'] = ruyb__fwmub
    kcs__mxrgo = []
    for i, arr_typ in enumerate(toty.data):
        tly__ola = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        mus__fbxri = ', '.join('0' for qwjia__bzf in range(tly__ola))
        dxiqh__uufg = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, mus__fbxri, ', ' if tly__ola == 1 else ''))
        kcs__mxrgo.append(dxiqh__uufg)
        bwro__aidf[f'arr_type{i}'] = arr_typ
    kcs__mxrgo = ', '.join(kcs__mxrgo)
    lbk__tltl = 'def impl():\n'
    oui__dab = bodo.hiframes.dataframe_impl._gen_init_df(lbk__tltl, toty.
        columns, kcs__mxrgo, index, bwro__aidf)
    df = context.compile_internal(builder, oui__dab, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    bfdj__yxf = toty.table_type
    qal__ikr = cgutils.create_struct_proxy(bfdj__yxf)(context, builder)
    qal__ikr.parent = in_dataframe_payload.parent
    for qfo__xtvjj, gieip__avga in bfdj__yxf.type_to_blk.items():
        ntdrd__ymbx = context.get_constant(types.int64, len(bfdj__yxf.
            block_to_arr_ind[gieip__avga]))
        qwjia__bzf, pxdbv__tlbin = ListInstance.allocate_ex(context,
            builder, types.List(qfo__xtvjj), ntdrd__ymbx)
        pxdbv__tlbin.size = ntdrd__ymbx
        setattr(qal__ikr, f'block_{gieip__avga}', pxdbv__tlbin.value)
    for i, qfo__xtvjj in enumerate(fromty.data):
        eoi__vllbi = toty.data[i]
        if qfo__xtvjj != eoi__vllbi:
            evxqb__xxot = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*evxqb__xxot)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        pnp__oqw = builder.extract_value(in_dataframe_payload.data, i)
        if qfo__xtvjj != eoi__vllbi:
            tuho__tzwpa = context.cast(builder, pnp__oqw, qfo__xtvjj,
                eoi__vllbi)
            euvp__fhp = False
        else:
            tuho__tzwpa = pnp__oqw
            euvp__fhp = True
        gieip__avga = bfdj__yxf.type_to_blk[qfo__xtvjj]
        ccn__gfdi = getattr(qal__ikr, f'block_{gieip__avga}')
        lerbe__wfgv = ListInstance(context, builder, types.List(qfo__xtvjj),
            ccn__gfdi)
        eyo__wnt = context.get_constant(types.int64, bfdj__yxf.block_offsets[i]
            )
        lerbe__wfgv.setitem(eyo__wnt, tuho__tzwpa, euvp__fhp)
    data_tup = context.make_tuple(builder, types.Tuple([bfdj__yxf]), [
        qal__ikr._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    rmn__swp = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            evxqb__xxot = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*evxqb__xxot)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            pnp__oqw = builder.extract_value(in_dataframe_payload.data, i)
            tuho__tzwpa = context.cast(builder, pnp__oqw, fromty.data[i],
                toty.data[i])
            euvp__fhp = False
        else:
            tuho__tzwpa = builder.extract_value(in_dataframe_payload.data, i)
            euvp__fhp = True
        if euvp__fhp:
            context.nrt.incref(builder, toty.data[i], tuho__tzwpa)
        rmn__swp.append(tuho__tzwpa)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), rmn__swp)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    ycgv__uri = fromty.table_type
    ohda__wawu = cgutils.create_struct_proxy(ycgv__uri)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    yxznx__plv = toty.table_type
    zxbie__qelud = cgutils.create_struct_proxy(yxznx__plv)(context, builder)
    zxbie__qelud.parent = in_dataframe_payload.parent
    for qfo__xtvjj, gieip__avga in yxznx__plv.type_to_blk.items():
        ntdrd__ymbx = context.get_constant(types.int64, len(yxznx__plv.
            block_to_arr_ind[gieip__avga]))
        qwjia__bzf, pxdbv__tlbin = ListInstance.allocate_ex(context,
            builder, types.List(qfo__xtvjj), ntdrd__ymbx)
        pxdbv__tlbin.size = ntdrd__ymbx
        setattr(zxbie__qelud, f'block_{gieip__avga}', pxdbv__tlbin.value)
    for i in range(len(fromty.data)):
        ztls__vgw = fromty.data[i]
        eoi__vllbi = toty.data[i]
        if ztls__vgw != eoi__vllbi:
            evxqb__xxot = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*evxqb__xxot)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        xqwf__sxesi = ycgv__uri.type_to_blk[ztls__vgw]
        jkcsl__ghv = getattr(ohda__wawu, f'block_{xqwf__sxesi}')
        ioo__dnd = ListInstance(context, builder, types.List(ztls__vgw),
            jkcsl__ghv)
        lkdn__bknt = context.get_constant(types.int64, ycgv__uri.
            block_offsets[i])
        pnp__oqw = ioo__dnd.getitem(lkdn__bknt)
        if ztls__vgw != eoi__vllbi:
            tuho__tzwpa = context.cast(builder, pnp__oqw, ztls__vgw, eoi__vllbi
                )
            euvp__fhp = False
        else:
            tuho__tzwpa = pnp__oqw
            euvp__fhp = True
        kmafi__rcro = yxznx__plv.type_to_blk[qfo__xtvjj]
        pxdbv__tlbin = getattr(zxbie__qelud, f'block_{kmafi__rcro}')
        ueeai__abj = ListInstance(context, builder, types.List(eoi__vllbi),
            pxdbv__tlbin)
        qzlo__pff = context.get_constant(types.int64, yxznx__plv.
            block_offsets[i])
        ueeai__abj.setitem(qzlo__pff, tuho__tzwpa, euvp__fhp)
    data_tup = context.make_tuple(builder, types.Tuple([yxznx__plv]), [
        zxbie__qelud._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    bfdj__yxf = fromty.table_type
    qal__ikr = cgutils.create_struct_proxy(bfdj__yxf)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    rmn__swp = []
    for i, qfo__xtvjj in enumerate(toty.data):
        ztls__vgw = fromty.data[i]
        if qfo__xtvjj != ztls__vgw:
            evxqb__xxot = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*evxqb__xxot)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        gieip__avga = bfdj__yxf.type_to_blk[ztls__vgw]
        ccn__gfdi = getattr(qal__ikr, f'block_{gieip__avga}')
        lerbe__wfgv = ListInstance(context, builder, types.List(ztls__vgw),
            ccn__gfdi)
        eyo__wnt = context.get_constant(types.int64, bfdj__yxf.block_offsets[i]
            )
        pnp__oqw = lerbe__wfgv.getitem(eyo__wnt)
        if qfo__xtvjj != ztls__vgw:
            tuho__tzwpa = context.cast(builder, pnp__oqw, ztls__vgw, qfo__xtvjj
                )
        else:
            tuho__tzwpa = pnp__oqw
            context.nrt.incref(builder, qfo__xtvjj, tuho__tzwpa)
        rmn__swp.append(tuho__tzwpa)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), rmn__swp)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    odfoc__gqz, kcs__mxrgo, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    xpmh__zfey = ColNamesMetaType(tuple(odfoc__gqz))
    lbk__tltl = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    lbk__tltl += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(kcs__mxrgo, index_arg))
    nrm__sused = {}
    exec(lbk__tltl, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': xpmh__zfey}, nrm__sused)
    kovhg__wny = nrm__sused['_init_df']
    return kovhg__wny


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    thl__nqon = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(thl__nqon, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    thl__nqon = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(thl__nqon, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    rrtf__enid = ''
    if not is_overload_none(dtype):
        rrtf__enid = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        tgbyd__zjoo = (len(data.types) - 1) // 2
        qta__mic = [qfo__xtvjj.literal_value for qfo__xtvjj in data.types[1
            :tgbyd__zjoo + 1]]
        data_val_types = dict(zip(qta__mic, data.types[tgbyd__zjoo + 1:]))
        rmn__swp = ['data[{}]'.format(i) for i in range(tgbyd__zjoo + 1, 2 *
            tgbyd__zjoo + 1)]
        data_dict = dict(zip(qta__mic, rmn__swp))
        if is_overload_none(index):
            for i, qfo__xtvjj in enumerate(data.types[tgbyd__zjoo + 1:]):
                if isinstance(qfo__xtvjj, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(tgbyd__zjoo + 1 + i))
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
        outtg__gnsvc = '.copy()' if copy else ''
        hzfqy__elsp = get_overload_const_list(columns)
        tgbyd__zjoo = len(hzfqy__elsp)
        data_val_types = {rzdcq__fqboi: data.copy(ndim=1) for rzdcq__fqboi in
            hzfqy__elsp}
        rmn__swp = ['data[:,{}]{}'.format(i, outtg__gnsvc) for i in range(
            tgbyd__zjoo)]
        data_dict = dict(zip(hzfqy__elsp, rmn__swp))
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
    kcs__mxrgo = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[rzdcq__fqboi], df_len, rrtf__enid) for
        rzdcq__fqboi in col_names))
    if len(col_names) == 0:
        kcs__mxrgo = '()'
    return col_names, kcs__mxrgo, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for rzdcq__fqboi in col_names:
        if rzdcq__fqboi in data_dict and is_iterable_type(data_val_types[
            rzdcq__fqboi]):
            df_len = 'len({})'.format(data_dict[rzdcq__fqboi])
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
    if all(rzdcq__fqboi in data_dict for rzdcq__fqboi in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    xzg__zkqwt = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for rzdcq__fqboi in col_names:
        if rzdcq__fqboi not in data_dict:
            data_dict[rzdcq__fqboi] = xzg__zkqwt


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
            qfo__xtvjj = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(qfo__xtvjj)
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
        qrps__dwk = idx.literal_value
        if isinstance(qrps__dwk, int):
            snrqi__qczpb = tup.types[qrps__dwk]
        elif isinstance(qrps__dwk, slice):
            snrqi__qczpb = types.BaseTuple.from_types(tup.types[qrps__dwk])
        return signature(snrqi__qczpb, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    ffmc__hmt, idx = sig.args
    idx = idx.literal_value
    tup, qwjia__bzf = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(ffmc__hmt)
        if not 0 <= idx < len(ffmc__hmt):
            raise IndexError('cannot index at %d in %s' % (idx, ffmc__hmt))
        nfh__zde = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        gabw__dkxf = cgutils.unpack_tuple(builder, tup)[idx]
        nfh__zde = context.make_tuple(builder, sig.return_type, gabw__dkxf)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, nfh__zde)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, ssjoi__cdi, suffix_x,
            suffix_y, is_join, indicator, qwjia__bzf, qwjia__bzf) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        auv__idurz = {rzdcq__fqboi: i for i, rzdcq__fqboi in enumerate(left_on)
            }
        dimdy__dls = {rzdcq__fqboi: i for i, rzdcq__fqboi in enumerate(
            right_on)}
        wcr__cwd = set(left_on) & set(right_on)
        ortr__mmxin = set(left_df.columns) & set(right_df.columns)
        ofuil__oadtt = ortr__mmxin - wcr__cwd
        qnuwf__tgrx = '$_bodo_index_' in left_on
        zcqd__kdshh = '$_bodo_index_' in right_on
        how = get_overload_const_str(ssjoi__cdi)
        behop__qyl = how in {'left', 'outer'}
        rbhix__rmwc = how in {'right', 'outer'}
        columns = []
        data = []
        if qnuwf__tgrx:
            cjq__aho = bodo.utils.typing.get_index_data_arr_types(left_df.index
                )[0]
        else:
            cjq__aho = left_df.data[left_df.column_index[left_on[0]]]
        if zcqd__kdshh:
            tpx__vzwvd = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            tpx__vzwvd = right_df.data[right_df.column_index[right_on[0]]]
        if qnuwf__tgrx and not zcqd__kdshh and not is_join.literal_value:
            ucm__xkcgw = right_on[0]
            if ucm__xkcgw in left_df.column_index:
                columns.append(ucm__xkcgw)
                if (tpx__vzwvd == bodo.dict_str_arr_type and cjq__aho ==
                    bodo.string_array_type):
                    rceh__ygfik = bodo.string_array_type
                else:
                    rceh__ygfik = tpx__vzwvd
                data.append(rceh__ygfik)
        if zcqd__kdshh and not qnuwf__tgrx and not is_join.literal_value:
            weut__jzy = left_on[0]
            if weut__jzy in right_df.column_index:
                columns.append(weut__jzy)
                if (cjq__aho == bodo.dict_str_arr_type and tpx__vzwvd ==
                    bodo.string_array_type):
                    rceh__ygfik = bodo.string_array_type
                else:
                    rceh__ygfik = cjq__aho
                data.append(rceh__ygfik)
        for ztls__vgw, yftos__fbwp in zip(left_df.data, left_df.columns):
            columns.append(str(yftos__fbwp) + suffix_x.literal_value if 
                yftos__fbwp in ofuil__oadtt else yftos__fbwp)
            if yftos__fbwp in wcr__cwd:
                if ztls__vgw == bodo.dict_str_arr_type:
                    ztls__vgw = right_df.data[right_df.column_index[
                        yftos__fbwp]]
                data.append(ztls__vgw)
            else:
                if (ztls__vgw == bodo.dict_str_arr_type and yftos__fbwp in
                    auv__idurz):
                    if zcqd__kdshh:
                        ztls__vgw = tpx__vzwvd
                    else:
                        ifps__puz = auv__idurz[yftos__fbwp]
                        bdya__rwo = right_on[ifps__puz]
                        ztls__vgw = right_df.data[right_df.column_index[
                            bdya__rwo]]
                if rbhix__rmwc:
                    ztls__vgw = to_nullable_type(ztls__vgw)
                data.append(ztls__vgw)
        for ztls__vgw, yftos__fbwp in zip(right_df.data, right_df.columns):
            if yftos__fbwp not in wcr__cwd:
                columns.append(str(yftos__fbwp) + suffix_y.literal_value if
                    yftos__fbwp in ofuil__oadtt else yftos__fbwp)
                if (ztls__vgw == bodo.dict_str_arr_type and yftos__fbwp in
                    dimdy__dls):
                    if qnuwf__tgrx:
                        ztls__vgw = cjq__aho
                    else:
                        ifps__puz = dimdy__dls[yftos__fbwp]
                        bxz__yhrei = left_on[ifps__puz]
                        ztls__vgw = left_df.data[left_df.column_index[
                            bxz__yhrei]]
                if behop__qyl:
                    ztls__vgw = to_nullable_type(ztls__vgw)
                data.append(ztls__vgw)
        bwpts__viqgg = get_overload_const_bool(indicator)
        if bwpts__viqgg:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        lwlom__ezinj = False
        if qnuwf__tgrx and zcqd__kdshh and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            lwlom__ezinj = True
        elif qnuwf__tgrx and not zcqd__kdshh:
            index_typ = right_df.index
            lwlom__ezinj = True
        elif zcqd__kdshh and not qnuwf__tgrx:
            index_typ = left_df.index
            lwlom__ezinj = True
        if lwlom__ezinj and isinstance(index_typ, bodo.hiframes.
            pd_index_ext.RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        izma__vzn = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(izma__vzn, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    fql__clkn = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return fql__clkn._getvalue()


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
    cyqtp__rcmw = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    gtq__lkjp = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', cyqtp__rcmw, gtq__lkjp,
        package_name='pandas', module_name='General')
    lbk__tltl = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        bfij__hhtt = 0
        kcs__mxrgo = []
        names = []
        for i, sep__vaeza in enumerate(objs.types):
            assert isinstance(sep__vaeza, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(sep__vaeza, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                sep__vaeza, 'pandas.concat()')
            if isinstance(sep__vaeza, SeriesType):
                names.append(str(bfij__hhtt))
                bfij__hhtt += 1
                kcs__mxrgo.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(sep__vaeza.columns)
                for zao__picpy in range(len(sep__vaeza.data)):
                    kcs__mxrgo.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, zao__picpy))
        return bodo.hiframes.dataframe_impl._gen_init_df(lbk__tltl, names,
            ', '.join(kcs__mxrgo), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(qfo__xtvjj, DataFrameType) for qfo__xtvjj in
            objs.types)
        nivfk__dmy = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            nivfk__dmy.extend(df.columns)
        nivfk__dmy = list(dict.fromkeys(nivfk__dmy).keys())
        tul__tysm = {}
        for bfij__hhtt, rzdcq__fqboi in enumerate(nivfk__dmy):
            for i, df in enumerate(objs.types):
                if rzdcq__fqboi in df.column_index:
                    tul__tysm[f'arr_typ{bfij__hhtt}'] = df.data[df.
                        column_index[rzdcq__fqboi]]
                    break
        assert len(tul__tysm) == len(nivfk__dmy)
        bau__pff = []
        for bfij__hhtt, rzdcq__fqboi in enumerate(nivfk__dmy):
            args = []
            for i, df in enumerate(objs.types):
                if rzdcq__fqboi in df.column_index:
                    kegn__opv = df.column_index[rzdcq__fqboi]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, kegn__opv))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, bfij__hhtt))
            lbk__tltl += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(bfij__hhtt, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(lbk__tltl,
            nivfk__dmy, ', '.join('A{}'.format(i) for i in range(len(
            nivfk__dmy))), index, tul__tysm)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(qfo__xtvjj, SeriesType) for qfo__xtvjj in
            objs.types)
        lbk__tltl += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            lbk__tltl += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            lbk__tltl += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        lbk__tltl += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        nrm__sused = {}
        exec(lbk__tltl, {'bodo': bodo, 'np': np, 'numba': numba}, nrm__sused)
        return nrm__sused['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for bfij__hhtt, rzdcq__fqboi in enumerate(df_type.columns):
            lbk__tltl += '  arrs{} = []\n'.format(bfij__hhtt)
            lbk__tltl += '  for i in range(len(objs)):\n'
            lbk__tltl += '    df = objs[i]\n'
            lbk__tltl += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(bfij__hhtt))
            lbk__tltl += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(bfij__hhtt))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            lbk__tltl += '  arrs_index = []\n'
            lbk__tltl += '  for i in range(len(objs)):\n'
            lbk__tltl += '    df = objs[i]\n'
            lbk__tltl += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(lbk__tltl, df_type
            .columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        lbk__tltl += '  arrs = []\n'
        lbk__tltl += '  for i in range(len(objs)):\n'
        lbk__tltl += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        lbk__tltl += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            lbk__tltl += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            lbk__tltl += '  arrs_index = []\n'
            lbk__tltl += '  for i in range(len(objs)):\n'
            lbk__tltl += '    S = objs[i]\n'
            lbk__tltl += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            lbk__tltl += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        lbk__tltl += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        nrm__sused = {}
        exec(lbk__tltl, {'bodo': bodo, 'np': np, 'numba': numba}, nrm__sused)
        return nrm__sused['impl']
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
        thl__nqon = df.copy(index=index)
        return signature(thl__nqon, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    ala__klah = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ala__klah._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    cyqtp__rcmw = dict(index=index, name=name)
    gtq__lkjp = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', cyqtp__rcmw, gtq__lkjp,
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
        tul__tysm = (types.Array(types.int64, 1, 'C'),) + df.data
        aedk__yysw = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, tul__tysm)
        return signature(aedk__yysw, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    ala__klah = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ala__klah._getvalue()


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
    ala__klah = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ala__klah._getvalue()


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
    ala__klah = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ala__klah._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    war__awqzt = get_overload_const_bool(check_duplicates)
    vzh__ouc = not get_overload_const_bool(is_already_shuffled)
    pnq__her = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    qkey__wndfc = len(value_names) > 1
    vlhtm__mpo = None
    xjc__vhwtm = None
    jda__ipn = None
    mvo__iog = None
    qsal__wejv = isinstance(values_tup, types.UniTuple)
    if qsal__wejv:
        errmm__ufr = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        errmm__ufr = [to_str_arr_if_dict_array(to_nullable_type(qze__amct)) for
            qze__amct in values_tup]
    lbk__tltl = 'def impl(\n'
    lbk__tltl += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    lbk__tltl += '):\n'
    lbk__tltl += "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n"
    if vzh__ouc:
        lbk__tltl += '    if parallel:\n'
        lbk__tltl += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        xcshx__gqg = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        lbk__tltl += f'        info_list = [{xcshx__gqg}]\n'
        lbk__tltl += '        cpp_table = arr_info_list_to_table(info_list)\n'
        lbk__tltl += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        qtpx__xdq = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        fxzq__ame = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        kiobf__ptwm = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        lbk__tltl += f'        index_tup = ({qtpx__xdq},)\n'
        lbk__tltl += f'        columns_tup = ({fxzq__ame},)\n'
        lbk__tltl += f'        values_tup = ({kiobf__ptwm},)\n'
        lbk__tltl += '        delete_table(cpp_table)\n'
        lbk__tltl += '        delete_table(out_cpp_table)\n'
        lbk__tltl += '        ev_shuffle.finalize()\n'
    lbk__tltl += '    columns_arr = columns_tup[0]\n'
    if qsal__wejv:
        lbk__tltl += '    values_arrs = [arr for arr in values_tup]\n'
    lbk__tltl += (
        "    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)\n"
        )
    lbk__tltl += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    lbk__tltl += '        index_tup\n'
    lbk__tltl += '    )\n'
    lbk__tltl += '    n_rows = len(unique_index_arr_tup[0])\n'
    lbk__tltl += '    num_values_arrays = len(values_tup)\n'
    lbk__tltl += '    n_unique_pivots = len(pivot_values)\n'
    if qsal__wejv:
        lbk__tltl += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        lbk__tltl += '    n_cols = n_unique_pivots\n'
    lbk__tltl += '    col_map = {}\n'
    lbk__tltl += '    for i in range(n_unique_pivots):\n'
    lbk__tltl += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    lbk__tltl += '            raise ValueError(\n'
    lbk__tltl += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    lbk__tltl += '            )\n'
    lbk__tltl += '        col_map[pivot_values[i]] = i\n'
    lbk__tltl += '    ev_unique.finalize()\n'
    lbk__tltl += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    pthvz__lar = False
    for i, dajys__fblku in enumerate(errmm__ufr):
        if is_str_arr_type(dajys__fblku):
            pthvz__lar = True
            lbk__tltl += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            lbk__tltl += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if pthvz__lar:
        if war__awqzt:
            lbk__tltl += '    nbytes = (n_rows + 7) >> 3\n'
            lbk__tltl += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        lbk__tltl += '    for i in range(len(columns_arr)):\n'
        lbk__tltl += '        col_name = columns_arr[i]\n'
        lbk__tltl += '        pivot_idx = col_map[col_name]\n'
        lbk__tltl += '        row_idx = row_vector[i]\n'
        if war__awqzt:
            lbk__tltl += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            lbk__tltl += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            lbk__tltl += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            lbk__tltl += '        else:\n'
            lbk__tltl += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if qsal__wejv:
            lbk__tltl += '        for j in range(num_values_arrays):\n'
            lbk__tltl += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            lbk__tltl += '            len_arr = len_arrs_0[col_idx]\n'
            lbk__tltl += '            values_arr = values_arrs[j]\n'
            lbk__tltl += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            lbk__tltl += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            lbk__tltl += '                len_arr[row_idx] = str_val_len\n'
            lbk__tltl += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, dajys__fblku in enumerate(errmm__ufr):
                if is_str_arr_type(dajys__fblku):
                    lbk__tltl += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    lbk__tltl += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    lbk__tltl += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    lbk__tltl += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    lbk__tltl += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, dajys__fblku in enumerate(errmm__ufr):
        if is_str_arr_type(dajys__fblku):
            lbk__tltl += f'    data_arrs_{i} = [\n'
            lbk__tltl += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            lbk__tltl += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            lbk__tltl += '        )\n'
            lbk__tltl += '        for i in range(n_cols)\n'
            lbk__tltl += '    ]\n'
            lbk__tltl += f'    if tracing.is_tracing():\n'
            lbk__tltl += '         for i in range(n_cols):'
            lbk__tltl += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            lbk__tltl += f'    data_arrs_{i} = [\n'
            lbk__tltl += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            lbk__tltl += '        for _ in range(n_cols)\n'
            lbk__tltl += '    ]\n'
    if not pthvz__lar and war__awqzt:
        lbk__tltl += '    nbytes = (n_rows + 7) >> 3\n'
        lbk__tltl += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    lbk__tltl += '    ev_alloc.finalize()\n'
    lbk__tltl += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    lbk__tltl += '    for i in range(len(columns_arr)):\n'
    lbk__tltl += '        col_name = columns_arr[i]\n'
    lbk__tltl += '        pivot_idx = col_map[col_name]\n'
    lbk__tltl += '        row_idx = row_vector[i]\n'
    if not pthvz__lar and war__awqzt:
        lbk__tltl += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        lbk__tltl += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        lbk__tltl += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        lbk__tltl += '        else:\n'
        lbk__tltl += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if qsal__wejv:
        lbk__tltl += '        for j in range(num_values_arrays):\n'
        lbk__tltl += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        lbk__tltl += '            col_arr = data_arrs_0[col_idx]\n'
        lbk__tltl += '            values_arr = values_arrs[j]\n'
        lbk__tltl += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        lbk__tltl += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        lbk__tltl += '            else:\n'
        lbk__tltl += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, dajys__fblku in enumerate(errmm__ufr):
            lbk__tltl += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            lbk__tltl += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            lbk__tltl += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            lbk__tltl += f'        else:\n'
            lbk__tltl += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        lbk__tltl += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        vlhtm__mpo = index_names.meta[0]
    else:
        lbk__tltl += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        vlhtm__mpo = tuple(index_names.meta)
    lbk__tltl += f'    if tracing.is_tracing():\n'
    lbk__tltl += f'        index_nbytes = index.nbytes\n'
    lbk__tltl += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not pnq__her:
        jda__ipn = columns_name.meta[0]
        if qkey__wndfc:
            lbk__tltl += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            xjc__vhwtm = value_names.meta
            if all(isinstance(rzdcq__fqboi, str) for rzdcq__fqboi in xjc__vhwtm
                ):
                xjc__vhwtm = pd.array(xjc__vhwtm, 'string')
            elif all(isinstance(rzdcq__fqboi, int) for rzdcq__fqboi in
                xjc__vhwtm):
                xjc__vhwtm = np.array(xjc__vhwtm, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(xjc__vhwtm.dtype, pd.StringDtype):
                lbk__tltl += '    total_chars = 0\n'
                lbk__tltl += f'    for i in range({len(value_names)}):\n'
                lbk__tltl += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                lbk__tltl += '        total_chars += value_name_str_len\n'
                lbk__tltl += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                lbk__tltl += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                lbk__tltl += '    total_chars = 0\n'
                lbk__tltl += '    for i in range(len(pivot_values)):\n'
                lbk__tltl += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                lbk__tltl += '        total_chars += pivot_val_str_len\n'
                lbk__tltl += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                lbk__tltl += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            lbk__tltl += f'    for i in range({len(value_names)}):\n'
            lbk__tltl += '        for j in range(len(pivot_values)):\n'
            lbk__tltl += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            lbk__tltl += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            lbk__tltl += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            lbk__tltl += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    lbk__tltl += '    ev_fill.finalize()\n'
    bfdj__yxf = None
    if pnq__her:
        if qkey__wndfc:
            nzt__jio = []
            for umbqv__ootsx in _constant_pivot_values.meta:
                for guohq__kkfna in value_names.meta:
                    nzt__jio.append((umbqv__ootsx, guohq__kkfna))
            column_names = tuple(nzt__jio)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        mvo__iog = ColNamesMetaType(column_names)
        aln__ilvy = []
        for qze__amct in errmm__ufr:
            aln__ilvy.extend([qze__amct] * len(_constant_pivot_values))
        msikw__lkizu = tuple(aln__ilvy)
        bfdj__yxf = TableType(msikw__lkizu)
        lbk__tltl += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        lbk__tltl += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, qze__amct in enumerate(errmm__ufr):
            lbk__tltl += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {bfdj__yxf.type_to_blk[qze__amct]})
"""
        lbk__tltl += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        lbk__tltl += '        (table,), index, columns_typ\n'
        lbk__tltl += '    )\n'
    else:
        lxnpy__sgok = ', '.join(f'data_arrs_{i}' for i in range(len(
            errmm__ufr)))
        lbk__tltl += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({lxnpy__sgok},), n_rows)
"""
        lbk__tltl += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        lbk__tltl += '        (table,), index, column_index\n'
        lbk__tltl += '    )\n'
    lbk__tltl += '    ev.finalize()\n'
    lbk__tltl += '    return result\n'
    nrm__sused = {}
    obs__pct = {f'data_arr_typ_{i}': dajys__fblku for i, dajys__fblku in
        enumerate(errmm__ufr)}
    wlaib__yahf = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        bfdj__yxf, 'columns_typ': mvo__iog, 'index_names_lit': vlhtm__mpo,
        'value_names_lit': xjc__vhwtm, 'columns_name_lit': jda__ipn, **
        obs__pct, 'tracing': tracing}
    exec(lbk__tltl, wlaib__yahf, nrm__sused)
    impl = nrm__sused['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    ypy__yzd = {}
    ypy__yzd['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, heh__fjvot in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        xfgde__mqova = None
        if isinstance(heh__fjvot, bodo.DatetimeArrayType):
            oyurx__mme = 'datetimetz'
            eutps__bjiai = 'datetime64[ns]'
            if isinstance(heh__fjvot.tz, int):
                swwb__elx = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(heh__fjvot.tz))
            else:
                swwb__elx = pd.DatetimeTZDtype(tz=heh__fjvot.tz).tz
            xfgde__mqova = {'timezone': pa.lib.tzinfo_to_string(swwb__elx)}
        elif isinstance(heh__fjvot, types.Array
            ) or heh__fjvot == boolean_array:
            oyurx__mme = eutps__bjiai = heh__fjvot.dtype.name
            if eutps__bjiai.startswith('datetime'):
                oyurx__mme = 'datetime'
        elif is_str_arr_type(heh__fjvot):
            oyurx__mme = 'unicode'
            eutps__bjiai = 'object'
        elif heh__fjvot == binary_array_type:
            oyurx__mme = 'bytes'
            eutps__bjiai = 'object'
        elif isinstance(heh__fjvot, DecimalArrayType):
            oyurx__mme = eutps__bjiai = 'object'
        elif isinstance(heh__fjvot, IntegerArrayType):
            iejxd__rcd = heh__fjvot.dtype.name
            if iejxd__rcd.startswith('int'):
                oyurx__mme = 'Int' + iejxd__rcd[3:]
            elif iejxd__rcd.startswith('uint'):
                oyurx__mme = 'UInt' + iejxd__rcd[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, heh__fjvot))
            eutps__bjiai = heh__fjvot.dtype.name
        elif heh__fjvot == datetime_date_array_type:
            oyurx__mme = 'datetime'
            eutps__bjiai = 'object'
        elif isinstance(heh__fjvot, TimeArrayType):
            oyurx__mme = 'datetime'
            eutps__bjiai = 'object'
        elif isinstance(heh__fjvot, (StructArrayType, ArrayItemArrayType)):
            oyurx__mme = 'object'
            eutps__bjiai = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, heh__fjvot))
        nae__emp = {'name': col_name, 'field_name': col_name, 'pandas_type':
            oyurx__mme, 'numpy_type': eutps__bjiai, 'metadata': xfgde__mqova}
        ypy__yzd['columns'].append(nae__emp)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            vcghk__oog = '__index_level_0__'
            umcdu__zyctg = None
        else:
            vcghk__oog = '%s'
            umcdu__zyctg = '%s'
        ypy__yzd['index_columns'] = [vcghk__oog]
        ypy__yzd['columns'].append({'name': umcdu__zyctg, 'field_name':
            vcghk__oog, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        ypy__yzd['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        ypy__yzd['index_columns'] = []
    ypy__yzd['pandas_version'] = pd.__version__
    return ypy__yzd


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
        acu__romvo = []
        for etj__tqvy in partition_cols:
            try:
                idx = df.columns.index(etj__tqvy)
            except ValueError as wmv__lkayi:
                raise BodoError(
                    f'Partition column {etj__tqvy} is not in dataframe')
            acu__romvo.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    zasl__rae = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    kjbeo__nalf = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not zasl__rae)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not zasl__rae or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and zasl__rae and not is_overload_true(_is_parallel)
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
        wwcyu__pqqr = df.runtime_data_types
        qwr__kvq = len(wwcyu__pqqr)
        xfgde__mqova = gen_pandas_parquet_metadata([''] * qwr__kvq,
            wwcyu__pqqr, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        ahkyd__jkjq = xfgde__mqova['columns'][:qwr__kvq]
        xfgde__mqova['columns'] = xfgde__mqova['columns'][qwr__kvq:]
        ahkyd__jkjq = [json.dumps(judhb__telgy).replace('""', '{0}') for
            judhb__telgy in ahkyd__jkjq]
        qbnd__mtpzn = json.dumps(xfgde__mqova)
        igyou__kebx = '"columns": ['
        klwf__jhmlu = qbnd__mtpzn.find(igyou__kebx)
        if klwf__jhmlu == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        rsa__dowu = klwf__jhmlu + len(igyou__kebx)
        yutz__amghm = qbnd__mtpzn[:rsa__dowu]
        qbnd__mtpzn = qbnd__mtpzn[rsa__dowu:]
        rcbc__yluj = len(xfgde__mqova['columns'])
    else:
        qbnd__mtpzn = json.dumps(gen_pandas_parquet_metadata(df.columns, df
            .data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and zasl__rae:
        qbnd__mtpzn = qbnd__mtpzn.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            qbnd__mtpzn = qbnd__mtpzn.replace('"%s"', '%s')
    if not df.is_table_format:
        kcs__mxrgo = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    lbk__tltl = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        lbk__tltl += '    py_table = get_dataframe_table(df)\n'
        lbk__tltl += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        lbk__tltl += '    info_list = [{}]\n'.format(kcs__mxrgo)
        lbk__tltl += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        lbk__tltl += '    columns_index = get_dataframe_column_names(df)\n'
        lbk__tltl += '    names_arr = index_to_array(columns_index)\n'
        lbk__tltl += '    col_names = array_to_info(names_arr)\n'
    else:
        lbk__tltl += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and kjbeo__nalf:
        lbk__tltl += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        ndnu__qbzpw = True
    else:
        lbk__tltl += '    index_col = array_to_info(np.empty(0))\n'
        ndnu__qbzpw = False
    if df.has_runtime_cols:
        lbk__tltl += '    columns_lst = []\n'
        lbk__tltl += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            lbk__tltl += f'    for _ in range(len(py_table.block_{i})):\n'
            lbk__tltl += f"""        columns_lst.append({ahkyd__jkjq[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            lbk__tltl += '        num_cols += 1\n'
        if rcbc__yluj:
            lbk__tltl += "    columns_lst.append('')\n"
        lbk__tltl += '    columns_str = ", ".join(columns_lst)\n'
        lbk__tltl += ('    metadata = """' + yutz__amghm +
            '""" + columns_str + """' + qbnd__mtpzn + '"""\n')
    else:
        lbk__tltl += '    metadata = """' + qbnd__mtpzn + '"""\n'
    lbk__tltl += '    if compression is None:\n'
    lbk__tltl += "        compression = 'none'\n"
    lbk__tltl += '    if df.index.name is not None:\n'
    lbk__tltl += '        name_ptr = df.index.name\n'
    lbk__tltl += '    else:\n'
    lbk__tltl += "        name_ptr = 'null'\n"
    lbk__tltl += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    fmgej__dxms = None
    if partition_cols:
        fmgej__dxms = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        uicdj__rad = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in acu__romvo)
        if uicdj__rad:
            lbk__tltl += '    cat_info_list = [{}]\n'.format(uicdj__rad)
            lbk__tltl += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            lbk__tltl += '    cat_table = table\n'
        lbk__tltl += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        lbk__tltl += (
            f'    part_cols_idxs = np.array({acu__romvo}, dtype=np.int32)\n')
        lbk__tltl += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        lbk__tltl += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        lbk__tltl += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        lbk__tltl += (
            '                            unicode_to_utf8(compression),\n')
        lbk__tltl += '                            _is_parallel,\n'
        lbk__tltl += (
            '                            unicode_to_utf8(bucket_region),\n')
        lbk__tltl += '                            row_group_size,\n'
        lbk__tltl += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        lbk__tltl += '    delete_table_decref_arrays(table)\n'
        lbk__tltl += '    delete_info_decref_array(index_col)\n'
        lbk__tltl += '    delete_info_decref_array(col_names_no_partitions)\n'
        lbk__tltl += '    delete_info_decref_array(col_names)\n'
        if uicdj__rad:
            lbk__tltl += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        lbk__tltl += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        lbk__tltl += (
            '                            table, col_names, index_col,\n')
        lbk__tltl += '                            ' + str(ndnu__qbzpw) + ',\n'
        lbk__tltl += '                            unicode_to_utf8(metadata),\n'
        lbk__tltl += (
            '                            unicode_to_utf8(compression),\n')
        lbk__tltl += (
            '                            _is_parallel, 1, df.index.start,\n')
        lbk__tltl += (
            '                            df.index.stop, df.index.step,\n')
        lbk__tltl += '                            unicode_to_utf8(name_ptr),\n'
        lbk__tltl += (
            '                            unicode_to_utf8(bucket_region),\n')
        lbk__tltl += '                            row_group_size,\n'
        lbk__tltl += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        lbk__tltl += '    delete_table_decref_arrays(table)\n'
        lbk__tltl += '    delete_info_decref_array(index_col)\n'
        lbk__tltl += '    delete_info_decref_array(col_names)\n'
    else:
        lbk__tltl += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        lbk__tltl += (
            '                            table, col_names, index_col,\n')
        lbk__tltl += '                            ' + str(ndnu__qbzpw) + ',\n'
        lbk__tltl += '                            unicode_to_utf8(metadata),\n'
        lbk__tltl += (
            '                            unicode_to_utf8(compression),\n')
        lbk__tltl += '                            _is_parallel, 0, 0, 0, 0,\n'
        lbk__tltl += '                            unicode_to_utf8(name_ptr),\n'
        lbk__tltl += (
            '                            unicode_to_utf8(bucket_region),\n')
        lbk__tltl += '                            row_group_size,\n'
        lbk__tltl += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        lbk__tltl += '    delete_table_decref_arrays(table)\n'
        lbk__tltl += '    delete_info_decref_array(index_col)\n'
        lbk__tltl += '    delete_info_decref_array(col_names)\n'
    nrm__sused = {}
    if df.has_runtime_cols:
        ogzwl__ecly = None
    else:
        for yftos__fbwp in df.columns:
            if not isinstance(yftos__fbwp, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        ogzwl__ecly = pd.array(df.columns)
    exec(lbk__tltl, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': ogzwl__ecly,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': fmgej__dxms, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, nrm__sused)
    dibr__lwmf = nrm__sused['df_to_parquet']
    return dibr__lwmf


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    mkh__nnkbj = 'all_ok'
    vlq__chov, lmot__rada = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        vqlr__xjbai = 100
        if chunksize is None:
            ybkvq__nsj = vqlr__xjbai
        else:
            ybkvq__nsj = min(chunksize, vqlr__xjbai)
        if _is_table_create:
            df = df.iloc[:ybkvq__nsj, :]
        else:
            df = df.iloc[ybkvq__nsj:, :]
            if len(df) == 0:
                return mkh__nnkbj
    mgzf__drdz = df.columns
    try:
        if vlq__chov == 'snowflake':
            if lmot__rada and con.count(lmot__rada) == 1:
                con = con.replace(lmot__rada, quote(lmot__rada))
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
                df.columns = [(rzdcq__fqboi.upper() if rzdcq__fqboi.islower
                    () else rzdcq__fqboi) for rzdcq__fqboi in df.columns]
            except ImportError as wmv__lkayi:
                mkh__nnkbj = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return mkh__nnkbj
        if vlq__chov == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            nqlkm__kan = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            jxqwh__lhm = bodo.typeof(df)
            ikuhn__yni = {}
            for rzdcq__fqboi, zhdn__syrmh in zip(jxqwh__lhm.columns,
                jxqwh__lhm.data):
                if df[rzdcq__fqboi].dtype == 'object':
                    if zhdn__syrmh == datetime_date_array_type:
                        ikuhn__yni[rzdcq__fqboi] = sa.types.Date
                    elif zhdn__syrmh in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not nqlkm__kan or 
                        nqlkm__kan == '0'):
                        ikuhn__yni[rzdcq__fqboi] = VARCHAR2(4000)
            dtype = ikuhn__yni
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as uhk__jidjp:
            mkh__nnkbj = uhk__jidjp.args[0]
            if vlq__chov == 'oracle' and 'ORA-12899' in mkh__nnkbj:
                mkh__nnkbj += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return mkh__nnkbj
    finally:
        df.columns = mgzf__drdz


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
    lbk__tltl = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    lbk__tltl += f"    if con.startswith('iceberg'):\n"
    lbk__tltl += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    lbk__tltl += f'        if schema is None:\n'
    lbk__tltl += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    lbk__tltl += f'        if chunksize is not None:\n'
    lbk__tltl += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    lbk__tltl += f'        if index and bodo.get_rank() == 0:\n'
    lbk__tltl += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    lbk__tltl += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    lbk__tltl += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        lbk__tltl += f'        py_table = get_dataframe_table(df)\n'
        lbk__tltl += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        kcs__mxrgo = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        lbk__tltl += f'        info_list = [{kcs__mxrgo}]\n'
        lbk__tltl += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        lbk__tltl += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        lbk__tltl += f'        names_arr = index_to_array(columns_index)\n'
        lbk__tltl += f'        col_names = array_to_info(names_arr)\n'
    else:
        lbk__tltl += f'        col_names = array_to_info(col_names_arr)\n'
    lbk__tltl += """        bodo.io.iceberg.iceberg_write(
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
    lbk__tltl += f'        delete_table_decref_arrays(table)\n'
    lbk__tltl += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        ogzwl__ecly = None
    else:
        for yftos__fbwp in df.columns:
            if not isinstance(yftos__fbwp, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        ogzwl__ecly = pd.array(df.columns)
    lbk__tltl += f'    else:\n'
    lbk__tltl += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    lbk__tltl += f"        err_msg = 'unset'\n"
    lbk__tltl += f'        if rank != 0:\n'
    lbk__tltl += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    lbk__tltl += f'        elif rank == 0:\n'
    lbk__tltl += f'            err_msg = to_sql_exception_guard_encaps(\n'
    lbk__tltl += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    lbk__tltl += f'                          chunksize, dtype, method,\n'
    lbk__tltl += f'                          True, _is_parallel,\n'
    lbk__tltl += f'                      )\n'
    lbk__tltl += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    lbk__tltl += f"        if_exists = 'append'\n"
    lbk__tltl += f"        if _is_parallel and err_msg == 'all_ok':\n"
    lbk__tltl += f'            err_msg = to_sql_exception_guard_encaps(\n'
    lbk__tltl += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    lbk__tltl += f'                          chunksize, dtype, method,\n'
    lbk__tltl += f'                          False, _is_parallel,\n'
    lbk__tltl += f'                      )\n'
    lbk__tltl += f"        if err_msg != 'all_ok':\n"
    lbk__tltl += f"            print('err_msg=', err_msg)\n"
    lbk__tltl += (
        f"            raise ValueError('error in to_sql() operation')\n")
    nrm__sused = {}
    exec(lbk__tltl, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': ogzwl__ecly, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, nrm__sused)
    _impl = nrm__sused['df_to_sql']
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
        dra__dbxti = get_overload_const_str(path_or_buf)
        if dra__dbxti.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        cnfo__diee = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(cnfo__diee), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(cnfo__diee), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    vehd__wgo = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    wado__eacrr = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', vehd__wgo, wado__eacrr,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    lbk__tltl = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        gndtm__xbkb = data.data.dtype.categories
        lbk__tltl += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        gndtm__xbkb = data.dtype.categories
        lbk__tltl += '  data_values = data\n'
    tgbyd__zjoo = len(gndtm__xbkb)
    lbk__tltl += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    lbk__tltl += '  numba.parfors.parfor.init_prange()\n'
    lbk__tltl += '  n = len(data_values)\n'
    for i in range(tgbyd__zjoo):
        lbk__tltl += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    lbk__tltl += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    lbk__tltl += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for zao__picpy in range(tgbyd__zjoo):
        lbk__tltl += '          data_arr_{}[i] = 0\n'.format(zao__picpy)
    lbk__tltl += '      else:\n'
    for aooq__vcd in range(tgbyd__zjoo):
        lbk__tltl += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            aooq__vcd)
    kcs__mxrgo = ', '.join(f'data_arr_{i}' for i in range(tgbyd__zjoo))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(gndtm__xbkb[0], np.datetime64):
        gndtm__xbkb = tuple(pd.Timestamp(rzdcq__fqboi) for rzdcq__fqboi in
            gndtm__xbkb)
    elif isinstance(gndtm__xbkb[0], np.timedelta64):
        gndtm__xbkb = tuple(pd.Timedelta(rzdcq__fqboi) for rzdcq__fqboi in
            gndtm__xbkb)
    return bodo.hiframes.dataframe_impl._gen_init_df(lbk__tltl, gndtm__xbkb,
        kcs__mxrgo, index)


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
    for dymqx__nsjy in pd_unsupported:
        aih__exw = mod_name + '.' + dymqx__nsjy.__name__
        overload(dymqx__nsjy, no_unliteral=True)(create_unsupported_overload
            (aih__exw))


def _install_dataframe_unsupported():
    for whvg__nyr in dataframe_unsupported_attrs:
        tlyli__ohiob = 'DataFrame.' + whvg__nyr
        overload_attribute(DataFrameType, whvg__nyr)(
            create_unsupported_overload(tlyli__ohiob))
    for aih__exw in dataframe_unsupported:
        tlyli__ohiob = 'DataFrame.' + aih__exw + '()'
        overload_method(DataFrameType, aih__exw)(create_unsupported_overload
            (tlyli__ohiob))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
