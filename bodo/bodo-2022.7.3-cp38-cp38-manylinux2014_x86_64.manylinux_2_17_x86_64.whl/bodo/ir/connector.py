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
    vlxr__apijg = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    ysv__zgz = []
    for nqjep__eyro in node.out_vars:
        lyfdi__lfn = typemap[nqjep__eyro.name]
        if lyfdi__lfn == types.none:
            continue
        axdxp__iegqe = array_analysis._gen_shape_call(equiv_set,
            nqjep__eyro, lyfdi__lfn.ndim, None, vlxr__apijg)
        equiv_set.insert_equiv(nqjep__eyro, axdxp__iegqe)
        ysv__zgz.append(axdxp__iegqe[0])
        equiv_set.define(nqjep__eyro, set())
    if len(ysv__zgz) > 1:
        equiv_set.insert_equiv(*ysv__zgz)
    return [], vlxr__apijg


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        uqg__nejvl = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        uqg__nejvl = Distribution.OneD_Var
    else:
        uqg__nejvl = Distribution.OneD
    for ksf__gosmz in node.out_vars:
        if ksf__gosmz.name in array_dists:
            uqg__nejvl = Distribution(min(uqg__nejvl.value, array_dists[
                ksf__gosmz.name].value))
    for ksf__gosmz in node.out_vars:
        array_dists[ksf__gosmz.name] = uqg__nejvl


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
    for nqjep__eyro, lyfdi__lfn in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(nqjep__eyro.name, lyfdi__lfn, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    mvr__geh = []
    for nqjep__eyro in node.out_vars:
        afdj__lxoob = visit_vars_inner(nqjep__eyro, callback, cbdata)
        mvr__geh.append(afdj__lxoob)
    node.out_vars = mvr__geh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for unq__iyd in node.filters:
            for mozl__jmjv in range(len(unq__iyd)):
                xxa__ytw = unq__iyd[mozl__jmjv]
                unq__iyd[mozl__jmjv] = xxa__ytw[0], xxa__ytw[1
                    ], visit_vars_inner(xxa__ytw[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({ksf__gosmz.name for ksf__gosmz in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for cvy__nzy in node.filters:
            for ksf__gosmz in cvy__nzy:
                if isinstance(ksf__gosmz[2], ir.Var):
                    use_set.add(ksf__gosmz[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    anez__ntvo = set(ksf__gosmz.name for ksf__gosmz in node.out_vars)
    return set(), anez__ntvo


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    mvr__geh = []
    for nqjep__eyro in node.out_vars:
        afdj__lxoob = replace_vars_inner(nqjep__eyro, var_dict)
        mvr__geh.append(afdj__lxoob)
    node.out_vars = mvr__geh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for unq__iyd in node.filters:
            for mozl__jmjv in range(len(unq__iyd)):
                xxa__ytw = unq__iyd[mozl__jmjv]
                unq__iyd[mozl__jmjv] = xxa__ytw[0], xxa__ytw[1
                    ], replace_vars_inner(xxa__ytw[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for nqjep__eyro in node.out_vars:
        agy__tyll = definitions[nqjep__eyro.name]
        if node not in agy__tyll:
            agy__tyll.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        zmaf__dal = [ksf__gosmz[2] for cvy__nzy in filters for ksf__gosmz in
            cvy__nzy]
        opxfx__ajj = set()
        for pouys__joig in zmaf__dal:
            if isinstance(pouys__joig, ir.Var):
                if pouys__joig.name not in opxfx__ajj:
                    filter_vars.append(pouys__joig)
                opxfx__ajj.add(pouys__joig.name)
        return {ksf__gosmz.name: f'f{mozl__jmjv}' for mozl__jmjv,
            ksf__gosmz in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {mozl__jmjv for mozl__jmjv in used_columns if mozl__jmjv <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    jdb__azee = {}
    for mozl__jmjv, fkx__gyouv in enumerate(df_type.data):
        if isinstance(fkx__gyouv, bodo.IntegerArrayType):
            kmabj__enh = fkx__gyouv.get_pandas_scalar_type_instance
            if kmabj__enh not in jdb__azee:
                jdb__azee[kmabj__enh] = []
            jdb__azee[kmabj__enh].append(df.columns[mozl__jmjv])
    for lyfdi__lfn, nge__ymzx in jdb__azee.items():
        df[nge__ymzx] = df[nge__ymzx].astype(lyfdi__lfn)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols, require_one_column=True):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    zurn__itin = node.out_vars[0].name
    assert isinstance(typemap[zurn__itin], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, zxx__huy, ors__bll = get_live_column_nums_block(
            column_live_map, equiv_vars, zurn__itin)
        if not (zxx__huy or ors__bll):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns and require_one_column:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    remfp__ufhl = False
    if array_dists is not None:
        llbgm__ntiw = node.out_vars[0].name
        remfp__ufhl = array_dists[llbgm__ntiw] in (Distribution.OneD,
            Distribution.OneD_Var)
        xybe__wrlo = node.out_vars[1].name
        assert typemap[xybe__wrlo
            ] == types.none or not remfp__ufhl or array_dists[xybe__wrlo] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return remfp__ufhl


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    dgecg__wxg = 'None'
    chx__kubhv = 'None'
    if filters:
        mlbah__ehn = []
        pvf__ifk = []
        byjj__kbi = False
        orig_colname_map = {xjiz__klr: mozl__jmjv for mozl__jmjv, xjiz__klr in
            enumerate(col_names)}
        for unq__iyd in filters:
            nam__gsmkb = []
            rfd__dlcal = []
            for ksf__gosmz in unq__iyd:
                if isinstance(ksf__gosmz[2], ir.Var):
                    eyhvg__wus, kdnzy__ydjaq = determine_filter_cast(
                        original_out_types, typemap, ksf__gosmz,
                        orig_colname_map, partition_names, source)
                    if ksf__gosmz[1] == 'in':
                        gvuw__lzv = (
                            f"(ds.field('{ksf__gosmz[0]}').isin({filter_map[ksf__gosmz[2].name]}))"
                            )
                    else:
                        gvuw__lzv = (
                            f"(ds.field('{ksf__gosmz[0]}'){eyhvg__wus} {ksf__gosmz[1]} ds.scalar({filter_map[ksf__gosmz[2].name]}){kdnzy__ydjaq})"
                            )
                else:
                    assert ksf__gosmz[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if ksf__gosmz[1] == 'is not':
                        tashz__meko = '~'
                    else:
                        tashz__meko = ''
                    gvuw__lzv = (
                        f"({tashz__meko}ds.field('{ksf__gosmz[0]}').is_null())"
                        )
                rfd__dlcal.append(gvuw__lzv)
                if not byjj__kbi:
                    if ksf__gosmz[0] in partition_names and isinstance(
                        ksf__gosmz[2], ir.Var):
                        if output_dnf:
                            kato__xmp = (
                                f"('{ksf__gosmz[0]}', '{ksf__gosmz[1]}', {filter_map[ksf__gosmz[2].name]})"
                                )
                        else:
                            kato__xmp = gvuw__lzv
                        nam__gsmkb.append(kato__xmp)
                    elif ksf__gosmz[0] in partition_names and not isinstance(
                        ksf__gosmz[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            kato__xmp = (
                                f"('{ksf__gosmz[0]}', '{ksf__gosmz[1]}', '{ksf__gosmz[2]}')"
                                )
                        else:
                            kato__xmp = gvuw__lzv
                        nam__gsmkb.append(kato__xmp)
            wuys__nsmiz = ''
            if nam__gsmkb:
                if output_dnf:
                    wuys__nsmiz = ', '.join(nam__gsmkb)
                else:
                    wuys__nsmiz = ' & '.join(nam__gsmkb)
            else:
                byjj__kbi = True
            lesjf__mkom = ' & '.join(rfd__dlcal)
            if wuys__nsmiz:
                if output_dnf:
                    mlbah__ehn.append(f'[{wuys__nsmiz}]')
                else:
                    mlbah__ehn.append(f'({wuys__nsmiz})')
            pvf__ifk.append(f'({lesjf__mkom})')
        if output_dnf:
            pwj__wkw = ', '.join(mlbah__ehn)
        else:
            pwj__wkw = ' | '.join(mlbah__ehn)
        dtl__ppbcr = ' | '.join(pvf__ifk)
        if pwj__wkw and not byjj__kbi:
            if output_dnf:
                dgecg__wxg = f'[{pwj__wkw}]'
            else:
                dgecg__wxg = f'({pwj__wkw})'
        chx__kubhv = f'({dtl__ppbcr})'
    return dgecg__wxg, chx__kubhv


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    rqxu__fdjc = filter_val[0]
    akp__ywjc = col_types[orig_colname_map[rqxu__fdjc]]
    sgzs__qullr = bodo.utils.typing.element_type(akp__ywjc)
    if source == 'parquet' and rqxu__fdjc in partition_names:
        if sgzs__qullr == types.unicode_type:
            mwujb__uhzgp = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(sgzs__qullr, types.Integer):
            mwujb__uhzgp = f'.cast(pyarrow.{sgzs__qullr.name}(), safe=False)'
        else:
            mwujb__uhzgp = ''
    else:
        mwujb__uhzgp = ''
    gzcdq__sgxg = typemap[filter_val[2].name]
    if isinstance(gzcdq__sgxg, (types.List, types.Set)):
        usb__pses = gzcdq__sgxg.dtype
    else:
        usb__pses = gzcdq__sgxg
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(sgzs__qullr,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(usb__pses,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([sgzs__qullr, usb__pses]):
        if not bodo.utils.typing.is_safe_arrow_cast(sgzs__qullr, usb__pses):
            raise BodoError(
                f'Unsupported Arrow cast from {sgzs__qullr} to {usb__pses} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if sgzs__qullr == types.unicode_type and usb__pses in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif usb__pses == types.unicode_type and sgzs__qullr in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(gzcdq__sgxg, (types.List, types.Set)):
                zbu__eds = 'list' if isinstance(gzcdq__sgxg, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {zbu__eds} values with isin filter pushdown.'
                    )
            return mwujb__uhzgp, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif sgzs__qullr == bodo.datetime_date_type and usb__pses in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif usb__pses == bodo.datetime_date_type and sgzs__qullr in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return mwujb__uhzgp, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return mwujb__uhzgp, ''
