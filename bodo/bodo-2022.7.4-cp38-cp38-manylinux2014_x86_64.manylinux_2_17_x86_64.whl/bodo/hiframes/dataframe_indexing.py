"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            iis__jik = idx
            xlu__kwwo = df.data
            yxjny__ngxyv = df.columns
            vvi__gyaxq = self.replace_range_with_numeric_idx_if_needed(df,
                iis__jik)
            lfa__djdmy = DataFrameType(xlu__kwwo, vvi__gyaxq, yxjny__ngxyv,
                is_table_format=df.is_table_format)
            return lfa__djdmy(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            wgv__vitg = idx.types[0]
            vvu__nsy = idx.types[1]
            if isinstance(wgv__vitg, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(vvu__nsy):
                    lap__alaa = get_overload_const_str(vvu__nsy)
                    if lap__alaa not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, lap__alaa))
                    bdi__wqoqk = df.columns.index(lap__alaa)
                    return df.data[bdi__wqoqk].dtype(*args)
                if isinstance(vvu__nsy, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(wgv__vitg
                ) and wgv__vitg.dtype == types.bool_ or isinstance(wgv__vitg,
                types.SliceType):
                vvi__gyaxq = self.replace_range_with_numeric_idx_if_needed(df,
                    wgv__vitg)
                if is_overload_constant_str(vvu__nsy):
                    ypn__szpsb = get_overload_const_str(vvu__nsy)
                    if ypn__szpsb not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {ypn__szpsb}'
                            )
                    bdi__wqoqk = df.columns.index(ypn__szpsb)
                    gaix__fjdqy = df.data[bdi__wqoqk]
                    nzr__sxcw = gaix__fjdqy.dtype
                    gucc__zjj = types.literal(df.columns[bdi__wqoqk])
                    lfa__djdmy = bodo.SeriesType(nzr__sxcw, gaix__fjdqy,
                        vvi__gyaxq, gucc__zjj)
                    return lfa__djdmy(*args)
                if isinstance(vvu__nsy, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(vvu__nsy):
                    nrrdc__wzv = get_overload_const_list(vvu__nsy)
                    ymnz__nhsjj = types.unliteral(vvu__nsy)
                    if ymnz__nhsjj.dtype == types.bool_:
                        if len(df.columns) != len(nrrdc__wzv):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {nrrdc__wzv} has {len(nrrdc__wzv)} values'
                                )
                        beux__ooxh = []
                        yvgs__bdj = []
                        for feazj__hnozc in range(len(nrrdc__wzv)):
                            if nrrdc__wzv[feazj__hnozc]:
                                beux__ooxh.append(df.columns[feazj__hnozc])
                                yvgs__bdj.append(df.data[feazj__hnozc])
                        peve__ygui = tuple()
                        bnzqb__vql = df.is_table_format and len(beux__ooxh
                            ) > 0 and len(beux__ooxh
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        lfa__djdmy = DataFrameType(tuple(yvgs__bdj),
                            vvi__gyaxq, tuple(beux__ooxh), is_table_format=
                            bnzqb__vql)
                        return lfa__djdmy(*args)
                    elif ymnz__nhsjj.dtype == bodo.string_type:
                        peve__ygui, yvgs__bdj = (
                            get_df_getitem_kept_cols_and_data(df, nrrdc__wzv))
                        bnzqb__vql = df.is_table_format and len(nrrdc__wzv
                            ) > 0 and len(nrrdc__wzv
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        lfa__djdmy = DataFrameType(yvgs__bdj, vvi__gyaxq,
                            peve__ygui, is_table_format=bnzqb__vql)
                        return lfa__djdmy(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                beux__ooxh = []
                yvgs__bdj = []
                for feazj__hnozc, evv__fjzqb in enumerate(df.columns):
                    if evv__fjzqb[0] != ind_val:
                        continue
                    beux__ooxh.append(evv__fjzqb[1] if len(evv__fjzqb) == 2
                         else evv__fjzqb[1:])
                    yvgs__bdj.append(df.data[feazj__hnozc])
                gaix__fjdqy = tuple(yvgs__bdj)
                hlaxh__yzqbn = df.index
                chhbu__sugek = tuple(beux__ooxh)
                lfa__djdmy = DataFrameType(gaix__fjdqy, hlaxh__yzqbn,
                    chhbu__sugek)
                return lfa__djdmy(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                bdi__wqoqk = df.columns.index(ind_val)
                gaix__fjdqy = df.data[bdi__wqoqk]
                nzr__sxcw = gaix__fjdqy.dtype
                hlaxh__yzqbn = df.index
                gucc__zjj = types.literal(df.columns[bdi__wqoqk])
                lfa__djdmy = bodo.SeriesType(nzr__sxcw, gaix__fjdqy,
                    hlaxh__yzqbn, gucc__zjj)
                return lfa__djdmy(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            gaix__fjdqy = df.data
            hlaxh__yzqbn = self.replace_range_with_numeric_idx_if_needed(df,
                ind)
            chhbu__sugek = df.columns
            lfa__djdmy = DataFrameType(gaix__fjdqy, hlaxh__yzqbn,
                chhbu__sugek, is_table_format=df.is_table_format)
            return lfa__djdmy(*args)
        elif is_overload_constant_list(ind):
            hhf__ogh = get_overload_const_list(ind)
            chhbu__sugek, gaix__fjdqy = get_df_getitem_kept_cols_and_data(df,
                hhf__ogh)
            hlaxh__yzqbn = df.index
            bnzqb__vql = df.is_table_format and len(hhf__ogh) > 0 and len(
                hhf__ogh) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            lfa__djdmy = DataFrameType(gaix__fjdqy, hlaxh__yzqbn,
                chhbu__sugek, is_table_format=bnzqb__vql)
            return lfa__djdmy(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        vvi__gyaxq = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return vvi__gyaxq


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for xzp__xznm in cols_to_keep_list:
        if xzp__xznm not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(xzp__xznm, df.columns))
    chhbu__sugek = tuple(cols_to_keep_list)
    gaix__fjdqy = tuple(df.data[df.column_index[dpoid__num]] for dpoid__num in
        chhbu__sugek)
    return chhbu__sugek, gaix__fjdqy


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            beux__ooxh = []
            yvgs__bdj = []
            for feazj__hnozc, evv__fjzqb in enumerate(df.columns):
                if evv__fjzqb[0] != ind_val:
                    continue
                beux__ooxh.append(evv__fjzqb[1] if len(evv__fjzqb) == 2 else
                    evv__fjzqb[1:])
                yvgs__bdj.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(feazj__hnozc))
            knop__qee = 'def impl(df, ind):\n'
            cqe__isdk = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee,
                beux__ooxh, ', '.join(yvgs__bdj), cqe__isdk)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        hhf__ogh = get_overload_const_list(ind)
        for xzp__xznm in hhf__ogh:
            if xzp__xznm not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(xzp__xznm, df.columns))
        jel__aln = None
        if df.is_table_format and len(hhf__ogh) > 0 and len(hhf__ogh
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            ulwl__hckgh = [df.column_index[xzp__xznm] for xzp__xznm in hhf__ogh
                ]
            jel__aln = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
                ulwl__hckgh))}
            yvgs__bdj = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            yvgs__bdj = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[xzp__xznm]}).copy()'
                 for xzp__xznm in hhf__ogh)
        knop__qee = 'def impl(df, ind):\n'
        cqe__isdk = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee,
            hhf__ogh, yvgs__bdj, cqe__isdk, extra_globals=jel__aln)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        knop__qee = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            knop__qee += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        cqe__isdk = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            yvgs__bdj = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            yvgs__bdj = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[xzp__xznm]})[ind]'
                 for xzp__xznm in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee, df.
            columns, yvgs__bdj, cqe__isdk)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        dpoid__num = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(dpoid__num)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kkzl__bfrb = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, kkzl__bfrb)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ulv__kbn, = args
        bdzjc__rck = signature.return_type
        cavq__vnuno = cgutils.create_struct_proxy(bdzjc__rck)(context, builder)
        cavq__vnuno.obj = ulv__kbn
        context.nrt.incref(builder, signature.args[0], ulv__kbn)
        return cavq__vnuno._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        joj__dlj = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            oovdj__smq = get_overload_const_int(idx.types[1])
            if oovdj__smq < 0 or oovdj__smq >= joj__dlj:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            eytt__ykc = [oovdj__smq]
        else:
            is_out_series = False
            eytt__ykc = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= joj__dlj for
                ind in eytt__ykc):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[eytt__ykc])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                oovdj__smq = eytt__ykc[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, oovdj__smq)
                        [idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    knop__qee = 'def impl(I, idx):\n'
    knop__qee += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        knop__qee += f'  idx_t = {idx}\n'
    else:
        knop__qee += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    cqe__isdk = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]'
    jel__aln = None
    if df.is_table_format and not is_out_series:
        ulwl__hckgh = [df.column_index[xzp__xznm] for xzp__xznm in col_names]
        jel__aln = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            ulwl__hckgh))}
        yvgs__bdj = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        yvgs__bdj = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[xzp__xznm]})[idx_t]'
             for xzp__xznm in col_names)
    if is_out_series:
        nhk__uliuu = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        knop__qee += f"""  return bodo.hiframes.pd_series_ext.init_series({yvgs__bdj}, {cqe__isdk}, {nhk__uliuu})
"""
        pii__ueiq = {}
        exec(knop__qee, {'bodo': bodo}, pii__ueiq)
        return pii__ueiq['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee, col_names,
        yvgs__bdj, cqe__isdk, extra_globals=jel__aln)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    knop__qee = 'def impl(I, idx):\n'
    knop__qee += '  df = I._obj\n'
    gafz__vklu = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[xzp__xznm]})[{idx}]'
         for xzp__xznm in col_names)
    knop__qee += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    knop__qee += f"""  return bodo.hiframes.pd_series_ext.init_series(({gafz__vklu},), row_idx, None)
"""
    pii__ueiq = {}
    exec(knop__qee, {'bodo': bodo}, pii__ueiq)
    impl = pii__ueiq['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        dpoid__num = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(dpoid__num)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kkzl__bfrb = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, kkzl__bfrb)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ulv__kbn, = args
        kdw__vrvug = signature.return_type
        zlz__xeffa = cgutils.create_struct_proxy(kdw__vrvug)(context, builder)
        zlz__xeffa.obj = ulv__kbn
        context.nrt.incref(builder, signature.args[0], ulv__kbn)
        return zlz__xeffa._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        knop__qee = 'def impl(I, idx):\n'
        knop__qee += '  df = I._obj\n'
        knop__qee += '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n'
        cqe__isdk = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            yvgs__bdj = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            yvgs__bdj = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[xzp__xznm]})[idx_t]'
                 for xzp__xznm in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee, df.
            columns, yvgs__bdj, cqe__isdk)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        ymwu__jrfnr = idx.types[1]
        if is_overload_constant_str(ymwu__jrfnr):
            gadp__nznjf = get_overload_const_str(ymwu__jrfnr)
            oovdj__smq = df.columns.index(gadp__nznjf)

            def impl_col_name(I, idx):
                df = I._obj
                cqe__isdk = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
                    df)
                ksux__iiwti = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, oovdj__smq))
                return bodo.hiframes.pd_series_ext.init_series(ksux__iiwti,
                    cqe__isdk, gadp__nznjf).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(ymwu__jrfnr):
            col_idx_list = get_overload_const_list(ymwu__jrfnr)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(xzp__xznm in df.column_index for
                xzp__xznm in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    eytt__ykc = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for feazj__hnozc, nlx__bkm in enumerate(col_idx_list):
            if nlx__bkm:
                eytt__ykc.append(feazj__hnozc)
                col_names.append(df.columns[feazj__hnozc])
    else:
        col_names = col_idx_list
        eytt__ykc = [df.column_index[xzp__xznm] for xzp__xznm in col_idx_list]
    jel__aln = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        jel__aln = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            eytt__ykc))}
        yvgs__bdj = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        yvgs__bdj = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in eytt__ykc)
    cqe__isdk = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    knop__qee = 'def impl(I, idx):\n'
    knop__qee += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(knop__qee, col_names,
        yvgs__bdj, cqe__isdk, extra_globals=jel__aln)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        dpoid__num = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(dpoid__num)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kkzl__bfrb = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, kkzl__bfrb)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ulv__kbn, = args
        bxc__hsoc = signature.return_type
        kjceh__ywug = cgutils.create_struct_proxy(bxc__hsoc)(context, builder)
        kjceh__ywug.obj = ulv__kbn
        context.nrt.incref(builder, signature.args[0], ulv__kbn)
        return kjceh__ywug._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        oovdj__smq = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            ksux__iiwti = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                oovdj__smq)
            return bodo.utils.conversion.box_if_dt64(ksux__iiwti[idx[0]])
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        oovdj__smq = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[oovdj__smq]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            ksux__iiwti = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                oovdj__smq)
            ksux__iiwti[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    kjceh__ywug = cgutils.create_struct_proxy(fromty)(context, builder, val)
    jehbm__clr = context.cast(builder, kjceh__ywug.obj, fromty.df_type,
        toty.df_type)
    skmaj__drghf = cgutils.create_struct_proxy(toty)(context, builder)
    skmaj__drghf.obj = jehbm__clr
    return skmaj__drghf._getvalue()
