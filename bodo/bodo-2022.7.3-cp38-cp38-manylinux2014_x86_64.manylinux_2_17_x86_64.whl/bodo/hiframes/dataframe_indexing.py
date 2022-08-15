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
            dys__egeh = idx
            rvlqg__cszt = df.data
            ctmsr__sql = df.columns
            ipuh__ynwgr = self.replace_range_with_numeric_idx_if_needed(df,
                dys__egeh)
            pkoti__kvkjf = DataFrameType(rvlqg__cszt, ipuh__ynwgr,
                ctmsr__sql, is_table_format=df.is_table_format)
            return pkoti__kvkjf(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            rsg__rhxbp = idx.types[0]
            jqbm__jvw = idx.types[1]
            if isinstance(rsg__rhxbp, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(jqbm__jvw):
                    oygiy__qpidi = get_overload_const_str(jqbm__jvw)
                    if oygiy__qpidi not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, oygiy__qpidi))
                    qhkr__cbd = df.columns.index(oygiy__qpidi)
                    return df.data[qhkr__cbd].dtype(*args)
                if isinstance(jqbm__jvw, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(rsg__rhxbp
                ) and rsg__rhxbp.dtype == types.bool_ or isinstance(rsg__rhxbp,
                types.SliceType):
                ipuh__ynwgr = self.replace_range_with_numeric_idx_if_needed(df,
                    rsg__rhxbp)
                if is_overload_constant_str(jqbm__jvw):
                    lhdt__tzayg = get_overload_const_str(jqbm__jvw)
                    if lhdt__tzayg not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {lhdt__tzayg}'
                            )
                    qhkr__cbd = df.columns.index(lhdt__tzayg)
                    smn__sbeo = df.data[qhkr__cbd]
                    xyw__yqmrl = smn__sbeo.dtype
                    osap__qbb = types.literal(df.columns[qhkr__cbd])
                    pkoti__kvkjf = bodo.SeriesType(xyw__yqmrl, smn__sbeo,
                        ipuh__ynwgr, osap__qbb)
                    return pkoti__kvkjf(*args)
                if isinstance(jqbm__jvw, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(jqbm__jvw):
                    wpnmo__dxn = get_overload_const_list(jqbm__jvw)
                    ztlco__gqgiv = types.unliteral(jqbm__jvw)
                    if ztlco__gqgiv.dtype == types.bool_:
                        if len(df.columns) != len(wpnmo__dxn):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {wpnmo__dxn} has {len(wpnmo__dxn)} values'
                                )
                        oebq__gnnyn = []
                        gwbm__yxm = []
                        for wog__uoqq in range(len(wpnmo__dxn)):
                            if wpnmo__dxn[wog__uoqq]:
                                oebq__gnnyn.append(df.columns[wog__uoqq])
                                gwbm__yxm.append(df.data[wog__uoqq])
                        srfz__fuup = tuple()
                        ydhrb__rab = df.is_table_format and len(oebq__gnnyn
                            ) > 0 and len(oebq__gnnyn
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        pkoti__kvkjf = DataFrameType(tuple(gwbm__yxm),
                            ipuh__ynwgr, tuple(oebq__gnnyn),
                            is_table_format=ydhrb__rab)
                        return pkoti__kvkjf(*args)
                    elif ztlco__gqgiv.dtype == bodo.string_type:
                        srfz__fuup, gwbm__yxm = (
                            get_df_getitem_kept_cols_and_data(df, wpnmo__dxn))
                        ydhrb__rab = df.is_table_format and len(wpnmo__dxn
                            ) > 0 and len(wpnmo__dxn
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        pkoti__kvkjf = DataFrameType(gwbm__yxm, ipuh__ynwgr,
                            srfz__fuup, is_table_format=ydhrb__rab)
                        return pkoti__kvkjf(*args)
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
                oebq__gnnyn = []
                gwbm__yxm = []
                for wog__uoqq, tuisq__kkhi in enumerate(df.columns):
                    if tuisq__kkhi[0] != ind_val:
                        continue
                    oebq__gnnyn.append(tuisq__kkhi[1] if len(tuisq__kkhi) ==
                        2 else tuisq__kkhi[1:])
                    gwbm__yxm.append(df.data[wog__uoqq])
                smn__sbeo = tuple(gwbm__yxm)
                psvs__eblvl = df.index
                cjl__gihq = tuple(oebq__gnnyn)
                pkoti__kvkjf = DataFrameType(smn__sbeo, psvs__eblvl, cjl__gihq)
                return pkoti__kvkjf(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                qhkr__cbd = df.columns.index(ind_val)
                smn__sbeo = df.data[qhkr__cbd]
                xyw__yqmrl = smn__sbeo.dtype
                psvs__eblvl = df.index
                osap__qbb = types.literal(df.columns[qhkr__cbd])
                pkoti__kvkjf = bodo.SeriesType(xyw__yqmrl, smn__sbeo,
                    psvs__eblvl, osap__qbb)
                return pkoti__kvkjf(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            smn__sbeo = df.data
            psvs__eblvl = self.replace_range_with_numeric_idx_if_needed(df, ind
                )
            cjl__gihq = df.columns
            pkoti__kvkjf = DataFrameType(smn__sbeo, psvs__eblvl, cjl__gihq,
                is_table_format=df.is_table_format)
            return pkoti__kvkjf(*args)
        elif is_overload_constant_list(ind):
            pzyx__tqd = get_overload_const_list(ind)
            cjl__gihq, smn__sbeo = get_df_getitem_kept_cols_and_data(df,
                pzyx__tqd)
            psvs__eblvl = df.index
            ydhrb__rab = df.is_table_format and len(pzyx__tqd) > 0 and len(
                pzyx__tqd) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            pkoti__kvkjf = DataFrameType(smn__sbeo, psvs__eblvl, cjl__gihq,
                is_table_format=ydhrb__rab)
            return pkoti__kvkjf(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        ipuh__ynwgr = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return ipuh__ynwgr


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for ece__uyv in cols_to_keep_list:
        if ece__uyv not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(ece__uyv, df.columns))
    cjl__gihq = tuple(cols_to_keep_list)
    smn__sbeo = tuple(df.data[df.column_index[qwchb__tmmt]] for qwchb__tmmt in
        cjl__gihq)
    return cjl__gihq, smn__sbeo


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
            oebq__gnnyn = []
            gwbm__yxm = []
            for wog__uoqq, tuisq__kkhi in enumerate(df.columns):
                if tuisq__kkhi[0] != ind_val:
                    continue
                oebq__gnnyn.append(tuisq__kkhi[1] if len(tuisq__kkhi) == 2 else
                    tuisq__kkhi[1:])
                gwbm__yxm.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(wog__uoqq))
            alsb__qiazt = 'def impl(df, ind):\n'
            eug__relrh = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt,
                oebq__gnnyn, ', '.join(gwbm__yxm), eug__relrh)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        pzyx__tqd = get_overload_const_list(ind)
        for ece__uyv in pzyx__tqd:
            if ece__uyv not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(ece__uyv, df.columns))
        hflf__qpzc = None
        if df.is_table_format and len(pzyx__tqd) > 0 and len(pzyx__tqd
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            csxdz__rhh = [df.column_index[ece__uyv] for ece__uyv in pzyx__tqd]
            hflf__qpzc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (csxdz__rhh))}
            gwbm__yxm = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            gwbm__yxm = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ece__uyv]}).copy()'
                 for ece__uyv in pzyx__tqd)
        alsb__qiazt = 'def impl(df, ind):\n'
        eug__relrh = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt,
            pzyx__tqd, gwbm__yxm, eug__relrh, extra_globals=hflf__qpzc)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        alsb__qiazt = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            alsb__qiazt += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        eug__relrh = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            gwbm__yxm = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            gwbm__yxm = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ece__uyv]})[ind]'
                 for ece__uyv in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt, df.
            columns, gwbm__yxm, eug__relrh)
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
        qwchb__tmmt = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(qwchb__tmmt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ore__upis = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, ore__upis)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        vjkkr__vtuj, = args
        ecwlf__ubj = signature.return_type
        ymn__tjns = cgutils.create_struct_proxy(ecwlf__ubj)(context, builder)
        ymn__tjns.obj = vjkkr__vtuj
        context.nrt.incref(builder, signature.args[0], vjkkr__vtuj)
        return ymn__tjns._getvalue()
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
        pza__mxjan = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            oda__phazq = get_overload_const_int(idx.types[1])
            if oda__phazq < 0 or oda__phazq >= pza__mxjan:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            jnpj__qgqyl = [oda__phazq]
        else:
            is_out_series = False
            jnpj__qgqyl = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= pza__mxjan for
                ind in jnpj__qgqyl):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[jnpj__qgqyl])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                oda__phazq = jnpj__qgqyl[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, oda__phazq)
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
    alsb__qiazt = 'def impl(I, idx):\n'
    alsb__qiazt += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        alsb__qiazt += f'  idx_t = {idx}\n'
    else:
        alsb__qiazt += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    eug__relrh = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    hflf__qpzc = None
    if df.is_table_format and not is_out_series:
        csxdz__rhh = [df.column_index[ece__uyv] for ece__uyv in col_names]
        hflf__qpzc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            csxdz__rhh))}
        gwbm__yxm = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        gwbm__yxm = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ece__uyv]})[idx_t]'
             for ece__uyv in col_names)
    if is_out_series:
        ycgd__qha = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        alsb__qiazt += f"""  return bodo.hiframes.pd_series_ext.init_series({gwbm__yxm}, {eug__relrh}, {ycgd__qha})
"""
        kqsq__dowaj = {}
        exec(alsb__qiazt, {'bodo': bodo}, kqsq__dowaj)
        return kqsq__dowaj['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt, col_names,
        gwbm__yxm, eug__relrh, extra_globals=hflf__qpzc)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    alsb__qiazt = 'def impl(I, idx):\n'
    alsb__qiazt += '  df = I._obj\n'
    yqnmm__ozel = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ece__uyv]})[{idx}]'
         for ece__uyv in col_names)
    alsb__qiazt += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    alsb__qiazt += f"""  return bodo.hiframes.pd_series_ext.init_series(({yqnmm__ozel},), row_idx, None)
"""
    kqsq__dowaj = {}
    exec(alsb__qiazt, {'bodo': bodo}, kqsq__dowaj)
    impl = kqsq__dowaj['impl']
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
        qwchb__tmmt = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(qwchb__tmmt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ore__upis = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, ore__upis)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        vjkkr__vtuj, = args
        quqrl__epjm = signature.return_type
        jwul__vqsql = cgutils.create_struct_proxy(quqrl__epjm)(context, builder
            )
        jwul__vqsql.obj = vjkkr__vtuj
        context.nrt.incref(builder, signature.args[0], vjkkr__vtuj)
        return jwul__vqsql._getvalue()
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
        alsb__qiazt = 'def impl(I, idx):\n'
        alsb__qiazt += '  df = I._obj\n'
        alsb__qiazt += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        eug__relrh = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            gwbm__yxm = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            gwbm__yxm = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ece__uyv]})[idx_t]'
                 for ece__uyv in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt, df.
            columns, gwbm__yxm, eug__relrh)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        shf__gva = idx.types[1]
        if is_overload_constant_str(shf__gva):
            iaxu__zpbra = get_overload_const_str(shf__gva)
            oda__phazq = df.columns.index(iaxu__zpbra)

            def impl_col_name(I, idx):
                df = I._obj
                eug__relrh = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                jtvag__lbw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, oda__phazq)
                return bodo.hiframes.pd_series_ext.init_series(jtvag__lbw,
                    eug__relrh, iaxu__zpbra).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(shf__gva):
            col_idx_list = get_overload_const_list(shf__gva)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(ece__uyv in df.column_index for
                ece__uyv in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    jnpj__qgqyl = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for wog__uoqq, tezgg__gtk in enumerate(col_idx_list):
            if tezgg__gtk:
                jnpj__qgqyl.append(wog__uoqq)
                col_names.append(df.columns[wog__uoqq])
    else:
        col_names = col_idx_list
        jnpj__qgqyl = [df.column_index[ece__uyv] for ece__uyv in col_idx_list]
    hflf__qpzc = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        hflf__qpzc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            jnpj__qgqyl))}
        gwbm__yxm = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        gwbm__yxm = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in jnpj__qgqyl)
    eug__relrh = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    alsb__qiazt = 'def impl(I, idx):\n'
    alsb__qiazt += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(alsb__qiazt, col_names,
        gwbm__yxm, eug__relrh, extra_globals=hflf__qpzc)


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
        qwchb__tmmt = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(qwchb__tmmt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ore__upis = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, ore__upis)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        vjkkr__vtuj, = args
        qljm__muqsu = signature.return_type
        cxja__nxxo = cgutils.create_struct_proxy(qljm__muqsu)(context, builder)
        cxja__nxxo.obj = vjkkr__vtuj
        context.nrt.incref(builder, signature.args[0], vjkkr__vtuj)
        return cxja__nxxo._getvalue()
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
        oda__phazq = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            jtvag__lbw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                oda__phazq)
            return bodo.utils.conversion.box_if_dt64(jtvag__lbw[idx[0]])
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
        oda__phazq = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[oda__phazq]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            jtvag__lbw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                oda__phazq)
            jtvag__lbw[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    cxja__nxxo = cgutils.create_struct_proxy(fromty)(context, builder, val)
    xibk__gqyue = context.cast(builder, cxja__nxxo.obj, fromty.df_type,
        toty.df_type)
    hmyvq__vjo = cgutils.create_struct_proxy(toty)(context, builder)
    hmyvq__vjo.obj = xibk__gqyue
    return hmyvq__vjo._getvalue()
