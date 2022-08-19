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
            yxp__rpd = idx
            seq__dvgdh = df.data
            peai__lkm = df.columns
            npxn__hrpsy = self.replace_range_with_numeric_idx_if_needed(df,
                yxp__rpd)
            yjgnv__mop = DataFrameType(seq__dvgdh, npxn__hrpsy, peai__lkm,
                is_table_format=df.is_table_format)
            return yjgnv__mop(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            juszq__rcd = idx.types[0]
            ezrhz__tflm = idx.types[1]
            if isinstance(juszq__rcd, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(ezrhz__tflm):
                    roaw__zrok = get_overload_const_str(ezrhz__tflm)
                    if roaw__zrok not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, roaw__zrok))
                    hjtux__xmd = df.columns.index(roaw__zrok)
                    return df.data[hjtux__xmd].dtype(*args)
                if isinstance(ezrhz__tflm, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(juszq__rcd
                ) and juszq__rcd.dtype == types.bool_ or isinstance(juszq__rcd,
                types.SliceType):
                npxn__hrpsy = self.replace_range_with_numeric_idx_if_needed(df,
                    juszq__rcd)
                if is_overload_constant_str(ezrhz__tflm):
                    vzfgw__qho = get_overload_const_str(ezrhz__tflm)
                    if vzfgw__qho not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {vzfgw__qho}'
                            )
                    hjtux__xmd = df.columns.index(vzfgw__qho)
                    dcvk__bbwb = df.data[hjtux__xmd]
                    ydi__xbgqq = dcvk__bbwb.dtype
                    vac__uhq = types.literal(df.columns[hjtux__xmd])
                    yjgnv__mop = bodo.SeriesType(ydi__xbgqq, dcvk__bbwb,
                        npxn__hrpsy, vac__uhq)
                    return yjgnv__mop(*args)
                if isinstance(ezrhz__tflm, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(ezrhz__tflm):
                    cgkm__hinbu = get_overload_const_list(ezrhz__tflm)
                    qaz__usa = types.unliteral(ezrhz__tflm)
                    if qaz__usa.dtype == types.bool_:
                        if len(df.columns) != len(cgkm__hinbu):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {cgkm__hinbu} has {len(cgkm__hinbu)} values'
                                )
                        ivq__dcc = []
                        ikxw__rypln = []
                        for qpycz__yafh in range(len(cgkm__hinbu)):
                            if cgkm__hinbu[qpycz__yafh]:
                                ivq__dcc.append(df.columns[qpycz__yafh])
                                ikxw__rypln.append(df.data[qpycz__yafh])
                        ngv__rpdtr = tuple()
                        akcn__ycvnf = df.is_table_format and len(ivq__dcc
                            ) > 0 and len(ivq__dcc
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        yjgnv__mop = DataFrameType(tuple(ikxw__rypln),
                            npxn__hrpsy, tuple(ivq__dcc), is_table_format=
                            akcn__ycvnf)
                        return yjgnv__mop(*args)
                    elif qaz__usa.dtype == bodo.string_type:
                        ngv__rpdtr, ikxw__rypln = (
                            get_df_getitem_kept_cols_and_data(df, cgkm__hinbu))
                        akcn__ycvnf = df.is_table_format and len(cgkm__hinbu
                            ) > 0 and len(cgkm__hinbu
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        yjgnv__mop = DataFrameType(ikxw__rypln, npxn__hrpsy,
                            ngv__rpdtr, is_table_format=akcn__ycvnf)
                        return yjgnv__mop(*args)
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
                ivq__dcc = []
                ikxw__rypln = []
                for qpycz__yafh, gieqk__mft in enumerate(df.columns):
                    if gieqk__mft[0] != ind_val:
                        continue
                    ivq__dcc.append(gieqk__mft[1] if len(gieqk__mft) == 2 else
                        gieqk__mft[1:])
                    ikxw__rypln.append(df.data[qpycz__yafh])
                dcvk__bbwb = tuple(ikxw__rypln)
                kdgb__osbmv = df.index
                ntb__ynpx = tuple(ivq__dcc)
                yjgnv__mop = DataFrameType(dcvk__bbwb, kdgb__osbmv, ntb__ynpx)
                return yjgnv__mop(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                hjtux__xmd = df.columns.index(ind_val)
                dcvk__bbwb = df.data[hjtux__xmd]
                ydi__xbgqq = dcvk__bbwb.dtype
                kdgb__osbmv = df.index
                vac__uhq = types.literal(df.columns[hjtux__xmd])
                yjgnv__mop = bodo.SeriesType(ydi__xbgqq, dcvk__bbwb,
                    kdgb__osbmv, vac__uhq)
                return yjgnv__mop(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            dcvk__bbwb = df.data
            kdgb__osbmv = self.replace_range_with_numeric_idx_if_needed(df, ind
                )
            ntb__ynpx = df.columns
            yjgnv__mop = DataFrameType(dcvk__bbwb, kdgb__osbmv, ntb__ynpx,
                is_table_format=df.is_table_format)
            return yjgnv__mop(*args)
        elif is_overload_constant_list(ind):
            qfxou__rvgu = get_overload_const_list(ind)
            ntb__ynpx, dcvk__bbwb = get_df_getitem_kept_cols_and_data(df,
                qfxou__rvgu)
            kdgb__osbmv = df.index
            akcn__ycvnf = df.is_table_format and len(qfxou__rvgu) > 0 and len(
                qfxou__rvgu) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            yjgnv__mop = DataFrameType(dcvk__bbwb, kdgb__osbmv, ntb__ynpx,
                is_table_format=akcn__ycvnf)
            return yjgnv__mop(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        npxn__hrpsy = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return npxn__hrpsy


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for pgzbe__medrm in cols_to_keep_list:
        if pgzbe__medrm not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(pgzbe__medrm, df.columns))
    ntb__ynpx = tuple(cols_to_keep_list)
    dcvk__bbwb = tuple(df.data[df.column_index[yrfkw__aiv]] for yrfkw__aiv in
        ntb__ynpx)
    return ntb__ynpx, dcvk__bbwb


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
            ivq__dcc = []
            ikxw__rypln = []
            for qpycz__yafh, gieqk__mft in enumerate(df.columns):
                if gieqk__mft[0] != ind_val:
                    continue
                ivq__dcc.append(gieqk__mft[1] if len(gieqk__mft) == 2 else
                    gieqk__mft[1:])
                ikxw__rypln.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(qpycz__yafh))
            lgcgo__jyeyw = 'def impl(df, ind):\n'
            jobw__egnoc = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw,
                ivq__dcc, ', '.join(ikxw__rypln), jobw__egnoc)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        qfxou__rvgu = get_overload_const_list(ind)
        for pgzbe__medrm in qfxou__rvgu:
            if pgzbe__medrm not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(pgzbe__medrm, df.columns))
        egeut__lmbyj = None
        if df.is_table_format and len(qfxou__rvgu) > 0 and len(qfxou__rvgu
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            nqi__zpuwv = [df.column_index[pgzbe__medrm] for pgzbe__medrm in
                qfxou__rvgu]
            egeut__lmbyj = {'col_nums_meta': bodo.utils.typing.MetaType(
                tuple(nqi__zpuwv))}
            ikxw__rypln = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            ikxw__rypln = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pgzbe__medrm]}).copy()'
                 for pgzbe__medrm in qfxou__rvgu)
        lgcgo__jyeyw = 'def impl(df, ind):\n'
        jobw__egnoc = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw,
            qfxou__rvgu, ikxw__rypln, jobw__egnoc, extra_globals=egeut__lmbyj)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        lgcgo__jyeyw = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            lgcgo__jyeyw += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        jobw__egnoc = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            ikxw__rypln = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            ikxw__rypln = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pgzbe__medrm]})[ind]'
                 for pgzbe__medrm in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw, df.
            columns, ikxw__rypln, jobw__egnoc)
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
        yrfkw__aiv = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(yrfkw__aiv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        axsn__jmak = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, axsn__jmak)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        tedlz__trh, = args
        jdtu__ppacy = signature.return_type
        bhwn__vtrff = cgutils.create_struct_proxy(jdtu__ppacy)(context, builder
            )
        bhwn__vtrff.obj = tedlz__trh
        context.nrt.incref(builder, signature.args[0], tedlz__trh)
        return bhwn__vtrff._getvalue()
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
        vyv__baug = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            vpej__ilhee = get_overload_const_int(idx.types[1])
            if vpej__ilhee < 0 or vpej__ilhee >= vyv__baug:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            rznzs__vfivt = [vpej__ilhee]
        else:
            is_out_series = False
            rznzs__vfivt = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= vyv__baug for
                ind in rznzs__vfivt):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[rznzs__vfivt])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                vpej__ilhee = rznzs__vfivt[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, vpej__ilhee
                        )[idx[0]])
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
    lgcgo__jyeyw = 'def impl(I, idx):\n'
    lgcgo__jyeyw += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        lgcgo__jyeyw += f'  idx_t = {idx}\n'
    else:
        lgcgo__jyeyw += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    jobw__egnoc = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    egeut__lmbyj = None
    if df.is_table_format and not is_out_series:
        nqi__zpuwv = [df.column_index[pgzbe__medrm] for pgzbe__medrm in
            col_names]
        egeut__lmbyj = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            nqi__zpuwv))}
        ikxw__rypln = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        ikxw__rypln = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pgzbe__medrm]})[idx_t]'
             for pgzbe__medrm in col_names)
    if is_out_series:
        hpq__wgby = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        lgcgo__jyeyw += f"""  return bodo.hiframes.pd_series_ext.init_series({ikxw__rypln}, {jobw__egnoc}, {hpq__wgby})
"""
        zbdp__map = {}
        exec(lgcgo__jyeyw, {'bodo': bodo}, zbdp__map)
        return zbdp__map['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw,
        col_names, ikxw__rypln, jobw__egnoc, extra_globals=egeut__lmbyj)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    lgcgo__jyeyw = 'def impl(I, idx):\n'
    lgcgo__jyeyw += '  df = I._obj\n'
    rzjt__nprl = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pgzbe__medrm]})[{idx}]'
         for pgzbe__medrm in col_names)
    lgcgo__jyeyw += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    lgcgo__jyeyw += f"""  return bodo.hiframes.pd_series_ext.init_series(({rzjt__nprl},), row_idx, None)
"""
    zbdp__map = {}
    exec(lgcgo__jyeyw, {'bodo': bodo}, zbdp__map)
    impl = zbdp__map['impl']
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
        yrfkw__aiv = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(yrfkw__aiv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        axsn__jmak = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, axsn__jmak)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        tedlz__trh, = args
        zoql__evza = signature.return_type
        gvdvs__gkc = cgutils.create_struct_proxy(zoql__evza)(context, builder)
        gvdvs__gkc.obj = tedlz__trh
        context.nrt.incref(builder, signature.args[0], tedlz__trh)
        return gvdvs__gkc._getvalue()
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
        lgcgo__jyeyw = 'def impl(I, idx):\n'
        lgcgo__jyeyw += '  df = I._obj\n'
        lgcgo__jyeyw += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        jobw__egnoc = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            ikxw__rypln = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            ikxw__rypln = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pgzbe__medrm]})[idx_t]'
                 for pgzbe__medrm in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw, df.
            columns, ikxw__rypln, jobw__egnoc)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        xhs__zwefr = idx.types[1]
        if is_overload_constant_str(xhs__zwefr):
            nwi__bbw = get_overload_const_str(xhs__zwefr)
            vpej__ilhee = df.columns.index(nwi__bbw)

            def impl_col_name(I, idx):
                df = I._obj
                jobw__egnoc = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                ndc__alrov = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, vpej__ilhee)
                return bodo.hiframes.pd_series_ext.init_series(ndc__alrov,
                    jobw__egnoc, nwi__bbw).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(xhs__zwefr):
            col_idx_list = get_overload_const_list(xhs__zwefr)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(pgzbe__medrm in df.
                column_index for pgzbe__medrm in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    rznzs__vfivt = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for qpycz__yafh, zfy__gtsq in enumerate(col_idx_list):
            if zfy__gtsq:
                rznzs__vfivt.append(qpycz__yafh)
                col_names.append(df.columns[qpycz__yafh])
    else:
        col_names = col_idx_list
        rznzs__vfivt = [df.column_index[pgzbe__medrm] for pgzbe__medrm in
            col_idx_list]
    egeut__lmbyj = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        egeut__lmbyj = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            rznzs__vfivt))}
        ikxw__rypln = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        ikxw__rypln = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in rznzs__vfivt)
    jobw__egnoc = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    lgcgo__jyeyw = 'def impl(I, idx):\n'
    lgcgo__jyeyw += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(lgcgo__jyeyw,
        col_names, ikxw__rypln, jobw__egnoc, extra_globals=egeut__lmbyj)


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
        yrfkw__aiv = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(yrfkw__aiv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        axsn__jmak = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, axsn__jmak)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        tedlz__trh, = args
        kqsj__ahuj = signature.return_type
        pjv__xhy = cgutils.create_struct_proxy(kqsj__ahuj)(context, builder)
        pjv__xhy.obj = tedlz__trh
        context.nrt.incref(builder, signature.args[0], tedlz__trh)
        return pjv__xhy._getvalue()
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
        vpej__ilhee = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            ndc__alrov = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                vpej__ilhee)
            return bodo.utils.conversion.box_if_dt64(ndc__alrov[idx[0]])
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
        vpej__ilhee = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[vpej__ilhee]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            ndc__alrov = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                vpej__ilhee)
            ndc__alrov[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    pjv__xhy = cgutils.create_struct_proxy(fromty)(context, builder, val)
    rah__pyr = context.cast(builder, pjv__xhy.obj, fromty.df_type, toty.df_type
        )
    dslvm__fcbz = cgutils.create_struct_proxy(toty)(context, builder)
    dslvm__fcbz.obj = rah__pyr
    return dslvm__fcbz._getvalue()
