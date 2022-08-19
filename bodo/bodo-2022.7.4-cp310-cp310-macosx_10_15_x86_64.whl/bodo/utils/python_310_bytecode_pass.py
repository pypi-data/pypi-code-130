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
    for ovob__xuknn in func_ir.blocks.values():
        new_body = []
        eje__gyl = {}
        for wepv__dip, dwjvg__jdr in enumerate(ovob__xuknn.body):
            phscw__sqee = None
            if isinstance(dwjvg__jdr, ir.Assign) and isinstance(dwjvg__jdr.
                value, ir.Expr):
                yvte__ajjtm = dwjvg__jdr.target.name
                if dwjvg__jdr.value.op == 'build_tuple':
                    phscw__sqee = yvte__ajjtm
                    eje__gyl[yvte__ajjtm] = dwjvg__jdr.value.items
                elif dwjvg__jdr.value.op == 'binop' and dwjvg__jdr.value.fn == operator.add and dwjvg__jdr.value.lhs.name in eje__gyl and dwjvg__jdr.value.rhs.name in eje__gyl:
                    phscw__sqee = yvte__ajjtm
                    new_items = eje__gyl[dwjvg__jdr.value.lhs.name] + eje__gyl[
                        dwjvg__jdr.value.rhs.name]
                    xtcoj__oarep = ir.Expr.build_tuple(new_items,
                        dwjvg__jdr.value.loc)
                    eje__gyl[yvte__ajjtm] = new_items
                    del eje__gyl[dwjvg__jdr.value.lhs.name]
                    del eje__gyl[dwjvg__jdr.value.rhs.name]
                    if dwjvg__jdr.value in func_ir._definitions[yvte__ajjtm]:
                        func_ir._definitions[yvte__ajjtm].remove(dwjvg__jdr
                            .value)
                    func_ir._definitions[yvte__ajjtm].append(xtcoj__oarep)
                    dwjvg__jdr = ir.Assign(xtcoj__oarep, dwjvg__jdr.target,
                        dwjvg__jdr.loc)
            for xaf__rrt in dwjvg__jdr.list_vars():
                if xaf__rrt.name in eje__gyl and xaf__rrt.name != phscw__sqee:
                    del eje__gyl[xaf__rrt.name]
            new_body.append(dwjvg__jdr)
        ovob__xuknn.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    fnbkt__wnwaz = keyword_expr.items.copy()
    hpat__dor = keyword_expr.value_indexes
    for lhu__cuw, iwotk__tam in hpat__dor.items():
        fnbkt__wnwaz[iwotk__tam] = lhu__cuw, fnbkt__wnwaz[iwotk__tam][1]
    new_body[buildmap_idx] = None
    return fnbkt__wnwaz


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    jysy__nlipa = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    fnbkt__wnwaz = []
    qnm__opn = buildmap_idx + 1
    while qnm__opn <= search_end:
        meqym__hdw = body[qnm__opn]
        if not (isinstance(meqym__hdw, ir.Assign) and isinstance(meqym__hdw
            .value, ir.Const)):
            raise UnsupportedError(jysy__nlipa)
        vyn__evwo = meqym__hdw.target.name
        ieyep__slo = meqym__hdw.value.value
        qnm__opn += 1
        wrw__opil = True
        while qnm__opn <= search_end and wrw__opil:
            plh__byjwy = body[qnm__opn]
            if (isinstance(plh__byjwy, ir.Assign) and isinstance(plh__byjwy
                .value, ir.Expr) and plh__byjwy.value.op == 'getattr' and 
                plh__byjwy.value.value.name == buildmap_name and plh__byjwy
                .value.attr == '__setitem__'):
                wrw__opil = False
            else:
                qnm__opn += 1
        if wrw__opil or qnm__opn == search_end:
            raise UnsupportedError(jysy__nlipa)
        qaz__tvydn = body[qnm__opn + 1]
        if not (isinstance(qaz__tvydn, ir.Assign) and isinstance(qaz__tvydn
            .value, ir.Expr) and qaz__tvydn.value.op == 'call' and 
            qaz__tvydn.value.func.name == plh__byjwy.target.name and len(
            qaz__tvydn.value.args) == 2 and qaz__tvydn.value.args[0].name ==
            vyn__evwo):
            raise UnsupportedError(jysy__nlipa)
        sum__eqrg = qaz__tvydn.value.args[1]
        fnbkt__wnwaz.append((ieyep__slo, sum__eqrg))
        new_body[qnm__opn] = None
        new_body[qnm__opn + 1] = None
        qnm__opn += 2
    return fnbkt__wnwaz


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    jysy__nlipa = 'CALL_FUNCTION_EX with **kwargs not supported'
    qnm__opn = 0
    niucq__cklx = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        pxpxw__hdbkh = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        pxpxw__hdbkh = vararg_stmt.target.name
    feqr__fyx = True
    while search_end >= qnm__opn and feqr__fyx:
        mfzig__wsif = body[search_end]
        if (isinstance(mfzig__wsif, ir.Assign) and mfzig__wsif.target.name ==
            pxpxw__hdbkh and isinstance(mfzig__wsif.value, ir.Expr) and 
            mfzig__wsif.value.op == 'build_tuple' and not mfzig__wsif.value
            .items):
            feqr__fyx = False
            new_body[search_end] = None
        else:
            if search_end == qnm__opn or not (isinstance(mfzig__wsif, ir.
                Assign) and mfzig__wsif.target.name == pxpxw__hdbkh and
                isinstance(mfzig__wsif.value, ir.Expr) and mfzig__wsif.
                value.op == 'binop' and mfzig__wsif.value.fn == operator.add):
                raise UnsupportedError(jysy__nlipa)
            aal__vuji = mfzig__wsif.value.lhs.name
            mdt__lvg = mfzig__wsif.value.rhs.name
            idt__qflkf = body[search_end - 1]
            if not (isinstance(idt__qflkf, ir.Assign) and isinstance(
                idt__qflkf.value, ir.Expr) and idt__qflkf.value.op ==
                'build_tuple' and len(idt__qflkf.value.items) == 1):
                raise UnsupportedError(jysy__nlipa)
            if idt__qflkf.target.name == aal__vuji:
                pxpxw__hdbkh = mdt__lvg
            elif idt__qflkf.target.name == mdt__lvg:
                pxpxw__hdbkh = aal__vuji
            else:
                raise UnsupportedError(jysy__nlipa)
            niucq__cklx.append(idt__qflkf.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            xdkmx__sir = True
            while search_end >= qnm__opn and xdkmx__sir:
                pgedl__tcw = body[search_end]
                if isinstance(pgedl__tcw, ir.Assign
                    ) and pgedl__tcw.target.name == pxpxw__hdbkh:
                    xdkmx__sir = False
                else:
                    search_end -= 1
    if feqr__fyx:
        raise UnsupportedError(jysy__nlipa)
    return niucq__cklx[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    jysy__nlipa = 'CALL_FUNCTION_EX with **kwargs not supported'
    for ovob__xuknn in func_ir.blocks.values():
        rei__war = False
        new_body = []
        for wepv__dip, dwjvg__jdr in enumerate(ovob__xuknn.body):
            if (isinstance(dwjvg__jdr, ir.Assign) and isinstance(dwjvg__jdr
                .value, ir.Expr) and dwjvg__jdr.value.op == 'call' and 
                dwjvg__jdr.value.varkwarg is not None):
                rei__war = True
                jvqlm__zwky = dwjvg__jdr.value
                args = jvqlm__zwky.args
                fnbkt__wnwaz = jvqlm__zwky.kws
                vke__ldacj = jvqlm__zwky.vararg
                gtl__szw = jvqlm__zwky.varkwarg
                duns__tbh = wepv__dip - 1
                ucu__lnv = duns__tbh
                vsqmr__vvj = None
                dxkjy__uoc = True
                while ucu__lnv >= 0 and dxkjy__uoc:
                    vsqmr__vvj = ovob__xuknn.body[ucu__lnv]
                    if isinstance(vsqmr__vvj, ir.Assign
                        ) and vsqmr__vvj.target.name == gtl__szw.name:
                        dxkjy__uoc = False
                    else:
                        ucu__lnv -= 1
                if fnbkt__wnwaz or dxkjy__uoc or not (isinstance(vsqmr__vvj
                    .value, ir.Expr) and vsqmr__vvj.value.op == 'build_map'):
                    raise UnsupportedError(jysy__nlipa)
                if vsqmr__vvj.value.items:
                    fnbkt__wnwaz = _call_function_ex_replace_kws_small(
                        vsqmr__vvj.value, new_body, ucu__lnv)
                else:
                    fnbkt__wnwaz = _call_function_ex_replace_kws_large(
                        ovob__xuknn.body, gtl__szw.name, ucu__lnv, 
                        wepv__dip - 1, new_body)
                duns__tbh = ucu__lnv
                if vke__ldacj is not None:
                    if args:
                        raise UnsupportedError(jysy__nlipa)
                    fngkw__uyai = duns__tbh
                    nesr__rjmcp = None
                    dxkjy__uoc = True
                    while fngkw__uyai >= 0 and dxkjy__uoc:
                        nesr__rjmcp = ovob__xuknn.body[fngkw__uyai]
                        if isinstance(nesr__rjmcp, ir.Assign
                            ) and nesr__rjmcp.target.name == vke__ldacj.name:
                            dxkjy__uoc = False
                        else:
                            fngkw__uyai -= 1
                    if dxkjy__uoc:
                        raise UnsupportedError(jysy__nlipa)
                    if isinstance(nesr__rjmcp.value, ir.Expr
                        ) and nesr__rjmcp.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(nesr__rjmcp
                            .value, new_body, fngkw__uyai)
                    else:
                        args = _call_function_ex_replace_args_large(nesr__rjmcp
                            , ovob__xuknn.body, new_body, fngkw__uyai)
                fcuik__fsy = ir.Expr.call(jvqlm__zwky.func, args,
                    fnbkt__wnwaz, jvqlm__zwky.loc, target=jvqlm__zwky.target)
                if dwjvg__jdr.target.name in func_ir._definitions and len(
                    func_ir._definitions[dwjvg__jdr.target.name]) == 1:
                    func_ir._definitions[dwjvg__jdr.target.name].clear()
                func_ir._definitions[dwjvg__jdr.target.name].append(fcuik__fsy)
                dwjvg__jdr = ir.Assign(fcuik__fsy, dwjvg__jdr.target,
                    dwjvg__jdr.loc)
            new_body.append(dwjvg__jdr)
        if rei__war:
            ovob__xuknn.body = [vfzyk__jhgq for vfzyk__jhgq in new_body if 
                vfzyk__jhgq is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for ovob__xuknn in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        rei__war = False
        for wepv__dip, dwjvg__jdr in enumerate(ovob__xuknn.body):
            rlbis__rzdsm = True
            xxhj__onfi = None
            if isinstance(dwjvg__jdr, ir.Assign) and isinstance(dwjvg__jdr.
                value, ir.Expr):
                if dwjvg__jdr.value.op == 'build_map':
                    xxhj__onfi = dwjvg__jdr.target.name
                    lit_old_idx[dwjvg__jdr.target.name] = wepv__dip
                    lit_new_idx[dwjvg__jdr.target.name] = wepv__dip
                    map_updates[dwjvg__jdr.target.name
                        ] = dwjvg__jdr.value.items.copy()
                    rlbis__rzdsm = False
                elif dwjvg__jdr.value.op == 'call' and wepv__dip > 0:
                    gua__grd = dwjvg__jdr.value.func.name
                    plh__byjwy = ovob__xuknn.body[wepv__dip - 1]
                    args = dwjvg__jdr.value.args
                    if (isinstance(plh__byjwy, ir.Assign) and plh__byjwy.
                        target.name == gua__grd and isinstance(plh__byjwy.
                        value, ir.Expr) and plh__byjwy.value.op ==
                        'getattr' and plh__byjwy.value.value.name in
                        lit_old_idx):
                        rjl__zylfs = plh__byjwy.value.value.name
                        pme__kduh = plh__byjwy.value.attr
                        if pme__kduh == '__setitem__':
                            rlbis__rzdsm = False
                            map_updates[rjl__zylfs].append(args)
                            new_body[-1] = None
                        elif pme__kduh == 'update' and args[0
                            ].name in lit_old_idx:
                            rlbis__rzdsm = False
                            map_updates[rjl__zylfs].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not rlbis__rzdsm:
                            lit_new_idx[rjl__zylfs] = wepv__dip
                            func_ir._definitions[plh__byjwy.target.name
                                ].remove(plh__byjwy.value)
            if not (isinstance(dwjvg__jdr, ir.Assign) and isinstance(
                dwjvg__jdr.value, ir.Expr) and dwjvg__jdr.value.op ==
                'getattr' and dwjvg__jdr.value.value.name in lit_old_idx and
                dwjvg__jdr.value.attr in ('__setitem__', 'update')):
                for xaf__rrt in dwjvg__jdr.list_vars():
                    if (xaf__rrt.name in lit_old_idx and xaf__rrt.name !=
                        xxhj__onfi):
                        _insert_build_map(func_ir, xaf__rrt.name,
                            ovob__xuknn.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if rlbis__rzdsm:
                new_body.append(dwjvg__jdr)
            else:
                func_ir._definitions[dwjvg__jdr.target.name].remove(dwjvg__jdr
                    .value)
                rei__war = True
                new_body.append(None)
        xkyh__rui = list(lit_old_idx.keys())
        for wtq__prbh in xkyh__rui:
            _insert_build_map(func_ir, wtq__prbh, ovob__xuknn.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if rei__war:
            ovob__xuknn.body = [vfzyk__jhgq for vfzyk__jhgq in new_body if 
                vfzyk__jhgq is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    mrjw__zrv = lit_old_idx[name]
    bru__ilek = lit_new_idx[name]
    qyj__ooh = map_updates[name]
    new_body[bru__ilek] = _build_new_build_map(func_ir, name, old_body,
        mrjw__zrv, qyj__ooh)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    ylzdh__surm = old_body[old_lineno]
    usew__dqgg = ylzdh__surm.target
    khknu__gfw = ylzdh__surm.value
    bztl__aqvr = []
    ndrn__zxdpf = []
    for ggyg__lokk in new_items:
        kksmd__hlo, hsgq__ypbdk = ggyg__lokk
        dow__mev = guard(get_definition, func_ir, kksmd__hlo)
        if isinstance(dow__mev, (ir.Const, ir.Global, ir.FreeVar)):
            bztl__aqvr.append(dow__mev.value)
        org__ozhza = guard(get_definition, func_ir, hsgq__ypbdk)
        if isinstance(org__ozhza, (ir.Const, ir.Global, ir.FreeVar)):
            ndrn__zxdpf.append(org__ozhza.value)
        else:
            ndrn__zxdpf.append(numba.core.interpreter._UNKNOWN_VALUE(
                hsgq__ypbdk.name))
    hpat__dor = {}
    if len(bztl__aqvr) == len(new_items):
        vzue__lpx = {vfzyk__jhgq: xclcs__hsvze for vfzyk__jhgq,
            xclcs__hsvze in zip(bztl__aqvr, ndrn__zxdpf)}
        for wepv__dip, kksmd__hlo in enumerate(bztl__aqvr):
            hpat__dor[kksmd__hlo] = wepv__dip
    else:
        vzue__lpx = None
    kdhnf__ofdq = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=vzue__lpx, value_indexes=hpat__dor, loc=khknu__gfw.loc)
    func_ir._definitions[name].append(kdhnf__ofdq)
    return ir.Assign(kdhnf__ofdq, ir.Var(usew__dqgg.scope, name, usew__dqgg
        .loc), kdhnf__ofdq.loc)
