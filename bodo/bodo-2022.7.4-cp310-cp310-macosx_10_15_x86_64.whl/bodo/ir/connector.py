"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
import sys
from collections import defaultdict
from typing import Literal, Set, Tuple
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import get_live_column_nums_block
from bodo.utils.py_objs import install_py_obj_class
from bodo.utils.typing import BodoError
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    ehxt__apgw = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    rmjbr__qkdok = []
    for rqkmq__lcppk in node.out_vars:
        mwkb__kkiww = typemap[rqkmq__lcppk.name]
        if mwkb__kkiww == types.none:
            continue
        ohymi__wvzk = array_analysis._gen_shape_call(equiv_set,
            rqkmq__lcppk, mwkb__kkiww.ndim, None, ehxt__apgw)
        equiv_set.insert_equiv(rqkmq__lcppk, ohymi__wvzk)
        rmjbr__qkdok.append(ohymi__wvzk[0])
        equiv_set.define(rqkmq__lcppk, set())
    if len(rmjbr__qkdok) > 1:
        equiv_set.insert_equiv(*rmjbr__qkdok)
    return [], ehxt__apgw


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        plwi__hia = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        plwi__hia = Distribution.OneD_Var
    else:
        plwi__hia = Distribution.OneD
    for yfxi__mokn in node.out_vars:
        if yfxi__mokn.name in array_dists:
            plwi__hia = Distribution(min(plwi__hia.value, array_dists[
                yfxi__mokn.name].value))
    for yfxi__mokn in node.out_vars:
        array_dists[yfxi__mokn.name] = plwi__hia


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ in ('parquet', 'sql'):
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for rqkmq__lcppk, mwkb__kkiww in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(rqkmq__lcppk.name, mwkb__kkiww, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    qts__hgvh = []
    for rqkmq__lcppk in node.out_vars:
        qstdz__jgxq = visit_vars_inner(rqkmq__lcppk, callback, cbdata)
        qts__hgvh.append(qstdz__jgxq)
    node.out_vars = qts__hgvh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for gwqz__xdwvz in node.filters:
            for gqinh__llpwg in range(len(gwqz__xdwvz)):
                qdahu__zili = gwqz__xdwvz[gqinh__llpwg]
                gwqz__xdwvz[gqinh__llpwg] = qdahu__zili[0], qdahu__zili[1
                    ], visit_vars_inner(qdahu__zili[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({yfxi__mokn.name for yfxi__mokn in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for uegdn__zgrs in node.filters:
            for yfxi__mokn in uegdn__zgrs:
                if isinstance(yfxi__mokn[2], ir.Var):
                    use_set.add(yfxi__mokn[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    iuprd__aww = set(yfxi__mokn.name for yfxi__mokn in node.out_vars)
    return set(), iuprd__aww


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    qts__hgvh = []
    for rqkmq__lcppk in node.out_vars:
        qstdz__jgxq = replace_vars_inner(rqkmq__lcppk, var_dict)
        qts__hgvh.append(qstdz__jgxq)
    node.out_vars = qts__hgvh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for gwqz__xdwvz in node.filters:
            for gqinh__llpwg in range(len(gwqz__xdwvz)):
                qdahu__zili = gwqz__xdwvz[gqinh__llpwg]
                gwqz__xdwvz[gqinh__llpwg] = qdahu__zili[0], qdahu__zili[1
                    ], replace_vars_inner(qdahu__zili[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for rqkmq__lcppk in node.out_vars:
        mcqe__ery = definitions[rqkmq__lcppk.name]
        if node not in mcqe__ery:
            mcqe__ery.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        zxvjh__hmzld = [yfxi__mokn[2] for uegdn__zgrs in filters for
            yfxi__mokn in uegdn__zgrs]
        ivgab__bhnsy = set()
        for reg__xen in zxvjh__hmzld:
            if isinstance(reg__xen, ir.Var):
                if reg__xen.name not in ivgab__bhnsy:
                    filter_vars.append(reg__xen)
                ivgab__bhnsy.add(reg__xen.name)
        return {yfxi__mokn.name: f'f{gqinh__llpwg}' for gqinh__llpwg,
            yfxi__mokn in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {gqinh__llpwg for gqinh__llpwg in used_columns if gqinh__llpwg <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    iwlm__bqrj = {}
    for gqinh__llpwg, prvr__qjp in enumerate(df_type.data):
        if isinstance(prvr__qjp, bodo.IntegerArrayType):
            lfhen__huys = prvr__qjp.get_pandas_scalar_type_instance
            if lfhen__huys not in iwlm__bqrj:
                iwlm__bqrj[lfhen__huys] = []
            iwlm__bqrj[lfhen__huys].append(df.columns[gqinh__llpwg])
    for mwkb__kkiww, iaxm__lan in iwlm__bqrj.items():
        df[iaxm__lan] = df[iaxm__lan].astype(mwkb__kkiww)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols, require_one_column=True):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    jfry__rxk = node.out_vars[0].name
    assert isinstance(typemap[jfry__rxk], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, anxuv__fjfm, kaq__crnf = get_live_column_nums_block(
            column_live_map, equiv_vars, jfry__rxk)
        if not (anxuv__fjfm or kaq__crnf):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns and require_one_column:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    wsd__afnmm = False
    if array_dists is not None:
        wee__cdgu = node.out_vars[0].name
        wsd__afnmm = array_dists[wee__cdgu] in (Distribution.OneD,
            Distribution.OneD_Var)
        upwp__dxczd = node.out_vars[1].name
        assert typemap[upwp__dxczd
            ] == types.none or not wsd__afnmm or array_dists[upwp__dxczd] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return wsd__afnmm


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    usww__kuhi = 'None'
    bna__mpnr = 'None'
    if filters:
        gjhe__irqf = []
        mnh__gop = []
        icffr__qfk = False
        orig_colname_map = {bzmkp__jvxw: gqinh__llpwg for gqinh__llpwg,
            bzmkp__jvxw in enumerate(col_names)}
        for gwqz__xdwvz in filters:
            jsx__wakl = []
            cym__cvgn = []
            for yfxi__mokn in gwqz__xdwvz:
                if isinstance(yfxi__mokn[2], ir.Var):
                    gvorf__putw, apav__sypuh = determine_filter_cast(
                        original_out_types, typemap, yfxi__mokn,
                        orig_colname_map, partition_names, source)
                    if yfxi__mokn[1] == 'in':
                        qsza__mre = (
                            f"(ds.field('{yfxi__mokn[0]}').isin({filter_map[yfxi__mokn[2].name]}))"
                            )
                    else:
                        qsza__mre = (
                            f"(ds.field('{yfxi__mokn[0]}'){gvorf__putw} {yfxi__mokn[1]} ds.scalar({filter_map[yfxi__mokn[2].name]}){apav__sypuh})"
                            )
                else:
                    assert yfxi__mokn[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if yfxi__mokn[1] == 'is not':
                        rahxs__ccl = '~'
                    else:
                        rahxs__ccl = ''
                    qsza__mre = (
                        f"({rahxs__ccl}ds.field('{yfxi__mokn[0]}').is_null())")
                cym__cvgn.append(qsza__mre)
                if not icffr__qfk:
                    if yfxi__mokn[0] in partition_names and isinstance(
                        yfxi__mokn[2], ir.Var):
                        if output_dnf:
                            yoi__lfuy = (
                                f"('{yfxi__mokn[0]}', '{yfxi__mokn[1]}', {filter_map[yfxi__mokn[2].name]})"
                                )
                        else:
                            yoi__lfuy = qsza__mre
                        jsx__wakl.append(yoi__lfuy)
                    elif yfxi__mokn[0] in partition_names and not isinstance(
                        yfxi__mokn[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            yoi__lfuy = (
                                f"('{yfxi__mokn[0]}', '{yfxi__mokn[1]}', '{yfxi__mokn[2]}')"
                                )
                        else:
                            yoi__lfuy = qsza__mre
                        jsx__wakl.append(yoi__lfuy)
            vkoht__wtb = ''
            if jsx__wakl:
                if output_dnf:
                    vkoht__wtb = ', '.join(jsx__wakl)
                else:
                    vkoht__wtb = ' & '.join(jsx__wakl)
            else:
                icffr__qfk = True
            uwht__tfqcv = ' & '.join(cym__cvgn)
            if vkoht__wtb:
                if output_dnf:
                    gjhe__irqf.append(f'[{vkoht__wtb}]')
                else:
                    gjhe__irqf.append(f'({vkoht__wtb})')
            mnh__gop.append(f'({uwht__tfqcv})')
        if output_dnf:
            mlgt__sndmc = ', '.join(gjhe__irqf)
        else:
            mlgt__sndmc = ' | '.join(gjhe__irqf)
        bpht__xpik = ' | '.join(mnh__gop)
        if mlgt__sndmc and not icffr__qfk:
            if output_dnf:
                usww__kuhi = f'[{mlgt__sndmc}]'
            else:
                usww__kuhi = f'({mlgt__sndmc})'
        bna__mpnr = f'({bpht__xpik})'
    return usww__kuhi, bna__mpnr


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    fweio__ncrt = filter_val[0]
    dqflm__kix = col_types[orig_colname_map[fweio__ncrt]]
    wodc__wtudc = bodo.utils.typing.element_type(dqflm__kix)
    if source == 'parquet' and fweio__ncrt in partition_names:
        if wodc__wtudc == types.unicode_type:
            acl__uwe = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(wodc__wtudc, types.Integer):
            acl__uwe = f'.cast(pyarrow.{wodc__wtudc.name}(), safe=False)'
        else:
            acl__uwe = ''
    else:
        acl__uwe = ''
    zhikt__jpsb = typemap[filter_val[2].name]
    if isinstance(zhikt__jpsb, (types.List, types.Set)):
        fheg__gzlc = zhikt__jpsb.dtype
    else:
        fheg__gzlc = zhikt__jpsb
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(wodc__wtudc,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(fheg__gzlc,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([wodc__wtudc, fheg__gzlc]):
        if not bodo.utils.typing.is_safe_arrow_cast(wodc__wtudc, fheg__gzlc):
            raise BodoError(
                f'Unsupported Arrow cast from {wodc__wtudc} to {fheg__gzlc} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if wodc__wtudc == types.unicode_type and fheg__gzlc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif fheg__gzlc == types.unicode_type and wodc__wtudc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(zhikt__jpsb, (types.List, types.Set)):
                piyeh__wamu = 'list' if isinstance(zhikt__jpsb, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {piyeh__wamu} values with isin filter pushdown.'
                    )
            return acl__uwe, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif wodc__wtudc == bodo.datetime_date_type and fheg__gzlc in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif fheg__gzlc == bodo.datetime_date_type and wodc__wtudc in (bodo
            .datetime64ns, bodo.pd_timestamp_type):
            return acl__uwe, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return acl__uwe, ''
