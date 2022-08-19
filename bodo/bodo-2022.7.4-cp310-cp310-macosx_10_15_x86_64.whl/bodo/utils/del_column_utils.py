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
        kef__srb = typemap[call_expr.args[1].name].literal_value
        return {kef__srb}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        vbyl__lbzjn = dict(call_expr.kws)
        if 'used_cols' in vbyl__lbzjn:
            gyd__ciwka = vbyl__lbzjn['used_cols']
            dujuq__dnotw = typemap[gyd__ciwka.name]
            dujuq__dnotw = dujuq__dnotw.instance_type
            return set(dujuq__dnotw.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        gyd__ciwka = call_expr.args[1]
        dujuq__dnotw = typemap[gyd__ciwka.name]
        dujuq__dnotw = dujuq__dnotw.instance_type
        return set(dujuq__dnotw.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        xyrjq__rly = call_expr.args[1]
        bjn__inbzu = typemap[xyrjq__rly.name]
        bjn__inbzu = bjn__inbzu.instance_type
        oel__bxn = bjn__inbzu.meta
        vbyl__lbzjn = dict(call_expr.kws)
        if 'used_cols' in vbyl__lbzjn:
            gyd__ciwka = vbyl__lbzjn['used_cols']
            dujuq__dnotw = typemap[gyd__ciwka.name]
            dujuq__dnotw = dujuq__dnotw.instance_type
            cgfh__smxk = set(dujuq__dnotw.meta)
            qspow__qihtc = set()
            for sbra__ugi, cvzdn__iqt in enumerate(oel__bxn):
                if sbra__ugi in cgfh__smxk:
                    qspow__qihtc.add(cvzdn__iqt)
            return qspow__qihtc
        else:
            return set(oel__bxn)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        towx__sjz = typemap[call_expr.args[2].name].instance_type.meta
        cgwnz__ssv = len(typemap[call_expr.args[0].name].arr_types)
        return set(sbra__ugi for sbra__ugi in towx__sjz if sbra__ugi <
            cgwnz__ssv)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        iqs__nzi = typemap[call_expr.args[2].name].instance_type.meta
        cmeby__pcmml = len(typemap[call_expr.args[0].name].arr_types)
        vbyl__lbzjn = dict(call_expr.kws)
        if 'used_cols' in vbyl__lbzjn:
            cgfh__smxk = set(typemap[vbyl__lbzjn['used_cols'].name].
                instance_type.meta)
            bwa__hvm = set()
            for qzksc__bbw, eods__rwbeb in enumerate(iqs__nzi):
                if qzksc__bbw in cgfh__smxk and eods__rwbeb < cmeby__pcmml:
                    bwa__hvm.add(eods__rwbeb)
            return bwa__hvm
        else:
            return set(sbra__ugi for sbra__ugi in iqs__nzi if sbra__ugi <
                cmeby__pcmml)
    return None
