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
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        tsiw__bcwy = 'bodo' if distributed else 'bodo_seq'
        tsiw__bcwy = (tsiw__bcwy + '_inline' if inline_calls_pass else
            tsiw__bcwy)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, tsiw__bcwy
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
    for vlmf__natbx, (psvu__gszks, quxyu__oxntq) in enumerate(pm.passes):
        if psvu__gszks == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(vlmf__natbx, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for vlmf__natbx, (psvu__gszks, quxyu__oxntq) in enumerate(pm.passes):
        if psvu__gszks == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[vlmf__natbx] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for vlmf__natbx, (psvu__gszks, quxyu__oxntq) in enumerate(pm.passes):
        if psvu__gszks == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(vlmf__natbx)
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
    eylc__hqdbb = guard(get_definition, func_ir, rhs.func)
    if isinstance(eylc__hqdbb, (ir.Global, ir.FreeVar, ir.Const)):
        cbuuz__lffd = eylc__hqdbb.value
    else:
        bosxg__xxc = guard(find_callname, func_ir, rhs)
        if not (bosxg__xxc and isinstance(bosxg__xxc[0], str) and
            isinstance(bosxg__xxc[1], str)):
            return
        func_name, func_mod = bosxg__xxc
        try:
            import importlib
            lss__zxk = importlib.import_module(func_mod)
            cbuuz__lffd = getattr(lss__zxk, func_name)
        except:
            return
    if isinstance(cbuuz__lffd, CPUDispatcher) and issubclass(cbuuz__lffd.
        _compiler.pipeline_class, BodoCompiler
        ) and cbuuz__lffd._compiler.pipeline_class != BodoCompilerUDF:
        cbuuz__lffd._compiler.pipeline_class = BodoCompilerUDF
        cbuuz__lffd.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for bln__cngpg in block.body:
                if is_call_assign(bln__cngpg):
                    _convert_bodo_dispatcher_to_udf(bln__cngpg.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        fxhbb__msfm = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        fxhbb__msfm.run()
        return True


def _update_definitions(func_ir, node_list):
    zfv__dasuu = ir.Loc('', 0)
    glbk__jrzb = ir.Block(ir.Scope(None, zfv__dasuu), zfv__dasuu)
    glbk__jrzb.body = node_list
    build_definitions({(0): glbk__jrzb}, func_ir._definitions)


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
        wmqf__jrou = 'overload_series_' + rhs.attr
        zbut__bvzs = getattr(bodo.hiframes.series_impl, wmqf__jrou)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        wmqf__jrou = 'overload_dataframe_' + rhs.attr
        zbut__bvzs = getattr(bodo.hiframes.dataframe_impl, wmqf__jrou)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    pet__zkyoo = zbut__bvzs(rhs_type)
    zrnu__ffp = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    sdd__srn = compile_func_single_block(pet__zkyoo, (rhs.value,), stmt.
        target, zrnu__ffp)
    _update_definitions(func_ir, sdd__srn)
    new_body += sdd__srn
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
        eksnx__gom = tuple(typemap[cooon__qujbd.name] for cooon__qujbd in
            rhs.args)
        lfam__dlxn = {tsiw__bcwy: typemap[cooon__qujbd.name] for tsiw__bcwy,
            cooon__qujbd in dict(rhs.kws).items()}
        pet__zkyoo = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*eksnx__gom, **lfam__dlxn)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        eksnx__gom = tuple(typemap[cooon__qujbd.name] for cooon__qujbd in
            rhs.args)
        lfam__dlxn = {tsiw__bcwy: typemap[cooon__qujbd.name] for tsiw__bcwy,
            cooon__qujbd in dict(rhs.kws).items()}
        pet__zkyoo = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*eksnx__gom, **lfam__dlxn)
    else:
        return False
    srzc__xma = replace_func(pass_info, pet__zkyoo, rhs.args, pysig=numba.
        core.utils.pysignature(pet__zkyoo), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    maig__cir, quxyu__oxntq = inline_closure_call(func_ir, srzc__xma.glbls,
        block, len(new_body), srzc__xma.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=srzc__xma.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for hcjz__rwpl in maig__cir.values():
        hcjz__rwpl.loc = rhs.loc
        update_locs(hcjz__rwpl.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    stvu__ppkl = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = stvu__ppkl(func_ir, typemap)
    lxqzn__zqmh = func_ir.blocks
    work_list = list((dhmq__qxnjv, lxqzn__zqmh[dhmq__qxnjv]) for
        dhmq__qxnjv in reversed(lxqzn__zqmh.keys()))
    while work_list:
        ejyw__gfgye, block = work_list.pop()
        new_body = []
        trzi__cugn = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                bosxg__xxc = guard(find_callname, func_ir, rhs, typemap)
                if bosxg__xxc is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = bosxg__xxc
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    trzi__cugn = True
                    break
            new_body.append(stmt)
        if not trzi__cugn:
            lxqzn__zqmh[ejyw__gfgye].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        qznec__xmm = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = qznec__xmm.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        hitw__rccjp = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        ueq__ysb = hitw__rccjp.run()
        dml__brtw = ueq__ysb
        if dml__brtw:
            dml__brtw = hitw__rccjp.run()
        if dml__brtw:
            hitw__rccjp.run()
        return ueq__ysb


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        gvpwu__ysv = 0
        zmuuh__hpvto = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            gvpwu__ysv = int(os.environ[zmuuh__hpvto])
        except:
            pass
        if gvpwu__ysv > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(gvpwu__ysv,
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
        zrnu__ffp = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, zrnu__ffp)
        for block in state.func_ir.blocks.values():
            new_body = []
            for bln__cngpg in block.body:
                if type(bln__cngpg) in distributed_run_extensions:
                    xjyy__qss = distributed_run_extensions[type(bln__cngpg)]
                    jjviz__lvy = xjyy__qss(bln__cngpg, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += jjviz__lvy
                elif is_call_assign(bln__cngpg):
                    rhs = bln__cngpg.value
                    bosxg__xxc = guard(find_callname, state.func_ir, rhs)
                    if bosxg__xxc == ('gatherv', 'bodo') or bosxg__xxc == (
                        'allgatherv', 'bodo'):
                        hpxbu__nmjw = state.typemap[bln__cngpg.target.name]
                        oyora__hvf = state.typemap[rhs.args[0].name]
                        if isinstance(oyora__hvf, types.Array) and isinstance(
                            hpxbu__nmjw, types.Array):
                            nuu__gliw = oyora__hvf.copy(readonly=False)
                            rhcg__ndkq = hpxbu__nmjw.copy(readonly=False)
                            if nuu__gliw == rhcg__ndkq:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), bln__cngpg.target, zrnu__ffp)
                                continue
                        if (hpxbu__nmjw != oyora__hvf and 
                            to_str_arr_if_dict_array(hpxbu__nmjw) ==
                            to_str_arr_if_dict_array(oyora__hvf)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), bln__cngpg.target,
                                zrnu__ffp, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            bln__cngpg.value = rhs.args[0]
                    new_body.append(bln__cngpg)
                else:
                    new_body.append(bln__cngpg)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        gln__ztk = TableColumnDelPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes)
        return gln__ztk.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    hnv__kesv = set()
    while work_list:
        ejyw__gfgye, block = work_list.pop()
        hnv__kesv.add(ejyw__gfgye)
        for i, flc__mkebp in enumerate(block.body):
            if isinstance(flc__mkebp, ir.Assign):
                vpht__nvju = flc__mkebp.value
                if isinstance(vpht__nvju, ir.Expr) and vpht__nvju.op == 'call':
                    eylc__hqdbb = guard(get_definition, func_ir, vpht__nvju
                        .func)
                    if isinstance(eylc__hqdbb, (ir.Global, ir.FreeVar)
                        ) and isinstance(eylc__hqdbb.value, CPUDispatcher
                        ) and issubclass(eylc__hqdbb.value._compiler.
                        pipeline_class, BodoCompiler):
                        tgvan__rfkl = eylc__hqdbb.value.py_func
                        arg_types = None
                        if typingctx:
                            xbr__wnryw = dict(vpht__nvju.kws)
                            fos__czixk = tuple(typemap[cooon__qujbd.name] for
                                cooon__qujbd in vpht__nvju.args)
                            cwt__bpvcu = {uzjws__ekca: typemap[cooon__qujbd
                                .name] for uzjws__ekca, cooon__qujbd in
                                xbr__wnryw.items()}
                            quxyu__oxntq, arg_types = (eylc__hqdbb.value.
                                fold_argument_types(fos__czixk, cwt__bpvcu))
                        quxyu__oxntq, lrw__ppdcq = inline_closure_call(func_ir,
                            tgvan__rfkl.__globals__, block, i, tgvan__rfkl,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((lrw__ppdcq[uzjws__ekca].name,
                            cooon__qujbd) for uzjws__ekca, cooon__qujbd in
                            eylc__hqdbb.value.locals.items() if uzjws__ekca in
                            lrw__ppdcq)
                        break
    return hnv__kesv


def udf_jit(signature_or_function=None, **options):
    ptkw__tawp = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=ptkw__tawp,
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
    for vlmf__natbx, (psvu__gszks, quxyu__oxntq) in enumerate(pm.passes):
        if psvu__gszks == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:vlmf__natbx + 1]
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
    kzs__fvk = None
    ovkr__ssxn = None
    _locals = {}
    yliy__egfi = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(yliy__egfi, arg_types,
        kw_types)
    wtr__sapxj = numba.core.compiler.Flags()
    cpjwg__lmu = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    bnl__gou = {'nopython': True, 'boundscheck': False, 'parallel': cpjwg__lmu}
    numba.core.registry.cpu_target.options.parse_as_flags(wtr__sapxj, bnl__gou)
    frs__zjg = TyperCompiler(typingctx, targetctx, kzs__fvk, args,
        ovkr__ssxn, wtr__sapxj, _locals)
    return frs__zjg.compile_extra(func)
