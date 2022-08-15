"""Helper information to keep table column deletion
pass organized. This contains information about all
table operations for optimizations.
"""
from typing import Dict, Tuple
from numba.core import ir, types
from bodo.hiframes.table import TableType
table_usecol_funcs = {('get_table_data', 'bodo.hiframes.table'), (
    'table_filter', 'bodo.hiframes.table'), ('table_subset',
    'bodo.hiframes.table'), ('set_table_data', 'bodo.hiframes.table'), (
    'set_table_data_null', 'bodo.hiframes.table'), (
    'generate_mappable_table_func', 'bodo.utils.table_utils'), (
    'table_astype', 'bodo.utils.table_utils'), ('generate_table_nbytes',
    'bodo.utils.table_utils'), ('table_concat', 'bodo.utils.table_utils'),
    ('py_data_to_cpp_table', 'bodo.libs.array'), ('logical_table_to_table',
    'bodo.hiframes.table')}


def is_table_use_column_ops(fdef: Tuple[str, str], args, typemap):
    return fdef in table_usecol_funcs and len(args) > 0 and isinstance(typemap
        [args[0].name], TableType)


def get_table_used_columns(fdef: Tuple[str, str], call_expr: ir.Expr,
    typemap: Dict[str, types.Type]):
    if fdef == ('get_table_data', 'bodo.hiframes.table'):
        jnxt__lxsic = typemap[call_expr.args[1].name].literal_value
        return {jnxt__lxsic}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        ldwp__aqb = dict(call_expr.kws)
        if 'used_cols' in ldwp__aqb:
            kmz__rlbyn = ldwp__aqb['used_cols']
            dql__vzpuu = typemap[kmz__rlbyn.name]
            dql__vzpuu = dql__vzpuu.instance_type
            return set(dql__vzpuu.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        kmz__rlbyn = call_expr.args[1]
        dql__vzpuu = typemap[kmz__rlbyn.name]
        dql__vzpuu = dql__vzpuu.instance_type
        return set(dql__vzpuu.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        hivv__tddr = call_expr.args[1]
        gwtus__jmix = typemap[hivv__tddr.name]
        gwtus__jmix = gwtus__jmix.instance_type
        bvu__euw = gwtus__jmix.meta
        ldwp__aqb = dict(call_expr.kws)
        if 'used_cols' in ldwp__aqb:
            kmz__rlbyn = ldwp__aqb['used_cols']
            dql__vzpuu = typemap[kmz__rlbyn.name]
            dql__vzpuu = dql__vzpuu.instance_type
            qopb__eehmy = set(dql__vzpuu.meta)
            bvncp__jyh = set()
            for meb__trb, kdjjq__qnca in enumerate(bvu__euw):
                if meb__trb in qopb__eehmy:
                    bvncp__jyh.add(kdjjq__qnca)
            return bvncp__jyh
        else:
            return set(bvu__euw)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        kwn__hyp = typemap[call_expr.args[2].name].instance_type.meta
        mibp__vfpc = len(typemap[call_expr.args[0].name].arr_types)
        return set(meb__trb for meb__trb in kwn__hyp if meb__trb < mibp__vfpc)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        tahsk__zmev = typemap[call_expr.args[2].name].instance_type.meta
        xquy__qrhoy = len(typemap[call_expr.args[0].name].arr_types)
        ldwp__aqb = dict(call_expr.kws)
        if 'used_cols' in ldwp__aqb:
            qopb__eehmy = set(typemap[ldwp__aqb['used_cols'].name].
                instance_type.meta)
            bqmi__ylkfv = set()
            for vvd__pagbq, rgreh__lczy in enumerate(tahsk__zmev):
                if vvd__pagbq in qopb__eehmy and rgreh__lczy < xquy__qrhoy:
                    bqmi__ylkfv.add(rgreh__lczy)
            return bqmi__ylkfv
        else:
            return set(meb__trb for meb__trb in tahsk__zmev if meb__trb <
                xquy__qrhoy)
    return None
