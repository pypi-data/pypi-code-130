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
    pluz__tea = numba.core.bytecode.FunctionIdentity.from_function(func)
    plyyl__fxo = numba.core.interpreter.Interpreter(pluz__tea)
    wdixq__fihu = numba.core.bytecode.ByteCode(func_id=pluz__tea)
    func_ir = plyyl__fxo.interpret(wdixq__fihu)
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
        bdt__twss = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        bdt__twss.run()
    lqwjh__tnqze = numba.core.postproc.PostProcessor(func_ir)
    lqwjh__tnqze.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, zll__fwa in visit_vars_extensions.items():
        if isinstance(stmt, t):
            zll__fwa(stmt, callback, cbdata)
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
    aysse__xwyy = ['ravel', 'transpose', 'reshape']
    for idsb__ggl in blocks.values():
        for lbkqy__kpjer in idsb__ggl.body:
            if type(lbkqy__kpjer) in alias_analysis_extensions:
                zll__fwa = alias_analysis_extensions[type(lbkqy__kpjer)]
                zll__fwa(lbkqy__kpjer, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(lbkqy__kpjer, ir.Assign):
                ksb__wvq = lbkqy__kpjer.value
                bcr__otqmn = lbkqy__kpjer.target.name
                if is_immutable_type(bcr__otqmn, typemap):
                    continue
                if isinstance(ksb__wvq, ir.Var
                    ) and bcr__otqmn != ksb__wvq.name:
                    _add_alias(bcr__otqmn, ksb__wvq.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr) and (ksb__wvq.op == 'cast' or
                    ksb__wvq.op in ['getitem', 'static_getitem']):
                    _add_alias(bcr__otqmn, ksb__wvq.value.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr
                    ) and ksb__wvq.op == 'inplace_binop':
                    _add_alias(bcr__otqmn, ksb__wvq.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr
                    ) and ksb__wvq.op == 'getattr' and ksb__wvq.attr in ['T',
                    'ctypes', 'flat']:
                    _add_alias(bcr__otqmn, ksb__wvq.value.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr
                    ) and ksb__wvq.op == 'getattr' and ksb__wvq.attr not in [
                    'shape'] and ksb__wvq.value.name in arg_aliases:
                    _add_alias(bcr__otqmn, ksb__wvq.value.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr
                    ) and ksb__wvq.op == 'getattr' and ksb__wvq.attr in ('loc',
                    'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(bcr__otqmn, ksb__wvq.value.name, alias_map,
                        arg_aliases)
                if isinstance(ksb__wvq, ir.Expr) and ksb__wvq.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(bcr__otqmn, typemap):
                    for zhup__zhfx in ksb__wvq.items:
                        _add_alias(bcr__otqmn, zhup__zhfx.name, alias_map,
                            arg_aliases)
                if isinstance(ksb__wvq, ir.Expr) and ksb__wvq.op == 'call':
                    tvbs__rhody = guard(find_callname, func_ir, ksb__wvq,
                        typemap)
                    if tvbs__rhody is None:
                        continue
                    uqw__dnei, wgje__nqrpa = tvbs__rhody
                    if tvbs__rhody in alias_func_extensions:
                        chdw__uuhw = alias_func_extensions[tvbs__rhody]
                        chdw__uuhw(bcr__otqmn, ksb__wvq.args, alias_map,
                            arg_aliases)
                    if wgje__nqrpa == 'numpy' and uqw__dnei in aysse__xwyy:
                        _add_alias(bcr__otqmn, ksb__wvq.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(wgje__nqrpa, ir.Var
                        ) and uqw__dnei in aysse__xwyy:
                        _add_alias(bcr__otqmn, wgje__nqrpa.name, alias_map,
                            arg_aliases)
    rtqj__uxh = copy.deepcopy(alias_map)
    for zhup__zhfx in rtqj__uxh:
        for dev__bxpa in rtqj__uxh[zhup__zhfx]:
            alias_map[zhup__zhfx] |= alias_map[dev__bxpa]
        for dev__bxpa in rtqj__uxh[zhup__zhfx]:
            alias_map[dev__bxpa] = alias_map[zhup__zhfx]
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
    ftbnx__vqjl = compute_cfg_from_blocks(func_ir.blocks)
    ray__gbma = compute_use_defs(func_ir.blocks)
    yjsn__ujxhp = compute_live_map(ftbnx__vqjl, func_ir.blocks, ray__gbma.
        usemap, ray__gbma.defmap)
    xusx__yxkip = True
    while xusx__yxkip:
        xusx__yxkip = False
        for label, block in func_ir.blocks.items():
            lives = {zhup__zhfx.name for zhup__zhfx in block.terminator.
                list_vars()}
            for kbcd__ick, fstsa__knmx in ftbnx__vqjl.successors(label):
                lives |= yjsn__ujxhp[kbcd__ick]
            dey__bzy = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    bcr__otqmn = stmt.target
                    mitt__ozgt = stmt.value
                    if bcr__otqmn.name not in lives:
                        if isinstance(mitt__ozgt, ir.Expr
                            ) and mitt__ozgt.op == 'make_function':
                            continue
                        if isinstance(mitt__ozgt, ir.Expr
                            ) and mitt__ozgt.op == 'getattr':
                            continue
                        if isinstance(mitt__ozgt, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(bcr__otqmn,
                            None), types.Function):
                            continue
                        if isinstance(mitt__ozgt, ir.Expr
                            ) and mitt__ozgt.op == 'build_map':
                            continue
                        if isinstance(mitt__ozgt, ir.Expr
                            ) and mitt__ozgt.op == 'build_tuple':
                            continue
                    if isinstance(mitt__ozgt, ir.Var
                        ) and bcr__otqmn.name == mitt__ozgt.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    zffj__geotx = analysis.ir_extension_usedefs[type(stmt)]
                    wuxaf__ntcd, xoy__oxn = zffj__geotx(stmt)
                    lives -= xoy__oxn
                    lives |= wuxaf__ntcd
                else:
                    lives |= {zhup__zhfx.name for zhup__zhfx in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(bcr__otqmn.name)
                dey__bzy.append(stmt)
            dey__bzy.reverse()
            if len(block.body) != len(dey__bzy):
                xusx__yxkip = True
            block.body = dey__bzy


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    khrj__rttfb = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (khrj__rttfb,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    ytpvf__fvgkq = dict(key=func, _overload_func=staticmethod(overload_func
        ), _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), ytpvf__fvgkq)


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
            for lzoys__jydh in fnty.templates:
                self._inline_overloads.update(lzoys__jydh._inline_overloads)
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
    ytpvf__fvgkq = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), ytpvf__fvgkq)
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
    flmop__dmy, gvkdh__kdvin = self._get_impl(args, kws)
    if flmop__dmy is None:
        return
    iaixd__gprv = types.Dispatcher(flmop__dmy)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        gswz__vkmf = flmop__dmy._compiler
        flags = compiler.Flags()
        bxr__lyx = gswz__vkmf.targetdescr.typing_context
        dxpd__mzg = gswz__vkmf.targetdescr.target_context
        nnmye__vqz = gswz__vkmf.pipeline_class(bxr__lyx, dxpd__mzg, None,
            None, None, flags, None)
        qght__cxkpu = InlineWorker(bxr__lyx, dxpd__mzg, gswz__vkmf.locals,
            nnmye__vqz, flags, None)
        dziq__zeda = iaixd__gprv.dispatcher.get_call_template
        lzoys__jydh, wridq__wyt, cbb__psxlk, kws = dziq__zeda(gvkdh__kdvin, kws
            )
        if cbb__psxlk in self._inline_overloads:
            return self._inline_overloads[cbb__psxlk]['iinfo'].signature
        ir = qght__cxkpu.run_untyped_passes(iaixd__gprv.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, dxpd__mzg, ir, cbb__psxlk, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, cbb__psxlk, None)
        self._inline_overloads[sig.args] = {'folded_args': cbb__psxlk}
        cgiqw__iavc = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = cgiqw__iavc
        if not self._inline.is_always_inline:
            sig = iaixd__gprv.get_call_type(self.context, gvkdh__kdvin, kws)
            self._compiled_overloads[sig.args] = iaixd__gprv.get_overload(sig)
        ehlrs__kwowk = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': cbb__psxlk,
            'iinfo': ehlrs__kwowk}
    else:
        sig = iaixd__gprv.get_call_type(self.context, gvkdh__kdvin, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = iaixd__gprv.get_overload(sig)
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
    lkvlp__khub = [True, False]
    oabmp__kwc = [False, True]
    forqw__dwd = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    zmw__mkive = get_local_target(context)
    mvfil__idha = utils.order_by_target_specificity(zmw__mkive, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for gwk__flxn in mvfil__idha:
        vuixq__wrdr = gwk__flxn(context)
        zjl__skkp = lkvlp__khub if vuixq__wrdr.prefer_literal else oabmp__kwc
        zjl__skkp = [True] if getattr(vuixq__wrdr, '_no_unliteral', False
            ) else zjl__skkp
        for aggac__sgs in zjl__skkp:
            try:
                if aggac__sgs:
                    sig = vuixq__wrdr.apply(args, kws)
                else:
                    npxl__qju = tuple([_unlit_non_poison(a) for a in args])
                    mllr__mxcbp = {jmmtk__paej: _unlit_non_poison(
                        zhup__zhfx) for jmmtk__paej, zhup__zhfx in kws.items()}
                    sig = vuixq__wrdr.apply(npxl__qju, mllr__mxcbp)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    forqw__dwd.add_error(vuixq__wrdr, False, e, aggac__sgs)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = vuixq__wrdr.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    enk__fhze = getattr(vuixq__wrdr, 'cases', None)
                    if enk__fhze is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            enk__fhze)
                    else:
                        msg = 'No match.'
                    forqw__dwd.add_error(vuixq__wrdr, True, msg, aggac__sgs)
    forqw__dwd.raise_error()


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
    lzoys__jydh = self.template(context)
    wzzu__ioi = None
    jdej__qniwp = None
    ogjp__tpsgw = None
    zjl__skkp = [True, False] if lzoys__jydh.prefer_literal else [False, True]
    zjl__skkp = [True] if getattr(lzoys__jydh, '_no_unliteral', False
        ) else zjl__skkp
    for aggac__sgs in zjl__skkp:
        if aggac__sgs:
            try:
                ogjp__tpsgw = lzoys__jydh.apply(args, kws)
            except Exception as fnbg__pzaal:
                if isinstance(fnbg__pzaal, errors.ForceLiteralArg):
                    raise fnbg__pzaal
                wzzu__ioi = fnbg__pzaal
                ogjp__tpsgw = None
            else:
                break
        else:
            suzvb__giyo = tuple([_unlit_non_poison(a) for a in args])
            eozr__ujja = {jmmtk__paej: _unlit_non_poison(zhup__zhfx) for 
                jmmtk__paej, zhup__zhfx in kws.items()}
            qyj__ufbgn = suzvb__giyo == args and kws == eozr__ujja
            if not qyj__ufbgn and ogjp__tpsgw is None:
                try:
                    ogjp__tpsgw = lzoys__jydh.apply(suzvb__giyo, eozr__ujja)
                except Exception as fnbg__pzaal:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        fnbg__pzaal, errors.NumbaError):
                        raise fnbg__pzaal
                    if isinstance(fnbg__pzaal, errors.ForceLiteralArg):
                        if lzoys__jydh.prefer_literal:
                            raise fnbg__pzaal
                    jdej__qniwp = fnbg__pzaal
                else:
                    break
    if ogjp__tpsgw is None and (jdej__qniwp is not None or wzzu__ioi is not
        None):
        abni__fso = '- Resolution failure for {} arguments:\n{}\n'
        vuvc__vdviz = _termcolor.highlight(abni__fso)
        if numba.core.config.DEVELOPER_MODE:
            xibxe__fqilj = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    yfmh__awcb = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    yfmh__awcb = ['']
                gprog__pahk = '\n{}'.format(2 * xibxe__fqilj)
                glx__ygphw = _termcolor.reset(gprog__pahk + gprog__pahk.
                    join(_bt_as_lines(yfmh__awcb)))
                return _termcolor.reset(glx__ygphw)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            aigc__mjywy = str(e)
            aigc__mjywy = aigc__mjywy if aigc__mjywy else str(repr(e)
                ) + add_bt(e)
            kmy__tkej = errors.TypingError(textwrap.dedent(aigc__mjywy))
            return vuvc__vdviz.format(literalness, str(kmy__tkej))
        import bodo
        if isinstance(wzzu__ioi, bodo.utils.typing.BodoError):
            raise wzzu__ioi
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', wzzu__ioi) +
                nested_msg('non-literal', jdej__qniwp))
        else:
            if 'missing a required argument' in wzzu__ioi.msg:
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
            raise errors.TypingError(msg, loc=wzzu__ioi.loc)
    return ogjp__tpsgw


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
    uqw__dnei = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=uqw__dnei)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            fzfjm__lpp = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), fzfjm__lpp)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    ixwok__icdob = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            ixwok__icdob.append(types.Omitted(a.value))
        else:
            ixwok__icdob.append(self.typeof_pyval(a))
    ufyu__hmr = None
    try:
        error = None
        ufyu__hmr = self.compile(tuple(ixwok__icdob))
    except errors.ForceLiteralArg as e:
        bdocp__xdbck = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if bdocp__xdbck:
            haivn__dadh = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            sefu__bbpb = ', '.join('Arg #{} is {}'.format(i, args[i]) for i in
                sorted(bdocp__xdbck))
            raise errors.CompilerError(haivn__dadh.format(sefu__bbpb))
        gvkdh__kdvin = []
        try:
            for i, zhup__zhfx in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        gvkdh__kdvin.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        gvkdh__kdvin.append(types.literal(args[i]))
                else:
                    gvkdh__kdvin.append(args[i])
            args = gvkdh__kdvin
        except (OSError, FileNotFoundError) as wto__ixfv:
            error = FileNotFoundError(str(wto__ixfv) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                ufyu__hmr = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        igvd__vug = []
        for i, roia__buo in enumerate(args):
            val = roia__buo.value if isinstance(roia__buo, numba.core.
                dispatcher.OmittedArg) else roia__buo
            try:
                bss__adv = typeof(val, Purpose.argument)
            except ValueError as auyev__iguyq:
                igvd__vug.append((i, str(auyev__iguyq)))
            else:
                if bss__adv is None:
                    igvd__vug.append((i,
                        f'cannot determine Numba type of value {val}'))
        if igvd__vug:
            yrwf__kql = '\n'.join(f'- argument {i}: {iqlsn__vwvti}' for i,
                iqlsn__vwvti in igvd__vug)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{yrwf__kql}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                vaso__oih = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                lww__chjj = False
                for thgaf__zums in vaso__oih:
                    if thgaf__zums in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        lww__chjj = True
                        break
                if not lww__chjj:
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
                fzfjm__lpp = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), fzfjm__lpp)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return ufyu__hmr


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
    for qmlp__bhz in cres.library._codegen._engine._defined_symbols:
        if qmlp__bhz.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in qmlp__bhz and (
            'bodo_gb_udf_update_local' in qmlp__bhz or 
            'bodo_gb_udf_combine' in qmlp__bhz or 'bodo_gb_udf_eval' in
            qmlp__bhz or 'bodo_gb_apply_general_udfs' in qmlp__bhz):
            gb_agg_cfunc_addr[qmlp__bhz
                ] = cres.library.get_pointer_to_function(qmlp__bhz)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for qmlp__bhz in cres.library._codegen._engine._defined_symbols:
        if qmlp__bhz.startswith('cfunc') and ('get_join_cond_addr' not in
            qmlp__bhz or 'bodo_join_gen_cond' in qmlp__bhz):
            join_gen_cond_cfunc_addr[qmlp__bhz
                ] = cres.library.get_pointer_to_function(qmlp__bhz)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    flmop__dmy = self._get_dispatcher_for_current_target()
    if flmop__dmy is not self:
        return flmop__dmy.compile(sig)
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
            atwjm__livs = self.overloads.get(tuple(args))
            if atwjm__livs is not None:
                return atwjm__livs.entry_point
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
            rnxgi__hyz = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=rnxgi__hyz):
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
                lqxs__bsep = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in lqxs__bsep:
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
    accz__ustw = self._final_module
    sla__drgyy = []
    anea__fuyp = 0
    for fn in accz__ustw.functions:
        anea__fuyp += 1
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
            sla__drgyy.append(fn.name)
    if anea__fuyp == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if sla__drgyy:
        accz__ustw = accz__ustw.clone()
        for name in sla__drgyy:
            accz__ustw.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = accz__ustw
    return accz__ustw


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
    for oknr__vxjjk in self.constraints:
        loc = oknr__vxjjk.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                oknr__vxjjk(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                xfmck__yimi = numba.core.errors.TypingError(str(e), loc=
                    oknr__vxjjk.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(xfmck__yimi, e))
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
                    xfmck__yimi = numba.core.errors.TypingError(msg.format(
                        con=oknr__vxjjk, err=str(e)), loc=oknr__vxjjk.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(xfmck__yimi, e))
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
    for daf__uyeug in self._failures.values():
        for hehcs__dmof in daf__uyeug:
            if isinstance(hehcs__dmof.error, ForceLiteralArg):
                raise hehcs__dmof.error
            if isinstance(hehcs__dmof.error, bodo.utils.typing.BodoError):
                raise hehcs__dmof.error
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
    mra__dvns = False
    dey__bzy = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        dvmxt__jweia = set()
        xvtss__oqb = lives & alias_set
        for zhup__zhfx in xvtss__oqb:
            dvmxt__jweia |= alias_map[zhup__zhfx]
        lives_n_aliases = lives | dvmxt__jweia | arg_aliases
        if type(stmt) in remove_dead_extensions:
            zll__fwa = remove_dead_extensions[type(stmt)]
            stmt = zll__fwa(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                mra__dvns = True
                continue
        if isinstance(stmt, ir.Assign):
            bcr__otqmn = stmt.target
            mitt__ozgt = stmt.value
            if bcr__otqmn.name not in lives:
                if has_no_side_effect(mitt__ozgt, lives_n_aliases, call_table):
                    mra__dvns = True
                    continue
                if isinstance(mitt__ozgt, ir.Expr
                    ) and mitt__ozgt.op == 'call' and call_table[mitt__ozgt
                    .func.name] == ['astype']:
                    wbkn__xtdf = guard(get_definition, func_ir, mitt__ozgt.func
                        )
                    if (wbkn__xtdf is not None and wbkn__xtdf.op ==
                        'getattr' and isinstance(typemap[wbkn__xtdf.value.
                        name], types.Array) and wbkn__xtdf.attr == 'astype'):
                        mra__dvns = True
                        continue
            if saved_array_analysis and bcr__otqmn.name in lives and is_expr(
                mitt__ozgt, 'getattr'
                ) and mitt__ozgt.attr == 'shape' and is_array_typ(typemap[
                mitt__ozgt.value.name]) and mitt__ozgt.value.name not in lives:
                qqva__rmq = {zhup__zhfx: jmmtk__paej for jmmtk__paej,
                    zhup__zhfx in func_ir.blocks.items()}
                if block in qqva__rmq:
                    label = qqva__rmq[block]
                    axt__yzhir = saved_array_analysis.get_equiv_set(label)
                    ojvzd__jye = axt__yzhir.get_equiv_set(mitt__ozgt.value)
                    if ojvzd__jye is not None:
                        for zhup__zhfx in ojvzd__jye:
                            if zhup__zhfx.endswith('#0'):
                                zhup__zhfx = zhup__zhfx[:-2]
                            if zhup__zhfx in typemap and is_array_typ(typemap
                                [zhup__zhfx]) and zhup__zhfx in lives:
                                mitt__ozgt.value = ir.Var(mitt__ozgt.value.
                                    scope, zhup__zhfx, mitt__ozgt.value.loc)
                                mra__dvns = True
                                break
            if isinstance(mitt__ozgt, ir.Var
                ) and bcr__otqmn.name == mitt__ozgt.name:
                mra__dvns = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                mra__dvns = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            zffj__geotx = analysis.ir_extension_usedefs[type(stmt)]
            wuxaf__ntcd, xoy__oxn = zffj__geotx(stmt)
            lives -= xoy__oxn
            lives |= wuxaf__ntcd
        else:
            lives |= {zhup__zhfx.name for zhup__zhfx in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                rel__edi = set()
                if isinstance(mitt__ozgt, ir.Expr):
                    rel__edi = {zhup__zhfx.name for zhup__zhfx in
                        mitt__ozgt.list_vars()}
                if bcr__otqmn.name not in rel__edi:
                    lives.remove(bcr__otqmn.name)
        dey__bzy.append(stmt)
    dey__bzy.reverse()
    block.body = dey__bzy
    return mra__dvns


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            ajlcs__hqly, = args
            if isinstance(ajlcs__hqly, types.IterableType):
                dtype = ajlcs__hqly.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), ajlcs__hqly)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    brtr__nwb = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (brtr__nwb, self.dtype)
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
        except LiteralTypingError as xymx__iyvf:
            return
    try:
        return literal(value)
    except LiteralTypingError as xymx__iyvf:
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
        oemr__dgznd = py_func.__qualname__
    except AttributeError as xymx__iyvf:
        oemr__dgznd = py_func.__name__
    kfvve__ofcwv = inspect.getfile(py_func)
    for cls in self._locator_classes:
        tyg__tycpa = cls.from_function(py_func, kfvve__ofcwv)
        if tyg__tycpa is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (oemr__dgznd, kfvve__ofcwv))
    self._locator = tyg__tycpa
    hecop__ywuj = inspect.getfile(py_func)
    esiz__kuv = os.path.splitext(os.path.basename(hecop__ywuj))[0]
    if kfvve__ofcwv.startswith('<ipython-'):
        hwuu__zsnfw = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', esiz__kuv, count=1)
        if hwuu__zsnfw == esiz__kuv:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        esiz__kuv = hwuu__zsnfw
    fktt__wpf = '%s.%s' % (esiz__kuv, oemr__dgznd)
    sueqk__pvy = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(fktt__wpf, sueqk__pvy
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    admf__qsjzf = list(filter(lambda a: self._istuple(a.name), args))
    if len(admf__qsjzf) == 2 and fn.__name__ == 'add':
        vyolq__cte = self.typemap[admf__qsjzf[0].name]
        feg__qvh = self.typemap[admf__qsjzf[1].name]
        if vyolq__cte.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                admf__qsjzf[1]))
        if feg__qvh.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                admf__qsjzf[0]))
        try:
            carl__hjc = [equiv_set.get_shape(x) for x in admf__qsjzf]
            if None in carl__hjc:
                return None
            nyig__mjj = sum(carl__hjc, ())
            return ArrayAnalysis.AnalyzeResult(shape=nyig__mjj)
        except GuardException as xymx__iyvf:
            return None
    hce__hlnoo = list(filter(lambda a: self._isarray(a.name), args))
    require(len(hce__hlnoo) > 0)
    oadyw__pzaus = [x.name for x in hce__hlnoo]
    efoqz__nfd = [self.typemap[x.name].ndim for x in hce__hlnoo]
    kqbf__rtsqc = max(efoqz__nfd)
    require(kqbf__rtsqc > 0)
    carl__hjc = [equiv_set.get_shape(x) for x in hce__hlnoo]
    if any(a is None for a in carl__hjc):
        return ArrayAnalysis.AnalyzeResult(shape=hce__hlnoo[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, hce__hlnoo))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, carl__hjc,
        oadyw__pzaus)


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
    aggp__lmi = code_obj.code
    flfl__rnh = len(aggp__lmi.co_freevars)
    ijtz__lyzgi = aggp__lmi.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        fzuam__kid, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ijtz__lyzgi = [zhup__zhfx.name for zhup__zhfx in fzuam__kid]
    uempf__bap = caller_ir.func_id.func.__globals__
    try:
        uempf__bap = getattr(code_obj, 'globals', uempf__bap)
    except KeyError as xymx__iyvf:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    ghyg__zbxu = []
    for x in ijtz__lyzgi:
        try:
            ximc__ogj = caller_ir.get_definition(x)
        except KeyError as xymx__iyvf:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(ximc__ogj, (ir.Const, ir.Global, ir.FreeVar)):
            val = ximc__ogj.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                khrj__rttfb = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                uempf__bap[khrj__rttfb] = bodo.jit(distributed=False)(val)
                uempf__bap[khrj__rttfb].is_nested_func = True
                val = khrj__rttfb
            if isinstance(val, CPUDispatcher):
                khrj__rttfb = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                uempf__bap[khrj__rttfb] = val
                val = khrj__rttfb
            ghyg__zbxu.append(val)
        elif isinstance(ximc__ogj, ir.Expr
            ) and ximc__ogj.op == 'make_function':
            sdmw__sxres = convert_code_obj_to_function(ximc__ogj, caller_ir)
            khrj__rttfb = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            uempf__bap[khrj__rttfb] = bodo.jit(distributed=False)(sdmw__sxres)
            uempf__bap[khrj__rttfb].is_nested_func = True
            ghyg__zbxu.append(khrj__rttfb)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    izgd__qpp = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        ghyg__zbxu)])
    qba__lbxp = ','.join([('c_%d' % i) for i in range(flfl__rnh)])
    zvq__oohqn = list(aggp__lmi.co_varnames)
    dimw__rwqfp = 0
    vnq__fyex = aggp__lmi.co_argcount
    vovn__lqu = caller_ir.get_definition(code_obj.defaults)
    if vovn__lqu is not None:
        if isinstance(vovn__lqu, tuple):
            d = [caller_ir.get_definition(x).value for x in vovn__lqu]
            xwqlc__iyyt = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in vovn__lqu.items]
            xwqlc__iyyt = tuple(d)
        dimw__rwqfp = len(xwqlc__iyyt)
    uxbrx__wwzs = vnq__fyex - dimw__rwqfp
    awq__qjstv = ','.join([('%s' % zvq__oohqn[i]) for i in range(uxbrx__wwzs)])
    if dimw__rwqfp:
        yjyc__ibokp = [('%s = %s' % (zvq__oohqn[i + uxbrx__wwzs],
            xwqlc__iyyt[i])) for i in range(dimw__rwqfp)]
        awq__qjstv += ', '
        awq__qjstv += ', '.join(yjyc__ibokp)
    return _create_function_from_code_obj(aggp__lmi, izgd__qpp, awq__qjstv,
        qba__lbxp, uempf__bap)


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
    for byb__lqmmg, (pcwe__daxf, zkm__kohd) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % zkm__kohd)
            kygqf__tvb = _pass_registry.get(pcwe__daxf).pass_inst
            if isinstance(kygqf__tvb, CompilerPass):
                self._runPass(byb__lqmmg, kygqf__tvb, state)
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
                    pipeline_name, zkm__kohd)
                segyi__nxmn = self._patch_error(msg, e)
                raise segyi__nxmn
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
    ovqod__idf = None
    xoy__oxn = {}

    def lookup(var, already_seen, varonly=True):
        val = xoy__oxn.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    ksehr__kpl = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        bcr__otqmn = stmt.target
        mitt__ozgt = stmt.value
        xoy__oxn[bcr__otqmn.name] = mitt__ozgt
        if isinstance(mitt__ozgt, ir.Var) and mitt__ozgt.name in xoy__oxn:
            mitt__ozgt = lookup(mitt__ozgt, set())
        if isinstance(mitt__ozgt, ir.Expr):
            vzjnw__lfaa = set(lookup(zhup__zhfx, set(), True).name for
                zhup__zhfx in mitt__ozgt.list_vars())
            if name in vzjnw__lfaa:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(mitt__ozgt)]
                yujye__zefgu = [x for x, sioa__dnuns in args if sioa__dnuns
                    .name != name]
                args = [(x, sioa__dnuns) for x, sioa__dnuns in args if x !=
                    sioa__dnuns.name]
                toqf__nied = dict(args)
                if len(yujye__zefgu) == 1:
                    toqf__nied[yujye__zefgu[0]] = ir.Var(bcr__otqmn.scope, 
                        name + '#init', bcr__otqmn.loc)
                replace_vars_inner(mitt__ozgt, toqf__nied)
                ovqod__idf = nodes[i:]
                break
    return ovqod__idf


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
        ofa__xsz = expand_aliases({zhup__zhfx.name for zhup__zhfx in stmt.
            list_vars()}, alias_map, arg_aliases)
        qyzii__aoz = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        lpofn__ioap = expand_aliases({zhup__zhfx.name for zhup__zhfx in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        rli__cpe = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(qyzii__aoz & lpofn__ioap | rli__cpe & ofa__xsz) == 0:
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
    dgi__zdk = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            dgi__zdk.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                dgi__zdk.update(get_parfor_writes(stmt, func_ir))
    return dgi__zdk


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    dgi__zdk = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        dgi__zdk.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        dgi__zdk = {zhup__zhfx.name for zhup__zhfx in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        dgi__zdk = {zhup__zhfx.name for zhup__zhfx in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            dgi__zdk.update({zhup__zhfx.name for zhup__zhfx in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        tvbs__rhody = guard(find_callname, func_ir, stmt.value)
        if tvbs__rhody in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            dgi__zdk.add(stmt.value.args[0].name)
        if tvbs__rhody == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            dgi__zdk.add(stmt.value.args[1].name)
    return dgi__zdk


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
        zll__fwa = _termcolor.errmsg('{0}') + _termcolor.filename('During: {1}'
            )
        tlfz__vadsx = zll__fwa.format(self, msg)
        self.args = tlfz__vadsx,
    else:
        zll__fwa = _termcolor.errmsg('{0}')
        tlfz__vadsx = zll__fwa.format(self)
        self.args = tlfz__vadsx,
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
        for skqb__evzm in options['distributed']:
            dist_spec[skqb__evzm] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for skqb__evzm in options['distributed_block']:
            dist_spec[skqb__evzm] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    xmx__ilbci = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, zts__tvr in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(zts__tvr)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    iov__otgqv = {}
    for smsi__qwcq in reversed(inspect.getmro(cls)):
        iov__otgqv.update(smsi__qwcq.__dict__)
    qbzt__sgz, mueqm__siypg, laj__dke, epw__ebon = {}, {}, {}, {}
    for jmmtk__paej, zhup__zhfx in iov__otgqv.items():
        if isinstance(zhup__zhfx, pytypes.FunctionType):
            qbzt__sgz[jmmtk__paej] = zhup__zhfx
        elif isinstance(zhup__zhfx, property):
            mueqm__siypg[jmmtk__paej] = zhup__zhfx
        elif isinstance(zhup__zhfx, staticmethod):
            laj__dke[jmmtk__paej] = zhup__zhfx
        else:
            epw__ebon[jmmtk__paej] = zhup__zhfx
    jxd__its = (set(qbzt__sgz) | set(mueqm__siypg) | set(laj__dke)) & set(spec)
    if jxd__its:
        raise NameError('name shadowing: {0}'.format(', '.join(jxd__its)))
    cun__wiqpb = epw__ebon.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(epw__ebon)
    if epw__ebon:
        msg = 'class members are not yet supported: {0}'
        odywr__mlo = ', '.join(epw__ebon.keys())
        raise TypeError(msg.format(odywr__mlo))
    for jmmtk__paej, zhup__zhfx in mueqm__siypg.items():
        if zhup__zhfx.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(jmmtk__paej)
                )
    jit_methods = {jmmtk__paej: bodo.jit(returns_maybe_distributed=
        xmx__ilbci)(zhup__zhfx) for jmmtk__paej, zhup__zhfx in qbzt__sgz.
        items()}
    jit_props = {}
    for jmmtk__paej, zhup__zhfx in mueqm__siypg.items():
        ytpvf__fvgkq = {}
        if zhup__zhfx.fget:
            ytpvf__fvgkq['get'] = bodo.jit(zhup__zhfx.fget)
        if zhup__zhfx.fset:
            ytpvf__fvgkq['set'] = bodo.jit(zhup__zhfx.fset)
        jit_props[jmmtk__paej] = ytpvf__fvgkq
    jit_static_methods = {jmmtk__paej: bodo.jit(zhup__zhfx.__func__) for 
        jmmtk__paej, zhup__zhfx in laj__dke.items()}
    jif__kriy = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    ilul__sogw = dict(class_type=jif__kriy, __doc__=cun__wiqpb)
    ilul__sogw.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), ilul__sogw)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, jif__kriy)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(jif__kriy, typingctx, targetctx).register()
    as_numba_type.register(cls, jif__kriy.instance_type)
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
    woeuh__nscwv = ','.join('{0}:{1}'.format(jmmtk__paej, zhup__zhfx) for 
        jmmtk__paej, zhup__zhfx in struct.items())
    dop__pholq = ','.join('{0}:{1}'.format(jmmtk__paej, zhup__zhfx) for 
        jmmtk__paej, zhup__zhfx in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), woeuh__nscwv, dop__pholq)
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
    sijr__nhx = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if sijr__nhx is None:
        return
    htm__qwlqm, dwea__nfm = sijr__nhx
    for a in itertools.chain(htm__qwlqm, dwea__nfm.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, htm__qwlqm, dwea__nfm)
    except ForceLiteralArg as e:
        kqrwt__wkc = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(kqrwt__wkc, self.kws)
        lwczy__ybra = set()
        vfwoy__uyqz = set()
        nuccm__dad = {}
        for byb__lqmmg in e.requested_args:
            zfvl__dnh = typeinfer.func_ir.get_definition(folded[byb__lqmmg])
            if isinstance(zfvl__dnh, ir.Arg):
                lwczy__ybra.add(zfvl__dnh.index)
                if zfvl__dnh.index in e.file_infos:
                    nuccm__dad[zfvl__dnh.index] = e.file_infos[zfvl__dnh.index]
            else:
                vfwoy__uyqz.add(byb__lqmmg)
        if vfwoy__uyqz:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif lwczy__ybra:
            raise ForceLiteralArg(lwczy__ybra, loc=self.loc, file_infos=
                nuccm__dad)
    if sig is None:
        fgqpx__qkxnr = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in htm__qwlqm]
        args += [('%s=%s' % (jmmtk__paej, zhup__zhfx)) for jmmtk__paej,
            zhup__zhfx in sorted(dwea__nfm.items())]
        llb__krfzk = fgqpx__qkxnr.format(fnty, ', '.join(map(str, args)))
        nmrdx__wazc = context.explain_function_type(fnty)
        msg = '\n'.join([llb__krfzk, nmrdx__wazc])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        ics__icb = context.unify_pairs(sig.recvr, fnty.this)
        if ics__icb is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if ics__icb is not None and ics__icb.is_precise():
            wbumw__qoz = fnty.copy(this=ics__icb)
            typeinfer.propagate_refined_type(self.func, wbumw__qoz)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            pmbwa__inv = target.getone()
            if context.unify_pairs(pmbwa__inv, sig.return_type) == pmbwa__inv:
                sig = sig.replace(return_type=pmbwa__inv)
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
        haivn__dadh = '*other* must be a {} but got a {} instead'
        raise TypeError(haivn__dadh.format(ForceLiteralArg, type(other)))
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
    fvku__fhkme = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for jmmtk__paej, zhup__zhfx in kwargs.items():
        uen__xhu = None
        try:
            wkmto__hfiu = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[wkmto__hfiu.name] = [zhup__zhfx]
            uen__xhu = get_const_value_inner(func_ir, wkmto__hfiu)
            func_ir._definitions.pop(wkmto__hfiu.name)
            if isinstance(uen__xhu, str):
                uen__xhu = sigutils._parse_signature_string(uen__xhu)
            if isinstance(uen__xhu, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {jmmtk__paej} is annotated as type class {uen__xhu}."""
                    )
            assert isinstance(uen__xhu, types.Type)
            if isinstance(uen__xhu, (types.List, types.Set)):
                uen__xhu = uen__xhu.copy(reflected=False)
            fvku__fhkme[jmmtk__paej] = uen__xhu
        except BodoError as xymx__iyvf:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(uen__xhu, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(zhup__zhfx, ir.Global):
                    msg = f'Global {zhup__zhfx.name!r} is not defined.'
                if isinstance(zhup__zhfx, ir.FreeVar):
                    msg = f'Freevar {zhup__zhfx.name!r} is not defined.'
            if isinstance(zhup__zhfx, ir.Expr) and zhup__zhfx.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=jmmtk__paej, msg=msg, loc=loc)
    for name, typ in fvku__fhkme.items():
        self._legalize_arg_type(name, typ, loc)
    return fvku__fhkme


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
    evox__vcl = inst.arg
    assert evox__vcl > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(evox__vcl)]))
    tmps = [state.make_temp() for _ in range(evox__vcl - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    ojh__eef = ir.Global('format', format, loc=self.loc)
    self.store(value=ojh__eef, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    lwuh__qnkb = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=lwuh__qnkb, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    evox__vcl = inst.arg
    assert evox__vcl > 0, 'invalid BUILD_STRING count'
    wxez__ewo = self.get(strings[0])
    for other, gyil__uuiyr in zip(strings[1:], tmps):
        other = self.get(other)
        ksb__wvq = ir.Expr.binop(operator.add, lhs=wxez__ewo, rhs=other,
            loc=self.loc)
        self.store(ksb__wvq, gyil__uuiyr)
        wxez__ewo = self.get(gyil__uuiyr)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    ygti__ien = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, ygti__ien])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    ergj__uvh = mk_unique_var(f'{var_name}')
    wrbvu__bxzhw = ergj__uvh.replace('<', '_').replace('>', '_')
    wrbvu__bxzhw = wrbvu__bxzhw.replace('.', '_').replace('$', '_v')
    return wrbvu__bxzhw


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
                vkc__pqu = get_overload_const_str(val2)
                if vkc__pqu != 'ns':
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
        oencv__fhxa = states['defmap']
        if len(oencv__fhxa) == 0:
            sumrn__irbho = assign.target
            numba.core.ssa._logger.debug('first assign: %s', sumrn__irbho)
            if sumrn__irbho.name not in scope.localvars:
                sumrn__irbho = scope.define(assign.target.name, loc=assign.loc)
        else:
            sumrn__irbho = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=sumrn__irbho, value=assign.value, loc=
            assign.loc)
        oencv__fhxa[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    hnhe__crah = []
    for jmmtk__paej, zhup__zhfx in typing.npydecl.registry.globals:
        if jmmtk__paej == func:
            hnhe__crah.append(zhup__zhfx)
    for jmmtk__paej, zhup__zhfx in typing.templates.builtin_registry.globals:
        if jmmtk__paej == func:
            hnhe__crah.append(zhup__zhfx)
    if len(hnhe__crah) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return hnhe__crah


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    rhtcm__qkmmi = {}
    fxwmn__tqt = find_topo_order(blocks)
    oyel__wext = {}
    for label in fxwmn__tqt:
        block = blocks[label]
        dey__bzy = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                bcr__otqmn = stmt.target.name
                mitt__ozgt = stmt.value
                if (mitt__ozgt.op == 'getattr' and mitt__ozgt.attr in
                    arr_math and isinstance(typemap[mitt__ozgt.value.name],
                    types.npytypes.Array)):
                    mitt__ozgt = stmt.value
                    vbrah__agvl = mitt__ozgt.value
                    rhtcm__qkmmi[bcr__otqmn] = vbrah__agvl
                    scope = vbrah__agvl.scope
                    loc = vbrah__agvl.loc
                    ncyx__jcug = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[ncyx__jcug.name] = types.misc.Module(numpy)
                    tkyxq__phgd = ir.Global('np', numpy, loc)
                    ewm__eqo = ir.Assign(tkyxq__phgd, ncyx__jcug, loc)
                    mitt__ozgt.value = ncyx__jcug
                    dey__bzy.append(ewm__eqo)
                    func_ir._definitions[ncyx__jcug.name] = [tkyxq__phgd]
                    func = getattr(numpy, mitt__ozgt.attr)
                    csevn__hqi = get_np_ufunc_typ_lst(func)
                    oyel__wext[bcr__otqmn] = csevn__hqi
                if (mitt__ozgt.op == 'call' and mitt__ozgt.func.name in
                    rhtcm__qkmmi):
                    vbrah__agvl = rhtcm__qkmmi[mitt__ozgt.func.name]
                    bfmjl__anzf = calltypes.pop(mitt__ozgt)
                    ugd__yhyuy = bfmjl__anzf.args[:len(mitt__ozgt.args)]
                    vmi__qwz = {name: typemap[zhup__zhfx.name] for name,
                        zhup__zhfx in mitt__ozgt.kws}
                    pzmrk__brbh = oyel__wext[mitt__ozgt.func.name]
                    cpqg__tjsiq = None
                    for lyb__axeda in pzmrk__brbh:
                        try:
                            cpqg__tjsiq = lyb__axeda.get_call_type(typingctx,
                                [typemap[vbrah__agvl.name]] + list(
                                ugd__yhyuy), vmi__qwz)
                            typemap.pop(mitt__ozgt.func.name)
                            typemap[mitt__ozgt.func.name] = lyb__axeda
                            calltypes[mitt__ozgt] = cpqg__tjsiq
                            break
                        except Exception as xymx__iyvf:
                            pass
                    if cpqg__tjsiq is None:
                        raise TypeError(
                            f'No valid template found for {mitt__ozgt.func.name}'
                            )
                    mitt__ozgt.args = [vbrah__agvl] + mitt__ozgt.args
            dey__bzy.append(stmt)
        block.body = dey__bzy


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    wzb__mnvyr = ufunc.nin
    ealab__yiwjm = ufunc.nout
    uxbrx__wwzs = ufunc.nargs
    assert uxbrx__wwzs == wzb__mnvyr + ealab__yiwjm
    if len(args) < wzb__mnvyr:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), wzb__mnvyr)
            )
    if len(args) > uxbrx__wwzs:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            uxbrx__wwzs))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    tat__iivu = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    qga__rsxoa = max(tat__iivu)
    gor__mms = args[wzb__mnvyr:]
    if not all(d == qga__rsxoa for d in tat__iivu[wzb__mnvyr:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(mdjk__uah, types.ArrayCompatible) and not
        isinstance(mdjk__uah, types.Bytes) for mdjk__uah in gor__mms):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(mdjk__uah.mutable for mdjk__uah in gor__mms):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    vnhsx__zgws = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    ftqk__toseb = None
    if qga__rsxoa > 0 and len(gor__mms) < ufunc.nout:
        ftqk__toseb = 'C'
        cgji__mphp = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in cgji__mphp and 'F' in cgji__mphp:
            ftqk__toseb = 'F'
    return vnhsx__zgws, gor__mms, qga__rsxoa, ftqk__toseb


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
        cat__ektsc = 'Dict.key_type cannot be of type {}'
        raise TypingError(cat__ektsc.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        cat__ektsc = 'Dict.value_type cannot be of type {}'
        raise TypingError(cat__ektsc.format(valty))
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
    yyozr__vfel = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[yyozr__vfel]
        return impl, args
    except KeyError as xymx__iyvf:
        pass
    impl, args = self._build_impl(yyozr__vfel, args, kws)
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
    xusx__yxkip = False
    blocks = parfor.loop_body.copy()
    for label, block in blocks.items():
        if len(block.body):
            bvc__znayj = block.body[-1]
            if isinstance(bvc__znayj, ir.Branch):
                if len(blocks[bvc__znayj.truebr].body) == 1 and len(blocks[
                    bvc__znayj.falsebr].body) == 1:
                    yni__gnyqg = blocks[bvc__znayj.truebr].body[0]
                    jtyp__puza = blocks[bvc__znayj.falsebr].body[0]
                    if isinstance(yni__gnyqg, ir.Jump) and isinstance(
                        jtyp__puza, ir.Jump
                        ) and yni__gnyqg.target == jtyp__puza.target:
                        parfor.loop_body[label].body[-1] = ir.Jump(yni__gnyqg
                            .target, bvc__znayj.loc)
                        xusx__yxkip = True
                elif len(blocks[bvc__znayj.truebr].body) == 1:
                    yni__gnyqg = blocks[bvc__znayj.truebr].body[0]
                    if isinstance(yni__gnyqg, ir.Jump
                        ) and yni__gnyqg.target == bvc__znayj.falsebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(yni__gnyqg
                            .target, bvc__znayj.loc)
                        xusx__yxkip = True
                elif len(blocks[bvc__znayj.falsebr].body) == 1:
                    jtyp__puza = blocks[bvc__znayj.falsebr].body[0]
                    if isinstance(jtyp__puza, ir.Jump
                        ) and jtyp__puza.target == bvc__znayj.truebr:
                        parfor.loop_body[label].body[-1] = ir.Jump(jtyp__puza
                            .target, bvc__znayj.loc)
                        xusx__yxkip = True
    return xusx__yxkip


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        yhoqz__jxbp = find_topo_order(parfor.loop_body)
    bazb__jnje = yhoqz__jxbp[0]
    yns__qrep = {}
    _update_parfor_get_setitems(parfor.loop_body[bazb__jnje].body, parfor.
        index_var, alias_map, yns__qrep, lives_n_aliases)
    dkzr__lcdr = set(yns__qrep.keys())
    for vqvrq__grzaz in yhoqz__jxbp:
        if vqvrq__grzaz == bazb__jnje:
            continue
        for stmt in parfor.loop_body[vqvrq__grzaz].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            byqsq__fult = set(zhup__zhfx.name for zhup__zhfx in stmt.
                list_vars())
            wesj__xput = byqsq__fult & dkzr__lcdr
            for a in wesj__xput:
                yns__qrep.pop(a, None)
    for vqvrq__grzaz in yhoqz__jxbp:
        if vqvrq__grzaz == bazb__jnje:
            continue
        block = parfor.loop_body[vqvrq__grzaz]
        shcj__ier = yns__qrep.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            shcj__ier, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    wkfkx__tal = max(blocks.keys())
    ancj__vrg, ajq__fqmbd = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    feu__wfush = ir.Jump(ancj__vrg, ir.Loc('parfors_dummy', -1))
    blocks[wkfkx__tal].body.append(feu__wfush)
    ftbnx__vqjl = compute_cfg_from_blocks(blocks)
    ray__gbma = compute_use_defs(blocks)
    yjsn__ujxhp = compute_live_map(ftbnx__vqjl, blocks, ray__gbma.usemap,
        ray__gbma.defmap)
    alias_set = set(alias_map.keys())
    for label, block in blocks.items():
        dey__bzy = []
        ehfl__eyk = {zhup__zhfx.name for zhup__zhfx in block.terminator.
            list_vars()}
        for kbcd__ick, fstsa__knmx in ftbnx__vqjl.successors(label):
            ehfl__eyk |= yjsn__ujxhp[kbcd__ick]
        for stmt in reversed(block.body):
            dvmxt__jweia = ehfl__eyk & alias_set
            for zhup__zhfx in dvmxt__jweia:
                ehfl__eyk |= alias_map[zhup__zhfx]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in ehfl__eyk and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                tvbs__rhody = guard(find_callname, func_ir, stmt.value)
                if tvbs__rhody == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in ehfl__eyk and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            ehfl__eyk |= {zhup__zhfx.name for zhup__zhfx in stmt.list_vars()}
            dey__bzy.append(stmt)
        dey__bzy.reverse()
        block.body = dey__bzy
    typemap.pop(ajq__fqmbd.name)
    blocks[wkfkx__tal].body.pop()
    xusx__yxkip = True
    while xusx__yxkip:
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
        xusx__yxkip = trim_empty_parfor_branches(parfor)
    qwfbz__hncn = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        qwfbz__hncn &= len(block.body) == 0
    if qwfbz__hncn:
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
    hewuk__cgtef = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                hewuk__cgtef += 1
                parfor = stmt
                ukhan__ktqt = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = ukhan__ktqt.scope
                loc = ir.Loc('parfors_dummy', -1)
                gngn__wzy = ir.Var(scope, mk_unique_var('$const'), loc)
                ukhan__ktqt.body.append(ir.Assign(ir.Const(0, loc),
                    gngn__wzy, loc))
                ukhan__ktqt.body.append(ir.Return(gngn__wzy, loc))
                ftbnx__vqjl = compute_cfg_from_blocks(parfor.loop_body)
                for ritla__vrv in ftbnx__vqjl.dead_nodes():
                    del parfor.loop_body[ritla__vrv]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                ukhan__ktqt = parfor.loop_body[max(parfor.loop_body.keys())]
                ukhan__ktqt.body.pop()
                ukhan__ktqt.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return hewuk__cgtef


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def simplify_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import merge_adjacent_blocks, rename_labels
    ftbnx__vqjl = compute_cfg_from_blocks(blocks)

    def find_single_branch(label):
        block = blocks[label]
        return len(block.body) == 1 and isinstance(block.body[0], ir.Branch
            ) and label != ftbnx__vqjl.entry_point()
    pun__mqgg = list(filter(find_single_branch, blocks.keys()))
    kwiw__yvg = set()
    for label in pun__mqgg:
        inst = blocks[label].body[0]
        lmo__rrwvi = ftbnx__vqjl.predecessors(label)
        yxyi__lfk = True
        for bokj__hmlr, lcq__sucx in lmo__rrwvi:
            block = blocks[bokj__hmlr]
            if isinstance(block.body[-1], ir.Jump):
                block.body[-1] = copy.copy(inst)
            else:
                yxyi__lfk = False
        if yxyi__lfk:
            kwiw__yvg.add(label)
    for label in kwiw__yvg:
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
            atwjm__livs = self.overloads.get(tuple(args))
            if atwjm__livs is not None:
                return atwjm__livs.entry_point
            self._pre_compile(args, return_type, flags)
            lpozc__qdgjj = self.func_ir
            rnxgi__hyz = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=rnxgi__hyz):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=lpozc__qdgjj, args=
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
        pznzp__vep = copy.deepcopy(flags)
        pznzp__vep.no_rewrites = True

        def compile_local(the_ir, the_flags):
            revl__lvgn = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return revl__lvgn.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        kbdws__zedn = compile_local(func_ir, pznzp__vep)
        hogbr__fzqne = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    hogbr__fzqne = compile_local(func_ir, flags)
                except Exception as xymx__iyvf:
                    pass
        if hogbr__fzqne is not None:
            cres = hogbr__fzqne
        else:
            cres = kbdws__zedn
        return cres
    else:
        revl__lvgn = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return revl__lvgn.compile_ir(func_ir=func_ir, lifted=lifted,
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
    evke__rfquv = self.get_data_type(typ.dtype)
    ohil__auik = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        ohil__auik):
        rxrf__fkoix = ary.ctypes.data
        soaha__nbzx = self.add_dynamic_addr(builder, rxrf__fkoix, info=str(
            type(rxrf__fkoix)))
        gpde__uhxzw = self.add_dynamic_addr(builder, id(ary), info=str(type
            (ary)))
        self.global_arrays.append(ary)
    else:
        cls__hsu = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            cls__hsu = cls__hsu.view('int64')
        val = bytearray(cls__hsu.data)
        lbq__ewp = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        soaha__nbzx = cgutils.global_constant(builder, '.const.array.data',
            lbq__ewp)
        soaha__nbzx.align = self.get_abi_alignment(evke__rfquv)
        gpde__uhxzw = None
    seafp__zlhso = self.get_value_type(types.intp)
    fwp__vhie = [self.get_constant(types.intp, sjyx__sorzl) for sjyx__sorzl in
        ary.shape]
    vjrqo__vjtus = lir.Constant(lir.ArrayType(seafp__zlhso, len(fwp__vhie)),
        fwp__vhie)
    dofg__rmwd = [self.get_constant(types.intp, sjyx__sorzl) for
        sjyx__sorzl in ary.strides]
    vdixu__lpaex = lir.Constant(lir.ArrayType(seafp__zlhso, len(dofg__rmwd)
        ), dofg__rmwd)
    kzi__kamu = self.get_constant(types.intp, ary.dtype.itemsize)
    usw__dhf = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        usw__dhf, kzi__kamu, soaha__nbzx.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), vjrqo__vjtus, vdixu__lpaex])


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
    jpass__kckak = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    gzuw__ikpd = lir.Function(module, jpass__kckak, name='nrt_atomic_{0}'.
        format(op))
    [efhmt__smrsa] = gzuw__ikpd.args
    sjo__akkvy = gzuw__ikpd.append_basic_block()
    builder = lir.IRBuilder(sjo__akkvy)
    rnp__ayjrl = lir.Constant(_word_type, 1)
    if False:
        ektq__sjaq = builder.atomic_rmw(op, efhmt__smrsa, rnp__ayjrl,
            ordering=ordering)
        res = getattr(builder, op)(ektq__sjaq, rnp__ayjrl)
        builder.ret(res)
    else:
        ektq__sjaq = builder.load(efhmt__smrsa)
        gzxk__uvnct = getattr(builder, op)(ektq__sjaq, rnp__ayjrl)
        muxt__wjudf = builder.icmp_signed('!=', ektq__sjaq, lir.Constant(
            ektq__sjaq.type, -1))
        with cgutils.if_likely(builder, muxt__wjudf):
            builder.store(gzxk__uvnct, efhmt__smrsa)
        builder.ret(gzxk__uvnct)
    return gzuw__ikpd


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
        nwwq__ltdbb = state.targetctx.codegen()
        state.library = nwwq__ltdbb.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    plyyl__fxo = state.func_ir
    typemap = state.typemap
    ylaq__lhlj = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    lfp__usz = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            plyyl__fxo, typemap, ylaq__lhlj, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            rybap__gwnm = lowering.Lower(targetctx, library, fndesc,
                plyyl__fxo, metadata=metadata)
            rybap__gwnm.lower()
            if not flags.no_cpython_wrapper:
                rybap__gwnm.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(ylaq__lhlj, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        rybap__gwnm.create_cfunc_wrapper()
            env = rybap__gwnm.env
            ksj__ygt = rybap__gwnm.call_helper
            del rybap__gwnm
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, ksj__ygt, cfunc=None, env=env)
        else:
            pio__icg = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(pio__icg, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, ksj__ygt, cfunc=pio__icg,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        fjanp__qie = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = fjanp__qie - lfp__usz
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
        smn__wfmed = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, smn__wfmed),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            rslo__qlv.do_break()
        zvac__lbh = c.builder.icmp_signed('!=', smn__wfmed, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(zvac__lbh, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, smn__wfmed)
                c.pyapi.decref(smn__wfmed)
                rslo__qlv.do_break()
        c.pyapi.decref(smn__wfmed)
    rxzu__wugg, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(rxzu__wugg, likely=True) as (decv__fjqx, spq__gwq):
        with decv__fjqx:
            list.size = size
            big__hcj = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                big__hcj), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        big__hcj))
                    with cgutils.for_range(c.builder, size) as rslo__qlv:
                        itemobj = c.pyapi.list_getitem(obj, rslo__qlv.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        fwu__jesjl = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(fwu__jesjl.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            rslo__qlv.do_break()
                        list.setitem(rslo__qlv.index, fwu__jesjl.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with spq__gwq:
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
    jgko__eamp, chym__biagx, rvad__ckpir, qjxj__drhgn, jtg__lscyn = (
        compile_time_get_string_data(literal_string))
    accz__ustw = builder.module
    gv = context.insert_const_bytes(accz__ustw, jgko__eamp)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        chym__biagx), context.get_constant(types.int32, rvad__ckpir),
        context.get_constant(types.uint32, qjxj__drhgn), context.
        get_constant(_Py_hash_t, -1), context.get_constant_null(types.
        MemInfoPointer(types.voidptr)), context.get_constant_null(types.
        pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    fpyfg__moxqe = None
    if isinstance(shape, types.Integer):
        fpyfg__moxqe = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(sjyx__sorzl, (types.Integer, types.IntEnumMember)
            ) for sjyx__sorzl in shape):
            fpyfg__moxqe = len(shape)
    return fpyfg__moxqe


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
            fpyfg__moxqe = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if fpyfg__moxqe == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(
                    fpyfg__moxqe))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            oadyw__pzaus = self._get_names(x)
            if len(oadyw__pzaus) != 0:
                return oadyw__pzaus[0]
            return oadyw__pzaus
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    oadyw__pzaus = self._get_names(obj)
    if len(oadyw__pzaus) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(oadyw__pzaus[0])


def get_equiv_set(self, obj):
    oadyw__pzaus = self._get_names(obj)
    if len(oadyw__pzaus) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(oadyw__pzaus[0])


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
    tgq__jjx = []
    for zzqam__yrqqu in func_ir.arg_names:
        if zzqam__yrqqu in typemap and isinstance(typemap[zzqam__yrqqu],
            types.containers.UniTuple) and typemap[zzqam__yrqqu].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(zzqam__yrqqu))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for tviqp__mzcq in func_ir.blocks.values():
        for stmt in tviqp__mzcq.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    dcq__nru = getattr(val, 'code', None)
                    if dcq__nru is not None:
                        if getattr(val, 'closure', None) is not None:
                            arpf__otzfk = (
                                '<creating a function from a closure>')
                            ksb__wvq = ''
                        else:
                            arpf__otzfk = dcq__nru.co_name
                            ksb__wvq = '(%s) ' % arpf__otzfk
                    else:
                        arpf__otzfk = '<could not ascertain use case>'
                        ksb__wvq = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (arpf__otzfk, ksb__wvq))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                cfncp__avfzu = False
                if isinstance(val, pytypes.FunctionType):
                    cfncp__avfzu = val in {numba.gdb, numba.gdb_init}
                if not cfncp__avfzu:
                    cfncp__avfzu = getattr(val, '_name', '') == 'gdb_internal'
                if cfncp__avfzu:
                    tgq__jjx.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    gng__dvi = func_ir.get_definition(var)
                    eoow__mlz = guard(find_callname, func_ir, gng__dvi)
                    if eoow__mlz and eoow__mlz[1] == 'numpy':
                        ty = getattr(numpy, eoow__mlz[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    avxmo__ibflo = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(avxmo__ibflo), loc=stmt.loc)
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
    if len(tgq__jjx) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        zopdn__bru = '\n'.join([x.strformat() for x in tgq__jjx])
        raise errors.UnsupportedError(msg % zopdn__bru)


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
    jmmtk__paej, zhup__zhfx = next(iter(val.items()))
    sudc__bqzvu = typeof_impl(jmmtk__paej, c)
    owt__yxoh = typeof_impl(zhup__zhfx, c)
    if sudc__bqzvu is None or owt__yxoh is None:
        raise ValueError(
            f'Cannot type dict element type {type(jmmtk__paej)}, {type(zhup__zhfx)}'
            )
    return types.DictType(sudc__bqzvu, owt__yxoh)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    lvbsm__thkij = cgutils.alloca_once_value(c.builder, val)
    ndjy__fjqi = c.pyapi.object_hasattr_string(val, '_opaque')
    ovsl__ivfna = c.builder.icmp_unsigned('==', ndjy__fjqi, lir.Constant(
        ndjy__fjqi.type, 0))
    txl__znoa = typ.key_type
    vip__akru = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(txl__znoa, vip__akru)

    def copy_dict(out_dict, in_dict):
        for jmmtk__paej, zhup__zhfx in in_dict.items():
            out_dict[jmmtk__paej] = zhup__zhfx
    with c.builder.if_then(ovsl__ivfna):
        uauhq__jrms = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        efme__cjmab = c.pyapi.call_function_objargs(uauhq__jrms, [])
        ixl__ttve = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(ixl__ttve, [efme__cjmab, val])
        c.builder.store(efme__cjmab, lvbsm__thkij)
    val = c.builder.load(lvbsm__thkij)
    ctv__gyf = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    raa__uuj = c.pyapi.object_type(val)
    lcjj__kgn = c.builder.icmp_unsigned('==', raa__uuj, ctv__gyf)
    with c.builder.if_else(lcjj__kgn) as (knonm__iewlw, oww__hvl):
        with knonm__iewlw:
            qlkq__yxgw = c.pyapi.object_getattr_string(val, '_opaque')
            aqd__puak = types.MemInfoPointer(types.voidptr)
            fwu__jesjl = c.unbox(aqd__puak, qlkq__yxgw)
            mi = fwu__jesjl.value
            ixwok__icdob = aqd__puak, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *ixwok__icdob)
            xgpkg__kuor = context.get_constant_null(ixwok__icdob[1])
            args = mi, xgpkg__kuor
            qvzs__ygpr, dfjy__grfdo = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, dfjy__grfdo)
            c.pyapi.decref(qlkq__yxgw)
            pxe__fnymt = c.builder.basic_block
        with oww__hvl:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", raa__uuj, ctv__gyf)
            kpjrf__aoozf = c.builder.basic_block
    qmewv__ety = c.builder.phi(dfjy__grfdo.type)
    lzoj__dinpm = c.builder.phi(qvzs__ygpr.type)
    qmewv__ety.add_incoming(dfjy__grfdo, pxe__fnymt)
    qmewv__ety.add_incoming(dfjy__grfdo.type(None), kpjrf__aoozf)
    lzoj__dinpm.add_incoming(qvzs__ygpr, pxe__fnymt)
    lzoj__dinpm.add_incoming(cgutils.true_bit, kpjrf__aoozf)
    c.pyapi.decref(ctv__gyf)
    c.pyapi.decref(raa__uuj)
    with c.builder.if_then(ovsl__ivfna):
        c.pyapi.decref(val)
    return NativeValue(qmewv__ety, is_error=lzoj__dinpm)


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
    unx__ecte = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=unx__ecte, name=updatevar)
    yue__dgctg = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=yue__dgctg, name=res)


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
        for jmmtk__paej, zhup__zhfx in other.items():
            d[jmmtk__paej] = zhup__zhfx
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
    ksb__wvq = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(ksb__wvq, res)


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
    wzgng__kpjd = PassManager(name)
    if state.func_ir is None:
        wzgng__kpjd.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            wzgng__kpjd.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        wzgng__kpjd.add_pass(FixupArgs, 'fix up args')
    wzgng__kpjd.add_pass(IRProcessing, 'processing IR')
    wzgng__kpjd.add_pass(WithLifting, 'Handle with contexts')
    wzgng__kpjd.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        wzgng__kpjd.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        wzgng__kpjd.add_pass(DeadBranchPrune, 'dead branch pruning')
        wzgng__kpjd.add_pass(GenericRewrites, 'nopython rewrites')
    wzgng__kpjd.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    wzgng__kpjd.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        wzgng__kpjd.add_pass(DeadBranchPrune, 'dead branch pruning')
    wzgng__kpjd.add_pass(FindLiterallyCalls, 'find literally calls')
    wzgng__kpjd.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        wzgng__kpjd.add_pass(ReconstructSSA, 'ssa')
    wzgng__kpjd.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    wzgng__kpjd.finalize()
    return wzgng__kpjd


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
    a, ttrif__pqt = args
    if isinstance(a, types.List) and isinstance(ttrif__pqt, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(ttrif__pqt, types.List):
        return signature(ttrif__pqt, types.intp, ttrif__pqt)


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
        lpeic__lqml, dqx__lixa = 0, 1
    else:
        lpeic__lqml, dqx__lixa = 1, 0
    omp__wgi = ListInstance(context, builder, sig.args[lpeic__lqml], args[
        lpeic__lqml])
    byn__kcrc = omp__wgi.size
    tucbn__fwns = args[dqx__lixa]
    big__hcj = lir.Constant(tucbn__fwns.type, 0)
    tucbn__fwns = builder.select(cgutils.is_neg_int(builder, tucbn__fwns),
        big__hcj, tucbn__fwns)
    usw__dhf = builder.mul(tucbn__fwns, byn__kcrc)
    idwfi__nlq = ListInstance.allocate(context, builder, sig.return_type,
        usw__dhf)
    idwfi__nlq.size = usw__dhf
    with cgutils.for_range_slice(builder, big__hcj, usw__dhf, byn__kcrc,
        inc=True) as (dqqo__lqq, _):
        with cgutils.for_range(builder, byn__kcrc) as rslo__qlv:
            value = omp__wgi.getitem(rslo__qlv.index)
            idwfi__nlq.setitem(builder.add(rslo__qlv.index, dqqo__lqq),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, idwfi__nlq.value
        )


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
    wwx__zeqvc = first.unify(self, second)
    if wwx__zeqvc is not None:
        return wwx__zeqvc
    wwx__zeqvc = second.unify(self, first)
    if wwx__zeqvc is not None:
        return wwx__zeqvc
    fbe__tydt = self.can_convert(fromty=first, toty=second)
    if fbe__tydt is not None and fbe__tydt <= Conversion.safe:
        return second
    fbe__tydt = self.can_convert(fromty=second, toty=first)
    if fbe__tydt is not None and fbe__tydt <= Conversion.safe:
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
    usw__dhf = payload.used
    listobj = c.pyapi.list_new(usw__dhf)
    rxzu__wugg = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(rxzu__wugg, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(usw__dhf.
            type, 0))
        with payload._iterate() as rslo__qlv:
            i = c.builder.load(index)
            item = rslo__qlv.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return rxzu__wugg, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    dualz__luirj = h.type
    gdj__nci = self.mask
    dtype = self._ty.dtype
    bxr__lyx = context.typing_context
    fnty = bxr__lyx.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(bxr__lyx, (dtype, dtype), {})
    qawf__vkl = context.get_function(fnty, sig)
    wonm__nup = ir.Constant(dualz__luirj, 1)
    mrg__rncov = ir.Constant(dualz__luirj, 5)
    ngwc__olped = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, gdj__nci))
    if for_insert:
        vmixu__fardl = gdj__nci.type(-1)
        ibvl__olsgt = cgutils.alloca_once_value(builder, vmixu__fardl)
    vavaq__izl = builder.append_basic_block('lookup.body')
    kuu__hjdsu = builder.append_basic_block('lookup.found')
    tjip__haahk = builder.append_basic_block('lookup.not_found')
    ruxq__pqu = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        csgw__gqd = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, csgw__gqd)):
            nwscf__nnva = qawf__vkl(builder, (item, entry.key))
            with builder.if_then(nwscf__nnva):
                builder.branch(kuu__hjdsu)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, csgw__gqd)):
            builder.branch(tjip__haahk)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, csgw__gqd)):
                kjrbf__cllrs = builder.load(ibvl__olsgt)
                kjrbf__cllrs = builder.select(builder.icmp_unsigned('==',
                    kjrbf__cllrs, vmixu__fardl), i, kjrbf__cllrs)
                builder.store(kjrbf__cllrs, ibvl__olsgt)
    with cgutils.for_range(builder, ir.Constant(dualz__luirj, numba.cpython
        .setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, wonm__nup)
        i = builder.and_(i, gdj__nci)
        builder.store(i, index)
    builder.branch(vavaq__izl)
    with builder.goto_block(vavaq__izl):
        i = builder.load(index)
        check_entry(i)
        bokj__hmlr = builder.load(ngwc__olped)
        bokj__hmlr = builder.lshr(bokj__hmlr, mrg__rncov)
        i = builder.add(wonm__nup, builder.mul(i, mrg__rncov))
        i = builder.and_(gdj__nci, builder.add(i, bokj__hmlr))
        builder.store(i, index)
        builder.store(bokj__hmlr, ngwc__olped)
        builder.branch(vavaq__izl)
    with builder.goto_block(tjip__haahk):
        if for_insert:
            i = builder.load(index)
            kjrbf__cllrs = builder.load(ibvl__olsgt)
            i = builder.select(builder.icmp_unsigned('==', kjrbf__cllrs,
                vmixu__fardl), i, kjrbf__cllrs)
            builder.store(i, index)
        builder.branch(ruxq__pqu)
    with builder.goto_block(kuu__hjdsu):
        builder.branch(ruxq__pqu)
    builder.position_at_end(ruxq__pqu)
    cfncp__avfzu = builder.phi(ir.IntType(1), 'found')
    cfncp__avfzu.add_incoming(cgutils.true_bit, kuu__hjdsu)
    cfncp__avfzu.add_incoming(cgutils.false_bit, tjip__haahk)
    return cfncp__avfzu, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    hfu__ccvim = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    vrviu__lbt = payload.used
    wonm__nup = ir.Constant(vrviu__lbt.type, 1)
    vrviu__lbt = payload.used = builder.add(vrviu__lbt, wonm__nup)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, hfu__ccvim), likely=True):
        payload.fill = builder.add(payload.fill, wonm__nup)
    if do_resize:
        self.upsize(vrviu__lbt)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cfncp__avfzu, i = payload._lookup(item, h, for_insert=True)
    gzlu__qrrxj = builder.not_(cfncp__avfzu)
    with builder.if_then(gzlu__qrrxj):
        entry = payload.get_entry(i)
        hfu__ccvim = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        vrviu__lbt = payload.used
        wonm__nup = ir.Constant(vrviu__lbt.type, 1)
        vrviu__lbt = payload.used = builder.add(vrviu__lbt, wonm__nup)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, hfu__ccvim), likely=True):
            payload.fill = builder.add(payload.fill, wonm__nup)
        if do_resize:
            self.upsize(vrviu__lbt)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    vrviu__lbt = payload.used
    wonm__nup = ir.Constant(vrviu__lbt.type, 1)
    vrviu__lbt = payload.used = self._builder.sub(vrviu__lbt, wonm__nup)
    if do_resize:
        self.downsize(vrviu__lbt)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    wusbb__cqumc = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, wusbb__cqumc)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    fhtp__yryy = payload
    rxzu__wugg = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(rxzu__wugg), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with fhtp__yryy._iterate() as rslo__qlv:
        entry = rslo__qlv.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(fhtp__yryy.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as rslo__qlv:
        entry = rslo__qlv.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    rxzu__wugg = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(rxzu__wugg), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    rxzu__wugg = cgutils.alloca_once_value(builder, cgutils.true_bit)
    dualz__luirj = context.get_value_type(types.intp)
    big__hcj = ir.Constant(dualz__luirj, 0)
    wonm__nup = ir.Constant(dualz__luirj, 1)
    hkdd__opm = context.get_data_type(types.SetPayload(self._ty))
    qdhm__yaq = context.get_abi_sizeof(hkdd__opm)
    srsxh__zdgbx = self._entrysize
    qdhm__yaq -= srsxh__zdgbx
    feyf__rquhw, rlbis__hvps = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(dualz__luirj, srsxh__zdgbx), ir.Constant(
        dualz__luirj, qdhm__yaq))
    with builder.if_then(rlbis__hvps, likely=False):
        builder.store(cgutils.false_bit, rxzu__wugg)
    with builder.if_then(builder.load(rxzu__wugg), likely=True):
        if realloc:
            okx__zny = self._set.meminfo
            efhmt__smrsa = context.nrt.meminfo_varsize_alloc(builder,
                okx__zny, size=feyf__rquhw)
            gzi__neif = cgutils.is_null(builder, efhmt__smrsa)
        else:
            jzsp__twvvx = _imp_dtor(context, builder.module, self._ty)
            okx__zny = context.nrt.meminfo_new_varsize_dtor(builder,
                feyf__rquhw, builder.bitcast(jzsp__twvvx, cgutils.voidptr_t))
            gzi__neif = cgutils.is_null(builder, okx__zny)
        with builder.if_else(gzi__neif, likely=False) as (aieqk__dnnbs,
            decv__fjqx):
            with aieqk__dnnbs:
                builder.store(cgutils.false_bit, rxzu__wugg)
            with decv__fjqx:
                if not realloc:
                    self._set.meminfo = okx__zny
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, feyf__rquhw, 255)
                payload.used = big__hcj
                payload.fill = big__hcj
                payload.finger = big__hcj
                dyko__gczi = builder.sub(nentries, wonm__nup)
                payload.mask = dyko__gczi
    return builder.load(rxzu__wugg)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    rxzu__wugg = cgutils.alloca_once_value(builder, cgutils.true_bit)
    dualz__luirj = context.get_value_type(types.intp)
    big__hcj = ir.Constant(dualz__luirj, 0)
    wonm__nup = ir.Constant(dualz__luirj, 1)
    hkdd__opm = context.get_data_type(types.SetPayload(self._ty))
    qdhm__yaq = context.get_abi_sizeof(hkdd__opm)
    srsxh__zdgbx = self._entrysize
    qdhm__yaq -= srsxh__zdgbx
    gdj__nci = src_payload.mask
    nentries = builder.add(wonm__nup, gdj__nci)
    feyf__rquhw = builder.add(ir.Constant(dualz__luirj, qdhm__yaq), builder
        .mul(ir.Constant(dualz__luirj, srsxh__zdgbx), nentries))
    with builder.if_then(builder.load(rxzu__wugg), likely=True):
        jzsp__twvvx = _imp_dtor(context, builder.module, self._ty)
        okx__zny = context.nrt.meminfo_new_varsize_dtor(builder,
            feyf__rquhw, builder.bitcast(jzsp__twvvx, cgutils.voidptr_t))
        gzi__neif = cgutils.is_null(builder, okx__zny)
        with builder.if_else(gzi__neif, likely=False) as (aieqk__dnnbs,
            decv__fjqx):
            with aieqk__dnnbs:
                builder.store(cgutils.false_bit, rxzu__wugg)
            with decv__fjqx:
                self._set.meminfo = okx__zny
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = big__hcj
                payload.mask = gdj__nci
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, srsxh__zdgbx)
                with src_payload._iterate() as rslo__qlv:
                    context.nrt.incref(builder, self._ty.dtype, rslo__qlv.
                        entry.key)
    return builder.load(rxzu__wugg)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    gvjrh__pxk = context.get_value_type(types.voidptr)
    pte__jbw = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [gvjrh__pxk, pte__jbw, gvjrh__pxk])
    uqw__dnei = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=uqw__dnei)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        kna__fnhh = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, kna__fnhh)
        with payload._iterate() as rslo__qlv:
            entry = rslo__qlv.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    gwt__nlu, = sig.args
    fzuam__kid, = args
    dpfng__gwsfa = numba.core.imputils.call_len(context, builder, gwt__nlu,
        fzuam__kid)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, dpfng__gwsfa)
    with numba.core.imputils.for_iter(context, builder, gwt__nlu, fzuam__kid
        ) as rslo__qlv:
        inst.add(rslo__qlv.value)
        context.nrt.decref(builder, set_type.dtype, rslo__qlv.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    gwt__nlu = sig.args[1]
    fzuam__kid = args[1]
    dpfng__gwsfa = numba.core.imputils.call_len(context, builder, gwt__nlu,
        fzuam__kid)
    if dpfng__gwsfa is not None:
        cmzsz__zbqn = builder.add(inst.payload.used, dpfng__gwsfa)
        inst.upsize(cmzsz__zbqn)
    with numba.core.imputils.for_iter(context, builder, gwt__nlu, fzuam__kid
        ) as rslo__qlv:
        hre__vnqnf = context.cast(builder, rslo__qlv.value, gwt__nlu.dtype,
            inst.dtype)
        inst.add(hre__vnqnf)
        context.nrt.decref(builder, gwt__nlu.dtype, rslo__qlv.value)
    if dpfng__gwsfa is not None:
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
    leg__sgmbl = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, leg__sgmbl, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    pio__icg = target_context.get_executable(library, fndesc, env)
    qtjhs__gom = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=pio__icg, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return qtjhs__gom


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
        fbsjv__clkld = MPI.COMM_WORLD
        if fbsjv__clkld.Get_rank() == 0:
            lknk__pfjvt = self.get_cache_path()
            os.makedirs(lknk__pfjvt, exist_ok=True)
            tempfile.TemporaryFile(dir=lknk__pfjvt).close()
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
    iixq__erx = cgutils.create_struct_proxy(charseq.bytes_type)
    hplm__ejoqa = iixq__erx(context, builder)
    if isinstance(nbytes, int):
        nbytes = ir.Constant(hplm__ejoqa.nitems.type, nbytes)
    hplm__ejoqa.meminfo = context.nrt.meminfo_alloc(builder, nbytes)
    hplm__ejoqa.nitems = nbytes
    hplm__ejoqa.itemsize = ir.Constant(hplm__ejoqa.itemsize.type, 1)
    hplm__ejoqa.data = context.nrt.meminfo_data(builder, hplm__ejoqa.meminfo)
    hplm__ejoqa.parent = cgutils.get_null_value(hplm__ejoqa.parent.type)
    hplm__ejoqa.shape = cgutils.pack_array(builder, [hplm__ejoqa.nitems],
        context.get_value_type(types.intp))
    hplm__ejoqa.strides = cgutils.pack_array(builder, [ir.Constant(
        hplm__ejoqa.strides.type.element, 1)], context.get_value_type(types
        .intp))
    return hplm__ejoqa


if _check_numba_change:
    lines = inspect.getsource(charseq._make_constant_bytes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b3ed23ad58baff7b935912e3e22f4d8af67423d8fd0e5f1836ba0b3028a6eb18':
        warnings.warn('charseq._make_constant_bytes has changed')
charseq._make_constant_bytes = _make_constant_bytes
