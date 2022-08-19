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
        ensjl__wcari = typemap[call_expr.args[1].name].literal_value
        return {ensjl__wcari}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        jyid__vvqo = dict(call_expr.kws)
        if 'used_cols' in jyid__vvqo:
            nkh__ukik = jyid__vvqo['used_cols']
            cgby__dkzp = typemap[nkh__ukik.name]
            cgby__dkzp = cgby__dkzp.instance_type
            return set(cgby__dkzp.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        nkh__ukik = call_expr.args[1]
        cgby__dkzp = typemap[nkh__ukik.name]
        cgby__dkzp = cgby__dkzp.instance_type
        return set(cgby__dkzp.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        waexj__yonn = call_expr.args[1]
        skno__huodw = typemap[waexj__yonn.name]
        skno__huodw = skno__huodw.instance_type
        dvg__jgsp = skno__huodw.meta
        jyid__vvqo = dict(call_expr.kws)
        if 'used_cols' in jyid__vvqo:
            nkh__ukik = jyid__vvqo['used_cols']
            cgby__dkzp = typemap[nkh__ukik.name]
            cgby__dkzp = cgby__dkzp.instance_type
            xeba__wikr = set(cgby__dkzp.meta)
            ldnuu__clh = set()
            for kavm__pch, bhts__qiicn in enumerate(dvg__jgsp):
                if kavm__pch in xeba__wikr:
                    ldnuu__clh.add(bhts__qiicn)
            return ldnuu__clh
        else:
            return set(dvg__jgsp)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        cozw__upxll = typemap[call_expr.args[2].name].instance_type.meta
        enlqx__wtqhh = len(typemap[call_expr.args[0].name].arr_types)
        return set(kavm__pch for kavm__pch in cozw__upxll if kavm__pch <
            enlqx__wtqhh)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        tlvf__axlvx = typemap[call_expr.args[2].name].instance_type.meta
        mwxr__inrv = len(typemap[call_expr.args[0].name].arr_types)
        jyid__vvqo = dict(call_expr.kws)
        if 'used_cols' in jyid__vvqo:
            xeba__wikr = set(typemap[jyid__vvqo['used_cols'].name].
                instance_type.meta)
            hfeh__byqo = set()
            for xqy__wnc, yoifp__kph in enumerate(tlvf__axlvx):
                if xqy__wnc in xeba__wikr and yoifp__kph < mwxr__inrv:
                    hfeh__byqo.add(yoifp__kph)
            return hfeh__byqo
        else:
            return set(kavm__pch for kavm__pch in tlvf__axlvx if kavm__pch <
                mwxr__inrv)
    return None
