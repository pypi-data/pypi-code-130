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
    mvzce__ymoo = numba.core.bytecode.FunctionIdentity.from_function(func)
    cob__orbg = numba.core.interpreter.Interpreter(mvzce__ymoo)
    jgrbt__ppcmt = numba.core.bytecode.ByteCode(func_id=mvzce__ymoo)
    func_ir = cob__orbg.interpret(jgrbt__ppcmt)
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
        lwvc__xzxz = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        lwvc__xzxz.run()
    dxa__sjftu = numba.core.postproc.PostProcessor(func_ir)
    dxa__sjftu.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, kxf__byh in visit_vars_extensions.items():
        if isinstance(stmt, t):
            kxf__byh(stmt, callback, cbdata)
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
    liji__ubkg = ['ravel', 'transpose', 'reshape']
    for pgbi__kghx in blocks.values():
        for yyg__dpeo in pgbi__kghx.body:
            if type(yyg__dpeo) in alias_analysis_extensions:
                kxf__byh = alias_analysis_extensions[type(yyg__dpeo)]
                kxf__byh(yyg__dpeo, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(yyg__dpeo, ir.Assign):
                gvfev__dtws = yyg__dpeo.value
                jpa__rgx = yyg__dpeo.target.name
                if is_immutable_type(jpa__rgx, typemap):
                    continue
                if isinstance(gvfev__dtws, ir.Var
                    ) and jpa__rgx != gvfev__dtws.name:
                    _add_alias(jpa__rgx, gvfev__dtws.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr) and (gvfev__dtws.op ==
                    'cast' or gvfev__dtws.op in ['getitem', 'static_getitem']):
                    _add_alias(jpa__rgx, gvfev__dtws.value.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr
                    ) and gvfev__dtws.op == 'inplace_binop':
                    _add_alias(jpa__rgx, gvfev__dtws.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr
                    ) and gvfev__dtws.op == 'getattr' and gvfev__dtws.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(jpa__rgx, gvfev__dtws.value.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr
                    ) and gvfev__dtws.op == 'getattr' and gvfev__dtws.attr not in [
                    'shape'] and gvfev__dtws.value.name in arg_aliases:
                    _add_alias(jpa__rgx, gvfev__dtws.value.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr
                    ) and gvfev__dtws.op == 'getattr' and gvfev__dtws.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(jpa__rgx, gvfev__dtws.value.name, alias_map,
                        arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr) and gvfev__dtws.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(jpa__rgx, typemap):
                    for mhgb__tfjsm in gvfev__dtws.items:
                        _add_alias(jpa__rgx, mhgb__tfjsm.name, alias_map,
                            arg_aliases)
                if isinstance(gvfev__dtws, ir.Expr
                    ) and gvfev__dtws.op == 'call':
                    peh__vjfa = guard(find_callname, func_ir, gvfev__dtws,
                        typemap)
                    if peh__vjfa is None:
                        continue
                    esu__najs, pwm__wys = peh__vjfa
                    if peh__vjfa in alias_func_extensions:
                        dks__toqr = alias_func_extensions[peh__vjfa]
                        dks__toqr(jpa__rgx, gvfev__dtws.args, alias_map,
                            arg_aliases)
                    if pwm__wys == 'numpy' and esu__najs in liji__ubkg:
                        _add_alias(jpa__rgx, gvfev__dtws.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(pwm__wys, ir.Var
                        ) and esu__najs in liji__ubkg:
                        _add_alias(jpa__rgx, pwm__wys.name, alias_map,
                            arg_aliases)
    icvy__tae = copy.deepcopy(alias_map)
    for mhgb__tfjsm in icvy__tae:
        for eko__ziek in icvy__tae[mhgb__tfjsm]:
            alias_map[mhgb__tfjsm] |= alias_map[eko__ziek]
        for eko__ziek in icvy__tae[mhgb__tfjsm]:
            alias_map[eko__ziek] = alias_map[mhgb__tfjsm]
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
    srj__wusy = compute_cfg_from_blocks(func_ir.blocks)
    znlx__npcu = compute_use_defs(func_ir.blocks)
    pnz__nqln = compute_live_map(srj__wusy, func_ir.blocks, znlx__npcu.
        usemap, znlx__npcu.defmap)
    olw__whc = True
    while olw__whc:
        olw__whc = False
        for label, block in func_ir.blocks.items():
            lives = {mhgb__tfjsm.name for mhgb__tfjsm in block.terminator.
                list_vars()}
            for iqvvx__pqzx, sgcr__zjts in srj__wusy.successors(label):
                lives |= pnz__nqln[iqvvx__pqzx]
            iuk__wycpp = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    jpa__rgx = stmt.target
                    dadv__fhef = stmt.value
                    if jpa__rgx.name not in lives:
                        if isinstance(dadv__fhef, ir.Expr
                            ) and dadv__fhef.op == 'make_function':
                            continue
                        if isinstance(dadv__fhef, ir.Expr
                            ) and dadv__fhef.op == 'getattr':
                            continue
                        if isinstance(dadv__fhef, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(jpa__rgx,
                            None), types.Function):
                            continue
                        if isinstance(dadv__fhef, ir.Expr
                            ) and dadv__fhef.op == 'build_map':
                            continue
                        if isinstance(dadv__fhef, ir.Expr
                            ) and dadv__fhef.op == 'build_tuple':
                            continue
                    if isinstance(dadv__fhef, ir.Var
                        ) and jpa__rgx.name == dadv__fhef.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    esqj__wdc = analysis.ir_extension_usedefs[type(stmt)]
                    tjh__qom, ykpx__bpqpp = esqj__wdc(stmt)
                    lives -= ykpx__bpqpp
                    lives |= tjh__qom
                else:
                    lives |= {mhgb__tfjsm.name for mhgb__tfjsm in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(jpa__rgx.name)
                iuk__wycpp.append(stmt)
            iuk__wycpp.reverse()
            if len(block.body) != len(iuk__wycpp):
                olw__whc = True
            block.body = iuk__wycpp


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    lffj__vgrs = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (lffj__vgrs,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    ivz__xrwyo = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), ivz__xrwyo)


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
            for edv__gkld in fnty.templates:
                self._inline_overloads.update(edv__gkld._inline_overloads)
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
    ivz__xrwyo = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), ivz__xrwyo)
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
    elfa__ftdba, tekn__rhh = self._get_impl(args, kws)
    if elfa__ftdba is None:
        return
    upyxw__llbeu = types.Dispatcher(elfa__ftdba)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        sckn__ilssa = elfa__ftdba._compiler
        flags = compiler.Flags()
        azmth__vmmo = sckn__ilssa.targetdescr.typing_context
        swaln__xcpk = sckn__ilssa.targetdescr.target_context
        fabnm__seol = sckn__ilssa.pipeline_class(azmth__vmmo, swaln__xcpk,
            None, None, None, flags, None)
        cfgat__zwfze = InlineWorker(azmth__vmmo, swaln__xcpk, sckn__ilssa.
            locals, fabnm__seol, flags, None)
        aldp__rld = upyxw__llbeu.dispatcher.get_call_template
        edv__gkld, hig__viozz, ojdrm__evkk, kws = aldp__rld(tekn__rhh, kws)
        if ojdrm__evkk in self._inline_overloads:
            return self._inline_overloads[ojdrm__evkk]['iinfo'].signature
        ir = cfgat__zwfze.run_untyped_passes(upyxw__llbeu.dispatcher.
            py_func, enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, swaln__xcpk, ir, ojdrm__evkk, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, ojdrm__evkk, None)
        self._inline_overloads[sig.args] = {'folded_args': ojdrm__evkk}
        ztpu__ogvj = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = ztpu__ogvj
        if not self._inline.is_always_inline:
            sig = upyxw__llbeu.get_call_type(self.context, tekn__rhh, kws)
            self._compiled_overloads[sig.args] = upyxw__llbeu.get_overload(sig)
        hfnd__whlrd = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': ojdrm__evkk,
            'iinfo': hfnd__whlrd}
    else:
        sig = upyxw__llbeu.get_call_type(self.context, tekn__rhh, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = upyxw__llbeu.get_overload(sig)
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
    enl__cxz = [True, False]
    esjnc__pgftg = [False, True]
    ofr__igy = _ResolutionFailures(context, self, args, kws, depth=self._depth)
    from numba.core.target_extension import get_local_target
    eef__zau = get_local_target(context)
    vuvfb__nwdoy = utils.order_by_target_specificity(eef__zau, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for yqk__xbeqb in vuvfb__nwdoy:
        rwj__ukiaj = yqk__xbeqb(context)
        snr__tvf = enl__cxz if rwj__ukiaj.prefer_literal else esjnc__pgftg
        snr__tvf = [True] if getattr(rwj__ukiaj, '_no_unliteral', False
            ) else snr__tvf
        for autq__gdj in snr__tvf:
            try:
                if autq__gdj:
                    sig = rwj__ukiaj.apply(args, kws)
                else:
                    givs__wjem = tuple([_unlit_non_poison(a) for a in args])
                    itug__zsb = {nut__cqoa: _unlit_non_poison(mhgb__tfjsm) for
                        nut__cqoa, mhgb__tfjsm in kws.items()}
                    sig = rwj__ukiaj.apply(givs__wjem, itug__zsb)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    ofr__igy.add_error(rwj__ukiaj, False, e, autq__gdj)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = rwj__ukiaj.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    mtqyt__sdqcs = getattr(rwj__ukiaj, 'cases', None)
                    if mtqyt__sdqcs is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            mtqyt__sdqcs)
                    else:
                        msg = 'No match.'
                    ofr__igy.add_error(rwj__ukiaj, True, msg, autq__gdj)
    ofr__igy.raise_error()


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
    edv__gkld = self.template(context)
    bsnr__ajlo = None
    kii__xrbn = None
    mlmmk__wlz = None
    snr__tvf = [True, False] if edv__gkld.prefer_literal else [False, True]
    snr__tvf = [True] if getattr(edv__gkld, '_no_unliteral', False
        ) else snr__tvf
    for autq__gdj in snr__tvf:
        if autq__gdj:
            try:
                mlmmk__wlz = edv__gkld.apply(args, kws)
            except Exception as pmi__obpfj:
                if isinstance(pmi__obpfj, errors.ForceLiteralArg):
                    raise pmi__obpfj
                bsnr__ajlo = pmi__obpfj
                mlmmk__wlz = None
            else:
                break
        else:
            yne__pkusq = tuple([_unlit_non_poison(a) for a in args])
            myrn__wndy = {nut__cqoa: _unlit_non_poison(mhgb__tfjsm) for 
                nut__cqoa, mhgb__tfjsm in kws.items()}
            fzqub__elkls = yne__pkusq == args and kws == myrn__wndy
            if not fzqub__elkls and mlmmk__wlz is None:
                try:
                    mlmmk__wlz = edv__gkld.apply(yne__pkusq, myrn__wndy)
                except Exception as pmi__obpfj:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        pmi__obpfj, errors.NumbaError):
                        raise pmi__obpfj
                    if isinstance(pmi__obpfj, errors.ForceLiteralArg):
                        if edv__gkld.prefer_literal:
                            raise pmi__obpfj
                    kii__xrbn = pmi__obpfj
                else:
                    break
    if mlmmk__wlz is None and (kii__xrbn is not None or bsnr__ajlo is not None
        ):
        gtr__frma = '- Resolution failure for {} arguments:\n{}\n'
        rgqmq__yovld = _termcolor.highlight(gtr__frma)
        if numba.core.config.DEVELOPER_MODE:
            alrdu__nzt = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    gmp__tvoyj = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    gmp__tvoyj = ['']
                yjep__zly = '\n{}'.format(2 * alrdu__nzt)
                yqxjb__exgh = _termcolor.reset(yjep__zly + yjep__zly.join(
                    _bt_as_lines(gmp__tvoyj)))
                return _termcolor.reset(yqxjb__exgh)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            luln__cvl = str(e)
            luln__cvl = luln__cvl if luln__cvl else str(repr(e)) + add_bt(e)
            cxtn__eoh = errors.TypingError(textwrap.dedent(luln__cvl))
            return rgqmq__yovld.format(literalness, str(cxtn__eoh))
        import bodo
        if isinstance(bsnr__ajlo, bodo.utils.typing.BodoError):
            raise bsnr__ajlo
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', bsnr__ajlo) +
                nested_msg('non-literal', kii__xrbn))
        else:
            if 'missing a required argument' in bsnr__ajlo.msg:
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
            raise errors.TypingError(msg, loc=bsnr__ajlo.loc)
    return mlmmk__wlz


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
    esu__najs = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=esu__najs)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            rlq__xyg = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), rlq__xyg)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    vsp__fzki = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            vsp__fzki.append(types.Omitted(a.value))
        else:
            vsp__fzki.append(self.typeof_pyval(a))
    kvgo__aum = None
    try:
        error = None
        kvgo__aum = self.compile(tuple(vsp__fzki))
    except errors.ForceLiteralArg as e:
        fmmha__kcn = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if fmmha__kcn:
            etean__ojta = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            gpd__lklb = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(fmmha__kcn))
            raise errors.CompilerError(etean__ojta.format(gpd__lklb))
        tekn__rhh = []
        try:
            for i, mhgb__tfjsm in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        tekn__rhh.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        tekn__rhh.append(types.literal(args[i]))
                else:
                    tekn__rhh.append(args[i])
            args = tekn__rhh
        except (OSError, FileNotFoundError) as edz__nhbmt:
            error = FileNotFoundError(str(edz__nhbmt) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                kvgo__aum = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        zoud__zrvqh = []
        for i, hivz__cfgzc in enumerate(args):
            val = hivz__cfgzc.value if isinstance(hivz__cfgzc, numba.core.
                dispatcher.OmittedArg) else hivz__cfgzc
            try:
                huyyt__rbnu = typeof(val, Purpose.argument)
            except ValueError as nbg__vnfrn:
                zoud__zrvqh.append((i, str(nbg__vnfrn)))
            else:
                if huyyt__rbnu is None:
                    zoud__zrvqh.append((i,
                        f'cannot determine Numba type of value {val}'))
        if zoud__zrvqh:
            vuukn__jts = '\n'.join(f'- argument {i}: {wgvya__kfb}' for i,
                wgvya__kfb in zoud__zrvqh)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{vuukn__jts}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                xjg__yta = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                omrzc__qlda = False
                for krit__lkocr in xjg__yta:
                    if krit__lkocr in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        omrzc__qlda = True
                        break
                if not omrzc__qlda:
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
                rlq__xyg = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), rlq__xyg)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return kvgo__aum


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
    for cjb__cbxn in cres.library._codegen._engine._defined_symbols:
        if cjb__cbxn.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in cjb__cbxn and (
            'bodo_gb_udf_update_local' in cjb__cbxn or 
            'bodo_gb_udf_combine' in cjb__cbxn or 'bodo_gb_udf_eval' in
            cjb__cbxn or 'bodo_gb_apply_general_udfs' in cjb__cbxn):
            gb_agg_cfunc_addr[cjb__cbxn
                ] = cres.library.get_pointer_to_function(cjb__cbxn)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for cjb__cbxn in cres.library._codegen._engine._defined_symbols:
        if cjb__cbxn.startswith('cfunc') and ('get_join_cond_addr' not in
            cjb__cbxn or 'bodo_join_gen_cond' in cjb__cbxn):
            join_gen_cond_cfunc_addr[cjb__cbxn
                ] = cres.library.get_pointer_to_function(cjb__cbxn)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    elfa__ftdba = self._get_dispatcher_for_current_target()
    if elfa__ftdba is not self:
        return elfa__ftdba.compile(sig)
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
            fmklf__svi = self.overloads.get(tuple(args))
            if fmklf__svi is not None:
                return fmklf__svi.entry_point
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
            lyo__dzrj = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=lyo__dzrj):
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
                xyqwh__zdlb = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in xyqwh__zdlb:
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
    vsq__xtzm = self._final_module
    fxn__adbk = []
    rnvm__xxwxi = 0
    for fn in vsq__xtzm.functions:
        rnvm__xxwxi += 1
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
            fxn__adbk.append(fn.name)
    if rnvm__xxwxi == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if fxn__adbk:
        vsq__xtzm = vsq__xtzm.clone()
        for name in fxn__adbk:
            vsq__xtzm.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = vsq__xtzm
    return vsq__xtzm


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
    for kcc__bpgij in self.constraints:
        loc = kcc__bpgij.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                kcc__bpgij(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                pjf__crhe = numba.core.errors.TypingError(str(e), loc=
                    kcc__bpgij.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(pjf__crhe, e))
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
                    pjf__crhe = numba.core.errors.TypingError(msg.format(
                        con=kcc__bpgij, err=str(e)), loc=kcc__bpgij.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(pjf__crhe, e))
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
    for sukb__njsg in self._failures.values():
        for rsyxs__aninh in sukb__njsg:
            if isinstance(rsyxs__aninh.error, ForceLiteralArg):
                raise rsyxs__aninh.error
            if isinstance(rsyxs__aninh.error, bodo.utils.typing.BodoError):
                raise rsyxs__aninh.error
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
    bpi__pwxfd = False
    iuk__wycpp = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        mjalq__qltg = set()
        umz__afytt = lives & alias_set
        for mhgb__tfjsm in umz__afytt:
            mjalq__qltg |= alias_map[mhgb__tfjsm]
        lives_n_aliases = lives | mjalq__qltg | arg_aliases
        if type(stmt) in remove_dead_extensions:
            kxf__byh = remove_dead_extensions[type(stmt)]
            stmt = kxf__byh(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                bpi__pwxfd = True
                continue
        if isinstance(stmt, ir.Assign):
            jpa__rgx = stmt.target
            dadv__fhef = stmt.value
            if jpa__rgx.name not in lives:
                if has_no_side_effect(dadv__fhef, lives_n_aliases, call_table):
                    bpi__pwxfd = True
                    continue
                if isinstance(dadv__fhef, ir.Expr
                    ) and dadv__fhef.op == 'call' and call_table[dadv__fhef
                    .func.name] == ['astype']:
                    cpfm__pjyy = guard(get_definition, func_ir, dadv__fhef.func
                        )
                    if (cpfm__pjyy is not None and cpfm__pjyy.op ==
                        'getattr' and isinstance(typemap[cpfm__pjyy.value.
                        name], types.Array) and cpfm__pjyy.attr == 'astype'):
                        bpi__pwxfd = True
                        continue
            if saved_array_analysis and jpa__rgx.name in lives and is_expr(
                dadv__fhef, 'getattr'
                ) and dadv__fhef.attr == 'shape' and is_array_typ(typemap[
                dadv__fhef.value.name]) and dadv__fhef.value.name not in lives:
                imoin__kob = {mhgb__tfjsm: nut__cqoa for nut__cqoa,
                    mhgb__tfjsm in func_ir.blocks.items()}
                if block in imoin__kob:
                    label = imoin__kob[block]
                    rhkyx__plmgp = saved_array_analysis.get_equiv_set(label)
                    qrs__rkkbj = rhkyx__plmgp.get_equiv_set(dadv__fhef.value)
                    if qrs__rkkbj is not None:
                        for mhgb__tfjsm in qrs__rkkbj:
                            if mhgb__tfjsm.endswith('#0'):
                                mhgb__tfjsm = mhgb__tfjsm[:-2]
                            if mhgb__tfjsm in typemap and is_array_typ(typemap
                                [mhgb__tfjsm]) and mhgb__tfjsm in lives:
                                dadv__fhef.value = ir.Var(dadv__fhef.value.
                                    scope, mhgb__tfjsm, dadv__fhef.value.loc)
                                bpi__pwxfd = True
                                break
            if isinstance(dadv__fhef, ir.Var
                ) and jpa__rgx.name == dadv__fhef.name:
                bpi__pwxfd = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                bpi__pwxfd = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            esqj__wdc = analysis.ir_extension_usedefs[type(stmt)]
            tjh__qom, ykpx__bpqpp = esqj__wdc(stmt)
            lives -= ykpx__bpqpp
            lives |= tjh__qom
        else:
            lives |= {mhgb__tfjsm.name for mhgb__tfjsm in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                nrf__dzmeg = set()
                if isinstance(dadv__fhef, ir.Expr):
                    nrf__dzmeg = {mhgb__tfjsm.name for mhgb__tfjsm in
                        dadv__fhef.list_vars()}
                if jpa__rgx.name not in nrf__dzmeg:
                    lives.remove(jpa__rgx.name)
        iuk__wycpp.append(stmt)
    iuk__wycpp.reverse()
    block.body = iuk__wycpp
    return bpi__pwxfd


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            twrkb__kltg, = args
            if isinstance(twrkb__kltg, types.IterableType):
                dtype = twrkb__kltg.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), twrkb__kltg)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    pbxsh__lwwvm = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (pbxsh__lwwvm, self.dtype)
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
        except LiteralTypingError as wqn__kvd:
            return
    try:
        return literal(value)
    except LiteralTypingError as wqn__kvd:
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
        shqjj__funmx = py_func.__qualname__
    except AttributeError as wqn__kvd:
        shqjj__funmx = py_func.__name__
    vcmq__beks = inspect.getfile(py_func)
    for cls in self._locator_classes:
        kniv__ikjeh = cls.from_function(py_func, vcmq__beks)
        if kniv__ikjeh is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (shqjj__funmx, vcmq__beks))
    self._locator = kniv__ikjeh
    zeonx__mzex = inspect.getfile(py_func)
    yex__ptx = os.path.splitext(os.path.basename(zeonx__mzex))[0]
    if vcmq__beks.startswith('<ipython-'):
        kdhh__vgnb = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', yex__ptx, count=1)
        if kdhh__vgnb == yex__ptx:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        yex__ptx = kdhh__vgnb
    anbl__gvy = '%s.%s' % (yex__ptx, shqjj__funmx)
    zuc__bibcp = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(anbl__gvy, zuc__bibcp
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    sqxi__cvhu = list(filter(lambda a: self._istuple(a.name), args))
    if len(sqxi__cvhu) == 2 and fn.__name__ == 'add':
        kmch__wel = self.typemap[sqxi__cvhu[0].name]
        gpw__wayks = self.typemap[sqxi__cvhu[1].name]
        if kmch__wel.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                sqxi__cvhu[1]))
        if gpw__wayks.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                sqxi__cvhu[0]))
        try:
            ibue__zxa = [equiv_set.get_shape(x) for x in sqxi__cvhu]
            if None in ibue__zxa:
                return None
            zqyd__arnfa = sum(ibue__zxa, ())
            return ArrayAnalysis.AnalyzeResult(shape=zqyd__arnfa)
        except GuardException as wqn__kvd:
            return None
    titm__vqnlz = list(filter(lambda a: self._isarray(a.name), args))
    require(len(titm__vqnlz) > 0)
    zgvo__vww = [x.name for x in titm__vqnlz]
    oarzl__uuvt = [self.typemap[x.name].ndim for x in titm__vqnlz]
    dcug__hkm = max(oarzl__uuvt)
    require(dcug__hkm > 0)
    ibue__zxa = [equiv_set.get_shape(x) for x in titm__vqnlz]
    if any(a is None for a in ibue__zxa):
        return ArrayAnalysis.AnalyzeResult(shape=titm__vqnlz[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, titm__vqnlz))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, ibue__zxa,
        zgvo__vww)


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
    hphvm__ytjiu = code_obj.code
    ddvx__yqueb = len(hphvm__ytjiu.co_freevars)
    fhwwa__lfxde = hphvm__ytjiu.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        brl__wts, op = ir_utils.find_build_sequence(caller_ir, code_obj.closure
            )
        assert op == 'build_tuple'
        fhwwa__lfxde = [mhgb__tfjsm.name for mhgb__tfjsm in brl__wts]
    wwmsn__fpsp = caller_ir.func_id.func.__globals__
    try:
        wwmsn__fpsp = getattr(code_obj, 'globals', wwmsn__fpsp)
    except KeyError as wqn__kvd:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    ubedv__tobb = []
    for x in fhwwa__lfxde:
        try:
            wot__pajut = caller_ir.get_definition(x)
        except KeyError as wqn__kvd:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(wot__pajut, (ir.Const, ir.Global, ir.FreeVar)):
            val = wot__pajut.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                lffj__vgrs = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                wwmsn__fpsp[lffj__vgrs] = bodo.jit(distributed=False)(val)
                wwmsn__fpsp[lffj__vgrs].is_nested_func = True
                val = lffj__vgrs
            if isinstance(val, CPUDispatcher):
                lffj__vgrs = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                wwmsn__fpsp[lffj__vgrs] = val
                val = lffj__vgrs
            ubedv__tobb.append(val)
        elif isinstance(wot__pajut, ir.Expr
            ) and wot__pajut.op == 'make_function':
            axal__gpe = convert_code_obj_to_function(wot__pajut, caller_ir)
            lffj__vgrs = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            wwmsn__fpsp[lffj__vgrs] = bodo.jit(distributed=False)(axal__gpe)
            wwmsn__fpsp[lffj__vgrs].is_nested_func = True
            ubedv__tobb.append(lffj__vgrs)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    jciu__vkukq = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate
        (ubedv__tobb)])
    uozr__cma = ','.join([('c_%d' % i) for i in range(ddvx__yqueb)])
    uwop__oyb = list(hphvm__ytjiu.co_varnames)
    tfck__bthw = 0
    xzz__xwrjd = hphvm__ytjiu.co_argcount
    mqnjl__fugp = caller_ir.get_definition(code_obj.defaults)
    if mqnjl__fugp is not None:
        if isinstance(mqnjl__fugp, tuple):
            d = [caller_ir.get_definition(x).value for x in mqnjl__fugp]
            zeb__jxje = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in mqnjl__fugp.items]
            zeb__jxje = tuple(d)
        tfck__bthw = len(zeb__jxje)
    avnoq__iffsy = xzz__xwrjd - tfck__bthw
    uxjz__xzp = ','.join([('%s' % uwop__oyb[i]) for i in range(avnoq__iffsy)])
    if tfck__bthw:
        lcy__hewt = [('%s = %s' % (uwop__oyb[i + avnoq__iffsy], zeb__jxje[i
            ])) for i in range(tfck__bthw)]
        uxjz__xzp += ', '
        uxjz__xzp += ', '.join(lcy__hewt)
    return _create_function_from_code_obj(hphvm__ytjiu, jciu__vkukq,
        uxjz__xzp, uozr__cma, wwmsn__fpsp)


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
    for pgkp__amqy, (nkv__aww, dkwf__qtetk) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % dkwf__qtetk)
            czym__wix = _pass_registry.get(nkv__aww).pass_inst
            if isinstance(czym__wix, CompilerPass):
                self._runPass(pgkp__amqy, czym__wix, state)
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
                    pipeline_name, dkwf__qtetk)
                tgjuj__iecid = self._patch_error(msg, e)
                raise tgjuj__iecid
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
    femr__mpi = None
    ykpx__bpqpp = {}

    def lookup(var, already_seen, varonly=True):
        val = ykpx__bpqpp.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    vyhos__lbbla = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        jpa__rgx = stmt.target
        dadv__fhef = stmt.value
        ykpx__bpqpp[jpa__rgx.name] = dadv__fhef
        if isinstance(dadv__fhef, ir.Var) and dadv__fhef.name in ykpx__bpqpp:
            dadv__fhef = lookup(dadv__fhef, set())
        if isinstance(dadv__fhef, ir.Expr):
            kusxz__tni = set(lookup(mhgb__tfjsm, set(), True).name for
                mhgb__tfjsm in dadv__fhef.list_vars())
            if name in kusxz__tni:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(dadv__fhef)]
                yowv__nzn = [x for x, lut__qdkqu in args if lut__qdkqu.name !=
                    name]
                args = [(x, lut__qdkqu) for x, lut__qdkqu in args if x !=
                    lut__qdkqu.name]
                yflsj__bfpb = dict(args)
                if len(yowv__nzn) == 1:
                    yflsj__bfpb[yowv__nzn[0]] = ir.Var(jpa__rgx.scope, name +
                        '#init', jpa__rgx.loc)
                replace_vars_inner(dadv__fhef, yflsj__bfpb)
                femr__mpi = nodes[i:]
                break
    return femr__mpi


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
        gowdf__kxrfh = expand_aliases({mhgb__tfjsm.name for mhgb__tfjsm in
            stmt.list_vars()}, alias_map, arg_aliases)
        yvklh__gtycq = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        rvux__sod = expand_aliases({mhgb__tfjsm.name for mhgb__tfjsm in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        vlu__tndfb = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(yvklh__gtycq & rvux__sod | vlu__tndfb & gowdf__kxrfh) == 0:
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
    pswk__otkn = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            pswk__otkn.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                pswk__otkn.update(get_parfor_writes(stmt, func_ir))
    return pswk__otkn


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    pswk__otkn = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        pswk__otkn.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        pswk__otkn = {mhgb__tfjsm.name for mhgb__tfjsm in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        pswk__otkn = {mhgb__tfjsm.name for mhgb__tfjsm in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            pswk__otkn.update({mhgb__tfjsm.name for mhgb__tfjsm in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        peh__vjfa = guard(find_callname, func_ir, stmt.value)
        if peh__vjfa in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            pswk__otkn.add(stmt.value.args[0].name)
        if peh__vjfa == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            pswk__otkn.add(stmt.value.args[1].name)
    return pswk__otkn


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
        kxf__byh = _termcolor.errmsg('{0}') + _termcolor.filename('During: {1}'
            )
        fndj__exzbr = kxf__byh.format(self, msg)
        self.args = fndj__exzbr,
    else:
        kxf__byh = _termcolor.errmsg('{0}')
        fndj__exzbr = kxf__byh.format(self)
        self.args = fndj__exzbr,
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
        for plzko__qhlb in options['distributed']:
            dist_spec[plzko__qhlb] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for plzko__qhlb in options['distributed_block']:
            dist_spec[plzko__qhlb] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    pbww__jyp = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, rawie__mnimk in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(rawie__mnimk)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    bxysz__qmc = {}
    for nmr__sbaav in reversed(inspect.getmro(cls)):
        bxysz__qmc.update(nmr__sbaav.__dict__)
    zhclb__bvq, wjn__pily, pjn__rvdkj, yvv__bckm = {}, {}, {}, {}
    for nut__cqoa, mhgb__tfjsm in bxysz__qmc.items():
        if isinstance(mhgb__tfjsm, pytypes.FunctionType):
            zhclb__bvq[nut__cqoa] = mhgb__tfjsm
        elif isinstance(mhgb__tfjsm, property):
            wjn__pily[nut__cqoa] = mhgb__tfjsm
        elif isinstance(mhgb__tfjsm, staticmethod):
            pjn__rvdkj[nut__cqoa] = mhgb__tfjsm
        else:
            yvv__bckm[nut__cqoa] = mhgb__tfjsm
    rouxg__rxr = (set(zhclb__bvq) | set(wjn__pily) | set(pjn__rvdkj)) & set(
        spec)
    if rouxg__rxr:
        raise NameError('name shadowing: {0}'.format(', '.join(rouxg__rxr)))
    cbpzg__lprg = yvv__bckm.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(yvv__bckm)
    if yvv__bckm:
        msg = 'class members are not yet supported: {0}'
        wdzfr__jdtzy = ', '.join(yvv__bckm.keys())
        raise TypeError(msg.format(wdzfr__jdtzy))
    for nut__cqoa, mhgb__tfjsm in wjn__pily.items():
        if mhgb__tfjsm.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(nut__cqoa))
    jit_methods = {nut__cqoa: bodo.jit(returns_maybe_distributed=pbww__jyp)
        (mhgb__tfjsm) for nut__cqoa, mhgb__tfjsm in zhclb__bvq.items()}
    jit_props = {}
    for nut__cqoa, mhgb__tfjsm in wjn__pily.items():
        ivz__xrwyo = {}
        if mhgb__tfjsm.fget:
            ivz__xrwyo['get'] = bodo.jit(mhgb__tfjsm.fget)
        if mhgb__tfjsm.fset:
            ivz__xrwyo['set'] = bodo.jit(mhgb__tfjsm.fset)
        jit_props[nut__cqoa] = ivz__xrwyo
    jit_static_methods = {nut__cqoa: bodo.jit(mhgb__tfjsm.__func__) for 
        nut__cqoa, mhgb__tfjsm in pjn__rvdkj.items()}
    kmuo__yqfpo = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    jqz__cburj = dict(class_type=kmuo__yqfpo, __doc__=cbpzg__lprg)
    jqz__cburj.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), jqz__cburj)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, kmuo__yqfpo)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(kmuo__yqfpo, typingctx, targetctx).register()
    as_numba_type.register(cls, kmuo__yqfpo.instance_type)
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
    avv__xtmni = ','.join('{0}:{1}'.format(nut__cqoa, mhgb__tfjsm) for 
        nut__cqoa, mhgb__tfjsm in struct.items())
    otj__ziiof = ','.join('{0}:{1}'.format(nut__cqoa, mhgb__tfjsm) for 
        nut__cqoa, mhgb__tfjsm in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), avv__xtmni, otj__ziiof)
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
    spihg__mggyk = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if spihg__mggyk is None:
        return
    tnu__sebmb, oqs__btxs = spihg__mggyk
    for a in itertools.chain(tnu__sebmb, oqs__btxs.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, tnu__sebmb, oqs__btxs)
    except ForceLiteralArg as e:
        peeba__vmav = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(peeba__vmav, self.kws)
        eqx__djm = set()
        afoev__mjhgm = set()
        overf__tmg = {}
        for pgkp__amqy in e.requested_args:
            ktaqj__iba = typeinfer.func_ir.get_definition(folded[pgkp__amqy])
            if isinstance(ktaqj__iba, ir.Arg):
                eqx__djm.add(ktaqj__iba.index)
                if ktaqj__iba.index in e.file_infos:
                    overf__tmg[ktaqj__iba.index] = e.file_infos[ktaqj__iba.
                        index]
            else:
                afoev__mjhgm.add(pgkp__amqy)
        if afoev__mjhgm:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif eqx__djm:
            raise ForceLiteralArg(eqx__djm, loc=self.loc, file_infos=overf__tmg
                )
    if sig is None:
        miwzr__bsz = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in tnu__sebmb]
        args += [('%s=%s' % (nut__cqoa, mhgb__tfjsm)) for nut__cqoa,
            mhgb__tfjsm in sorted(oqs__btxs.items())]
        user__ruvdu = miwzr__bsz.format(fnty, ', '.join(map(str, args)))
        mln__tnb = context.explain_function_type(fnty)
        msg = '\n'.join([user__ruvdu, mln__tnb])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        vlx__jlydk = context.unify_pairs(sig.recvr, fnty.this)
        if vlx__jlydk is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if vlx__jlydk is not None and vlx__jlydk.is_precise():
            pjc__fevr = fnty.copy(this=vlx__jlydk)
            typeinfer.propagate_refined_type(self.func, pjc__fevr)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            mlfyo__swqpu = target.getone()
            if context.unify_pairs(mlfyo__swqpu, sig.return_type
                ) == mlfyo__swqpu:
                sig = sig.replace(return_type=mlfyo__swqpu)
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
        etean__ojta = '*other* must be a {} but got a {} instead'
        raise TypeError(etean__ojta.format(ForceLiteralArg, type(other)))
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
    ojyp__dxic = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for nut__cqoa, mhgb__tfjsm in kwargs.items():
        vggo__eqkv = None
        try:
            lcvvc__ojybt = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[lcvvc__ojybt.name] = [mhgb__tfjsm]
            vggo__eqkv = get_const_value_inner(func_ir, lcvvc__ojybt)
            func_ir._definitions.pop(lcvvc__ojybt.name)
            if isinstance(vggo__eqkv, str):
                vggo__eqkv = sigutils._parse_signature_string(vggo__eqkv)
            if isinstance(vggo__eqkv, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {nut__cqoa} is annotated as type class {vggo__eqkv}."""
                    )
            assert isinstance(vggo__eqkv, types.Type)
            if isinstance(vggo__eqkv, (types.List, types.Set)):
                vggo__eqkv = vggo__eqkv.copy(reflected=False)
            ojyp__dxic[nut__cqoa] = vggo__eqkv
        except BodoError as wqn__kvd:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(vggo__eqkv, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(mhgb__tfjsm, ir.Global):
                    msg = f'Global {mhgb__tfjsm.name!r} is not defined.'
                if isinstance(mhgb__tfjsm, ir.FreeVar):
                    msg = f'Freevar {mhgb__tfjsm.name!r} is not defined.'
            if isinstance(mhgb__tfjsm, ir.Expr
                ) and mhgb__tfjsm.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=nut__cqoa, msg=msg, loc=loc)
    for name, typ in ojyp__dxic.items():
        self._legalize_arg_type(name, typ, loc)
    return ojyp__dxic


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
    cha__gfsze = inst.arg
    assert cha__gfsze > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(cha__gfsze)]))
    tmps = [state.make_temp() for _ in range(cha__gfsze - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    ias__wjbg = ir.Global('format', format, loc=self.loc)
    self.store(value=ias__wjbg, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    bbr__okvlv = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=bbr__okvlv, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    cha__gfsze = inst.arg
    assert cha__gfsze > 0, 'invalid BUILD_STRING count'
    ssxoi__snefo = self.get(strings[0])
    for other, mli__ozde in zip(strings[1:], tmps):
        other = self.get(other)
        gvfev__dtws = ir.Expr.binop(operator.add, lhs=ssxoi__snefo, rhs=
            other, loc=self.loc)
        self.store(gvfev__dtws, mli__ozde)
        ssxoi__snefo = self.get(mli__ozde)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    xhh__hwufn = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, xhh__hwufn])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    gdrnx__oym = mk_unique_var(f'{var_name}')
    dccf__zmvdo = gdrnx__oym.replace('<', '_').replace('>', '_')
    dccf__zmvdo = dccf__zmvdo.replace('.', '_').replace('$', '_v')
    return dccf__zmvdo


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
                acxr__kds = get_overload_const_str(val2)
                if acxr__kds != 'ns':
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
        nxr__rif = states['defmap']
        if len(nxr__rif) == 0:
            kxl__xsl = assign.target
            numba.core.ssa._logger.debug('first assign: %s', kxl__xsl)
            if kxl__xsl.name not in scope.localvars:
                kxl__xsl = scope.define(assign.target.name, loc=assign.loc)
        else:
            kxl__xsl = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=kxl__xsl, value=assign.value, loc=assign.loc)
        nxr__rif[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    pwfvy__sfiw = []
    for nut__cqoa, mhgb__tfjsm in typing.npydecl.registry.globals:
        if nut__cqoa == func:
            pwfvy__sfiw.append(mhgb__tfjsm)
    for nut__cqoa, mhgb__tfjsm in typing.templates.builtin_registry.globals:
        if nut__cqoa == func:
            pwfvy__sfiw.append(mhgb__tfjsm)
    if len(pwfvy__sfiw) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return pwfvy__sfiw


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    gwi__qbxur = {}
    kvp__vbel = find_topo_order(blocks)
    tytn__vvveg = {}
    for label in kvp__vbel:
        block = blocks[label]
        iuk__wycpp = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                jpa__rgx = stmt.target.name
                dadv__fhef = stmt.value
                if (dadv__fhef.op == 'getattr' and dadv__fhef.attr in
                    arr_math and isinstance(typemap[dadv__fhef.value.name],
                    types.npytypes.Array)):
                    dadv__fhef = stmt.value
                    lrtcy__qsg = dadv__fhef.value
                    gwi__qbxur[jpa__rgx] = lrtcy__qsg
                    scope = lrtcy__qsg.scope
                    loc = lrtcy__qsg.loc
                    urx__swo = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[urx__swo.name] = types.misc.Module(numpy)
                    pgpjy__usfvo = ir.Global('np', numpy, loc)
                    krbs__ronx = ir.Assign(pgpjy__usfvo, urx__swo, loc)
                    dadv__fhef.value = urx__swo
                    iuk__wycpp.append(krbs__ronx)
                    func_ir._definitions[urx__swo.name] = [pgpjy__usfvo]
                    func = getattr(numpy, dadv__fhef.attr)
                    espvk__mybx = get_np_ufunc_typ_lst(func)
                    tytn__vvveg[jpa__rgx] = espvk__mybx
                if (dadv__fhef.op == 'call' and dadv__fhef.func.name in
                    gwi__qbxur):
                    lrtcy__qsg = gwi__qbxur[dadv__fhef.func.name]
                    pme__qbdb = calltypes.pop(dadv__fhef)
                    uyu__vshqo = pme__qbdb.args[:len(dadv__fhef.args)]
                    bea__kff = {name: typemap[mhgb__tfjsm.name] for name,
                        mhgb__tfjsm in dadv__fhef.kws}
                    jwgk__kfajl = tytn__vvveg[dadv__fhef.func.name]
                    bqsbp__hgo = None
                    for qvee__vnq in jwgk__kfajl:
                        try:
                            bqsbp__hgo = qvee__vnq.get_call_type(typingctx,
                                [typemap[lrtcy__qsg.name]] + list(
                                uyu__vshqo), bea__kff)
                            typemap.pop(dadv__fhef.func.name)
                            typemap[dadv__fhef.func.name] = qvee__vnq
                            calltypes[dadv__fhef] = bqsbp__hgo
                            break
                        except Exception as wqn__kvd:
                            pass
                    if bqsbp__hgo is None:
                        raise TypeError(
                            f'No valid template found for {dadv__fhef.func.name}'
                            )
                    dadv__fhef.args = [lrtcy__qsg] + dadv__fhef.args
            iuk__wycpp.append(stmt)
        block.body = iuk__wycpp


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    biuex__mevg = ufunc.nin
    gvsm__huram = ufunc.nout
    avnoq__iffsy = ufunc.nargs
    assert avnoq__iffsy == biuex__mevg + gvsm__huram
    if len(args) < biuex__mevg:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            biuex__mevg))
    if len(args) > avnoq__iffsy:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            avnoq__iffsy))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    bkwnn__eyiz = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    plte__lmz = max(bkwnn__eyiz)
    znxt__gqp = args[biuex__mevg:]
    if not all(d == plte__lmz for d in bkwnn__eyiz[biuex__mevg:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(cuv__ftr, types.ArrayCompatible) and not
        isinstance(cuv__ftr, types.Bytes) for cuv__ftr in znxt__gqp):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(cuv__ftr.mutable for cuv__ftr in znxt__gqp):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    tjs__ylbnf = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    rxh__bwdlx = None
    if plte__lmz > 0 and len(znxt__gqp) < ufunc.nout:
        rxh__bwdlx = 'C'
        iifx__cfoac = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in iifx__cfoac and 'F' in iifx__cfoac:
            rxh__bwdlx = 'F'
    return tjs__ylbnf, znxt__gqp, plte__lmz, rxh__bwdlx


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
        xklw__fnrrg = 'Dict.key_type cannot be of type {}'
        raise TypingError(xklw__fnrrg.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        xklw__fnrrg = 'Dict.value_type cannot be of type {}'
        raise TypingError(xklw__fnrrg.format(valty))
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
    nvz__spj = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[nvz__spj]
        return impl, args
    except KeyError as wqn__kvd:
        pass
    impl, args = self._build_impl(nvz__spj, args, kws)
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
    olw__whc = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            nzzw__hmnz = block.body[-1]
            if isinstance(nzzw__hmnz, ir.Branch):
                if len(blocks[nzzw__hmnz.truebr].body) == 1 and len(blocks[
                    nzzw__hmnz.falsebr].body) == 1:
                    acwd__dor = blocks[nzzw__hmnz.truebr].body[0]
                    ftz__twl = blocks[nzzw__hmnz.falsebr].body[0]
                    if isinstance(acwd__dor, ir.Jump) and isinstance(ftz__twl,
                        ir.Jump) and acwd__dor.target == ftz__twl.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(acwd__dor
                            .target, nzzw__hmnz.loc)
                        olw__whc = True
                elif len(blocks[nzzw__hmnz.truebr].body) == 1:
                    acwd__dor = blocks[nzzw__hmnz.truebr].body[0]
                    if isinstance(acwd__dor, ir.Jump
                        ) and acwd__dor.target == nzzw__hmnz.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(acwd__dor
                            .target, nzzw__hmnz.loc)
                        olw__whc = True
                elif len(blocks[nzzw__hmnz.falsebr].body) == 1:
                    ftz__twl = blocks[nzzw__hmnz.falsebr].body[0]
                    if isinstance(ftz__twl, ir.Jump
                        ) and ftz__twl.target == nzzw__hmnz.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(ftz__twl
                            .target, nzzw__hmnz.loc)
                        olw__whc = True
    return olw__whc


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        howmg__wjjwj = find_topo_order(parfor.loop_body)
    iryi__yoy = howmg__wjjwj[0]
    bataf__dnt = {}
    _update_parfor_get_setitems(parfor.loop_body[iryi__yoy].body, parfor.
        index_var, alias_map, bataf__dnt, lives_n_aliases)
    eztxn__tyiyz = set(bataf__dnt.keys())
    for fbay__zizmy in howmg__wjjwj:
        if fbay__zizmy == iryi__yoy:
            continue
        for stmt in parfor.loop_body[fbay__zizmy].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            bssj__vrls = set(mhgb__tfjsm.name for mhgb__tfjsm in stmt.
                list_vars())
            ymm__zbrv = bssj__vrls & eztxn__tyiyz
            for a in ymm__zbrv:
                bataf__dnt.pop(a, None)
    for fbay__zizmy in howmg__wjjwj:
        if fbay__zizmy == iryi__yoy:
            continue
        block = parfor.loop_body[fbay__zizmy]
        zfuni__hncsf = bataf__dnt.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            zfuni__hncsf, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    bnyt__djmyo = max(blocks.keys())
    yjv__dfy, rywh__xtbcd = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    ofh__rvsrv = ir.Jump(yjv__dfy, ir.Loc('parfors_dummy', -1))
    blocks[bnyt__djmyo].body.append(ofh__rvsrv)
    srj__wusy = compute_cfg_from_blocks(blocks)
    znlx__npcu = compute_use_defs(blocks)
    pnz__nqln = compute_live_map(srj__wusy, blocks, znlx__npcu.usemap,
        znlx__npcu.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        iuk__wycpp = []
        akig__ffwmo = {mhgb__tfjsm.name for mhgb__tfjsm in block.terminator
            .list_vars()}
        for iqvvx__pqzx, sgcr__zjts in srj__wusy.successors(label):
            akig__ffwmo |= pnz__nqln[iqvvx__pqzx]
        for stmt in reversed(block.body):
            mjalq__qltg = akig__ffwmo & alias_set
            for mhgb__tfjsm in mjalq__qltg:
                akig__ffwmo |= alias_map[mhgb__tfjsm]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in akig__ffwmo and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                peh__vjfa = guard(find_callname, func_ir, stmt.value)
                if peh__vjfa == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in akig__ffwmo and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            akig__ffwmo |= {mhgb__tfjsm.name for mhgb__tfjsm in stmt.
                list_vars()}
            iuk__wycpp.append(stmt)
        iuk__wycpp.reverse()
        block.body = iuk__wycpp
    typemap.pop(rywh__xtbcd.name)
    blocks[bnyt__djmyo].body.pop()
    olw__whc = True
    while olw__whc:
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
        olw__whc = trim_empty_parfor_branches(parfor)
    rxiz__ufqmo = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        rxiz__ufqmo &= len(block.body) == 0
    if rxiz__ufqmo:
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
    ttog__qjwyw = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                ttog__qjwyw += 1
                parfor = stmt
                omluo__djieu = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = omluo__djieu.scope
                loc = ir.Loc('parfors_dummy', -1)
                kvx__cfo = ir.Var(scope, mk_unique_var('$const'), loc)
                omluo__djieu.body.append(ir.Assign(ir.Const(0, loc),
                    kvx__cfo, loc))
                omluo__djieu.body.append(ir.Return(kvx__cfo, loc))
                srj__wusy = compute_cfg_from_blocks(parfor.loop_body)
                for wssaa__yei in srj__wusy.dead_nodes():
                    del parfor.loop_body[wssaa__yei]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                omluo__djieu = parfor.loop_body[max(parfor.loop_body.keys())]
                omluo__djieu.body.pop()
                omluo__djieu.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return ttog__qjwyw


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    srj__wusy = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != srj__wusy.entry_point()
    zbxy__kkqb = list(filter(find_single_branch, blocks.keys()))
    ulmn__dwb = set()
    for label in zbxy__kkqb:
        inst = blocks[label].body[0]
        lly__john = srj__wusy.predecessors(label)
        quaop__kmv = True
        for dwxis__lonwy, twq__dyxhw in lly__john:
            block = blocks[dwxis__lonwy]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                quaop__kmv = False
        if quaop__kmv:
            ulmn__dwb.add(label)
    for label in ulmn__dwb:
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
            fmklf__svi = self.overloads.get(tuple(args))
            if fmklf__svi is not None:
                return fmklf__svi.entry_point
            self._pre_compile(args, return_type, flags)
            dwgc__yahbl = self.func_ir
            lyo__dzrj = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=lyo__dzrj):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=dwgc__yahbl, args=
                    args, return_type=return_type, flags=flags, locals=self
                    .locals, lifted=(), lifted_from=self.lifted_from,
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
        ifmx__fmeos = copy.deepcopy(flags)
        ifmx__fmeos.no_rewrites = True

        def compile_local(the_ir, the_flags):
            abvr__rzg = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return abvr__rzg.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        xow__ppqr = compile_local(func_ir, ifmx__fmeos)
        ziji__qat = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    ziji__qat = compile_local(func_ir, flags)
                except Exception as wqn__kvd:
                    pass
        if ziji__qat is not None:
            cres = ziji__qat
        else:
            cres = xow__ppqr
        return cres
    else:
        abvr__rzg = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return abvr__rzg.compile_ir(func_ir=func_ir, lifted=lifted,
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
    wafo__guf = self.get_data_type(typ.dtype)
    jcg__hcs = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        jcg__hcs):
        gdsr__wflz = ary.ctypes.data
        dkot__klcu = self.add_dynamic_addr(builder, gdsr__wflz, info=str(
            type(gdsr__wflz)))
        setn__preez = self.add_dynamic_addr(builder, id(ary), info=str(type
            (ary)))
        self.global_arrays.append(ary)
    else:
        ier__agfv = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            ier__agfv = ier__agfv.view('int64')
        val = bytearray(ier__agfv.data)
        udymm__skuo = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val
            )
        dkot__klcu = cgutils.global_constant(builder, '.const.array.data',
            udymm__skuo)
        dkot__klcu.align = self.get_abi_alignment(wafo__guf)
        setn__preez = None
    hbvwr__kimsx = self.get_value_type(types.intp)
    viref__xgkw = [self.get_constant(types.intp, dit__doksf) for dit__doksf in
        ary.shape]
    uav__ewdc = lir.Constant(lir.ArrayType(hbvwr__kimsx, len(viref__xgkw)),
        viref__xgkw)
    tdv__kpfa = [self.get_constant(types.intp, dit__doksf) for dit__doksf in
        ary.strides]
    xxf__gwza = lir.Constant(lir.ArrayType(hbvwr__kimsx, len(tdv__kpfa)),
        tdv__kpfa)
    reqj__doc = self.get_constant(types.intp, ary.dtype.itemsize)
    enx__jzh = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        enx__jzh, reqj__doc, dkot__klcu.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), uav__ewdc, xxf__gwza])


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
    tugj__xxown = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    dkw__bued = lir.Function(module, tugj__xxown, name='nrt_atomic_{0}'.
        format(op))
    [frl__csqkz] = dkw__bued.args
    sjqo__lgkht = dkw__bued.append_basic_block()
    builder = lir.IRBuilder(sjqo__lgkht)
    kbmho__zqzio = lir.Constant(_word_type, 1)
    if False:
        ynqs__kgd = builder.atomic_rmw(op, frl__csqkz, kbmho__zqzio,
            ordering=ordering)
        res = getattr(builder, op)(ynqs__kgd, kbmho__zqzio)
        builder.ret(res)
    else:
        ynqs__kgd = builder.load(frl__csqkz)
        xmy__tgbc = getattr(builder, op)(ynqs__kgd, kbmho__zqzio)
        hno__znhh = builder.icmp_signed('!=', ynqs__kgd, lir.Constant(
            ynqs__kgd.type, -1))
        with cgutils.if_likely(builder, hno__znhh):
            builder.store(xmy__tgbc, frl__csqkz)
        builder.ret(xmy__tgbc)
    return dkw__bued


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
        pnej__lqmnd = state.targetctx.codegen()
        state.library = pnej__lqmnd.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    cob__orbg = state.func_ir
    typemap = state.typemap
    tspi__ecy = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    eqjtm__ptv = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            cob__orbg, typemap, tspi__ecy, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            dki__upvbe = lowering.Lower(targetctx, library, fndesc,
                cob__orbg, metadata=metadata)
            dki__upvbe.lower()
            if not flags.no_cpython_wrapper:
                dki__upvbe.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(tspi__ecy, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        dki__upvbe.create_cfunc_wrapper()
            env = dki__upvbe.env
            fmwqz__uql = dki__upvbe.call_helper
            del dki__upvbe
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, fmwqz__uql, cfunc=None, env=env)
        else:
            phiz__vohfd = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(phiz__vohfd, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, fmwqz__uql, cfunc=
                phiz__vohfd, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        fcmf__iwpr = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = fcmf__iwpr - eqjtm__ptv
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
        azsfw__pky = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, azsfw__pky),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            tbyri__ykhm.do_break()
        fokbf__pdc = c.builder.icmp_signed('!=', azsfw__pky, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(fokbf__pdc, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, azsfw__pky)
                c.pyapi.decref(azsfw__pky)
                tbyri__ykhm.do_break()
        c.pyapi.decref(azsfw__pky)
    ehf__pzxpl, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(ehf__pzxpl, likely=True) as (wrijf__uswqr, oaf__wny
        ):
        with wrijf__uswqr:
            list.size = size
            bumi__tacmj = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                bumi__tacmj), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        bumi__tacmj))
                    with cgutils.for_range(c.builder, size) as tbyri__ykhm:
                        itemobj = c.pyapi.list_getitem(obj, tbyri__ykhm.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        ubbw__cqe = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(ubbw__cqe.is_error, likely=False
                            ):
                            c.builder.store(cgutils.true_bit, errorptr)
                            tbyri__ykhm.do_break()
                        list.setitem(tbyri__ykhm.index, ubbw__cqe.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with oaf__wny:
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
    yrw__ybjeb, dgsf__frl, unvh__aow, jcfym__cnu, bym__nxdy = (
        compile_time_get_string_data(literal_string))
    vsq__xtzm = builder.module
    gv = context.insert_const_bytes(vsq__xtzm, yrw__ybjeb)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        dgsf__frl), context.get_constant(types.int32, unvh__aow), context.
        get_constant(types.uint32, jcfym__cnu), context.get_constant(
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
    jru__afyhd = None
    if isinstance(shape, types.Integer):
        jru__afyhd = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(dit__doksf, (types.Integer, types.IntEnumMember)) for
            dit__doksf in shape):
            jru__afyhd = len(shape)
    return jru__afyhd


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
            jru__afyhd = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if jru__afyhd == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(jru__afyhd)
                    )
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            zgvo__vww = self._get_names(x)
            if len(zgvo__vww) != 0:
                return zgvo__vww[0]
            return zgvo__vww
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    zgvo__vww = self._get_names(obj)
    if len(zgvo__vww) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(zgvo__vww[0])


def get_equiv_set(self, obj):
    zgvo__vww = self._get_names(obj)
    if len(zgvo__vww) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(zgvo__vww[0])


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
    bxby__mzyfb = []
    for dwko__oeph in func_ir.arg_names:
        if dwko__oeph in typemap and isinstance(typemap[dwko__oeph], types.
            containers.UniTuple) and typemap[dwko__oeph].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(dwko__oeph))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for znqzq__jndjq in func_ir.blocks.values():
        for stmt in znqzq__jndjq.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    xgdxg__txg = getattr(val, 'code', None)
                    if xgdxg__txg is not None:
                        if getattr(val, 'closure', None) is not None:
                            gdea__ivq = '<creating a function from a closure>'
                            gvfev__dtws = ''
                        else:
                            gdea__ivq = xgdxg__txg.co_name
                            gvfev__dtws = '(%s) ' % gdea__ivq
                    else:
                        gdea__ivq = '<could not ascertain use case>'
                        gvfev__dtws = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (gdea__ivq, gvfev__dtws))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                gyc__bjlm = False
                if isinstance(val, pytypes.FunctionType):
                    gyc__bjlm = val in {numba.gdb, numba.gdb_init}
                if not gyc__bjlm:
                    gyc__bjlm = getattr(val, '_name', '') == 'gdb_internal'
                if gyc__bjlm:
                    bxby__mzyfb.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    daeyv__sjws = func_ir.get_definition(var)
                    oylvn__zgv = guard(find_callname, func_ir, daeyv__sjws)
                    if oylvn__zgv and oylvn__zgv[1] == 'numpy':
                        ty = getattr(numpy, oylvn__zgv[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    giwq__alcnp = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(giwq__alcnp), loc=stmt.loc)
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
    if len(bxby__mzyfb) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        wcm__wox = '\n'.join([x.strformat() for x in bxby__mzyfb])
        raise errors.UnsupportedError(msg % wcm__wox)


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
    nut__cqoa, mhgb__tfjsm = next(iter(val.items()))
    zmti__rru = typeof_impl(nut__cqoa, c)
    pdp__yci = typeof_impl(mhgb__tfjsm, c)
    if zmti__rru is None or pdp__yci is None:
        raise ValueError(
            f'Cannot type dict element type {type(nut__cqoa)}, {type(mhgb__tfjsm)}'
            )
    return types.DictType(zmti__rru, pdp__yci)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    omi__xwbje = cgutils.alloca_once_value(c.builder, val)
    tgo__saec = c.pyapi.object_hasattr_string(val, '_opaque')
    dvzr__hqyp = c.builder.icmp_unsigned('==', tgo__saec, lir.Constant(
        tgo__saec.type, 0))
    snvn__ams = typ.key_type
    hym__ysqig = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(snvn__ams, hym__ysqig)

    def copy_dict(out_dict, in_dict):
        for nut__cqoa, mhgb__tfjsm in in_dict.items():
            out_dict[nut__cqoa] = mhgb__tfjsm
    with c.builder.if_then(dvzr__hqyp):
        fym__rwi = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        yoq__hlp = c.pyapi.call_function_objargs(fym__rwi, [])
        rntv__zska = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(rntv__zska, [yoq__hlp, val])
        c.builder.store(yoq__hlp, omi__xwbje)
    val = c.builder.load(omi__xwbje)
    voepd__peiph = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    znar__uifce = c.pyapi.object_type(val)
    veh__nzap = c.builder.icmp_unsigned('==', znar__uifce, voepd__peiph)
    with c.builder.if_else(veh__nzap) as (jzghl__qworj, ffgvh__rfpk):
        with jzghl__qworj:
            vqkzk__gleuf = c.pyapi.object_getattr_string(val, '_opaque')
            aof__axunw = types.MemInfoPointer(types.voidptr)
            ubbw__cqe = c.unbox(aof__axunw, vqkzk__gleuf)
            mi = ubbw__cqe.value
            vsp__fzki = aof__axunw, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *vsp__fzki)
            bljp__itgnd = context.get_constant_null(vsp__fzki[1])
            args = mi, bljp__itgnd
            rnwbe__bqkyu, dcz__hzkt = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, dcz__hzkt)
            c.pyapi.decref(vqkzk__gleuf)
            tyybe__lsch = c.builder.basic_block
        with ffgvh__rfpk:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", znar__uifce, voepd__peiph)
            fkee__rmrpm = c.builder.basic_block
    mkqsf__bag = c.builder.phi(dcz__hzkt.type)
    bxdpi__wmch = c.builder.phi(rnwbe__bqkyu.type)
    mkqsf__bag.add_incoming(dcz__hzkt, tyybe__lsch)
    mkqsf__bag.add_incoming(dcz__hzkt.type(None), fkee__rmrpm)
    bxdpi__wmch.add_incoming(rnwbe__bqkyu, tyybe__lsch)
    bxdpi__wmch.add_incoming(cgutils.true_bit, fkee__rmrpm)
    c.pyapi.decref(voepd__peiph)
    c.pyapi.decref(znar__uifce)
    with c.builder.if_then(dvzr__hqyp):
        c.pyapi.decref(val)
    return NativeValue(mkqsf__bag, is_error=bxdpi__wmch)


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
    ate__fxbe = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=ate__fxbe, name=updatevar)
    bcr__fdpif = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=bcr__fdpif, name=res)


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
        for nut__cqoa, mhgb__tfjsm in other.items():
            d[nut__cqoa] = mhgb__tfjsm
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
    gvfev__dtws = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(gvfev__dtws, res)


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
    wzvj__emf = PassManager(name)
    if state.func_ir is None:
        wzvj__emf.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            wzvj__emf.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        wzvj__emf.add_pass(FixupArgs, 'fix up args')
    wzvj__emf.add_pass(IRProcessing, 'processing IR')
    wzvj__emf.add_pass(WithLifting, 'Handle with contexts')
    wzvj__emf.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        wzvj__emf.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        wzvj__emf.add_pass(DeadBranchPrune, 'dead branch pruning')
        wzvj__emf.add_pass(GenericRewrites, 'nopython rewrites')
    wzvj__emf.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    wzvj__emf.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        wzvj__emf.add_pass(DeadBranchPrune, 'dead branch pruning')
    wzvj__emf.add_pass(FindLiterallyCalls, 'find literally calls')
    wzvj__emf.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        wzvj__emf.add_pass(ReconstructSSA, 'ssa')
    wzvj__emf.add_pass(LiteralPropagationSubPipelinePass, 'Literal propagation'
        )
    wzvj__emf.finalize()
    return wzvj__emf


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
    a, trej__pno = args
    if isinstance(a, types.List) and isinstance(trej__pno, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(trej__pno, types.List):
        return signature(trej__pno, types.intp, trej__pno)


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
        iuoxh__wgmuh, yzcv__rtg = 0, 1
    else:
        iuoxh__wgmuh, yzcv__rtg = 1, 0
    twb__lfyf = ListInstance(context, builder, sig.args[iuoxh__wgmuh], args
        [iuoxh__wgmuh])
    emq__snjk = twb__lfyf.size
    zmxoo__vlu = args[yzcv__rtg]
    bumi__tacmj = lir.Constant(zmxoo__vlu.type, 0)
    zmxoo__vlu = builder.select(cgutils.is_neg_int(builder, zmxoo__vlu),
        bumi__tacmj, zmxoo__vlu)
    enx__jzh = builder.mul(zmxoo__vlu, emq__snjk)
    pguh__pfl = ListInstance.allocate(context, builder, sig.return_type,
        enx__jzh)
    pguh__pfl.size = enx__jzh
    with cgutils.for_range_slice(builder, bumi__tacmj, enx__jzh, emq__snjk,
        inc=True) as (yzs__nfkh, _):
        with cgutils.for_range(builder, emq__snjk) as tbyri__ykhm:
            value = twb__lfyf.getitem(tbyri__ykhm.index)
            pguh__pfl.setitem(builder.add(tbyri__ykhm.index, yzs__nfkh),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, pguh__pfl.value)


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
    sxfri__vqsdk = first.unify(self, second)
    if sxfri__vqsdk is not None:
        return sxfri__vqsdk
    sxfri__vqsdk = second.unify(self, first)
    if sxfri__vqsdk is not None:
        return sxfri__vqsdk
    rwhxq__rau = self.can_convert(fromty=first, toty=second)
    if rwhxq__rau is not None and rwhxq__rau <= Conversion.safe:
        return second
    rwhxq__rau = self.can_convert(fromty=second, toty=first)
    if rwhxq__rau is not None and rwhxq__rau <= Conversion.safe:
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
    enx__jzh = payload.used
    listobj = c.pyapi.list_new(enx__jzh)
    ehf__pzxpl = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(ehf__pzxpl, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(enx__jzh.
            type, 0))
        with payload._iterate() as tbyri__ykhm:
            i = c.builder.load(index)
            item = tbyri__ykhm.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return ehf__pzxpl, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    fqbn__ujpbr = h.type
    jrrr__mkdmp = self.mask
    dtype = self._ty.dtype
    azmth__vmmo = context.typing_context
    fnty = azmth__vmmo.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(azmth__vmmo, (dtype, dtype), {})
    yjtj__nts = context.get_function(fnty, sig)
    hyrha__bdih = ir.Constant(fqbn__ujpbr, 1)
    tnosl__wzv = ir.Constant(fqbn__ujpbr, 5)
    jns__dcb = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, jrrr__mkdmp))
    if for_insert:
        gyw__sfju = jrrr__mkdmp.type(-1)
        xhrx__hjb = cgutils.alloca_once_value(builder, gyw__sfju)
    gvi__tqcyh = builder.append_basic_block('lookup.body')
    oea__avn = builder.append_basic_block('lookup.found')
    dxmap__kqtzq = builder.append_basic_block('lookup.not_found')
    zoobx__durng = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        oqu__ynd = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, oqu__ynd)):
            lhnje__dbv = yjtj__nts(builder, (item, entry.key))
            with builder.if_then(lhnje__dbv):
                builder.branch(oea__avn)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, oqu__ynd)):
            builder.branch(dxmap__kqtzq)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, oqu__ynd)):
                pid__ham = builder.load(xhrx__hjb)
                pid__ham = builder.select(builder.icmp_unsigned('==',
                    pid__ham, gyw__sfju), i, pid__ham)
                builder.store(pid__ham, xhrx__hjb)
    with cgutils.for_range(builder, ir.Constant(fqbn__ujpbr, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, hyrha__bdih)
        i = builder.and_(i, jrrr__mkdmp)
        builder.store(i, index)
    builder.branch(gvi__tqcyh)
    with builder.goto_block(gvi__tqcyh):
        i = builder.load(index)
        check_entry(i)
        dwxis__lonwy = builder.load(jns__dcb)
        dwxis__lonwy = builder.lshr(dwxis__lonwy, tnosl__wzv)
        i = builder.add(hyrha__bdih, builder.mul(i, tnosl__wzv))
        i = builder.and_(jrrr__mkdmp, builder.add(i, dwxis__lonwy))
        builder.store(i, index)
        builder.store(dwxis__lonwy, jns__dcb)
        builder.branch(gvi__tqcyh)
    with builder.goto_block(dxmap__kqtzq):
        if for_insert:
            i = builder.load(index)
            pid__ham = builder.load(xhrx__hjb)
            i = builder.select(builder.icmp_unsigned('==', pid__ham,
                gyw__sfju), i, pid__ham)
            builder.store(i, index)
        builder.branch(zoobx__durng)
    with builder.goto_block(oea__avn):
        builder.branch(zoobx__durng)
    builder.position_at_end(zoobx__durng)
    gyc__bjlm = builder.phi(ir.IntType(1), 'found')
    gyc__bjlm.add_incoming(cgutils.true_bit, oea__avn)
    gyc__bjlm.add_incoming(cgutils.false_bit, dxmap__kqtzq)
    return gyc__bjlm, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    xmtx__zswn = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    zgmbq__sjhw = payload.used
    hyrha__bdih = ir.Constant(zgmbq__sjhw.type, 1)
    zgmbq__sjhw = payload.used = builder.add(zgmbq__sjhw, hyrha__bdih)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, xmtx__zswn), likely=True):
        payload.fill = builder.add(payload.fill, hyrha__bdih)
    if do_resize:
        self.upsize(zgmbq__sjhw)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    gyc__bjlm, i = payload._lookup(item, h, for_insert=True)
    nwjzq__ofm = builder.not_(gyc__bjlm)
    with builder.if_then(nwjzq__ofm):
        entry = payload.get_entry(i)
        xmtx__zswn = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        zgmbq__sjhw = payload.used
        hyrha__bdih = ir.Constant(zgmbq__sjhw.type, 1)
        zgmbq__sjhw = payload.used = builder.add(zgmbq__sjhw, hyrha__bdih)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, xmtx__zswn), likely=True):
            payload.fill = builder.add(payload.fill, hyrha__bdih)
        if do_resize:
            self.upsize(zgmbq__sjhw)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    zgmbq__sjhw = payload.used
    hyrha__bdih = ir.Constant(zgmbq__sjhw.type, 1)
    zgmbq__sjhw = payload.used = self._builder.sub(zgmbq__sjhw, hyrha__bdih)
    if do_resize:
        self.downsize(zgmbq__sjhw)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    ucsgi__xpbk = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, ucsgi__xpbk)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    qxbtf__vfrc = payload
    ehf__pzxpl = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(ehf__pzxpl), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with qxbtf__vfrc._iterate() as tbyri__ykhm:
        entry = tbyri__ykhm.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(qxbtf__vfrc.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as tbyri__ykhm:
        entry = tbyri__ykhm.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    ehf__pzxpl = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(ehf__pzxpl), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    ehf__pzxpl = cgutils.alloca_once_value(builder, cgutils.true_bit)
    fqbn__ujpbr = context.get_value_type(types.intp)
    bumi__tacmj = ir.Constant(fqbn__ujpbr, 0)
    hyrha__bdih = ir.Constant(fqbn__ujpbr, 1)
    awilw__dgdj = context.get_data_type(types.SetPayload(self._ty))
    tvedd__ljdsz = context.get_abi_sizeof(awilw__dgdj)
    xbazs__hbd = self._entrysize
    tvedd__ljdsz -= xbazs__hbd
    xxivh__ekm, qhuob__xxwph = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(fqbn__ujpbr, xbazs__hbd), ir.Constant(
        fqbn__ujpbr, tvedd__ljdsz))
    with builder.if_then(qhuob__xxwph, likely=False):
        builder.store(cgutils.false_bit, ehf__pzxpl)
    with builder.if_then(builder.load(ehf__pzxpl), likely=True):
        if realloc:
            okmx__cwl = self._set.meminfo
            frl__csqkz = context.nrt.meminfo_varsize_alloc(builder,
                okmx__cwl, size=xxivh__ekm)
            fpg__dcqsl = cgutils.is_null(builder, frl__csqkz)
        else:
            wede__ixbe = _imp_dtor(context, builder.module, self._ty)
            okmx__cwl = context.nrt.meminfo_new_varsize_dtor(builder,
                xxivh__ekm, builder.bitcast(wede__ixbe, cgutils.voidptr_t))
            fpg__dcqsl = cgutils.is_null(builder, okmx__cwl)
        with builder.if_else(fpg__dcqsl, likely=False) as (qmr__isun,
            wrijf__uswqr):
            with qmr__isun:
                builder.store(cgutils.false_bit, ehf__pzxpl)
            with wrijf__uswqr:
                if not realloc:
                    self._set.meminfo = okmx__cwl
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, xxivh__ekm, 255)
                payload.used = bumi__tacmj
                payload.fill = bumi__tacmj
                payload.finger = bumi__tacmj
                cyykr__rqnc = builder.sub(nentries, hyrha__bdih)
                payload.mask = cyykr__rqnc
    return builder.load(ehf__pzxpl)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    ehf__pzxpl = cgutils.alloca_once_value(builder, cgutils.true_bit)
    fqbn__ujpbr = context.get_value_type(types.intp)
    bumi__tacmj = ir.Constant(fqbn__ujpbr, 0)
    hyrha__bdih = ir.Constant(fqbn__ujpbr, 1)
    awilw__dgdj = context.get_data_type(types.SetPayload(self._ty))
    tvedd__ljdsz = context.get_abi_sizeof(awilw__dgdj)
    xbazs__hbd = self._entrysize
    tvedd__ljdsz -= xbazs__hbd
    jrrr__mkdmp = src_payload.mask
    nentries = builder.add(hyrha__bdih, jrrr__mkdmp)
    xxivh__ekm = builder.add(ir.Constant(fqbn__ujpbr, tvedd__ljdsz),
        builder.mul(ir.Constant(fqbn__ujpbr, xbazs__hbd), nentries))
    with builder.if_then(builder.load(ehf__pzxpl), likely=True):
        wede__ixbe = _imp_dtor(context, builder.module, self._ty)
        okmx__cwl = context.nrt.meminfo_new_varsize_dtor(builder,
            xxivh__ekm, builder.bitcast(wede__ixbe, cgutils.voidptr_t))
        fpg__dcqsl = cgutils.is_null(builder, okmx__cwl)
        with builder.if_else(fpg__dcqsl, likely=False) as (qmr__isun,
            wrijf__uswqr):
            with qmr__isun:
                builder.store(cgutils.false_bit, ehf__pzxpl)
            with wrijf__uswqr:
                self._set.meminfo = okmx__cwl
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = bumi__tacmj
                payload.mask = jrrr__mkdmp
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, xbazs__hbd)
                with src_payload._iterate() as tbyri__ykhm:
                    context.nrt.incref(builder, self._ty.dtype, tbyri__ykhm
                        .entry.key)
    return builder.load(ehf__pzxpl)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    dwj__ztn = context.get_value_type(types.voidptr)
    wag__gzy = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [dwj__ztn, wag__gzy, dwj__ztn])
    esu__najs = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=esu__najs)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        hif__cmkx = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, hif__cmkx)
        with payload._iterate() as tbyri__ykhm:
            entry = tbyri__ykhm.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    lfekh__swm, = sig.args
    brl__wts, = args
    hzx__myypy = numba.core.imputils.call_len(context, builder, lfekh__swm,
        brl__wts)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, hzx__myypy)
    with numba.core.imputils.for_iter(context, builder, lfekh__swm, brl__wts
        ) as tbyri__ykhm:
        inst.add(tbyri__ykhm.value)
        context.nrt.decref(builder, set_type.dtype, tbyri__ykhm.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    lfekh__swm = sig.args[1]
    brl__wts = args[1]
    hzx__myypy = numba.core.imputils.call_len(context, builder, lfekh__swm,
        brl__wts)
    if hzx__myypy is not None:
        crguy__ttmky = builder.add(inst.payload.used, hzx__myypy)
        inst.upsize(crguy__ttmky)
    with numba.core.imputils.for_iter(context, builder, lfekh__swm, brl__wts
        ) as tbyri__ykhm:
        mrzh__ltr = context.cast(builder, tbyri__ykhm.value, lfekh__swm.
            dtype, inst.dtype)
        inst.add(mrzh__ltr)
        context.nrt.decref(builder, lfekh__swm.dtype, tbyri__ykhm.value)
    if hzx__myypy is not None:
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
    khnvo__iiee = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, khnvo__iiee, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    phiz__vohfd = target_context.get_executable(library, fndesc, env)
    hxz__qvp = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=phiz__vohfd, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return hxz__qvp


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
        yuv__fza = MPI.COMM_WORLD
        if yuv__fza.Get_rank() == 0:
            ayely__oic = self.get_cache_path()
            os.makedirs(ayely__oic, exist_ok=True)
            tempfile.TemporaryFile(dir=ayely__oic).close()
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
    ztm__aaa = cgutils.create_struct_proxy(charseq.bytes_type)
    wkut__hmh = ztm__aaa(context, builder)
    if isinstance(nbytes, int):
        nbytes = ir.Constant(wkut__hmh.nitems.type, nbytes)
    wkut__hmh.meminfo = context.nrt.meminfo_alloc(builder, nbytes)
    wkut__hmh.nitems = nbytes
    wkut__hmh.itemsize = ir.Constant(wkut__hmh.itemsize.type, 1)
    wkut__hmh.data = context.nrt.meminfo_data(builder, wkut__hmh.meminfo)
    wkut__hmh.parent = cgutils.get_null_value(wkut__hmh.parent.type)
    wkut__hmh.shape = cgutils.pack_array(builder, [wkut__hmh.nitems],
        context.get_value_type(types.intp))
    wkut__hmh.strides = cgutils.pack_array(builder, [ir.Constant(wkut__hmh.
        strides.type.element, 1)], context.get_value_type(types.intp))
    return wkut__hmh


if _check_numba_change:
    lines = inspect.getsource(charseq._make_constant_bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b3ed23ad58baff7b935912e3e22f4d8af67423d8fd0e5f1836ba0b3028a6eb18':
        warnings.warn('charseq._make_constant_bytes has changed')
charseq._make_constant_bytes = _make_constant_bytes
