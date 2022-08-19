"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils, types
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.table_utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        zvpal__idx = 'bodo' if distributed else 'bodo_seq'
        zvpal__idx = (zvpal__idx + '_inline' if inline_calls_pass else
            zvpal__idx)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, zvpal__idx
            )
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for gnp__zquay, (qcn__lzao, zyf__nfpz) in enumerate(pm.passes):
        if qcn__lzao == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(gnp__zquay, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for gnp__zquay, (qcn__lzao, zyf__nfpz) in enumerate(pm.passes):
        if qcn__lzao == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[gnp__zquay] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for gnp__zquay, (qcn__lzao, zyf__nfpz) in enumerate(pm.passes):
        if qcn__lzao == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(gnp__zquay)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    ukj__zteqn = guard(get_definition, func_ir, rhs.func)
    if isinstance(ukj__zteqn, (ir.Global, ir.FreeVar, ir.Const)):
        gluii__roh = ukj__zteqn.value
    else:
        lpju__eklfg = guard(find_callname, func_ir, rhs)
        if not (lpju__eklfg and isinstance(lpju__eklfg[0], str) and
            isinstance(lpju__eklfg[1], str)):
            return
        func_name, func_mod = lpju__eklfg
        try:
            import importlib
            goco__rhkhk = importlib.import_module(func_mod)
            gluii__roh = getattr(goco__rhkhk, func_name)
        except:
            return
    if isinstance(gluii__roh, CPUDispatcher) and issubclass(gluii__roh.
        _compiler.pipeline_class, BodoCompiler
        ) and gluii__roh._compiler.pipeline_class != BodoCompilerUDF:
        gluii__roh._compiler.pipeline_class = BodoCompilerUDF
        gluii__roh.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for rceqm__fwwtp in block.body:
                if is_call_assign(rceqm__fwwtp):
                    _convert_bodo_dispatcher_to_udf(rceqm__fwwtp.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        xfxx__mvhb = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        xfxx__mvhb.run()
        return True


def _update_definitions(func_ir, node_list):
    eohe__lxmrz = ir.Loc('', 0)
    rov__paosq = ir.Block(ir.Scope(None, eohe__lxmrz), eohe__lxmrz)
    rov__paosq.body = node_list
    build_definitions({(0): rov__paosq}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        rpl__nwkyr = 'overload_series_' + rhs.attr
        pkh__qix = getattr(bodo.hiframes.series_impl, rpl__nwkyr)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        rpl__nwkyr = 'overload_dataframe_' + rhs.attr
        pkh__qix = getattr(bodo.hiframes.dataframe_impl, rpl__nwkyr)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    qaoc__gnnf = pkh__qix(rhs_type)
    jscd__oxz = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    bqnjv__ahkxe = compile_func_single_block(qaoc__gnnf, (rhs.value,), stmt
        .target, jscd__oxz)
    _update_definitions(func_ir, bqnjv__ahkxe)
    new_body += bqnjv__ahkxe
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        cbi__vbt = tuple(typemap[kfgo__xgz.name] for kfgo__xgz in rhs.args)
        chb__calzf = {zvpal__idx: typemap[kfgo__xgz.name] for zvpal__idx,
            kfgo__xgz in dict(rhs.kws).items()}
        qaoc__gnnf = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*cbi__vbt, **chb__calzf)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        cbi__vbt = tuple(typemap[kfgo__xgz.name] for kfgo__xgz in rhs.args)
        chb__calzf = {zvpal__idx: typemap[kfgo__xgz.name] for zvpal__idx,
            kfgo__xgz in dict(rhs.kws).items()}
        qaoc__gnnf = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*cbi__vbt, **chb__calzf)
    else:
        return False
    nwp__pwux = replace_func(pass_info, qaoc__gnnf, rhs.args, pysig=numba.
        core.utils.pysignature(qaoc__gnnf), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    mkcis__zue, zyf__nfpz = inline_closure_call(func_ir, nwp__pwux.glbls,
        block, len(new_body), nwp__pwux.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=nwp__pwux.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for ezejy__ezwbf in mkcis__zue.values():
        ezejy__ezwbf.loc = rhs.loc
        update_locs(ezejy__ezwbf.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    tkux__tgoj = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = tkux__tgoj(func_ir, typemap)
    hdf__qiq = func_ir.blocks
    work_list = list((mgy__dyq, hdf__qiq[mgy__dyq]) for mgy__dyq in
        reversed(hdf__qiq.keys()))
    while work_list:
        hwrvz__hfxll, block = work_list.pop()
        new_body = []
        egtno__venjw = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                lpju__eklfg = guard(find_callname, func_ir, rhs, typemap)
                if lpju__eklfg is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = lpju__eklfg
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    egtno__venjw = True
                    break
            new_body.append(stmt)
        if not egtno__venjw:
            hdf__qiq[hwrvz__hfxll].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        kapqf__kczu = DistributedPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = kapqf__kczu.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        xrn__xrjuh = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        bxbr__jlnp = xrn__xrjuh.run()
        xbspa__uwan = bxbr__jlnp
        if xbspa__uwan:
            xbspa__uwan = xrn__xrjuh.run()
        if xbspa__uwan:
            xrn__xrjuh.run()
        return bxbr__jlnp


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        naef__lvzgi = 0
        enoar__obix = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            naef__lvzgi = int(os.environ[enoar__obix])
        except:
            pass
        if naef__lvzgi > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(naef__lvzgi,
                state.metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        from bodo.utils.transform import compile_func_single_block
        from bodo.utils.typing import decode_if_dict_array, to_str_arr_if_dict_array
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        jscd__oxz = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, jscd__oxz)
        for block in state.func_ir.blocks.values():
            new_body = []
            for rceqm__fwwtp in block.body:
                if type(rceqm__fwwtp) in distributed_run_extensions:
                    nua__wxcwm = distributed_run_extensions[type(rceqm__fwwtp)]
                    jobk__wsvj = nua__wxcwm(rceqm__fwwtp, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += jobk__wsvj
                elif is_call_assign(rceqm__fwwtp):
                    rhs = rceqm__fwwtp.value
                    lpju__eklfg = guard(find_callname, state.func_ir, rhs)
                    if lpju__eklfg == ('gatherv', 'bodo') or lpju__eklfg == (
                        'allgatherv', 'bodo'):
                        xwes__hka = state.typemap[rceqm__fwwtp.target.name]
                        cere__gqr = state.typemap[rhs.args[0].name]
                        if isinstance(cere__gqr, types.Array) and isinstance(
                            xwes__hka, types.Array):
                            goskc__yqye = cere__gqr.copy(readonly=False)
                            dpnk__bfcsw = xwes__hka.copy(readonly=False)
                            if goskc__yqye == dpnk__bfcsw:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), rceqm__fwwtp.target, jscd__oxz)
                                continue
                        if xwes__hka != cere__gqr and to_str_arr_if_dict_array(
                            xwes__hka) == to_str_arr_if_dict_array(cere__gqr):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), rceqm__fwwtp.target,
                                jscd__oxz, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            rceqm__fwwtp.value = rhs.args[0]
                    new_body.append(rceqm__fwwtp)
                else:
                    new_body.append(rceqm__fwwtp)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        ofhpr__stkh = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return ofhpr__stkh.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    rkrc__wwf = set()
    while work_list:
        hwrvz__hfxll, block = work_list.pop()
        rkrc__wwf.add(hwrvz__hfxll)
        for i, fsg__pxeg in enumerate(block.body):
            if isinstance(fsg__pxeg, ir.Assign):
                kkhdx__gzmj = fsg__pxeg.value
                if isinstance(kkhdx__gzmj, ir.Expr
                    ) and kkhdx__gzmj.op == 'call':
                    ukj__zteqn = guard(get_definition, func_ir, kkhdx__gzmj
                        .func)
                    if isinstance(ukj__zteqn, (ir.Global, ir.FreeVar)
                        ) and isinstance(ukj__zteqn.value, CPUDispatcher
                        ) and issubclass(ukj__zteqn.value._compiler.
                        pipeline_class, BodoCompiler):
                        oplh__uxd = ukj__zteqn.value.py_func
                        arg_types = None
                        if typingctx:
                            gmjko__jgnp = dict(kkhdx__gzmj.kws)
                            bgxn__zvqem = tuple(typemap[kfgo__xgz.name] for
                                kfgo__xgz in kkhdx__gzmj.args)
                            zqfh__trsp = {roslb__zpx: typemap[kfgo__xgz.
                                name] for roslb__zpx, kfgo__xgz in
                                gmjko__jgnp.items()}
                            zyf__nfpz, arg_types = (ukj__zteqn.value.
                                fold_argument_types(bgxn__zvqem, zqfh__trsp))
                        zyf__nfpz, xji__wdgue = inline_closure_call(func_ir,
                            oplh__uxd.__globals__, block, i, oplh__uxd,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((xji__wdgue[roslb__zpx].name,
                            kfgo__xgz) for roslb__zpx, kfgo__xgz in
                            ukj__zteqn.value.locals.items() if roslb__zpx in
                            xji__wdgue)
                        break
    return rkrc__wwf


def udf_jit(signature_or_function=None, **options):
    tplma__upre = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=tplma__upre,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for gnp__zquay, (qcn__lzao, zyf__nfpz) in enumerate(pm.passes):
        if qcn__lzao == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:gnp__zquay + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    xekxa__hjdf = None
    vthly__gpzyp = None
    _locals = {}
    tcxa__itli = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(tcxa__itli, arg_types,
        kw_types)
    xdaup__cpv = numba.core.compiler.Flags()
    lwi__deejr = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    zrviz__mjaln = {'nopython': True, 'boundscheck': False, 'parallel':
        lwi__deejr}
    numba.core.registry.cpu_target.options.parse_as_flags(xdaup__cpv,
        zrviz__mjaln)
    iyk__tya = TyperCompiler(typingctx, targetctx, xekxa__hjdf, args,
        vthly__gpzyp, xdaup__cpv, _locals)
    return iyk__tya.compile_extra(func)
