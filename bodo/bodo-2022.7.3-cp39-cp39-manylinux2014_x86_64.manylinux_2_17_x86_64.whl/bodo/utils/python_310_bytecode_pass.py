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
    for huan__viwfg in func_ir.blocks.values():
        new_body = []
        nmpa__iwufy = {}
        for fvt__xen, gwv__vkmkl in enumerate(huan__viwfg.body):
            jojij__cgoel = None
            if isinstance(gwv__vkmkl, ir.Assign) and isinstance(gwv__vkmkl.
                value, ir.Expr):
                yjut__eqb = gwv__vkmkl.target.name
                if gwv__vkmkl.value.op == 'build_tuple':
                    jojij__cgoel = yjut__eqb
                    nmpa__iwufy[yjut__eqb] = gwv__vkmkl.value.items
                elif gwv__vkmkl.value.op == 'binop' and gwv__vkmkl.value.fn == operator.add and gwv__vkmkl.value.lhs.name in nmpa__iwufy and gwv__vkmkl.value.rhs.name in nmpa__iwufy:
                    jojij__cgoel = yjut__eqb
                    new_items = nmpa__iwufy[gwv__vkmkl.value.lhs.name
                        ] + nmpa__iwufy[gwv__vkmkl.value.rhs.name]
                    jsn__tll = ir.Expr.build_tuple(new_items, gwv__vkmkl.
                        value.loc)
                    nmpa__iwufy[yjut__eqb] = new_items
                    del nmpa__iwufy[gwv__vkmkl.value.lhs.name]
                    del nmpa__iwufy[gwv__vkmkl.value.rhs.name]
                    if gwv__vkmkl.value in func_ir._definitions[yjut__eqb]:
                        func_ir._definitions[yjut__eqb].remove(gwv__vkmkl.value
                            )
                    func_ir._definitions[yjut__eqb].append(jsn__tll)
                    gwv__vkmkl = ir.Assign(jsn__tll, gwv__vkmkl.target,
                        gwv__vkmkl.loc)
            for sih__vhp in gwv__vkmkl.list_vars():
                if (sih__vhp.name in nmpa__iwufy and sih__vhp.name !=
                    jojij__cgoel):
                    del nmpa__iwufy[sih__vhp.name]
            new_body.append(gwv__vkmkl)
        huan__viwfg.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    nqo__qgo = keyword_expr.items.copy()
    qqtk__jqn = keyword_expr.value_indexes
    for wxmik__unntn, ohwhn__cwe in qqtk__jqn.items():
        nqo__qgo[ohwhn__cwe] = wxmik__unntn, nqo__qgo[ohwhn__cwe][1]
    new_body[buildmap_idx] = None
    return nqo__qgo


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    vkzxj__kafoe = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    nqo__qgo = []
    duph__japm = buildmap_idx + 1
    while duph__japm <= search_end:
        zvlcw__vfk = body[duph__japm]
        if not (isinstance(zvlcw__vfk, ir.Assign) and isinstance(zvlcw__vfk
            .value, ir.Const)):
            raise UnsupportedError(vkzxj__kafoe)
        fodwc__ntd = zvlcw__vfk.target.name
        sxtxz__xhop = zvlcw__vfk.value.value
        duph__japm += 1
        yyq__okuql = True
        while duph__japm <= search_end and yyq__okuql:
            wtqgm__dfz = body[duph__japm]
            if (isinstance(wtqgm__dfz, ir.Assign) and isinstance(wtqgm__dfz
                .value, ir.Expr) and wtqgm__dfz.value.op == 'getattr' and 
                wtqgm__dfz.value.value.name == buildmap_name and wtqgm__dfz
                .value.attr == '__setitem__'):
                yyq__okuql = False
            else:
                duph__japm += 1
        if yyq__okuql or duph__japm == search_end:
            raise UnsupportedError(vkzxj__kafoe)
        iohn__wzpan = body[duph__japm + 1]
        if not (isinstance(iohn__wzpan, ir.Assign) and isinstance(
            iohn__wzpan.value, ir.Expr) and iohn__wzpan.value.op == 'call' and
            iohn__wzpan.value.func.name == wtqgm__dfz.target.name and len(
            iohn__wzpan.value.args) == 2 and iohn__wzpan.value.args[0].name ==
            fodwc__ntd):
            raise UnsupportedError(vkzxj__kafoe)
        ozngt__soqw = iohn__wzpan.value.args[1]
        nqo__qgo.append((sxtxz__xhop, ozngt__soqw))
        new_body[duph__japm] = None
        new_body[duph__japm + 1] = None
        duph__japm += 2
    return nqo__qgo


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    vkzxj__kafoe = 'CALL_FUNCTION_EX with **kwargs not supported'
    duph__japm = 0
    zjsgc__ratr = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        yqs__rwv = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        yqs__rwv = vararg_stmt.target.name
    fuk__readk = True
    while search_end >= duph__japm and fuk__readk:
        nrxsv__wqeun = body[search_end]
        if (isinstance(nrxsv__wqeun, ir.Assign) and nrxsv__wqeun.target.
            name == yqs__rwv and isinstance(nrxsv__wqeun.value, ir.Expr) and
            nrxsv__wqeun.value.op == 'build_tuple' and not nrxsv__wqeun.
            value.items):
            fuk__readk = False
            new_body[search_end] = None
        else:
            if search_end == duph__japm or not (isinstance(nrxsv__wqeun, ir
                .Assign) and nrxsv__wqeun.target.name == yqs__rwv and
                isinstance(nrxsv__wqeun.value, ir.Expr) and nrxsv__wqeun.
                value.op == 'binop' and nrxsv__wqeun.value.fn == operator.add):
                raise UnsupportedError(vkzxj__kafoe)
            qxhx__kgno = nrxsv__wqeun.value.lhs.name
            igq__ikpru = nrxsv__wqeun.value.rhs.name
            zxr__sdxy = body[search_end - 1]
            if not (isinstance(zxr__sdxy, ir.Assign) and isinstance(
                zxr__sdxy.value, ir.Expr) and zxr__sdxy.value.op ==
                'build_tuple' and len(zxr__sdxy.value.items) == 1):
                raise UnsupportedError(vkzxj__kafoe)
            if zxr__sdxy.target.name == qxhx__kgno:
                yqs__rwv = igq__ikpru
            elif zxr__sdxy.target.name == igq__ikpru:
                yqs__rwv = qxhx__kgno
            else:
                raise UnsupportedError(vkzxj__kafoe)
            zjsgc__ratr.append(zxr__sdxy.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            eoir__gvs = True
            while search_end >= duph__japm and eoir__gvs:
                dnizr__vmv = body[search_end]
                if isinstance(dnizr__vmv, ir.Assign
                    ) and dnizr__vmv.target.name == yqs__rwv:
                    eoir__gvs = False
                else:
                    search_end -= 1
    if fuk__readk:
        raise UnsupportedError(vkzxj__kafoe)
    return zjsgc__ratr[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    vkzxj__kafoe = 'CALL_FUNCTION_EX with **kwargs not supported'
    for huan__viwfg in func_ir.blocks.values():
        kbz__kvb = False
        new_body = []
        for fvt__xen, gwv__vkmkl in enumerate(huan__viwfg.body):
            if (isinstance(gwv__vkmkl, ir.Assign) and isinstance(gwv__vkmkl
                .value, ir.Expr) and gwv__vkmkl.value.op == 'call' and 
                gwv__vkmkl.value.varkwarg is not None):
                kbz__kvb = True
                xntgm__jcv = gwv__vkmkl.value
                args = xntgm__jcv.args
                nqo__qgo = xntgm__jcv.kws
                fqt__nld = xntgm__jcv.vararg
                vzuqu__vadir = xntgm__jcv.varkwarg
                moitr__lirki = fvt__xen - 1
                dygaq__ijcg = moitr__lirki
                eulfy__mprl = None
                rdlal__vciq = True
                while dygaq__ijcg >= 0 and rdlal__vciq:
                    eulfy__mprl = huan__viwfg.body[dygaq__ijcg]
                    if isinstance(eulfy__mprl, ir.Assign
                        ) and eulfy__mprl.target.name == vzuqu__vadir.name:
                        rdlal__vciq = False
                    else:
                        dygaq__ijcg -= 1
                if nqo__qgo or rdlal__vciq or not (isinstance(eulfy__mprl.
                    value, ir.Expr) and eulfy__mprl.value.op == 'build_map'):
                    raise UnsupportedError(vkzxj__kafoe)
                if eulfy__mprl.value.items:
                    nqo__qgo = _call_function_ex_replace_kws_small(eulfy__mprl
                        .value, new_body, dygaq__ijcg)
                else:
                    nqo__qgo = _call_function_ex_replace_kws_large(huan__viwfg
                        .body, vzuqu__vadir.name, dygaq__ijcg, fvt__xen - 1,
                        new_body)
                moitr__lirki = dygaq__ijcg
                if fqt__nld is not None:
                    if args:
                        raise UnsupportedError(vkzxj__kafoe)
                    lsnik__cwzgv = moitr__lirki
                    lwmrn__hfxmz = None
                    rdlal__vciq = True
                    while lsnik__cwzgv >= 0 and rdlal__vciq:
                        lwmrn__hfxmz = huan__viwfg.body[lsnik__cwzgv]
                        if isinstance(lwmrn__hfxmz, ir.Assign
                            ) and lwmrn__hfxmz.target.name == fqt__nld.name:
                            rdlal__vciq = False
                        else:
                            lsnik__cwzgv -= 1
                    if rdlal__vciq:
                        raise UnsupportedError(vkzxj__kafoe)
                    if isinstance(lwmrn__hfxmz.value, ir.Expr
                        ) and lwmrn__hfxmz.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(
                            lwmrn__hfxmz.value, new_body, lsnik__cwzgv)
                    else:
                        args = _call_function_ex_replace_args_large(
                            lwmrn__hfxmz, huan__viwfg.body, new_body,
                            lsnik__cwzgv)
                njzgz__huen = ir.Expr.call(xntgm__jcv.func, args, nqo__qgo,
                    xntgm__jcv.loc, target=xntgm__jcv.target)
                if gwv__vkmkl.target.name in func_ir._definitions and len(
                    func_ir._definitions[gwv__vkmkl.target.name]) == 1:
                    func_ir._definitions[gwv__vkmkl.target.name].clear()
                func_ir._definitions[gwv__vkmkl.target.name].append(njzgz__huen
                    )
                gwv__vkmkl = ir.Assign(njzgz__huen, gwv__vkmkl.target,
                    gwv__vkmkl.loc)
            new_body.append(gwv__vkmkl)
        if kbz__kvb:
            huan__viwfg.body = [rykzk__xgn for rykzk__xgn in new_body if 
                rykzk__xgn is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for huan__viwfg in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        kbz__kvb = False
        for fvt__xen, gwv__vkmkl in enumerate(huan__viwfg.body):
            ctjqr__ekw = True
            uxaut__iptsv = None
            if isinstance(gwv__vkmkl, ir.Assign) and isinstance(gwv__vkmkl.
                value, ir.Expr):
                if gwv__vkmkl.value.op == 'build_map':
                    uxaut__iptsv = gwv__vkmkl.target.name
                    lit_old_idx[gwv__vkmkl.target.name] = fvt__xen
                    lit_new_idx[gwv__vkmkl.target.name] = fvt__xen
                    map_updates[gwv__vkmkl.target.name
                        ] = gwv__vkmkl.value.items.copy()
                    ctjqr__ekw = False
                elif gwv__vkmkl.value.op == 'call' and fvt__xen > 0:
                    vvdc__opbif = gwv__vkmkl.value.func.name
                    wtqgm__dfz = huan__viwfg.body[fvt__xen - 1]
                    args = gwv__vkmkl.value.args
                    if (isinstance(wtqgm__dfz, ir.Assign) and wtqgm__dfz.
                        target.name == vvdc__opbif and isinstance(
                        wtqgm__dfz.value, ir.Expr) and wtqgm__dfz.value.op ==
                        'getattr' and wtqgm__dfz.value.value.name in
                        lit_old_idx):
                        pgw__enuxd = wtqgm__dfz.value.value.name
                        xfp__rwj = wtqgm__dfz.value.attr
                        if xfp__rwj == '__setitem__':
                            ctjqr__ekw = False
                            map_updates[pgw__enuxd].append(args)
                            new_body[-1] = None
                        elif xfp__rwj == 'update' and args[0
                            ].name in lit_old_idx:
                            ctjqr__ekw = False
                            map_updates[pgw__enuxd].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not ctjqr__ekw:
                            lit_new_idx[pgw__enuxd] = fvt__xen
                            func_ir._definitions[wtqgm__dfz.target.name
                                ].remove(wtqgm__dfz.value)
            if not (isinstance(gwv__vkmkl, ir.Assign) and isinstance(
                gwv__vkmkl.value, ir.Expr) and gwv__vkmkl.value.op ==
                'getattr' and gwv__vkmkl.value.value.name in lit_old_idx and
                gwv__vkmkl.value.attr in ('__setitem__', 'update')):
                for sih__vhp in gwv__vkmkl.list_vars():
                    if (sih__vhp.name in lit_old_idx and sih__vhp.name !=
                        uxaut__iptsv):
                        _insert_build_map(func_ir, sih__vhp.name,
                            huan__viwfg.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if ctjqr__ekw:
                new_body.append(gwv__vkmkl)
            else:
                func_ir._definitions[gwv__vkmkl.target.name].remove(gwv__vkmkl
                    .value)
                kbz__kvb = True
                new_body.append(None)
        yowh__kveb = list(lit_old_idx.keys())
        for cfrv__llq in yowh__kveb:
            _insert_build_map(func_ir, cfrv__llq, huan__viwfg.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if kbz__kvb:
            huan__viwfg.body = [rykzk__xgn for rykzk__xgn in new_body if 
                rykzk__xgn is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    rga__aifb = lit_old_idx[name]
    qyzl__vlp = lit_new_idx[name]
    hrfa__xccg = map_updates[name]
    new_body[qyzl__vlp] = _build_new_build_map(func_ir, name, old_body,
        rga__aifb, hrfa__xccg)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    opnr__nuuno = old_body[old_lineno]
    dvzfr__tfgm = opnr__nuuno.target
    ykyv__ctu = opnr__nuuno.value
    qkf__dehwg = []
    rkhfn__xbee = []
    for hrjyo__onkdf in new_items:
        kiqu__iyp, voxs__jhe = hrjyo__onkdf
        qxn__gmcjg = guard(get_definition, func_ir, kiqu__iyp)
        if isinstance(qxn__gmcjg, (ir.Const, ir.Global, ir.FreeVar)):
            qkf__dehwg.append(qxn__gmcjg.value)
        aaceg__xgv = guard(get_definition, func_ir, voxs__jhe)
        if isinstance(aaceg__xgv, (ir.Const, ir.Global, ir.FreeVar)):
            rkhfn__xbee.append(aaceg__xgv.value)
        else:
            rkhfn__xbee.append(numba.core.interpreter._UNKNOWN_VALUE(
                voxs__jhe.name))
    qqtk__jqn = {}
    if len(qkf__dehwg) == len(new_items):
        etq__ufijw = {rykzk__xgn: jsi__usqo for rykzk__xgn, jsi__usqo in
            zip(qkf__dehwg, rkhfn__xbee)}
        for fvt__xen, kiqu__iyp in enumerate(qkf__dehwg):
            qqtk__jqn[kiqu__iyp] = fvt__xen
    else:
        etq__ufijw = None
    qlb__hvyzl = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=etq__ufijw, value_indexes=qqtk__jqn, loc=ykyv__ctu.loc)
    func_ir._definitions[name].append(qlb__hvyzl)
    return ir.Assign(qlb__hvyzl, ir.Var(dvzfr__tfgm.scope, name,
        dvzfr__tfgm.loc), qlb__hvyzl.loc)
