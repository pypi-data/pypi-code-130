"""
transforms the IR to handle bytecode issues in Python 3.10. This
should be removed once https://github.com/numba/numba/pull/7866
is included in Numba 0.56
"""
import operator
import numba
from numba.core import ir
from numba.core.compiler_machinery import FunctionPass, register_pass
from numba.core.errors import UnsupportedError
from numba.core.ir_utils import dprint_func_ir, get_definition, guard


@register_pass(mutates_CFG=False, analysis_only=False)
class Bodo310ByteCodePass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dprint_func_ir(state.func_ir,
            'starting Bodo 3.10 Bytecode optimizations pass')
        peep_hole_call_function_ex_to_call_function_kw(state.func_ir)
        peep_hole_fuse_dict_add_updates(state.func_ir)
        peep_hole_fuse_tuple_adds(state.func_ir)
        return True


def peep_hole_fuse_tuple_adds(func_ir):
    for eme__bzfv in func_ir.blocks.values():
        new_body = []
        evktx__sfip = {}
        for rqfhe__wots, glsca__rrdu in enumerate(eme__bzfv.body):
            ehdzt__ygpk = None
            if isinstance(glsca__rrdu, ir.Assign) and isinstance(glsca__rrdu
                .value, ir.Expr):
                oakv__gbl = glsca__rrdu.target.name
                if glsca__rrdu.value.op == 'build_tuple':
                    ehdzt__ygpk = oakv__gbl
                    evktx__sfip[oakv__gbl] = glsca__rrdu.value.items
                elif glsca__rrdu.value.op == 'binop' and glsca__rrdu.value.fn == operator.add and glsca__rrdu.value.lhs.name in evktx__sfip and glsca__rrdu.value.rhs.name in evktx__sfip:
                    ehdzt__ygpk = oakv__gbl
                    new_items = evktx__sfip[glsca__rrdu.value.lhs.name
                        ] + evktx__sfip[glsca__rrdu.value.rhs.name]
                    dwn__sgjc = ir.Expr.build_tuple(new_items, glsca__rrdu.
                        value.loc)
                    evktx__sfip[oakv__gbl] = new_items
                    del evktx__sfip[glsca__rrdu.value.lhs.name]
                    del evktx__sfip[glsca__rrdu.value.rhs.name]
                    if glsca__rrdu.value in func_ir._definitions[oakv__gbl]:
                        func_ir._definitions[oakv__gbl].remove(glsca__rrdu.
                            value)
                    func_ir._definitions[oakv__gbl].append(dwn__sgjc)
                    glsca__rrdu = ir.Assign(dwn__sgjc, glsca__rrdu.target,
                        glsca__rrdu.loc)
            for ddrr__bzabv in glsca__rrdu.list_vars():
                if (ddrr__bzabv.name in evktx__sfip and ddrr__bzabv.name !=
                    ehdzt__ygpk):
                    del evktx__sfip[ddrr__bzabv.name]
            new_body.append(glsca__rrdu)
        eme__bzfv.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    mpnc__shnjg = keyword_expr.items.copy()
    wzv__kiobi = keyword_expr.value_indexes
    for vuzch__dbyb, esz__zmecy in wzv__kiobi.items():
        mpnc__shnjg[esz__zmecy] = vuzch__dbyb, mpnc__shnjg[esz__zmecy][1]
    new_body[buildmap_idx] = None
    return mpnc__shnjg


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    tuox__zll = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    mpnc__shnjg = []
    wlpv__tqlt = buildmap_idx + 1
    while wlpv__tqlt <= search_end:
        pls__flwf = body[wlpv__tqlt]
        if not (isinstance(pls__flwf, ir.Assign) and isinstance(pls__flwf.
            value, ir.Const)):
            raise UnsupportedError(tuox__zll)
        fyj__qgd = pls__flwf.target.name
        pck__rru = pls__flwf.value.value
        wlpv__tqlt += 1
        spi__adaxe = True
        while wlpv__tqlt <= search_end and spi__adaxe:
            xoj__wjx = body[wlpv__tqlt]
            if (isinstance(xoj__wjx, ir.Assign) and isinstance(xoj__wjx.
                value, ir.Expr) and xoj__wjx.value.op == 'getattr' and 
                xoj__wjx.value.value.name == buildmap_name and xoj__wjx.
                value.attr == '__setitem__'):
                spi__adaxe = False
            else:
                wlpv__tqlt += 1
        if spi__adaxe or wlpv__tqlt == search_end:
            raise UnsupportedError(tuox__zll)
        vbn__oeo = body[wlpv__tqlt + 1]
        if not (isinstance(vbn__oeo, ir.Assign) and isinstance(vbn__oeo.
            value, ir.Expr) and vbn__oeo.value.op == 'call' and vbn__oeo.
            value.func.name == xoj__wjx.target.name and len(vbn__oeo.value.
            args) == 2 and vbn__oeo.value.args[0].name == fyj__qgd):
            raise UnsupportedError(tuox__zll)
        buygx__gewqx = vbn__oeo.value.args[1]
        mpnc__shnjg.append((pck__rru, buygx__gewqx))
        new_body[wlpv__tqlt] = None
        new_body[wlpv__tqlt + 1] = None
        wlpv__tqlt += 2
    return mpnc__shnjg


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    tuox__zll = 'CALL_FUNCTION_EX with **kwargs not supported'
    wlpv__tqlt = 0
    nmdv__knjkp = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        eitt__iqtt = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        eitt__iqtt = vararg_stmt.target.name
    ndtcg__kkpf = True
    while search_end >= wlpv__tqlt and ndtcg__kkpf:
        pgt__dfwm = body[search_end]
        if (isinstance(pgt__dfwm, ir.Assign) and pgt__dfwm.target.name ==
            eitt__iqtt and isinstance(pgt__dfwm.value, ir.Expr) and 
            pgt__dfwm.value.op == 'build_tuple' and not pgt__dfwm.value.items):
            ndtcg__kkpf = False
            new_body[search_end] = None
        else:
            if search_end == wlpv__tqlt or not (isinstance(pgt__dfwm, ir.
                Assign) and pgt__dfwm.target.name == eitt__iqtt and
                isinstance(pgt__dfwm.value, ir.Expr) and pgt__dfwm.value.op ==
                'binop' and pgt__dfwm.value.fn == operator.add):
                raise UnsupportedError(tuox__zll)
            yxdn__aqpr = pgt__dfwm.value.lhs.name
            ushy__mdawl = pgt__dfwm.value.rhs.name
            utuq__tmqc = body[search_end - 1]
            if not (isinstance(utuq__tmqc, ir.Assign) and isinstance(
                utuq__tmqc.value, ir.Expr) and utuq__tmqc.value.op ==
                'build_tuple' and len(utuq__tmqc.value.items) == 1):
                raise UnsupportedError(tuox__zll)
            if utuq__tmqc.target.name == yxdn__aqpr:
                eitt__iqtt = ushy__mdawl
            elif utuq__tmqc.target.name == ushy__mdawl:
                eitt__iqtt = yxdn__aqpr
            else:
                raise UnsupportedError(tuox__zll)
            nmdv__knjkp.append(utuq__tmqc.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            jcp__aoihd = True
            while search_end >= wlpv__tqlt and jcp__aoihd:
                mct__fwqsq = body[search_end]
                if isinstance(mct__fwqsq, ir.Assign
                    ) and mct__fwqsq.target.name == eitt__iqtt:
                    jcp__aoihd = False
                else:
                    search_end -= 1
    if ndtcg__kkpf:
        raise UnsupportedError(tuox__zll)
    return nmdv__knjkp[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    tuox__zll = 'CALL_FUNCTION_EX with **kwargs not supported'
    for eme__bzfv in func_ir.blocks.values():
        mvtj__dvhqh = False
        new_body = []
        for rqfhe__wots, glsca__rrdu in enumerate(eme__bzfv.body):
            if (isinstance(glsca__rrdu, ir.Assign) and isinstance(
                glsca__rrdu.value, ir.Expr) and glsca__rrdu.value.op ==
                'call' and glsca__rrdu.value.varkwarg is not None):
                mvtj__dvhqh = True
                wntg__dgspn = glsca__rrdu.value
                args = wntg__dgspn.args
                mpnc__shnjg = wntg__dgspn.kws
                jextc__nzp = wntg__dgspn.vararg
                eiouz__zxsx = wntg__dgspn.varkwarg
                dqt__uqkua = rqfhe__wots - 1
                jfqzs__bcy = dqt__uqkua
                rdad__iei = None
                ignf__mxinf = True
                while jfqzs__bcy >= 0 and ignf__mxinf:
                    rdad__iei = eme__bzfv.body[jfqzs__bcy]
                    if isinstance(rdad__iei, ir.Assign
                        ) and rdad__iei.target.name == eiouz__zxsx.name:
                        ignf__mxinf = False
                    else:
                        jfqzs__bcy -= 1
                if mpnc__shnjg or ignf__mxinf or not (isinstance(rdad__iei.
                    value, ir.Expr) and rdad__iei.value.op == 'build_map'):
                    raise UnsupportedError(tuox__zll)
                if rdad__iei.value.items:
                    mpnc__shnjg = _call_function_ex_replace_kws_small(rdad__iei
                        .value, new_body, jfqzs__bcy)
                else:
                    mpnc__shnjg = _call_function_ex_replace_kws_large(eme__bzfv
                        .body, eiouz__zxsx.name, jfqzs__bcy, rqfhe__wots - 
                        1, new_body)
                dqt__uqkua = jfqzs__bcy
                if jextc__nzp is not None:
                    if args:
                        raise UnsupportedError(tuox__zll)
                    sti__oyix = dqt__uqkua
                    ukw__ztul = None
                    ignf__mxinf = True
                    while sti__oyix >= 0 and ignf__mxinf:
                        ukw__ztul = eme__bzfv.body[sti__oyix]
                        if isinstance(ukw__ztul, ir.Assign
                            ) and ukw__ztul.target.name == jextc__nzp.name:
                            ignf__mxinf = False
                        else:
                            sti__oyix -= 1
                    if ignf__mxinf:
                        raise UnsupportedError(tuox__zll)
                    if isinstance(ukw__ztul.value, ir.Expr
                        ) and ukw__ztul.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(ukw__ztul
                            .value, new_body, sti__oyix)
                    else:
                        args = _call_function_ex_replace_args_large(ukw__ztul,
                            eme__bzfv.body, new_body, sti__oyix)
                ihw__xetx = ir.Expr.call(wntg__dgspn.func, args,
                    mpnc__shnjg, wntg__dgspn.loc, target=wntg__dgspn.target)
                if glsca__rrdu.target.name in func_ir._definitions and len(
                    func_ir._definitions[glsca__rrdu.target.name]) == 1:
                    func_ir._definitions[glsca__rrdu.target.name].clear()
                func_ir._definitions[glsca__rrdu.target.name].append(ihw__xetx)
                glsca__rrdu = ir.Assign(ihw__xetx, glsca__rrdu.target,
                    glsca__rrdu.loc)
            new_body.append(glsca__rrdu)
        if mvtj__dvhqh:
            eme__bzfv.body = [klvsh__wgyhc for klvsh__wgyhc in new_body if 
                klvsh__wgyhc is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for eme__bzfv in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        mvtj__dvhqh = False
        for rqfhe__wots, glsca__rrdu in enumerate(eme__bzfv.body):
            teu__wfhp = True
            zpgz__fzjtu = None
            if isinstance(glsca__rrdu, ir.Assign) and isinstance(glsca__rrdu
                .value, ir.Expr):
                if glsca__rrdu.value.op == 'build_map':
                    zpgz__fzjtu = glsca__rrdu.target.name
                    lit_old_idx[glsca__rrdu.target.name] = rqfhe__wots
                    lit_new_idx[glsca__rrdu.target.name] = rqfhe__wots
                    map_updates[glsca__rrdu.target.name
                        ] = glsca__rrdu.value.items.copy()
                    teu__wfhp = False
                elif glsca__rrdu.value.op == 'call' and rqfhe__wots > 0:
                    qysnn__fwi = glsca__rrdu.value.func.name
                    xoj__wjx = eme__bzfv.body[rqfhe__wots - 1]
                    args = glsca__rrdu.value.args
                    if (isinstance(xoj__wjx, ir.Assign) and xoj__wjx.target
                        .name == qysnn__fwi and isinstance(xoj__wjx.value,
                        ir.Expr) and xoj__wjx.value.op == 'getattr' and 
                        xoj__wjx.value.value.name in lit_old_idx):
                        ipj__lfe = xoj__wjx.value.value.name
                        mewh__gvct = xoj__wjx.value.attr
                        if mewh__gvct == '__setitem__':
                            teu__wfhp = False
                            map_updates[ipj__lfe].append(args)
                            new_body[-1] = None
                        elif mewh__gvct == 'update' and args[0
                            ].name in lit_old_idx:
                            teu__wfhp = False
                            map_updates[ipj__lfe].extend(map_updates[args[0
                                ].name])
                            new_body[-1] = None
                        if not teu__wfhp:
                            lit_new_idx[ipj__lfe] = rqfhe__wots
                            func_ir._definitions[xoj__wjx.target.name].remove(
                                xoj__wjx.value)
            if not (isinstance(glsca__rrdu, ir.Assign) and isinstance(
                glsca__rrdu.value, ir.Expr) and glsca__rrdu.value.op ==
                'getattr' and glsca__rrdu.value.value.name in lit_old_idx and
                glsca__rrdu.value.attr in ('__setitem__', 'update')):
                for ddrr__bzabv in glsca__rrdu.list_vars():
                    if (ddrr__bzabv.name in lit_old_idx and ddrr__bzabv.
                        name != zpgz__fzjtu):
                        _insert_build_map(func_ir, ddrr__bzabv.name,
                            eme__bzfv.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if teu__wfhp:
                new_body.append(glsca__rrdu)
            else:
                func_ir._definitions[glsca__rrdu.target.name].remove(
                    glsca__rrdu.value)
                mvtj__dvhqh = True
                new_body.append(None)
        wxy__noy = list(lit_old_idx.keys())
        for pizum__qjegm in wxy__noy:
            _insert_build_map(func_ir, pizum__qjegm, eme__bzfv.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if mvtj__dvhqh:
            eme__bzfv.body = [klvsh__wgyhc for klvsh__wgyhc in new_body if 
                klvsh__wgyhc is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    kaiwq__pwxjj = lit_old_idx[name]
    zlvzk__xxl = lit_new_idx[name]
    ayspq__itqb = map_updates[name]
    new_body[zlvzk__xxl] = _build_new_build_map(func_ir, name, old_body,
        kaiwq__pwxjj, ayspq__itqb)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    ncwkr__ryusl = old_body[old_lineno]
    ypea__idp = ncwkr__ryusl.target
    oxuw__xqhkq = ncwkr__ryusl.value
    key__due = []
    pcgmn__ezqi = []
    for yxkxt__qhnie in new_items:
        sakbx__ozq, hzrgz__krmh = yxkxt__qhnie
        lvx__ihyxj = guard(get_definition, func_ir, sakbx__ozq)
        if isinstance(lvx__ihyxj, (ir.Const, ir.Global, ir.FreeVar)):
            key__due.append(lvx__ihyxj.value)
        vclb__urlhm = guard(get_definition, func_ir, hzrgz__krmh)
        if isinstance(vclb__urlhm, (ir.Const, ir.Global, ir.FreeVar)):
            pcgmn__ezqi.append(vclb__urlhm.value)
        else:
            pcgmn__ezqi.append(numba.core.interpreter._UNKNOWN_VALUE(
                hzrgz__krmh.name))
    wzv__kiobi = {}
    if len(key__due) == len(new_items):
        tqa__rmhbf = {klvsh__wgyhc: souiy__xqm for klvsh__wgyhc, souiy__xqm in
            zip(key__due, pcgmn__ezqi)}
        for rqfhe__wots, sakbx__ozq in enumerate(key__due):
            wzv__kiobi[sakbx__ozq] = rqfhe__wots
    else:
        tqa__rmhbf = None
    ajdz__marub = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=tqa__rmhbf, value_indexes=wzv__kiobi, loc=oxuw__xqhkq.loc
        )
    func_ir._definitions[name].append(ajdz__marub)
    return ir.Assign(ajdz__marub, ir.Var(ypea__idp.scope, name, ypea__idp.
        loc), ajdz__marub.loc)
