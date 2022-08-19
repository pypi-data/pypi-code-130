"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, get_definition, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates, peep_hole_fuse_tuple_adds
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    oocg__vdle = numba.core.bytecode.FunctionIdentity.from_function(func)
    jtf__jblk = numba.core.interpreter.Interpreter(oocg__vdle)
    aorls__xjjjl = numba.core.bytecode.ByteCode(func_id=oocg__vdle)
    func_ir = jtf__jblk.interpret(aorls__xjjjl)
    if PYVERSION == (3, 10):
        func_ir = peep_hole_call_function_ex_to_call_function_kw(func_ir)
        func_ir = peep_hole_fuse_dict_add_updates(func_ir)
        func_ir = peep_hole_fuse_tuple_adds(func_ir)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        mizm__umf = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        mizm__umf.run()
    eolty__gujvy = numba.core.postproc.PostProcessor(func_ir)
    eolty__gujvy.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, qta__eqen in visit_vars_extensions.items():
        if isinstance(stmt, t):
            qta__eqen(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    zklhz__gtm = ['ravel', 'transpose', 'reshape']
    for tfe__dowd in blocks.values():
        for wuop__zmk in tfe__dowd.body:
            if type(wuop__zmk) in alias_analysis_extensions:
                qta__eqen = alias_analysis_extensions[type(wuop__zmk)]
                qta__eqen(wuop__zmk, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(wuop__zmk, ir.Assign):
                lxfqa__clko = wuop__zmk.value
                xhx__rnwvr = wuop__zmk.target.name
                if is_immutable_type(xhx__rnwvr, typemap):
                    continue
                if isinstance(lxfqa__clko, ir.Var
                    ) and xhx__rnwvr != lxfqa__clko.name:
                    _add_alias(xhx__rnwvr, lxfqa__clko.name, alias_map,
                        arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr) and (lxfqa__clko.op ==
                    'cast' or lxfqa__clko.op in ['getitem', 'static_getitem']):
                    _add_alias(xhx__rnwvr, lxfqa__clko.value.name,
                        alias_map, arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr
                    ) and lxfqa__clko.op == 'inplace_binop':
                    _add_alias(xhx__rnwvr, lxfqa__clko.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr
                    ) and lxfqa__clko.op == 'getattr' and lxfqa__clko.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(xhx__rnwvr, lxfqa__clko.value.name,
                        alias_map, arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr
                    ) and lxfqa__clko.op == 'getattr' and lxfqa__clko.attr not in [
                    'shape'] and lxfqa__clko.value.name in arg_aliases:
                    _add_alias(xhx__rnwvr, lxfqa__clko.value.name,
                        alias_map, arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr
                    ) and lxfqa__clko.op == 'getattr' and lxfqa__clko.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(xhx__rnwvr, lxfqa__clko.value.name,
                        alias_map, arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr) and lxfqa__clko.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(xhx__rnwvr, typemap):
                    for yrlju__gwzru in lxfqa__clko.items:
                        _add_alias(xhx__rnwvr, yrlju__gwzru.name, alias_map,
                            arg_aliases)
                if isinstance(lxfqa__clko, ir.Expr
                    ) and lxfqa__clko.op == 'call':
                    rhdq__plm = guard(find_callname, func_ir, lxfqa__clko,
                        typemap)
                    if rhdq__plm is None:
                        continue
                    zunpx__bkkk, hdqk__hqdzq = rhdq__plm
                    if rhdq__plm in alias_func_extensions:
                        sau__hyv = alias_func_extensions[rhdq__plm]
                        sau__hyv(xhx__rnwvr, lxfqa__clko.args, alias_map,
                            arg_aliases)
                    if hdqk__hqdzq == 'numpy' and zunpx__bkkk in zklhz__gtm:
                        _add_alias(xhx__rnwvr, lxfqa__clko.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(hdqk__hqdzq, ir.Var
                        ) and zunpx__bkkk in zklhz__gtm:
                        _add_alias(xhx__rnwvr, hdqk__hqdzq.name, alias_map,
                            arg_aliases)
    lha__wjot = copy.deepcopy(alias_map)
    for yrlju__gwzru in lha__wjot:
        for aoh__ydfya in lha__wjot[yrlju__gwzru]:
            alias_map[yrlju__gwzru] |= alias_map[aoh__ydfya]
        for aoh__ydfya in lha__wjot[yrlju__gwzru]:
            alias_map[aoh__ydfya] = alias_map[yrlju__gwzru]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    hapkz__gxjl = compute_cfg_from_blocks(func_ir.blocks)
    jdk__bfhjf = compute_use_defs(func_ir.blocks)
    qakuf__blqk = compute_live_map(hapkz__gxjl, func_ir.blocks, jdk__bfhjf.
        usemap, jdk__bfhjf.defmap)
    mmybw__rdt = True
    while mmybw__rdt:
        mmybw__rdt = False
        for label, block in func_ir.blocks.items():
            lives = {yrlju__gwzru.name for yrlju__gwzru in block.terminator
                .list_vars()}
            for dnhnw__pgeh, fzt__wvtp in hapkz__gxjl.successors(label):
                lives |= qakuf__blqk[dnhnw__pgeh]
            yfat__qnkm = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    xhx__rnwvr = stmt.target
                    gis__tcnj = stmt.value
                    if xhx__rnwvr.name not in lives:
                        if isinstance(gis__tcnj, ir.Expr
                            ) and gis__tcnj.op == 'make_function':
                            continue
                        if isinstance(gis__tcnj, ir.Expr
                            ) and gis__tcnj.op == 'getattr':
                            continue
                        if isinstance(gis__tcnj, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(xhx__rnwvr,
                            None), types.Function):
                            continue
                        if isinstance(gis__tcnj, ir.Expr
                            ) and gis__tcnj.op == 'build_map':
                            continue
                        if isinstance(gis__tcnj, ir.Expr
                            ) and gis__tcnj.op == 'build_tuple':
                            continue
                    if isinstance(gis__tcnj, ir.Var
                        ) and xhx__rnwvr.name == gis__tcnj.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    qlp__xolcn = analysis.ir_extension_usedefs[type(stmt)]
                    gjzb__extzg, fprb__idnjn = qlp__xolcn(stmt)
                    lives -= fprb__idnjn
                    lives |= gjzb__extzg
                else:
                    lives |= {yrlju__gwzru.name for yrlju__gwzru in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(xhx__rnwvr.name)
                yfat__qnkm.append(stmt)
            yfat__qnkm.reverse()
            if len(block.body) != len(yfat__qnkm):
                mmybw__rdt = True
            block.body = yfat__qnkm


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    alpp__ujgkx = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (alpp__ujgkx,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    gyzw__pkp = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), gyzw__pkp)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for ubnjs__bxmve in fnty.templates:
                self._inline_overloads.update(ubnjs__bxmve._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    gyzw__pkp = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), gyzw__pkp)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    kayzk__hpfn, fdiw__wcof = self._get_impl(args, kws)
    if kayzk__hpfn is None:
        return
    ncqhj__obpy = types.Dispatcher(kayzk__hpfn)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        aycro__fayd = kayzk__hpfn._compiler
        flags = compiler.Flags()
        cblz__blx = aycro__fayd.targetdescr.typing_context
        tokhx__pfimp = aycro__fayd.targetdescr.target_context
        jvcqu__pycr = aycro__fayd.pipeline_class(cblz__blx, tokhx__pfimp,
            None, None, None, flags, None)
        qkfrk__hkv = InlineWorker(cblz__blx, tokhx__pfimp, aycro__fayd.
            locals, jvcqu__pycr, flags, None)
        fjp__ien = ncqhj__obpy.dispatcher.get_call_template
        ubnjs__bxmve, zuv__dmdpd, osf__kysea, kws = fjp__ien(fdiw__wcof, kws)
        if osf__kysea in self._inline_overloads:
            return self._inline_overloads[osf__kysea]['iinfo'].signature
        ir = qkfrk__hkv.run_untyped_passes(ncqhj__obpy.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, tokhx__pfimp, ir, osf__kysea, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, osf__kysea, None)
        self._inline_overloads[sig.args] = {'folded_args': osf__kysea}
        puilw__poqp = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = puilw__poqp
        if not self._inline.is_always_inline:
            sig = ncqhj__obpy.get_call_type(self.context, fdiw__wcof, kws)
            self._compiled_overloads[sig.args] = ncqhj__obpy.get_overload(sig)
        yjj__rly = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': osf__kysea,
            'iinfo': yjj__rly}
    else:
        sig = ncqhj__obpy.get_call_type(self.context, fdiw__wcof, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = ncqhj__obpy.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    hlpam__xobp = [True, False]
    pqgko__bvdh = [False, True]
    gbcu__unq = _ResolutionFailures(context, self, args, kws, depth=self._depth
        )
    from numba.core.target_extension import get_local_target
    qtgmm__iyq = get_local_target(context)
    kyjfk__gpnws = utils.order_by_target_specificity(qtgmm__iyq, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for vfd__fix in kyjfk__gpnws:
        ecl__hgez = vfd__fix(context)
        xap__ueabb = hlpam__xobp if ecl__hgez.prefer_literal else pqgko__bvdh
        xap__ueabb = [True] if getattr(ecl__hgez, '_no_unliteral', False
            ) else xap__ueabb
        for uili__hhgoq in xap__ueabb:
            try:
                if uili__hhgoq:
                    sig = ecl__hgez.apply(args, kws)
                else:
                    dkteq__qog = tuple([_unlit_non_poison(a) for a in args])
                    nqx__lwe = {djmm__iya: _unlit_non_poison(yrlju__gwzru) for
                        djmm__iya, yrlju__gwzru in kws.items()}
                    sig = ecl__hgez.apply(dkteq__qog, nqx__lwe)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    gbcu__unq.add_error(ecl__hgez, False, e, uili__hhgoq)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = ecl__hgez.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    koxkf__nzkf = getattr(ecl__hgez, 'cases', None)
                    if koxkf__nzkf is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            koxkf__nzkf)
                    else:
                        msg = 'No match.'
                    gbcu__unq.add_error(ecl__hgez, True, msg, uili__hhgoq)
    gbcu__unq.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    ubnjs__bxmve = self.template(context)
    lmn__epnql = None
    omwqn__cgx = None
    odng__mnult = None
    xap__ueabb = [True, False] if ubnjs__bxmve.prefer_literal else [False, True
        ]
    xap__ueabb = [True] if getattr(ubnjs__bxmve, '_no_unliteral', False
        ) else xap__ueabb
    for uili__hhgoq in xap__ueabb:
        if uili__hhgoq:
            try:
                odng__mnult = ubnjs__bxmve.apply(args, kws)
            except Exception as yvcf__aclal:
                if isinstance(yvcf__aclal, errors.ForceLiteralArg):
                    raise yvcf__aclal
                lmn__epnql = yvcf__aclal
                odng__mnult = None
            else:
                break
        else:
            dpwy__dqm = tuple([_unlit_non_poison(a) for a in args])
            hfa__rebr = {djmm__iya: _unlit_non_poison(yrlju__gwzru) for 
                djmm__iya, yrlju__gwzru in kws.items()}
            zpd__npxzg = dpwy__dqm == args and kws == hfa__rebr
            if not zpd__npxzg and odng__mnult is None:
                try:
                    odng__mnult = ubnjs__bxmve.apply(dpwy__dqm, hfa__rebr)
                except Exception as yvcf__aclal:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        yvcf__aclal, errors.NumbaError):
                        raise yvcf__aclal
                    if isinstance(yvcf__aclal, errors.ForceLiteralArg):
                        if ubnjs__bxmve.prefer_literal:
                            raise yvcf__aclal
                    omwqn__cgx = yvcf__aclal
                else:
                    break
    if odng__mnult is None and (omwqn__cgx is not None or lmn__epnql is not
        None):
        giqch__xcs = '- Resolution failure for {} arguments:\n{}\n'
        jybn__pqiv = _termcolor.highlight(giqch__xcs)
        if numba.core.config.DEVELOPER_MODE:
            gzsv__dvftr = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    qad__lmq = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    qad__lmq = ['']
                mjtte__kopwa = '\n{}'.format(2 * gzsv__dvftr)
                rwo__xvbqx = _termcolor.reset(mjtte__kopwa + mjtte__kopwa.
                    join(_bt_as_lines(qad__lmq)))
                return _termcolor.reset(rwo__xvbqx)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            jnzuo__hewjv = str(e)
            jnzuo__hewjv = jnzuo__hewjv if jnzuo__hewjv else str(repr(e)
                ) + add_bt(e)
            mbdu__iqc = errors.TypingError(textwrap.dedent(jnzuo__hewjv))
            return jybn__pqiv.format(literalness, str(mbdu__iqc))
        import bodo
        if isinstance(lmn__epnql, bodo.utils.typing.BodoError):
            raise lmn__epnql
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', lmn__epnql) +
                nested_msg('non-literal', omwqn__cgx))
        else:
            if 'missing a required argument' in lmn__epnql.msg:
                msg = 'missing a required argument'
            else:
                msg = 'Compilation error for '
                if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                    DataFrameType):
                    msg += 'DataFrame.'
                elif isinstance(self.this, bodo.hiframes.pd_series_ext.
                    SeriesType):
                    msg += 'Series.'
                msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg, loc=lmn__epnql.loc)
    return odng__mnult


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite import ir as lir
    fnty = lir.FunctionType(self.pyobj, [self.cstring, self.py_ssize_t])
    zunpx__bkkk = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=zunpx__bkkk)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            qmhz__mry = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), qmhz__mry)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    kwk__dtpr = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            kwk__dtpr.append(types.Omitted(a.value))
        else:
            kwk__dtpr.append(self.typeof_pyval(a))
    vag__hwl = None
    try:
        error = None
        vag__hwl = self.compile(tuple(kwk__dtpr))
    except errors.ForceLiteralArg as e:
        lzjz__bpen = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if lzjz__bpen:
            vvj__wde = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            qhxcu__acs = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(lzjz__bpen))
            raise errors.CompilerError(vvj__wde.format(qhxcu__acs))
        fdiw__wcof = []
        try:
            for i, yrlju__gwzru in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        fdiw__wcof.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        fdiw__wcof.append(types.literal(args[i]))
                else:
                    fdiw__wcof.append(args[i])
            args = fdiw__wcof
        except (OSError, FileNotFoundError) as acry__zjsl:
            error = FileNotFoundError(str(acry__zjsl) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                vag__hwl = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        pcuc__wan = []
        for i, byaw__mgne in enumerate(args):
            val = byaw__mgne.value if isinstance(byaw__mgne, numba.core.
                dispatcher.OmittedArg) else byaw__mgne
            try:
                qznb__vconv = typeof(val, Purpose.argument)
            except ValueError as xjo__iiw:
                pcuc__wan.append((i, str(xjo__iiw)))
            else:
                if qznb__vconv is None:
                    pcuc__wan.append((i,
                        f'cannot determine Numba type of value {val}'))
        if pcuc__wan:
            dnwyh__zbszx = '\n'.join(f'- argument {i}: {rlpu__ihmiz}' for i,
                rlpu__ihmiz in pcuc__wan)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{dnwyh__zbszx}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                vuqh__wnwu = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                npsof__bndl = False
                for sreat__unnk in vuqh__wnwu:
                    if sreat__unnk in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        npsof__bndl = True
                        break
                if not npsof__bndl:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                qmhz__mry = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), qmhz__mry)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return vag__hwl


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for ysp__aoe in cres.library._codegen._engine._defined_symbols:
        if ysp__aoe.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in ysp__aoe and (
            'bodo_gb_udf_update_local' in ysp__aoe or 'bodo_gb_udf_combine' in
            ysp__aoe or 'bodo_gb_udf_eval' in ysp__aoe or 
            'bodo_gb_apply_general_udfs' in ysp__aoe):
            gb_agg_cfunc_addr[ysp__aoe] = cres.library.get_pointer_to_function(
                ysp__aoe)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for ysp__aoe in cres.library._codegen._engine._defined_symbols:
        if ysp__aoe.startswith('cfunc') and ('get_join_cond_addr' not in
            ysp__aoe or 'bodo_join_gen_cond' in ysp__aoe):
            join_gen_cond_cfunc_addr[ysp__aoe
                ] = cres.library.get_pointer_to_function(ysp__aoe)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    kayzk__hpfn = self._get_dispatcher_for_current_target()
    if kayzk__hpfn is not self:
        return kayzk__hpfn.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            wfyao__cmvjg = self.overloads.get(tuple(args))
            if wfyao__cmvjg is not None:
                return wfyao__cmvjg.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            tgdd__goq = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=tgdd__goq):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
                if bodo.get_rank() == 0:
                    self._cache.save_overload(sig, cres)
            else:
                ojwh__pita = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in ojwh__pita:
                    self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    eusmt__rdb = self._final_module
    nzim__uqn = []
    cujft__rsku = 0
    for fn in eusmt__rdb.functions:
        cujft__rsku += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            nzim__uqn.append(fn.name)
    if cujft__rsku == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if nzim__uqn:
        eusmt__rdb = eusmt__rdb.clone()
        for name in nzim__uqn:
            eusmt__rdb.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = eusmt__rdb
    return eusmt__rdb


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for fuldx__xsycf in self.constraints:
        loc = fuldx__xsycf.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                fuldx__xsycf(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                ldt__eoj = numba.core.errors.TypingError(str(e), loc=
                    fuldx__xsycf.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(ldt__eoj, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    ldt__eoj = numba.core.errors.TypingError(msg.format(con
                        =fuldx__xsycf, err=str(e)), loc=fuldx__xsycf.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(ldt__eoj, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for oxjdx__wgoej in self._failures.values():
        for hpjsl__rqxco in oxjdx__wgoej:
            if isinstance(hpjsl__rqxco.error, ForceLiteralArg):
                raise hpjsl__rqxco.error
            if isinstance(hpjsl__rqxco.error, bodo.utils.typing.BodoError):
                raise hpjsl__rqxco.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    jrjsh__rtxz = False
    yfat__qnkm = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        zfgd__ggngx = set()
        srdah__nakr = lives & alias_set
        for yrlju__gwzru in srdah__nakr:
            zfgd__ggngx |= alias_map[yrlju__gwzru]
        lives_n_aliases = lives | zfgd__ggngx | arg_aliases
        if type(stmt) in remove_dead_extensions:
            qta__eqen = remove_dead_extensions[type(stmt)]
            stmt = qta__eqen(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                jrjsh__rtxz = True
                continue
        if isinstance(stmt, ir.Assign):
            xhx__rnwvr = stmt.target
            gis__tcnj = stmt.value
            if xhx__rnwvr.name not in lives:
                if has_no_side_effect(gis__tcnj, lives_n_aliases, call_table):
                    jrjsh__rtxz = True
                    continue
                if isinstance(gis__tcnj, ir.Expr
                    ) and gis__tcnj.op == 'call' and call_table[gis__tcnj.
                    func.name] == ['astype']:
                    ewc__fuocw = guard(get_definition, func_ir, gis__tcnj.func)
                    if (ewc__fuocw is not None and ewc__fuocw.op ==
                        'getattr' and isinstance(typemap[ewc__fuocw.value.
                        name], types.Array) and ewc__fuocw.attr == 'astype'):
                        jrjsh__rtxz = True
                        continue
            if saved_array_analysis and xhx__rnwvr.name in lives and is_expr(
                gis__tcnj, 'getattr'
                ) and gis__tcnj.attr == 'shape' and is_array_typ(typemap[
                gis__tcnj.value.name]) and gis__tcnj.value.name not in lives:
                jlvx__jjpb = {yrlju__gwzru: djmm__iya for djmm__iya,
                    yrlju__gwzru in func_ir.blocks.items()}
                if block in jlvx__jjpb:
                    label = jlvx__jjpb[block]
                    bnlq__lxe = saved_array_analysis.get_equiv_set(label)
                    pqp__ahh = bnlq__lxe.get_equiv_set(gis__tcnj.value)
                    if pqp__ahh is not None:
                        for yrlju__gwzru in pqp__ahh:
                            if yrlju__gwzru.endswith('#0'):
                                yrlju__gwzru = yrlju__gwzru[:-2]
                            if yrlju__gwzru in typemap and is_array_typ(typemap
                                [yrlju__gwzru]) and yrlju__gwzru in lives:
                                gis__tcnj.value = ir.Var(gis__tcnj.value.
                                    scope, yrlju__gwzru, gis__tcnj.value.loc)
                                jrjsh__rtxz = True
                                break
            if isinstance(gis__tcnj, ir.Var
                ) and xhx__rnwvr.name == gis__tcnj.name:
                jrjsh__rtxz = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                jrjsh__rtxz = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            qlp__xolcn = analysis.ir_extension_usedefs[type(stmt)]
            gjzb__extzg, fprb__idnjn = qlp__xolcn(stmt)
            lives -= fprb__idnjn
            lives |= gjzb__extzg
        else:
            lives |= {yrlju__gwzru.name for yrlju__gwzru in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                mzmgy__mimi = set()
                if isinstance(gis__tcnj, ir.Expr):
                    mzmgy__mimi = {yrlju__gwzru.name for yrlju__gwzru in
                        gis__tcnj.list_vars()}
                if xhx__rnwvr.name not in mzmgy__mimi:
                    lives.remove(xhx__rnwvr.name)
        yfat__qnkm.append(stmt)
    yfat__qnkm.reverse()
    block.body = yfat__qnkm
    return jrjsh__rtxz


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            nebkq__rkzv, = args
            if isinstance(nebkq__rkzv, types.IterableType):
                dtype = nebkq__rkzv.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), nebkq__rkzv)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    pglcc__ymn = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (pglcc__ymn, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as hcx__cup:
            return
    try:
        return literal(value)
    except LiteralTypingError as hcx__cup:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        vlmh__ztmh = py_func.__qualname__
    except AttributeError as hcx__cup:
        vlmh__ztmh = py_func.__name__
    zhywh__tjcub = inspect.getfile(py_func)
    for cls in self._locator_classes:
        wvw__vldj = cls.from_function(py_func, zhywh__tjcub)
        if wvw__vldj is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (vlmh__ztmh, zhywh__tjcub))
    self._locator = wvw__vldj
    jlaz__jix = inspect.getfile(py_func)
    hocwx__dcfc = os.path.splitext(os.path.basename(jlaz__jix))[0]
    if zhywh__tjcub.startswith('<ipython-'):
        abpey__atbi = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', hocwx__dcfc, count=1)
        if abpey__atbi == hocwx__dcfc:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        hocwx__dcfc = abpey__atbi
    jnfug__yaqff = '%s.%s' % (hocwx__dcfc, vlmh__ztmh)
    tcw__dvc = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(jnfug__yaqff, tcw__dvc
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    wezep__kpgz = list(filter(lambda a: self._istuple(a.name), args))
    if len(wezep__kpgz) == 2 and fn.__name__ == 'add':
        jhlat__duodk = self.typemap[wezep__kpgz[0].name]
        hxca__alzz = self.typemap[wezep__kpgz[1].name]
        if jhlat__duodk.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wezep__kpgz[1]))
        if hxca__alzz.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                wezep__kpgz[0]))
        try:
            dcjt__uax = [equiv_set.get_shape(x) for x in wezep__kpgz]
            if None in dcjt__uax:
                return None
            kav__jfq = sum(dcjt__uax, ())
            return ArrayAnalysis.AnalyzeResult(shape=kav__jfq)
        except GuardException as hcx__cup:
            return None
    uiz__yyr = list(filter(lambda a: self._isarray(a.name), args))
    require(len(uiz__yyr) > 0)
    vyvk__gtn = [x.name for x in uiz__yyr]
    nhfbq__yld = [self.typemap[x.name].ndim for x in uiz__yyr]
    kgu__ncoiv = max(nhfbq__yld)
    require(kgu__ncoiv > 0)
    dcjt__uax = [equiv_set.get_shape(x) for x in uiz__yyr]
    if any(a is None for a in dcjt__uax):
        return ArrayAnalysis.AnalyzeResult(shape=uiz__yyr[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, uiz__yyr))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, dcjt__uax,
        vyvk__gtn)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    jnswz__jbnwv = code_obj.code
    jnsgw__ngpo = len(jnswz__jbnwv.co_freevars)
    usmwc__wxvny = jnswz__jbnwv.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        ctfu__wppw, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        usmwc__wxvny = [yrlju__gwzru.name for yrlju__gwzru in ctfu__wppw]
    eauts__tmgfd = caller_ir.func_id.func.__globals__
    try:
        eauts__tmgfd = getattr(code_obj, 'globals', eauts__tmgfd)
    except KeyError as hcx__cup:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    qwox__vimpq = []
    for x in usmwc__wxvny:
        try:
            jlbin__knzk = caller_ir.get_definition(x)
        except KeyError as hcx__cup:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(jlbin__knzk, (ir.Const, ir.Global, ir.FreeVar)):
            val = jlbin__knzk.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                alpp__ujgkx = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                eauts__tmgfd[alpp__ujgkx] = bodo.jit(distributed=False)(val)
                eauts__tmgfd[alpp__ujgkx].is_nested_func = True
                val = alpp__ujgkx
            if isinstance(val, CPUDispatcher):
                alpp__ujgkx = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                eauts__tmgfd[alpp__ujgkx] = val
                val = alpp__ujgkx
            qwox__vimpq.append(val)
        elif isinstance(jlbin__knzk, ir.Expr
            ) and jlbin__knzk.op == 'make_function':
            hbp__vxdn = convert_code_obj_to_function(jlbin__knzk, caller_ir)
            alpp__ujgkx = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            eauts__tmgfd[alpp__ujgkx] = bodo.jit(distributed=False)(hbp__vxdn)
            eauts__tmgfd[alpp__ujgkx].is_nested_func = True
            qwox__vimpq.append(alpp__ujgkx)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    oguxt__yrly = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate
        (qwox__vimpq)])
    hdy__cryhp = ','.join([('c_%d' % i) for i in range(jnsgw__ngpo)])
    gejef__wba = list(jnswz__jbnwv.co_varnames)
    ccw__ssw = 0
    ivlt__ilpm = jnswz__jbnwv.co_argcount
    utjhp__xzc = caller_ir.get_definition(code_obj.defaults)
    if utjhp__xzc is not None:
        if isinstance(utjhp__xzc, tuple):
            d = [caller_ir.get_definition(x).value for x in utjhp__xzc]
            sozf__osdz = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in utjhp__xzc.items]
            sozf__osdz = tuple(d)
        ccw__ssw = len(sozf__osdz)
    mokvo__wgmdo = ivlt__ilpm - ccw__ssw
    vwl__sjpm = ','.join([('%s' % gejef__wba[i]) for i in range(mokvo__wgmdo)])
    if ccw__ssw:
        ouqk__lrxv = [('%s = %s' % (gejef__wba[i + mokvo__wgmdo],
            sozf__osdz[i])) for i in range(ccw__ssw)]
        vwl__sjpm += ', '
        vwl__sjpm += ', '.join(ouqk__lrxv)
    return _create_function_from_code_obj(jnswz__jbnwv, oguxt__yrly,
        vwl__sjpm, hdy__cryhp, eauts__tmgfd)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for syi__ieij, (fqy__gpzdr, ccmgb__ojfld) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % ccmgb__ojfld)
            xhz__gnhz = _pass_registry.get(fqy__gpzdr).pass_inst
            if isinstance(xhz__gnhz, CompilerPass):
                self._runPass(syi__ieij, xhz__gnhz, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, ccmgb__ojfld)
                oyva__gfkt = self._patch_error(msg, e)
                raise oyva__gfkt
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    weth__xgxh = None
    fprb__idnjn = {}

    def lookup(var, already_seen, varonly=True):
        val = fprb__idnjn.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    jggc__vte = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        xhx__rnwvr = stmt.target
        gis__tcnj = stmt.value
        fprb__idnjn[xhx__rnwvr.name] = gis__tcnj
        if isinstance(gis__tcnj, ir.Var) and gis__tcnj.name in fprb__idnjn:
            gis__tcnj = lookup(gis__tcnj, set())
        if isinstance(gis__tcnj, ir.Expr):
            mmn__yexi = set(lookup(yrlju__gwzru, set(), True).name for
                yrlju__gwzru in gis__tcnj.list_vars())
            if name in mmn__yexi:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(gis__tcnj)]
                pjx__clgbw = [x for x, ckyp__lfj in args if ckyp__lfj.name !=
                    name]
                args = [(x, ckyp__lfj) for x, ckyp__lfj in args if x !=
                    ckyp__lfj.name]
                agx__itvn = dict(args)
                if len(pjx__clgbw) == 1:
                    agx__itvn[pjx__clgbw[0]] = ir.Var(xhx__rnwvr.scope, 
                        name + '#init', xhx__rnwvr.loc)
                replace_vars_inner(gis__tcnj, agx__itvn)
                weth__xgxh = nodes[i:]
                break
    return weth__xgxh


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        dnr__dyiy = expand_aliases({yrlju__gwzru.name for yrlju__gwzru in
            stmt.list_vars()}, alias_map, arg_aliases)
        wkwzy__xmic = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        vxp__qie = expand_aliases({yrlju__gwzru.name for yrlju__gwzru in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        dqq__wnad = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(wkwzy__xmic & vxp__qie | dqq__wnad & dnr__dyiy) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    tpewk__pjcg = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            tpewk__pjcg.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                tpewk__pjcg.update(get_parfor_writes(stmt, func_ir))
    return tpewk__pjcg


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    tpewk__pjcg = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        tpewk__pjcg.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        tpewk__pjcg = {yrlju__gwzru.name for yrlju__gwzru in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        tpewk__pjcg = {yrlju__gwzru.name for yrlju__gwzru in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            tpewk__pjcg.update({yrlju__gwzru.name for yrlju__gwzru in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        rhdq__plm = guard(find_callname, func_ir, stmt.value)
        if rhdq__plm in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            tpewk__pjcg.add(stmt.value.args[0].name)
        if rhdq__plm == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            tpewk__pjcg.add(stmt.value.args[1].name)
    return tpewk__pjcg


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        qta__eqen = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        tycdu__syuo = qta__eqen.format(self, msg)
        self.args = tycdu__syuo,
    else:
        qta__eqen = _termcolor.errmsg('{0}')
        tycdu__syuo = qta__eqen.format(self)
        self.args = tycdu__syuo,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for itlu__jjzn in options['distributed']:
            dist_spec[itlu__jjzn] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for itlu__jjzn in options['distributed_block']:
            dist_spec[itlu__jjzn] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    cof__eqd = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, qrpfz__uuj in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(qrpfz__uuj)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    cwlm__ugr = {}
    for crnj__hjh in reversed(inspect.getmro(cls)):
        cwlm__ugr.update(crnj__hjh.__dict__)
    ypgph__zai, fnu__wcdoo, zdbl__jxj, cwg__vdjfl = {}, {}, {}, {}
    for djmm__iya, yrlju__gwzru in cwlm__ugr.items():
        if isinstance(yrlju__gwzru, pytypes.FunctionType):
            ypgph__zai[djmm__iya] = yrlju__gwzru
        elif isinstance(yrlju__gwzru, property):
            fnu__wcdoo[djmm__iya] = yrlju__gwzru
        elif isinstance(yrlju__gwzru, staticmethod):
            zdbl__jxj[djmm__iya] = yrlju__gwzru
        else:
            cwg__vdjfl[djmm__iya] = yrlju__gwzru
    pigcg__cvg = (set(ypgph__zai) | set(fnu__wcdoo) | set(zdbl__jxj)) & set(
        spec)
    if pigcg__cvg:
        raise NameError('name shadowing: {0}'.format(', '.join(pigcg__cvg)))
    fhvt__rjq = cwg__vdjfl.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(cwg__vdjfl)
    if cwg__vdjfl:
        msg = 'class members are not yet supported: {0}'
        rnho__une = ', '.join(cwg__vdjfl.keys())
        raise TypeError(msg.format(rnho__une))
    for djmm__iya, yrlju__gwzru in fnu__wcdoo.items():
        if yrlju__gwzru.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(djmm__iya))
    jit_methods = {djmm__iya: bodo.jit(returns_maybe_distributed=cof__eqd)(
        yrlju__gwzru) for djmm__iya, yrlju__gwzru in ypgph__zai.items()}
    jit_props = {}
    for djmm__iya, yrlju__gwzru in fnu__wcdoo.items():
        gyzw__pkp = {}
        if yrlju__gwzru.fget:
            gyzw__pkp['get'] = bodo.jit(yrlju__gwzru.fget)
        if yrlju__gwzru.fset:
            gyzw__pkp['set'] = bodo.jit(yrlju__gwzru.fset)
        jit_props[djmm__iya] = gyzw__pkp
    jit_static_methods = {djmm__iya: bodo.jit(yrlju__gwzru.__func__) for 
        djmm__iya, yrlju__gwzru in zdbl__jxj.items()}
    cnu__qnsyc = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    qldt__xjehi = dict(class_type=cnu__qnsyc, __doc__=fhvt__rjq)
    qldt__xjehi.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), qldt__xjehi)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, cnu__qnsyc)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(cnu__qnsyc, typingctx, targetctx).register()
    as_numba_type.register(cls, cnu__qnsyc.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    fxalu__bhsu = ','.join('{0}:{1}'.format(djmm__iya, yrlju__gwzru) for 
        djmm__iya, yrlju__gwzru in struct.items())
    qbhq__lzvkd = ','.join('{0}:{1}'.format(djmm__iya, yrlju__gwzru) for 
        djmm__iya, yrlju__gwzru in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), fxalu__bhsu, qbhq__lzvkd)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    fuz__jxlq = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if fuz__jxlq is None:
        return
    xvox__vzl, xos__rxcf = fuz__jxlq
    for a in itertools.chain(xvox__vzl, xos__rxcf.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, xvox__vzl, xos__rxcf)
    except ForceLiteralArg as e:
        zsn__vlcz = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(zsn__vlcz, self.kws)
        dmtb__yncy = set()
        izq__eyrow = set()
        iigbr__zcqa = {}
        for syi__ieij in e.requested_args:
            mfzfi__eoheh = typeinfer.func_ir.get_definition(folded[syi__ieij])
            if isinstance(mfzfi__eoheh, ir.Arg):
                dmtb__yncy.add(mfzfi__eoheh.index)
                if mfzfi__eoheh.index in e.file_infos:
                    iigbr__zcqa[mfzfi__eoheh.index] = e.file_infos[mfzfi__eoheh
                        .index]
            else:
                izq__eyrow.add(syi__ieij)
        if izq__eyrow:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif dmtb__yncy:
            raise ForceLiteralArg(dmtb__yncy, loc=self.loc, file_infos=
                iigbr__zcqa)
    if sig is None:
        etyz__gbyi = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in xvox__vzl]
        args += [('%s=%s' % (djmm__iya, yrlju__gwzru)) for djmm__iya,
            yrlju__gwzru in sorted(xos__rxcf.items())]
        ukh__bhsu = etyz__gbyi.format(fnty, ', '.join(map(str, args)))
        xwr__nthrg = context.explain_function_type(fnty)
        msg = '\n'.join([ukh__bhsu, xwr__nthrg])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        hyo__peds = context.unify_pairs(sig.recvr, fnty.this)
        if hyo__peds is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if hyo__peds is not None and hyo__peds.is_precise():
            zwzh__hpboj = fnty.copy(this=hyo__peds)
            typeinfer.propagate_refined_type(self.func, zwzh__hpboj)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            dnu__uxvs = target.getone()
            if context.unify_pairs(dnu__uxvs, sig.return_type) == dnu__uxvs:
                sig = sig.replace(return_type=dnu__uxvs)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        vvj__wde = '*other* must be a {} but got a {} instead'
        raise TypeError(vvj__wde.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args,
        file_infos={**self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    kwo__fcaek = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for djmm__iya, yrlju__gwzru in kwargs.items():
        umki__jxh = None
        try:
            gorjv__zata = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[gorjv__zata.name] = [yrlju__gwzru]
            umki__jxh = get_const_value_inner(func_ir, gorjv__zata)
            func_ir._definitions.pop(gorjv__zata.name)
            if isinstance(umki__jxh, str):
                umki__jxh = sigutils._parse_signature_string(umki__jxh)
            if isinstance(umki__jxh, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {djmm__iya} is annotated as type class {umki__jxh}."""
                    )
            assert isinstance(umki__jxh, types.Type)
            if isinstance(umki__jxh, (types.List, types.Set)):
                umki__jxh = umki__jxh.copy(reflected=False)
            kwo__fcaek[djmm__iya] = umki__jxh
        except BodoError as hcx__cup:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(umki__jxh, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(yrlju__gwzru, ir.Global):
                    msg = f'Global {yrlju__gwzru.name!r} is not defined.'
                if isinstance(yrlju__gwzru, ir.FreeVar):
                    msg = f'Freevar {yrlju__gwzru.name!r} is not defined.'
            if isinstance(yrlju__gwzru, ir.Expr
                ) and yrlju__gwzru.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=djmm__iya, msg=msg, loc=loc)
    for name, typ in kwo__fcaek.items():
        self._legalize_arg_type(name, typ, loc)
    return kwo__fcaek


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    fke__jsxv = inst.arg
    assert fke__jsxv > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(fke__jsxv)]))
    tmps = [state.make_temp() for _ in range(fke__jsxv - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    vpw__pog = ir.Global('format', format, loc=self.loc)
    self.store(value=vpw__pog, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    emmgt__rog = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=emmgt__rog, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    fke__jsxv = inst.arg
    assert fke__jsxv > 0, 'invalid BUILD_STRING count'
    zrigw__mjxf = self.get(strings[0])
    for other, kobh__icdm in zip(strings[1:], tmps):
        other = self.get(other)
        lxfqa__clko = ir.Expr.binop(operator.add, lhs=zrigw__mjxf, rhs=
            other, loc=self.loc)
        self.store(lxfqa__clko, kobh__icdm)
        zrigw__mjxf = self.get(kobh__icdm)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    xst__fvqrz = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, xst__fvqrz])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    sfga__tphgt = mk_unique_var(f'{var_name}')
    qpovz__pcvp = sfga__tphgt.replace('<', '_').replace('>', '_')
    qpovz__pcvp = qpovz__pcvp.replace('.', '_').replace('$', '_v')
    return qpovz__pcvp


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    import bodo
    ty = classty.instance_type
    if isinstance(ty, types.NPDatetime):

        def typer(val1, val2):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(val1,
                'numpy.datetime64')
            if val1 == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
                if not is_overload_constant_str(val2):
                    raise_bodo_error(
                        "datetime64(): 'units' must be a 'str' specifying 'ns'"
                        )
                egicl__jxhf = get_overload_const_str(val2)
                if egicl__jxhf != 'ns':
                    raise BodoError("datetime64(): 'units' must be 'ns'")
                return types.NPDatetime('ns')
    else:

        def typer(val):
            if isinstance(val, (types.BaseTuple, types.Sequence)):
                fnty = self.context.resolve_value_type(np.array)
                sig = fnty.get_call_type(self.context, (val, types.DType(ty
                    )), {})
                return sig.return_type
            elif isinstance(val, (types.Number, types.Boolean, types.
                IntEnumMember)):
                return ty
            elif val == types.unicode_type:
                return ty
            elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
                if ty.bitwidth == 64:
                    return ty
                else:
                    msg = (
                        f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                        )
                    raise errors.TypingError(msg)
            elif isinstance(val, types.Array
                ) and val.ndim == 0 and val.dtype == ty:
                return ty
            else:
                msg = f'Casting {val} to {ty} directly is unsupported.'
                if isinstance(val, types.Array):
                    msg += f" Try doing '<array>.astype(np.{ty})' instead"
                raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        wqblz__whmfm = states['defmap']
        if len(wqblz__whmfm) == 0:
            yhk__hek = assign.target
            numba.core.ssa._logger.debug('first assign: %s', yhk__hek)
            if yhk__hek.name not in scope.localvars:
                yhk__hek = scope.define(assign.target.name, loc=assign.loc)
        else:
            yhk__hek = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=yhk__hek, value=assign.value, loc=assign.loc)
        wqblz__whmfm[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    nysn__pucb = []
    for djmm__iya, yrlju__gwzru in typing.npydecl.registry.globals:
        if djmm__iya == func:
            nysn__pucb.append(yrlju__gwzru)
    for djmm__iya, yrlju__gwzru in typing.templates.builtin_registry.globals:
        if djmm__iya == func:
            nysn__pucb.append(yrlju__gwzru)
    if len(nysn__pucb) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return nysn__pucb


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    kbqbw__tpt = {}
    sgrtm__vzoqo = find_topo_order(blocks)
    lfb__lzkne = {}
    for label in sgrtm__vzoqo:
        block = blocks[label]
        yfat__qnkm = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                xhx__rnwvr = stmt.target.name
                gis__tcnj = stmt.value
                if (gis__tcnj.op == 'getattr' and gis__tcnj.attr in
                    arr_math and isinstance(typemap[gis__tcnj.value.name],
                    types.npytypes.Array)):
                    gis__tcnj = stmt.value
                    nme__yqu = gis__tcnj.value
                    kbqbw__tpt[xhx__rnwvr] = nme__yqu
                    scope = nme__yqu.scope
                    loc = nme__yqu.loc
                    qessx__nwxw = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[qessx__nwxw.name] = types.misc.Module(numpy)
                    dvh__nqh = ir.Global('np', numpy, loc)
                    zwzzb__gqfwv = ir.Assign(dvh__nqh, qessx__nwxw, loc)
                    gis__tcnj.value = qessx__nwxw
                    yfat__qnkm.append(zwzzb__gqfwv)
                    func_ir._definitions[qessx__nwxw.name] = [dvh__nqh]
                    func = getattr(numpy, gis__tcnj.attr)
                    oynkm__pyhv = get_np_ufunc_typ_lst(func)
                    lfb__lzkne[xhx__rnwvr] = oynkm__pyhv
                if (gis__tcnj.op == 'call' and gis__tcnj.func.name in
                    kbqbw__tpt):
                    nme__yqu = kbqbw__tpt[gis__tcnj.func.name]
                    grer__rkgwf = calltypes.pop(gis__tcnj)
                    bpmf__kld = grer__rkgwf.args[:len(gis__tcnj.args)]
                    zpm__dtegi = {name: typemap[yrlju__gwzru.name] for name,
                        yrlju__gwzru in gis__tcnj.kws}
                    yfk__nstl = lfb__lzkne[gis__tcnj.func.name]
                    gwenv__qprsv = None
                    for oenak__uplt in yfk__nstl:
                        try:
                            gwenv__qprsv = oenak__uplt.get_call_type(typingctx,
                                [typemap[nme__yqu.name]] + list(bpmf__kld),
                                zpm__dtegi)
                            typemap.pop(gis__tcnj.func.name)
                            typemap[gis__tcnj.func.name] = oenak__uplt
                            calltypes[gis__tcnj] = gwenv__qprsv
                            break
                        except Exception as hcx__cup:
                            pass
                    if gwenv__qprsv is None:
                        raise TypeError(
                            f'No valid template found for {gis__tcnj.func.name}'
                            )
                    gis__tcnj.args = [nme__yqu] + gis__tcnj.args
            yfat__qnkm.append(stmt)
        block.body = yfat__qnkm


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    ilu__dukja = ufunc.nin
    anjrr__dhwnt = ufunc.nout
    mokvo__wgmdo = ufunc.nargs
    assert mokvo__wgmdo == ilu__dukja + anjrr__dhwnt
    if len(args) < ilu__dukja:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), ilu__dukja)
            )
    if len(args) > mokvo__wgmdo:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            mokvo__wgmdo))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    pxs__ljps = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    dsea__zsn = max(pxs__ljps)
    nxb__glbnk = args[ilu__dukja:]
    if not all(d == dsea__zsn for d in pxs__ljps[ilu__dukja:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(ejo__cidj, types.ArrayCompatible) and not
        isinstance(ejo__cidj, types.Bytes) for ejo__cidj in nxb__glbnk):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(ejo__cidj.mutable for ejo__cidj in nxb__glbnk):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    epzdf__bide = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    ngx__obvgf = None
    if dsea__zsn > 0 and len(nxb__glbnk) < ufunc.nout:
        ngx__obvgf = 'C'
        ncy__yvpzi = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in ncy__yvpzi and 'F' in ncy__yvpzi:
            ngx__obvgf = 'F'
    return epzdf__bide, nxb__glbnk, dsea__zsn, ngx__obvgf


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        jwtsd__lqkg = 'Dict.key_type cannot be of type {}'
        raise TypingError(jwtsd__lqkg.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        jwtsd__lqkg = 'Dict.value_type cannot be of type {}'
        raise TypingError(jwtsd__lqkg.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for i, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(i))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    pxg__bjejq = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[pxg__bjejq]
        return impl, args
    except KeyError as hcx__cup:
        pass
    impl, args = self._build_impl(pxg__bjejq, args, kws)
    return impl, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def trim_empty_parfor_branches(parfor):
    mmybw__rdt = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            siiq__sdnkl = block.body[-1]
            if isinstance(siiq__sdnkl, ir.Branch):
                if len(blocks[siiq__sdnkl.truebr].body) == 1 and len(blocks
                    [siiq__sdnkl.falsebr].body) == 1:
                    kwn__ftjc = blocks[siiq__sdnkl.truebr].body[0]
                    zgve__lraiq = blocks[siiq__sdnkl.falsebr].body[0]
                    if isinstance(kwn__ftjc, ir.Jump) and isinstance(
                        zgve__lraiq, ir.Jump
                        ) and kwn__ftjc.target == zgve__lraiq.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(kwn__ftjc
                            .target, siiq__sdnkl.loc)
                        mmybw__rdt = True
                elif len(blocks[siiq__sdnkl.truebr].body) == 1:
                    kwn__ftjc = blocks[siiq__sdnkl.truebr].body[0]
                    if isinstance(kwn__ftjc, ir.Jump
                        ) and kwn__ftjc.target == siiq__sdnkl.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(kwn__ftjc
                            .target, siiq__sdnkl.loc)
                        mmybw__rdt = True
                elif len(blocks[siiq__sdnkl.falsebr].body) == 1:
                    zgve__lraiq = blocks[siiq__sdnkl.falsebr].body[0]
                    if isinstance(zgve__lraiq, ir.Jump
                        ) and zgve__lraiq.target == siiq__sdnkl.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(zgve__lraiq
                            .target, siiq__sdnkl.loc)
                        mmybw__rdt = True
    return mmybw__rdt


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        cphdf__ypsh = find_topo_order(parfor.loop_body)
    iyojv__wrod = cphdf__ypsh[0]
    ibyu__mowd = {}
    _update_parfor_get_setitems(parfor.loop_body[iyojv__wrod].body, parfor.
        index_var, alias_map, ibyu__mowd, lives_n_aliases)
    quz__dng = set(ibyu__mowd.keys())
    for qfzu__ljzha in cphdf__ypsh:
        if qfzu__ljzha == iyojv__wrod:
            continue
        for stmt in parfor.loop_body[qfzu__ljzha].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            whn__njp = set(yrlju__gwzru.name for yrlju__gwzru in stmt.
                list_vars())
            izj__fnw = whn__njp & quz__dng
            for a in izj__fnw:
                ibyu__mowd.pop(a, None)
    for qfzu__ljzha in cphdf__ypsh:
        if qfzu__ljzha == iyojv__wrod:
            continue
        block = parfor.loop_body[qfzu__ljzha]
        lmng__apu = ibyu__mowd.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            lmng__apu, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    ksrqs__dwwwd = max(blocks.keys())
    prf__daali, hxd__imrul = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    fkpa__exyw = ir.Jump(prf__daali, ir.Loc('parfors_dummy', -1))
    blocks[ksrqs__dwwwd].body.append(fkpa__exyw)
    hapkz__gxjl = compute_cfg_from_blocks(blocks)
    jdk__bfhjf = compute_use_defs(blocks)
    qakuf__blqk = compute_live_map(hapkz__gxjl, blocks, jdk__bfhjf.usemap,
        jdk__bfhjf.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        yfat__qnkm = []
        xkhqd__nsk = {yrlju__gwzru.name for yrlju__gwzru in block.
            terminator.list_vars()}
        for dnhnw__pgeh, fzt__wvtp in hapkz__gxjl.successors(label):
            xkhqd__nsk |= qakuf__blqk[dnhnw__pgeh]
        for stmt in reversed(block.body):
            zfgd__ggngx = xkhqd__nsk & alias_set
            for yrlju__gwzru in zfgd__ggngx:
                xkhqd__nsk |= alias_map[yrlju__gwzru]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in xkhqd__nsk and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                rhdq__plm = guard(find_callname, func_ir, stmt.value)
                if rhdq__plm == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in xkhqd__nsk and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            xkhqd__nsk |= {yrlju__gwzru.name for yrlju__gwzru in stmt.
                list_vars()}
            yfat__qnkm.append(stmt)
        yfat__qnkm.reverse()
        block.body = yfat__qnkm
    typemap.pop(hxd__imrul.name)
    blocks[ksrqs__dwwwd].body.pop()
    mmybw__rdt = True
    while mmybw__rdt:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        mmybw__rdt = trim_empty_parfor_branches(parfor)
    rmi__spyef = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        rmi__spyef &= len(block.body) == 0
    if rmi__spyef:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.parfors.parfor import Parfor
    waef__mnaga = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                waef__mnaga += 1
                parfor = stmt
                vty__ncj = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = vty__ncj.scope
                loc = ir.Loc('parfors_dummy', -1)
                gdi__qak = ir.Var(scope, mk_unique_var('$const'), loc)
                vty__ncj.body.append(ir.Assign(ir.Const(0, loc), gdi__qak, loc)
                    )
                vty__ncj.body.append(ir.Return(gdi__qak, loc))
                hapkz__gxjl = compute_cfg_from_blocks(parfor.loop_body)
                for gcfm__jhuxh in hapkz__gxjl.dead_nodes():
                    del parfor.loop_body[gcfm__jhuxh]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                vty__ncj = parfor.loop_body[max(parfor.loop_body.keys())]
                vty__ncj.body.pop()
                vty__ncj.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return waef__mnaga


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    hapkz__gxjl = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != hapkz__gxjl.entry_point()
    ayi__ozln = list(filter(find_single_branch, blocks.keys()))
    dpjkn__gtrl = set()
    for label in ayi__ozln:
        inst = blocks[label].body[0]
        rwy__qjml = hapkz__gxjl.predecessors(label)
        xogj__dej = True
        for kbsj__btlc, ict__frunt in rwy__qjml:
            block = blocks[kbsj__btlc]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                xogj__dej = False
        if xogj__dej:
            dpjkn__gtrl.add(label)
    for label in dpjkn__gtrl:
        del blocks[label]
    merge_adjacent_blocks(blocks)
    return rename_labels(blocks)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.simplify_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0b3f2add05e5691155f08fc5945956d5cca5e068247d52cff8efb161b76388b7':
        warnings.warn('numba.core.ir_utils.simplify_CFG has changed')
numba.core.ir_utils.simplify_CFG = simplify_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            wfyao__cmvjg = self.overloads.get(tuple(args))
            if wfyao__cmvjg is not None:
                return wfyao__cmvjg.entry_point
            self._pre_compile(args, return_type, flags)
            kgmm__vsky = self.func_ir
            tgdd__goq = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=tgdd__goq):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=kgmm__vsky, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        mgq__nafil = copy.deepcopy(flags)
        mgq__nafil.no_rewrites = True

        def compile_local(the_ir, the_flags):
            dnhwj__glhn = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return dnhwj__glhn.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        psjz__udpt = compile_local(func_ir, mgq__nafil)
        akapl__idvbk = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    akapl__idvbk = compile_local(func_ir, flags)
                except Exception as hcx__cup:
                    pass
        if akapl__idvbk is not None:
            cres = akapl__idvbk
        else:
            cres = psjz__udpt
        return cres
    else:
        dnhwj__glhn = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return dnhwj__glhn.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    gwca__jhp = self.get_data_type(typ.dtype)
    bml__jakz = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        bml__jakz):
        ssi__syg = ary.ctypes.data
        vqg__tjoo = self.add_dynamic_addr(builder, ssi__syg, info=str(type(
            ssi__syg)))
        xrbd__vyvqx = self.add_dynamic_addr(builder, id(ary), info=str(type
            (ary)))
        self.global_arrays.append(ary)
    else:
        ubmu__gsp = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            ubmu__gsp = ubmu__gsp.view('int64')
        val = bytearray(ubmu__gsp.data)
        mjf__fudl = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        vqg__tjoo = cgutils.global_constant(builder, '.const.array.data',
            mjf__fudl)
        vqg__tjoo.align = self.get_abi_alignment(gwca__jhp)
        xrbd__vyvqx = None
    cir__omqtk = self.get_value_type(types.intp)
    zww__bwu = [self.get_constant(types.intp, vcu__jvaim) for vcu__jvaim in
        ary.shape]
    pcvza__kili = lir.Constant(lir.ArrayType(cir__omqtk, len(zww__bwu)),
        zww__bwu)
    tpoz__zwxgk = [self.get_constant(types.intp, vcu__jvaim) for vcu__jvaim in
        ary.strides]
    llxa__srs = lir.Constant(lir.ArrayType(cir__omqtk, len(tpoz__zwxgk)),
        tpoz__zwxgk)
    mjg__hougd = self.get_constant(types.intp, ary.dtype.itemsize)
    axcp__ubggy = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        axcp__ubggy, mjg__hougd, vqg__tjoo.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), pcvza__kili, llxa__srs])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    ipao__rbqy = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    drsv__wbs = lir.Function(module, ipao__rbqy, name='nrt_atomic_{0}'.
        format(op))
    [cgegn__kksak] = drsv__wbs.args
    khey__weykg = drsv__wbs.append_basic_block()
    builder = lir.IRBuilder(khey__weykg)
    gvc__yrz = lir.Constant(_word_type, 1)
    if False:
        dui__iyso = builder.atomic_rmw(op, cgegn__kksak, gvc__yrz, ordering
            =ordering)
        res = getattr(builder, op)(dui__iyso, gvc__yrz)
        builder.ret(res)
    else:
        dui__iyso = builder.load(cgegn__kksak)
        ytcb__rcxde = getattr(builder, op)(dui__iyso, gvc__yrz)
        tak__luu = builder.icmp_signed('!=', dui__iyso, lir.Constant(
            dui__iyso.type, -1))
        with cgutils.if_likely(builder, tak__luu):
            builder.store(ytcb__rcxde, cgegn__kksak)
        builder.ret(ytcb__rcxde)
    return drsv__wbs


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        she__ltyy = state.targetctx.codegen()
        state.library = she__ltyy.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    jtf__jblk = state.func_ir
    typemap = state.typemap
    gcybq__anbrg = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    afp__fici = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            jtf__jblk, typemap, gcybq__anbrg, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            mand__aujzo = lowering.Lower(targetctx, library, fndesc,
                jtf__jblk, metadata=metadata)
            mand__aujzo.lower()
            if not flags.no_cpython_wrapper:
                mand__aujzo.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(gcybq__anbrg, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        mand__aujzo.create_cfunc_wrapper()
            env = mand__aujzo.env
            mui__kqvf = mand__aujzo.call_helper
            del mand__aujzo
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, mui__kqvf, cfunc=None, env=env)
        else:
            itgx__whtx = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(itgx__whtx, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, mui__kqvf, cfunc=itgx__whtx,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        gkv__zwhh = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = gkv__zwhh - afp__fici
        metadata['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        oyy__cmn = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, oyy__cmn), likely
            =False):
            c.builder.store(cgutils.true_bit, errorptr)
            ojxlh__sbcsa.do_break()
        uubty__tuz = c.builder.icmp_signed('!=', oyy__cmn, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(uubty__tuz, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, oyy__cmn)
                c.pyapi.decref(oyy__cmn)
                ojxlh__sbcsa.do_break()
        c.pyapi.decref(oyy__cmn)
    kra__xkmh, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(kra__xkmh, likely=True) as (unc__biu, umjn__dpu):
        with unc__biu:
            list.size = size
            xrb__zwu = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                xrb__zwu), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        xrb__zwu))
                    with cgutils.for_range(c.builder, size) as ojxlh__sbcsa:
                        itemobj = c.pyapi.list_getitem(obj, ojxlh__sbcsa.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        georl__tlar = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(georl__tlar.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            ojxlh__sbcsa.do_break()
                        list.setitem(ojxlh__sbcsa.index, georl__tlar.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with umjn__dpu:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    pkok__lxpe, ucowi__hhv, vhus__mpk, mbdz__hturv, leafo__ecu = (
        compile_time_get_string_data(literal_string))
    eusmt__rdb = builder.module
    gv = context.insert_const_bytes(eusmt__rdb, pkok__lxpe)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        ucowi__hhv), context.get_constant(types.int32, vhus__mpk), context.
        get_constant(types.uint32, mbdz__hturv), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    zor__fzzq = None
    if isinstance(shape, types.Integer):
        zor__fzzq = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(vcu__jvaim, (types.Integer, types.IntEnumMember)) for
            vcu__jvaim in shape):
            zor__fzzq = len(shape)
    return zor__fzzq


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            zor__fzzq = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if zor__fzzq == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(zor__fzzq))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            vyvk__gtn = self._get_names(x)
            if len(vyvk__gtn) != 0:
                return vyvk__gtn[0]
            return vyvk__gtn
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    vyvk__gtn = self._get_names(obj)
    if len(vyvk__gtn) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(vyvk__gtn[0])


def get_equiv_set(self, obj):
    vyvk__gtn = self._get_names(obj)
    if len(vyvk__gtn) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(vyvk__gtn[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    motr__qgt = []
    for rdj__tnw in func_ir.arg_names:
        if rdj__tnw in typemap and isinstance(typemap[rdj__tnw], types.
            containers.UniTuple) and typemap[rdj__tnw].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(rdj__tnw))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for zmdaf__znzzy in func_ir.blocks.values():
        for stmt in zmdaf__znzzy.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    zcqzi__naz = getattr(val, 'code', None)
                    if zcqzi__naz is not None:
                        if getattr(val, 'closure', None) is not None:
                            ejvt__fezn = '<creating a function from a closure>'
                            lxfqa__clko = ''
                        else:
                            ejvt__fezn = zcqzi__naz.co_name
                            lxfqa__clko = '(%s) ' % ejvt__fezn
                    else:
                        ejvt__fezn = '<could not ascertain use case>'
                        lxfqa__clko = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (ejvt__fezn, lxfqa__clko))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                eghfp__gfvqo = False
                if isinstance(val, pytypes.FunctionType):
                    eghfp__gfvqo = val in {numba.gdb, numba.gdb_init}
                if not eghfp__gfvqo:
                    eghfp__gfvqo = getattr(val, '_name', '') == 'gdb_internal'
                if eghfp__gfvqo:
                    motr__qgt.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    put__nqc = func_ir.get_definition(var)
                    vkjww__ylhd = guard(find_callname, func_ir, put__nqc)
                    if vkjww__ylhd and vkjww__ylhd[1] == 'numpy':
                        ty = getattr(numpy, vkjww__ylhd[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    ldzs__tvcom = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(ldzs__tvcom), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(motr__qgt) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        mvsiz__fvbd = '\n'.join([x.strformat() for x in motr__qgt])
        raise errors.UnsupportedError(msg % mvsiz__fvbd)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    djmm__iya, yrlju__gwzru = next(iter(val.items()))
    ppd__cfvy = typeof_impl(djmm__iya, c)
    rkg__wled = typeof_impl(yrlju__gwzru, c)
    if ppd__cfvy is None or rkg__wled is None:
        raise ValueError(
            f'Cannot type dict element type {type(djmm__iya)}, {type(yrlju__gwzru)}'
            )
    return types.DictType(ppd__cfvy, rkg__wled)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    sqr__hpp = cgutils.alloca_once_value(c.builder, val)
    bps__qvry = c.pyapi.object_hasattr_string(val, '_opaque')
    gzj__gfkzn = c.builder.icmp_unsigned('==', bps__qvry, lir.Constant(
        bps__qvry.type, 0))
    nsg__iit = typ.key_type
    skg__ahcx = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(nsg__iit, skg__ahcx)

    def copy_dict(out_dict, in_dict):
        for djmm__iya, yrlju__gwzru in in_dict.items():
            out_dict[djmm__iya] = yrlju__gwzru
    with c.builder.if_then(gzj__gfkzn):
        vleq__yiol = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        srb__awfb = c.pyapi.call_function_objargs(vleq__yiol, [])
        ume__lqmm = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(ume__lqmm, [srb__awfb, val])
        c.builder.store(srb__awfb, sqr__hpp)
    val = c.builder.load(sqr__hpp)
    mktx__bkj = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    uhw__aoa = c.pyapi.object_type(val)
    razuq__ugekb = c.builder.icmp_unsigned('==', uhw__aoa, mktx__bkj)
    with c.builder.if_else(razuq__ugekb) as (joapr__btkus, ambq__zqr):
        with joapr__btkus:
            dvku__sfnus = c.pyapi.object_getattr_string(val, '_opaque')
            uijw__mklj = types.MemInfoPointer(types.voidptr)
            georl__tlar = c.unbox(uijw__mklj, dvku__sfnus)
            mi = georl__tlar.value
            kwk__dtpr = uijw__mklj, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *kwk__dtpr)
            yptgh__dxkv = context.get_constant_null(kwk__dtpr[1])
            args = mi, yptgh__dxkv
            ajkn__zdytt, fao__hnsjx = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, fao__hnsjx)
            c.pyapi.decref(dvku__sfnus)
            jekca__bytl = c.builder.basic_block
        with ambq__zqr:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", uhw__aoa, mktx__bkj)
            uxejf__ispj = c.builder.basic_block
    layl__sxs = c.builder.phi(fao__hnsjx.type)
    yhv__vtcy = c.builder.phi(ajkn__zdytt.type)
    layl__sxs.add_incoming(fao__hnsjx, jekca__bytl)
    layl__sxs.add_incoming(fao__hnsjx.type(None), uxejf__ispj)
    yhv__vtcy.add_incoming(ajkn__zdytt, jekca__bytl)
    yhv__vtcy.add_incoming(cgutils.true_bit, uxejf__ispj)
    c.pyapi.decref(mktx__bkj)
    c.pyapi.decref(uhw__aoa)
    with c.builder.if_then(gzj__gfkzn):
        c.pyapi.decref(val)
    return NativeValue(layl__sxs, is_error=yhv__vtcy)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def op_DICT_UPDATE_byteflow(self, state, inst):
    value = state.pop()
    index = inst.arg
    target = state.peek(index)
    updatevar = state.make_temp()
    res = state.make_temp()
    state.append(inst, target=target, value=value, updatevar=updatevar, res=res
        )


if _check_numba_change:
    if hasattr(numba.core.byteflow.TraceRunner, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_DICT_UPDATE has changed')
numba.core.byteflow.TraceRunner.op_DICT_UPDATE = op_DICT_UPDATE_byteflow


def op_DICT_UPDATE_interpreter(self, inst, target, value, updatevar, res):
    from numba.core import ir
    target = self.get(target)
    value = self.get(value)
    lfb__lmp = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=lfb__lmp, name=updatevar)
    uodw__dox = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=uodw__dox, name=res)


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_DICT_UPDATE has changed')
numba.core.interpreter.Interpreter.op_DICT_UPDATE = op_DICT_UPDATE_interpreter


@numba.extending.overload_method(numba.core.types.DictType, 'update')
def ol_dict_update(d, other):
    if not isinstance(d, numba.core.types.DictType):
        return
    if not isinstance(other, numba.core.types.DictType):
        return

    def impl(d, other):
        for djmm__iya, yrlju__gwzru in other.items():
            d[djmm__iya] = yrlju__gwzru
    return impl


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'ol_dict_update'):
        warnings.warn('numba.typed.dictobject.ol_dict_update has changed')


def op_CALL_FUNCTION_EX_byteflow(self, state, inst):
    from numba.core.utils import PYVERSION
    if inst.arg & 1 and PYVERSION != (3, 10):
        errmsg = 'CALL_FUNCTION_EX with **kwargs not supported'
        raise errors.UnsupportedError(errmsg)
    if inst.arg & 1:
        varkwarg = state.pop()
    else:
        varkwarg = None
    vararg = state.pop()
    func = state.pop()
    res = state.make_temp()
    state.append(inst, func=func, vararg=vararg, varkwarg=varkwarg, res=res)
    state.push(res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.byteflow.TraceRunner.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '349e7cfd27f5dab80fe15a7728c5f098f3f225ba8512d84331e39d01e863c6d4':
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX has changed')
numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_byteflow)


def op_CALL_FUNCTION_EX_interpreter(self, inst, func, vararg, varkwarg, res):
    func = self.get(func)
    vararg = self.get(vararg)
    if varkwarg is not None:
        varkwarg = self.get(varkwarg)
    lxfqa__clko = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(lxfqa__clko, res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.interpreter.Interpreter.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84846e5318ab7ccc8f9abaae6ab9e0ca879362648196f9d4b0ffb91cf2e01f5d':
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX has changed'
            )
numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_interpreter)


@classmethod
def ir_expr_call(cls, func, args, kws, loc, vararg=None, varkwarg=None,
    target=None):
    assert isinstance(func, ir.Var)
    assert isinstance(loc, ir.Loc)
    op = 'call'
    return cls(op=op, loc=loc, func=func, args=args, kws=kws, vararg=vararg,
        varkwarg=varkwarg, target=target)


if _check_numba_change:
    lines = inspect.getsource(ir.Expr.call)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '665601d0548d4f648d454492e542cb8aa241107a8df6bc68d0eec664c9ada738':
        warnings.warn('ir.Expr.call has changed')
ir.Expr.call = ir_expr_call


@staticmethod
def define_untyped_pipeline(state, name='untyped'):
    from numba.core.compiler_machinery import PassManager
    from numba.core.untyped_passes import DeadBranchPrune, FindLiterallyCalls, FixupArgs, GenericRewrites, InlineClosureLikes, InlineInlinables, IRProcessing, LiteralPropagationSubPipelinePass, LiteralUnroll, MakeFunctionToJitFunction, ReconstructSSA, RewriteSemanticConstants, TranslateByteCode, WithLifting
    from numba.core.utils import PYVERSION
    shgnn__wlc = PassManager(name)
    if state.func_ir is None:
        shgnn__wlc.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            shgnn__wlc.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        shgnn__wlc.add_pass(FixupArgs, 'fix up args')
    shgnn__wlc.add_pass(IRProcessing, 'processing IR')
    shgnn__wlc.add_pass(WithLifting, 'Handle with contexts')
    shgnn__wlc.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        shgnn__wlc.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        shgnn__wlc.add_pass(DeadBranchPrune, 'dead branch pruning')
        shgnn__wlc.add_pass(GenericRewrites, 'nopython rewrites')
    shgnn__wlc.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    shgnn__wlc.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        shgnn__wlc.add_pass(DeadBranchPrune, 'dead branch pruning')
    shgnn__wlc.add_pass(FindLiterallyCalls, 'find literally calls')
    shgnn__wlc.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        shgnn__wlc.add_pass(ReconstructSSA, 'ssa')
    shgnn__wlc.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    shgnn__wlc.finalize()
    return shgnn__wlc


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fc5a0665658cc30588a78aca984ac2d323d5d3a45dce538cc62688530c772896':
        warnings.warn(
            'numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline has changed'
            )
numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline = (
    define_untyped_pipeline)


def mul_list_generic(self, args, kws):
    a, qqh__ptfi = args
    if isinstance(a, types.List) and isinstance(qqh__ptfi, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(qqh__ptfi, types.List):
        return signature(qqh__ptfi, types.intp, qqh__ptfi)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        rvld__jycnw, muarm__hbc = 0, 1
    else:
        rvld__jycnw, muarm__hbc = 1, 0
    vgws__edq = ListInstance(context, builder, sig.args[rvld__jycnw], args[
        rvld__jycnw])
    ksdis__dwudt = vgws__edq.size
    ysbi__xtzd = args[muarm__hbc]
    xrb__zwu = lir.Constant(ysbi__xtzd.type, 0)
    ysbi__xtzd = builder.select(cgutils.is_neg_int(builder, ysbi__xtzd),
        xrb__zwu, ysbi__xtzd)
    axcp__ubggy = builder.mul(ysbi__xtzd, ksdis__dwudt)
    oqwvy__dlka = ListInstance.allocate(context, builder, sig.return_type,
        axcp__ubggy)
    oqwvy__dlka.size = axcp__ubggy
    with cgutils.for_range_slice(builder, xrb__zwu, axcp__ubggy,
        ksdis__dwudt, inc=True) as (cqrrm__krafn, _):
        with cgutils.for_range(builder, ksdis__dwudt) as ojxlh__sbcsa:
            value = vgws__edq.getitem(ojxlh__sbcsa.index)
            oqwvy__dlka.setitem(builder.add(ojxlh__sbcsa.index,
                cqrrm__krafn), value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, oqwvy__dlka.
        value)


def unify_pairs(self, first, second):
    from numba.core.typeconv import Conversion
    if first == second:
        return first
    if first is types.undefined:
        return second
    elif second is types.undefined:
        return first
    if first is types.unknown or second is types.unknown:
        return types.unknown
    skc__oyke = first.unify(self, second)
    if skc__oyke is not None:
        return skc__oyke
    skc__oyke = second.unify(self, first)
    if skc__oyke is not None:
        return skc__oyke
    tkcv__qksdu = self.can_convert(fromty=first, toty=second)
    if tkcv__qksdu is not None and tkcv__qksdu <= Conversion.safe:
        return second
    tkcv__qksdu = self.can_convert(fromty=second, toty=first)
    if tkcv__qksdu is not None and tkcv__qksdu <= Conversion.safe:
        return first
    if isinstance(first, types.Literal) or isinstance(second, types.Literal):
        first = types.unliteral(first)
        second = types.unliteral(second)
        return self.unify_pairs(first, second)
    return None


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.unify_pairs
        )
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f0eaf4cfdf1537691de26efd24d7e320f7c3f10d35e9aefe70cb946b3be0008c':
        warnings.warn(
            'numba.core.typing.context.BaseContext.unify_pairs has changed')
numba.core.typing.context.BaseContext.unify_pairs = unify_pairs


def _native_set_to_python_list(typ, payload, c):
    from llvmlite import ir
    axcp__ubggy = payload.used
    listobj = c.pyapi.list_new(axcp__ubggy)
    kra__xkmh = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(kra__xkmh, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(
            axcp__ubggy.type, 0))
        with payload._iterate() as ojxlh__sbcsa:
            i = c.builder.load(index)
            item = ojxlh__sbcsa.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return kra__xkmh, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    hsh__aqqux = h.type
    rhm__mfvdg = self.mask
    dtype = self._ty.dtype
    cblz__blx = context.typing_context
    fnty = cblz__blx.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(cblz__blx, (dtype, dtype), {})
    fngc__hvcn = context.get_function(fnty, sig)
    suzx__ckaj = ir.Constant(hsh__aqqux, 1)
    kmay__oum = ir.Constant(hsh__aqqux, 5)
    rnmh__kqkxf = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, rhm__mfvdg))
    if for_insert:
        jzh__bwul = rhm__mfvdg.type(-1)
        kapic__gfez = cgutils.alloca_once_value(builder, jzh__bwul)
    owh__wjszr = builder.append_basic_block('lookup.body')
    zmm__klear = builder.append_basic_block('lookup.found')
    aok__shdn = builder.append_basic_block('lookup.not_found')
    msq__zykrf = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        fboc__kuiy = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, fboc__kuiy)):
            ytww__whny = fngc__hvcn(builder, (item, entry.key))
            with builder.if_then(ytww__whny):
                builder.branch(zmm__klear)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, fboc__kuiy)):
            builder.branch(aok__shdn)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, fboc__kuiy)):
                ynu__ejfxc = builder.load(kapic__gfez)
                ynu__ejfxc = builder.select(builder.icmp_unsigned('==',
                    ynu__ejfxc, jzh__bwul), i, ynu__ejfxc)
                builder.store(ynu__ejfxc, kapic__gfez)
    with cgutils.for_range(builder, ir.Constant(hsh__aqqux, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, suzx__ckaj)
        i = builder.and_(i, rhm__mfvdg)
        builder.store(i, index)
    builder.branch(owh__wjszr)
    with builder.goto_block(owh__wjszr):
        i = builder.load(index)
        check_entry(i)
        kbsj__btlc = builder.load(rnmh__kqkxf)
        kbsj__btlc = builder.lshr(kbsj__btlc, kmay__oum)
        i = builder.add(suzx__ckaj, builder.mul(i, kmay__oum))
        i = builder.and_(rhm__mfvdg, builder.add(i, kbsj__btlc))
        builder.store(i, index)
        builder.store(kbsj__btlc, rnmh__kqkxf)
        builder.branch(owh__wjszr)
    with builder.goto_block(aok__shdn):
        if for_insert:
            i = builder.load(index)
            ynu__ejfxc = builder.load(kapic__gfez)
            i = builder.select(builder.icmp_unsigned('==', ynu__ejfxc,
                jzh__bwul), i, ynu__ejfxc)
            builder.store(i, index)
        builder.branch(msq__zykrf)
    with builder.goto_block(zmm__klear):
        builder.branch(msq__zykrf)
    builder.position_at_end(msq__zykrf)
    eghfp__gfvqo = builder.phi(ir.IntType(1), 'found')
    eghfp__gfvqo.add_incoming(cgutils.true_bit, zmm__klear)
    eghfp__gfvqo.add_incoming(cgutils.false_bit, aok__shdn)
    return eghfp__gfvqo, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    ixrrm__ornik = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    swtk__uuh = payload.used
    suzx__ckaj = ir.Constant(swtk__uuh.type, 1)
    swtk__uuh = payload.used = builder.add(swtk__uuh, suzx__ckaj)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, ixrrm__ornik), likely=True):
        payload.fill = builder.add(payload.fill, suzx__ckaj)
    if do_resize:
        self.upsize(swtk__uuh)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    eghfp__gfvqo, i = payload._lookup(item, h, for_insert=True)
    rgp__oyhc = builder.not_(eghfp__gfvqo)
    with builder.if_then(rgp__oyhc):
        entry = payload.get_entry(i)
        ixrrm__ornik = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        swtk__uuh = payload.used
        suzx__ckaj = ir.Constant(swtk__uuh.type, 1)
        swtk__uuh = payload.used = builder.add(swtk__uuh, suzx__ckaj)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, ixrrm__ornik), likely=True):
            payload.fill = builder.add(payload.fill, suzx__ckaj)
        if do_resize:
            self.upsize(swtk__uuh)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    swtk__uuh = payload.used
    suzx__ckaj = ir.Constant(swtk__uuh.type, 1)
    swtk__uuh = payload.used = self._builder.sub(swtk__uuh, suzx__ckaj)
    if do_resize:
        self.downsize(swtk__uuh)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    ksj__visw = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, ksj__visw)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    ysbie__hmwea = payload
    kra__xkmh = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(kra__xkmh), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with ysbie__hmwea._iterate() as ojxlh__sbcsa:
        entry = ojxlh__sbcsa.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(ysbie__hmwea.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as ojxlh__sbcsa:
        entry = ojxlh__sbcsa.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    kra__xkmh = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(kra__xkmh), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    kra__xkmh = cgutils.alloca_once_value(builder, cgutils.true_bit)
    hsh__aqqux = context.get_value_type(types.intp)
    xrb__zwu = ir.Constant(hsh__aqqux, 0)
    suzx__ckaj = ir.Constant(hsh__aqqux, 1)
    lief__cgagl = context.get_data_type(types.SetPayload(self._ty))
    hlx__jlqa = context.get_abi_sizeof(lief__cgagl)
    smtx__nmg = self._entrysize
    hlx__jlqa -= smtx__nmg
    rlsqi__vqwgx, gdm__tfsyt = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(hsh__aqqux, smtx__nmg), ir.Constant(
        hsh__aqqux, hlx__jlqa))
    with builder.if_then(gdm__tfsyt, likely=False):
        builder.store(cgutils.false_bit, kra__xkmh)
    with builder.if_then(builder.load(kra__xkmh), likely=True):
        if realloc:
            hwlbn__frps = self._set.meminfo
            cgegn__kksak = context.nrt.meminfo_varsize_alloc(builder,
                hwlbn__frps, size=rlsqi__vqwgx)
            ozdac__mdvr = cgutils.is_null(builder, cgegn__kksak)
        else:
            fwd__mvof = _imp_dtor(context, builder.module, self._ty)
            hwlbn__frps = context.nrt.meminfo_new_varsize_dtor(builder,
                rlsqi__vqwgx, builder.bitcast(fwd__mvof, cgutils.voidptr_t))
            ozdac__mdvr = cgutils.is_null(builder, hwlbn__frps)
        with builder.if_else(ozdac__mdvr, likely=False) as (dfnl__cfz, unc__biu
            ):
            with dfnl__cfz:
                builder.store(cgutils.false_bit, kra__xkmh)
            with unc__biu:
                if not realloc:
                    self._set.meminfo = hwlbn__frps
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, rlsqi__vqwgx, 255)
                payload.used = xrb__zwu
                payload.fill = xrb__zwu
                payload.finger = xrb__zwu
                tdr__zvmin = builder.sub(nentries, suzx__ckaj)
                payload.mask = tdr__zvmin
    return builder.load(kra__xkmh)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    kra__xkmh = cgutils.alloca_once_value(builder, cgutils.true_bit)
    hsh__aqqux = context.get_value_type(types.intp)
    xrb__zwu = ir.Constant(hsh__aqqux, 0)
    suzx__ckaj = ir.Constant(hsh__aqqux, 1)
    lief__cgagl = context.get_data_type(types.SetPayload(self._ty))
    hlx__jlqa = context.get_abi_sizeof(lief__cgagl)
    smtx__nmg = self._entrysize
    hlx__jlqa -= smtx__nmg
    rhm__mfvdg = src_payload.mask
    nentries = builder.add(suzx__ckaj, rhm__mfvdg)
    rlsqi__vqwgx = builder.add(ir.Constant(hsh__aqqux, hlx__jlqa), builder.
        mul(ir.Constant(hsh__aqqux, smtx__nmg), nentries))
    with builder.if_then(builder.load(kra__xkmh), likely=True):
        fwd__mvof = _imp_dtor(context, builder.module, self._ty)
        hwlbn__frps = context.nrt.meminfo_new_varsize_dtor(builder,
            rlsqi__vqwgx, builder.bitcast(fwd__mvof, cgutils.voidptr_t))
        ozdac__mdvr = cgutils.is_null(builder, hwlbn__frps)
        with builder.if_else(ozdac__mdvr, likely=False) as (dfnl__cfz, unc__biu
            ):
            with dfnl__cfz:
                builder.store(cgutils.false_bit, kra__xkmh)
            with unc__biu:
                self._set.meminfo = hwlbn__frps
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = xrb__zwu
                payload.mask = rhm__mfvdg
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, smtx__nmg)
                with src_payload._iterate() as ojxlh__sbcsa:
                    context.nrt.incref(builder, self._ty.dtype,
                        ojxlh__sbcsa.entry.key)
    return builder.load(kra__xkmh)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    rqks__qvv = context.get_value_type(types.voidptr)
    umi__loocf = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [rqks__qvv, umi__loocf, rqks__qvv])
    zunpx__bkkk = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=zunpx__bkkk)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        gxm__dme = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, gxm__dme)
        with payload._iterate() as ojxlh__sbcsa:
            entry = ojxlh__sbcsa.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    faibh__makta, = sig.args
    ctfu__wppw, = args
    exnhg__uer = numba.core.imputils.call_len(context, builder,
        faibh__makta, ctfu__wppw)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, exnhg__uer)
    with numba.core.imputils.for_iter(context, builder, faibh__makta,
        ctfu__wppw) as ojxlh__sbcsa:
        inst.add(ojxlh__sbcsa.value)
        context.nrt.decref(builder, set_type.dtype, ojxlh__sbcsa.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    faibh__makta = sig.args[1]
    ctfu__wppw = args[1]
    exnhg__uer = numba.core.imputils.call_len(context, builder,
        faibh__makta, ctfu__wppw)
    if exnhg__uer is not None:
        byuc__vzzhf = builder.add(inst.payload.used, exnhg__uer)
        inst.upsize(byuc__vzzhf)
    with numba.core.imputils.for_iter(context, builder, faibh__makta,
        ctfu__wppw) as ojxlh__sbcsa:
        xlwh__mei = context.cast(builder, ojxlh__sbcsa.value, faibh__makta.
            dtype, inst.dtype)
        inst.add(xlwh__mei)
        context.nrt.decref(builder, faibh__makta.dtype, ojxlh__sbcsa.value)
    if exnhg__uer is not None:
        inst.downsize(inst.payload.used)
    return context.get_dummy_value()


if _check_numba_change:
    for name, orig, hash in ((
        'numba.core.boxing._native_set_to_python_list', numba.core.boxing.
        _native_set_to_python_list,
        'b47f3d5e582c05d80899ee73e1c009a7e5121e7a660d42cb518bb86933f3c06f'),
        ('numba.cpython.setobj._SetPayload._lookup', numba.cpython.setobj.
        _SetPayload._lookup,
        'c797b5399d7b227fe4eea3a058b3d3103f59345699388afb125ae47124bee395'),
        ('numba.cpython.setobj.SetInstance._add_entry', numba.cpython.
        setobj.SetInstance._add_entry,
        'c5ed28a5fdb453f242e41907cb792b66da2df63282c17abe0b68fc46782a7f94'),
        ('numba.cpython.setobj.SetInstance._add_key', numba.cpython.setobj.
        SetInstance._add_key,
        '324d6172638d02a361cfa0ca7f86e241e5a56a008d4ab581a305f9ae5ea4a75f'),
        ('numba.cpython.setobj.SetInstance._remove_entry', numba.cpython.
        setobj.SetInstance._remove_entry,
        '2c441b00daac61976e673c0e738e8e76982669bd2851951890dd40526fa14da1'),
        ('numba.cpython.setobj.SetInstance.pop', numba.cpython.setobj.
        SetInstance.pop,
        '1a7b7464cbe0577f2a38f3af9acfef6d4d25d049b1e216157275fbadaab41d1b'),
        ('numba.cpython.setobj.SetInstance._resize', numba.cpython.setobj.
        SetInstance._resize,
        '5ca5c2ba4f8c4bf546fde106b9c2656d4b22a16d16e163fb64c5d85ea4d88746'),
        ('numba.cpython.setobj.SetInstance._replace_payload', numba.cpython
        .setobj.SetInstance._replace_payload,
        'ada75a6c85828bff69c8469538c1979801f560a43fb726221a9c21bf208ae78d'),
        ('numba.cpython.setobj.SetInstance._allocate_payload', numba.
        cpython.setobj.SetInstance._allocate_payload,
        '2e80c419df43ebc71075b4f97fc1701c10dbc576aed248845e176b8d5829e61b'),
        ('numba.cpython.setobj.SetInstance._copy_payload', numba.cpython.
        setobj.SetInstance._copy_payload,
        '0885ac36e1eb5a0a0fc4f5d91e54b2102b69e536091fed9f2610a71d225193ec'),
        ('numba.cpython.setobj.set_constructor', numba.cpython.setobj.
        set_constructor,
        '3d521a60c3b8eaf70aa0f7267427475dfddd8f5e5053b5bfe309bb5f1891b0ce'),
        ('numba.cpython.setobj.set_update', numba.cpython.setobj.set_update,
        '965c4f7f7abcea5cbe0491b602e6d4bcb1800fa1ec39b1ffccf07e1bc56051c3')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.boxing._native_set_to_python_list = _native_set_to_python_list
numba.cpython.setobj._SetPayload._lookup = _lookup
numba.cpython.setobj.SetInstance._add_entry = _add_entry
numba.cpython.setobj.SetInstance._add_key = _add_key
numba.cpython.setobj.SetInstance._remove_entry = _remove_entry
numba.cpython.setobj.SetInstance.pop = pop
numba.cpython.setobj.SetInstance._resize = _resize
numba.cpython.setobj.SetInstance._replace_payload = _replace_payload
numba.cpython.setobj.SetInstance._allocate_payload = _allocate_payload
numba.cpython.setobj.SetInstance._copy_payload = _copy_payload


def _reduce(self):
    libdata = self.library.serialize_using_object_code()
    typeann = str(self.type_annotation)
    fndesc = self.fndesc
    fndesc.typemap = fndesc.calltypes = None
    referenced_envs = self._find_referenced_environments()
    kto__pyr = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, kto__pyr, self.reload_init, tuple
        (referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    itgx__whtx = target_context.get_executable(library, fndesc, env)
    fjb__uqx = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=itgx__whtx, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return fjb__uqx


if _check_numba_change:
    for name, orig, hash in (('numba.core.compiler.CompileResult._reduce',
        numba.core.compiler.CompileResult._reduce,
        '5f86eacfa5202c202b3dc200f1a7a9b6d3f9d1ec16d43a52cb2d580c34fbfa82'),
        ('numba.core.compiler.CompileResult._rebuild', numba.core.compiler.
        CompileResult._rebuild,
        '44fa9dc2255883ab49195d18c3cca8c0ad715d0dd02033bd7e2376152edc4e84')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.compiler.CompileResult._reduce = _reduce
numba.core.compiler.CompileResult._rebuild = _rebuild
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._IPythonCacheLocator.
        get_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'eb33b7198697b8ef78edddcf69e58973c44744ff2cb2f54d4015611ad43baed0':
        warnings.warn(
            'numba.core.caching._IPythonCacheLocator.get_cache_path has changed'
            )
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:

    def _get_cache_path(self):
        return numba.config.CACHE_DIR
    numba.core.caching._IPythonCacheLocator.get_cache_path = _get_cache_path
if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.Bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '977423d833eeb4b8fd0c87f55dce7251c107d8d10793fe5723de6e5452da32e2':
        warnings.warn('numba.core.types.containers.Bytes has changed')
numba.core.types.containers.Bytes.slice_is_copy = True
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheLocator.
        ensure_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '906b6f516f76927dfbe69602c335fa151b9f33d40dfe171a9190c0d11627bc03':
        warnings.warn(
            'numba.core.caching._CacheLocator.ensure_cache_path has changed')
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
    import tempfile

    def _ensure_cache_path(self):
        from mpi4py import MPI
        cizk__kkbyf = MPI.COMM_WORLD
        if cizk__kkbyf.Get_rank() == 0:
            emlj__qczyy = self.get_cache_path()
            os.makedirs(emlj__qczyy, exist_ok=True)
            tempfile.TemporaryFile(dir=emlj__qczyy).close()
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path


def _analyze_op_call_builtins_len(self, scope, equiv_set, loc, args, kws):
    from numba.parfors.array_analysis import ArrayAnalysis
    require(len(args) == 1)
    var = args[0]
    typ = self.typemap[var.name]
    require(isinstance(typ, types.ArrayCompatible))
    require(not isinstance(typ, types.Bytes))
    shape = equiv_set._get_shape(var)
    return ArrayAnalysis.AnalyzeResult(shape=shape[0], rhs=shape[0])


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_op_call_builtins_len)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '612cbc67e8e462f25f348b2a5dd55595f4201a6af826cffcd38b16cd85fc70f7':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_op_call_builtins_len has changed'
            )
(numba.parfors.array_analysis.ArrayAnalysis._analyze_op_call_builtins_len
    ) = _analyze_op_call_builtins_len


def generic(self, args, kws):
    assert not kws
    val, = args
    if isinstance(val, (types.Buffer, types.BaseTuple)) and not isinstance(val,
        types.Bytes):
        return signature(types.intp, val)
    elif isinstance(val, types.RangeType):
        return signature(val.dtype, val)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.Len.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '88d54238ebe0896f4s69b7347105a6a68dec443036a61f9e494c1630c62b0fa76':
        warnings.warn('numba.core.typing.builtins.Len.generic has changed')
numba.core.typing.builtins.Len.generic = generic
from numba.cpython import charseq


def _make_constant_bytes(context, builder, nbytes):
    from llvmlite import ir
    lrh__ydsrb = cgutils.create_struct_proxy(charseq.bytes_type)
    jzv__uyr = lrh__ydsrb(context, builder)
    if isinstance(nbytes, int):
        nbytes = ir.Constant(jzv__uyr.nitems.type, nbytes)
    jzv__uyr.meminfo = context.nrt.meminfo_alloc(builder, nbytes)
    jzv__uyr.nitems = nbytes
    jzv__uyr.itemsize = ir.Constant(jzv__uyr.itemsize.type, 1)
    jzv__uyr.data = context.nrt.meminfo_data(builder, jzv__uyr.meminfo)
    jzv__uyr.parent = cgutils.get_null_value(jzv__uyr.parent.type)
    jzv__uyr.shape = cgutils.pack_array(builder, [jzv__uyr.nitems], context
        .get_value_type(types.intp))
    jzv__uyr.strides = cgutils.pack_array(builder, [ir.Constant(jzv__uyr.
        strides.type.element, 1)], context.get_value_type(types.intp))
    return jzv__uyr


if _check_numba_change:
    lines = inspect.getsource(charseq._make_constant_bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b3ed23ad58baff7b935912e3e22f4d8af67423d8fd0e5f1836ba0b3028a6eb18':
        warnings.warn('charseq._make_constant_bytes has changed')
charseq._make_constant_bytes = _make_constant_bytes
