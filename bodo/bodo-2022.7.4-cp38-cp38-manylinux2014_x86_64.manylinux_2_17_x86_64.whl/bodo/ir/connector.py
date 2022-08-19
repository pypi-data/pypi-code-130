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
    egtpv__usg = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    cucp__gfeof = []
    for nhrlp__lzh in node.out_vars:
        jeu__flu = typemap[nhrlp__lzh.name]
        if jeu__flu == types.none:
            continue
        sisf__wxhi = array_analysis._gen_shape_call(equiv_set, nhrlp__lzh,
            jeu__flu.ndim, None, egtpv__usg)
        equiv_set.insert_equiv(nhrlp__lzh, sisf__wxhi)
        cucp__gfeof.append(sisf__wxhi[0])
        equiv_set.define(nhrlp__lzh, set())
    if len(cucp__gfeof) > 1:
        equiv_set.insert_equiv(*cucp__gfeof)
    return [], egtpv__usg


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        fhw__xcz = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        fhw__xcz = Distribution.OneD_Var
    else:
        fhw__xcz = Distribution.OneD
    for wwkhg__ktrd in node.out_vars:
        if wwkhg__ktrd.name in array_dists:
            fhw__xcz = Distribution(min(fhw__xcz.value, array_dists[
                wwkhg__ktrd.name].value))
    for wwkhg__ktrd in node.out_vars:
        array_dists[wwkhg__ktrd.name] = fhw__xcz


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
    for nhrlp__lzh, jeu__flu in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(nhrlp__lzh.name, jeu__flu, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    phs__hbt = []
    for nhrlp__lzh in node.out_vars:
        eze__aqg = visit_vars_inner(nhrlp__lzh, callback, cbdata)
        phs__hbt.append(eze__aqg)
    node.out_vars = phs__hbt
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for jthbz__pwilq in node.filters:
            for svw__wkupz in range(len(jthbz__pwilq)):
                ailor__xmq = jthbz__pwilq[svw__wkupz]
                jthbz__pwilq[svw__wkupz] = ailor__xmq[0], ailor__xmq[1
                    ], visit_vars_inner(ailor__xmq[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({wwkhg__ktrd.name for wwkhg__ktrd in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for zsdf__rag in node.filters:
            for wwkhg__ktrd in zsdf__rag:
                if isinstance(wwkhg__ktrd[2], ir.Var):
                    use_set.add(wwkhg__ktrd[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    vjod__bxc = set(wwkhg__ktrd.name for wwkhg__ktrd in node.out_vars)
    return set(), vjod__bxc


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    phs__hbt = []
    for nhrlp__lzh in node.out_vars:
        eze__aqg = replace_vars_inner(nhrlp__lzh, var_dict)
        phs__hbt.append(eze__aqg)
    node.out_vars = phs__hbt
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for jthbz__pwilq in node.filters:
            for svw__wkupz in range(len(jthbz__pwilq)):
                ailor__xmq = jthbz__pwilq[svw__wkupz]
                jthbz__pwilq[svw__wkupz] = ailor__xmq[0], ailor__xmq[1
                    ], replace_vars_inner(ailor__xmq[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for nhrlp__lzh in node.out_vars:
        qmvl__zjdoo = definitions[nhrlp__lzh.name]
        if node not in qmvl__zjdoo:
            qmvl__zjdoo.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        sda__deq = [wwkhg__ktrd[2] for zsdf__rag in filters for wwkhg__ktrd in
            zsdf__rag]
        iijg__khs = set()
        for oiih__asqkh in sda__deq:
            if isinstance(oiih__asqkh, ir.Var):
                if oiih__asqkh.name not in iijg__khs:
                    filter_vars.append(oiih__asqkh)
                iijg__khs.add(oiih__asqkh.name)
        return {wwkhg__ktrd.name: f'f{svw__wkupz}' for svw__wkupz,
            wwkhg__ktrd in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {svw__wkupz for svw__wkupz in used_columns if svw__wkupz <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    bjo__agd = {}
    for svw__wkupz, zde__bmhvm in enumerate(df_type.data):
        if isinstance(zde__bmhvm, bodo.IntegerArrayType):
            yje__uiv = zde__bmhvm.get_pandas_scalar_type_instance
            if yje__uiv not in bjo__agd:
                bjo__agd[yje__uiv] = []
            bjo__agd[yje__uiv].append(df.columns[svw__wkupz])
    for jeu__flu, asxsv__zkb in bjo__agd.items():
        df[asxsv__zkb] = df[asxsv__zkb].astype(jeu__flu)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols, require_one_column=True):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    dxt__tqmj = node.out_vars[0].name
    assert isinstance(typemap[dxt__tqmj], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, yrv__giz, yaak__gpryu = get_live_column_nums_block(
            column_live_map, equiv_vars, dxt__tqmj)
        if not (yrv__giz or yaak__gpryu):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns and require_one_column:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    hdy__ecg = False
    if array_dists is not None:
        wlau__zqr = node.out_vars[0].name
        hdy__ecg = array_dists[wlau__zqr] in (Distribution.OneD,
            Distribution.OneD_Var)
        bkcv__wbw = node.out_vars[1].name
        assert typemap[bkcv__wbw] == types.none or not hdy__ecg or array_dists[
            bkcv__wbw] in (Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return hdy__ecg


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    cod__zwh = 'None'
    exxxa__blu = 'None'
    if filters:
        gssuc__hkg = []
        xymlk__frod = []
        ylc__kpt = False
        orig_colname_map = {nnc__zntl: svw__wkupz for svw__wkupz, nnc__zntl in
            enumerate(col_names)}
        for jthbz__pwilq in filters:
            lcnh__czzjm = []
            mopt__qaj = []
            for wwkhg__ktrd in jthbz__pwilq:
                if isinstance(wwkhg__ktrd[2], ir.Var):
                    flo__aclo, dfwzz__isqu = determine_filter_cast(
                        original_out_types, typemap, wwkhg__ktrd,
                        orig_colname_map, partition_names, source)
                    if wwkhg__ktrd[1] == 'in':
                        uleff__vuf = (
                            f"(ds.field('{wwkhg__ktrd[0]}').isin({filter_map[wwkhg__ktrd[2].name]}))"
                            )
                    else:
                        uleff__vuf = (
                            f"(ds.field('{wwkhg__ktrd[0]}'){flo__aclo} {wwkhg__ktrd[1]} ds.scalar({filter_map[wwkhg__ktrd[2].name]}){dfwzz__isqu})"
                            )
                else:
                    assert wwkhg__ktrd[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if wwkhg__ktrd[1] == 'is not':
                        sfy__tuore = '~'
                    else:
                        sfy__tuore = ''
                    uleff__vuf = (
                        f"({sfy__tuore}ds.field('{wwkhg__ktrd[0]}').is_null())"
                        )
                mopt__qaj.append(uleff__vuf)
                if not ylc__kpt:
                    if wwkhg__ktrd[0] in partition_names and isinstance(
                        wwkhg__ktrd[2], ir.Var):
                        if output_dnf:
                            pgcrw__ogdux = (
                                f"('{wwkhg__ktrd[0]}', '{wwkhg__ktrd[1]}', {filter_map[wwkhg__ktrd[2].name]})"
                                )
                        else:
                            pgcrw__ogdux = uleff__vuf
                        lcnh__czzjm.append(pgcrw__ogdux)
                    elif wwkhg__ktrd[0] in partition_names and not isinstance(
                        wwkhg__ktrd[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            pgcrw__ogdux = (
                                f"('{wwkhg__ktrd[0]}', '{wwkhg__ktrd[1]}', '{wwkhg__ktrd[2]}')"
                                )
                        else:
                            pgcrw__ogdux = uleff__vuf
                        lcnh__czzjm.append(pgcrw__ogdux)
            bsp__sqfxu = ''
            if lcnh__czzjm:
                if output_dnf:
                    bsp__sqfxu = ', '.join(lcnh__czzjm)
                else:
                    bsp__sqfxu = ' & '.join(lcnh__czzjm)
            else:
                ylc__kpt = True
            vyoy__mhlw = ' & '.join(mopt__qaj)
            if bsp__sqfxu:
                if output_dnf:
                    gssuc__hkg.append(f'[{bsp__sqfxu}]')
                else:
                    gssuc__hkg.append(f'({bsp__sqfxu})')
            xymlk__frod.append(f'({vyoy__mhlw})')
        if output_dnf:
            mgd__fpt = ', '.join(gssuc__hkg)
        else:
            mgd__fpt = ' | '.join(gssuc__hkg)
        suwcq__sskn = ' | '.join(xymlk__frod)
        if mgd__fpt and not ylc__kpt:
            if output_dnf:
                cod__zwh = f'[{mgd__fpt}]'
            else:
                cod__zwh = f'({mgd__fpt})'
        exxxa__blu = f'({suwcq__sskn})'
    return cod__zwh, exxxa__blu


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    pqub__aopun = filter_val[0]
    mcnsc__ihro = col_types[orig_colname_map[pqub__aopun]]
    jfxiz__khd = bodo.utils.typing.element_type(mcnsc__ihro)
    if source == 'parquet' and pqub__aopun in partition_names:
        if jfxiz__khd == types.unicode_type:
            wszsa__tnack = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(jfxiz__khd, types.Integer):
            wszsa__tnack = f'.cast(pyarrow.{jfxiz__khd.name}(), safe=False)'
        else:
            wszsa__tnack = ''
    else:
        wszsa__tnack = ''
    ucd__jje = typemap[filter_val[2].name]
    if isinstance(ucd__jje, (types.List, types.Set)):
        ghuc__jqc = ucd__jje.dtype
    else:
        ghuc__jqc = ucd__jje
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(jfxiz__khd,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ghuc__jqc,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([jfxiz__khd, ghuc__jqc]):
        if not bodo.utils.typing.is_safe_arrow_cast(jfxiz__khd, ghuc__jqc):
            raise BodoError(
                f'Unsupported Arrow cast from {jfxiz__khd} to {ghuc__jqc} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if jfxiz__khd == types.unicode_type and ghuc__jqc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ghuc__jqc == types.unicode_type and jfxiz__khd in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(ucd__jje, (types.List, types.Set)):
                ffcbk__kged = 'list' if isinstance(ucd__jje, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {ffcbk__kged} values with isin filter pushdown.'
                    )
            return wszsa__tnack, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif jfxiz__khd == bodo.datetime_date_type and ghuc__jqc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ghuc__jqc == bodo.datetime_date_type and jfxiz__khd in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return wszsa__tnack, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return wszsa__tnack, ''
