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
        rez__yzi = 'bodo' if distributed else 'bodo_seq'
        rez__yzi = rez__yzi + '_inline' if inline_calls_pass else rez__yzi
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, rez__yzi)
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
    for uaj__cyhki, (usd__xxvg, nfugk__hxqr) in enumerate(pm.passes):
        if usd__xxvg == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(uaj__cyhki, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for uaj__cyhki, (usd__xxvg, nfugk__hxqr) in enumerate(pm.passes):
        if usd__xxvg == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[uaj__cyhki] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for uaj__cyhki, (usd__xxvg, nfugk__hxqr) in enumerate(pm.passes):
        if usd__xxvg == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(uaj__cyhki)
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
    pex__abyqp = guard(get_definition, func_ir, rhs.func)
    if isinstance(pex__abyqp, (ir.Global, ir.FreeVar, ir.Const)):
        whjxy__fspep = pex__abyqp.value
    else:
        beodh__aqvhs = guard(find_callname, func_ir, rhs)
        if not (beodh__aqvhs and isinstance(beodh__aqvhs[0], str) and
            isinstance(beodh__aqvhs[1], str)):
            return
        func_name, func_mod = beodh__aqvhs
        try:
            import importlib
            pes__jxxsv = importlib.import_module(func_mod)
            whjxy__fspep = getattr(pes__jxxsv, func_name)
        except:
            return
    if isinstance(whjxy__fspep, CPUDispatcher) and issubclass(whjxy__fspep.
        _compiler.pipeline_class, BodoCompiler
        ) and whjxy__fspep._compiler.pipeline_class != BodoCompilerUDF:
        whjxy__fspep._compiler.pipeline_class = BodoCompilerUDF
        whjxy__fspep.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for ukgxc__tye in block.body:
                if is_call_assign(ukgxc__tye):
                    _convert_bodo_dispatcher_to_udf(ukgxc__tye.value, state
                        .func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ceh__lxu = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        ceh__lxu.run()
        return True


def _update_definitions(func_ir, node_list):
    jsar__ixoj = ir.Loc('', 0)
    xseoy__quo = ir.Block(ir.Scope(None, jsar__ixoj), jsar__ixoj)
    xseoy__quo.body = node_list
    build_definitions({(0): xseoy__quo}, func_ir._definitions)


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
        dsqvg__wbyak = 'overload_series_' + rhs.attr
        qorrf__fqwr = getattr(bodo.hiframes.series_impl, dsqvg__wbyak)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        dsqvg__wbyak = 'overload_dataframe_' + rhs.attr
        qorrf__fqwr = getattr(bodo.hiframes.dataframe_impl, dsqvg__wbyak)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    qzcd__crmll = qorrf__fqwr(rhs_type)
    cqre__ccp = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    eyf__rpocn = compile_func_single_block(qzcd__crmll, (rhs.value,), stmt.
        target, cqre__ccp)
    _update_definitions(func_ir, eyf__rpocn)
    new_body += eyf__rpocn
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
        bmvac__iyra = tuple(typemap[kbxm__hoqz.name] for kbxm__hoqz in rhs.args
            )
        scir__taz = {rez__yzi: typemap[kbxm__hoqz.name] for rez__yzi,
            kbxm__hoqz in dict(rhs.kws).items()}
        qzcd__crmll = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*bmvac__iyra, **scir__taz)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        bmvac__iyra = tuple(typemap[kbxm__hoqz.name] for kbxm__hoqz in rhs.args
            )
        scir__taz = {rez__yzi: typemap[kbxm__hoqz.name] for rez__yzi,
            kbxm__hoqz in dict(rhs.kws).items()}
        qzcd__crmll = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*bmvac__iyra, **scir__taz)
    else:
        return False
    unew__jcbgl = replace_func(pass_info, qzcd__crmll, rhs.args, pysig=
        numba.core.utils.pysignature(qzcd__crmll), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    puxl__cvf, nfugk__hxqr = inline_closure_call(func_ir, unew__jcbgl.glbls,
        block, len(new_body), unew__jcbgl.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=unew__jcbgl.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for yggm__nwuik in puxl__cvf.values():
        yggm__nwuik.loc = rhs.loc
        update_locs(yggm__nwuik.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    qzn__rfqyq = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = qzn__rfqyq(func_ir, typemap)
    emr__udr = func_ir.blocks
    work_list = list((dfdrm__wifuk, emr__udr[dfdrm__wifuk]) for
        dfdrm__wifuk in reversed(emr__udr.keys()))
    while work_list:
        cvszv__eezb, block = work_list.pop()
        new_body = []
        eaaj__jhb = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                beodh__aqvhs = guard(find_callname, func_ir, rhs, typemap)
                if beodh__aqvhs is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = beodh__aqvhs
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    eaaj__jhb = True
                    break
            new_body.append(stmt)
        if not eaaj__jhb:
            emr__udr[cvszv__eezb].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        ictu__gfwfy = DistributedPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = ictu__gfwfy.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        kmni__zhxn = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        zcf__icmwr = kmni__zhxn.run()
        aog__algl = zcf__icmwr
        if aog__algl:
            aog__algl = kmni__zhxn.run()
        if aog__algl:
            kmni__zhxn.run()
        return zcf__icmwr


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        naa__fai = 0
        zufs__nlf = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            naa__fai = int(os.environ[zufs__nlf])
        except:
            pass
        if naa__fai > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(naa__fai, state.
                metadata)
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
        cqre__ccp = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, cqre__ccp)
        for block in state.func_ir.blocks.values():
            new_body = []
            for ukgxc__tye in block.body:
                if type(ukgxc__tye) in distributed_run_extensions:
                    vekvi__irh = distributed_run_extensions[type(ukgxc__tye)]
                    qxsoe__zwrbq = vekvi__irh(ukgxc__tye, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += qxsoe__zwrbq
                elif is_call_assign(ukgxc__tye):
                    rhs = ukgxc__tye.value
                    beodh__aqvhs = guard(find_callname, state.func_ir, rhs)
                    if beodh__aqvhs == ('gatherv', 'bodo') or beodh__aqvhs == (
                        'allgatherv', 'bodo'):
                        grd__qcio = state.typemap[ukgxc__tye.target.name]
                        ixhz__koisd = state.typemap[rhs.args[0].name]
                        if isinstance(ixhz__koisd, types.Array) and isinstance(
                            grd__qcio, types.Array):
                            igjbk__yrpsj = ixhz__koisd.copy(readonly=False)
                            efcuf__rahfh = grd__qcio.copy(readonly=False)
                            if igjbk__yrpsj == efcuf__rahfh:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), ukgxc__tye.target, cqre__ccp)
                                continue
                        if (grd__qcio != ixhz__koisd and 
                            to_str_arr_if_dict_array(grd__qcio) ==
                            to_str_arr_if_dict_array(ixhz__koisd)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), ukgxc__tye.target,
                                cqre__ccp, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            ukgxc__tye.value = rhs.args[0]
                    new_body.append(ukgxc__tye)
                else:
                    new_body.append(ukgxc__tye)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        rnhj__blwe = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return rnhj__blwe.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    szye__wyl = set()
    while work_list:
        cvszv__eezb, block = work_list.pop()
        szye__wyl.add(cvszv__eezb)
        for i, hpdfe__smyvb in enumerate(block.body):
            if isinstance(hpdfe__smyvb, ir.Assign):
                frv__ibdtu = hpdfe__smyvb.value
                if isinstance(frv__ibdtu, ir.Expr) and frv__ibdtu.op == 'call':
                    pex__abyqp = guard(get_definition, func_ir, frv__ibdtu.func
                        )
                    if isinstance(pex__abyqp, (ir.Global, ir.FreeVar)
                        ) and isinstance(pex__abyqp.value, CPUDispatcher
                        ) and issubclass(pex__abyqp.value._compiler.
                        pipeline_class, BodoCompiler):
                        bjdej__ydww = pex__abyqp.value.py_func
                        arg_types = None
                        if typingctx:
                            gbeke__xho = dict(frv__ibdtu.kws)
                            kep__ypnh = tuple(typemap[kbxm__hoqz.name] for
                                kbxm__hoqz in frv__ibdtu.args)
                            ybw__rxk = {lcqkf__iyrhn: typemap[kbxm__hoqz.
                                name] for lcqkf__iyrhn, kbxm__hoqz in
                                gbeke__xho.items()}
                            nfugk__hxqr, arg_types = (pex__abyqp.value.
                                fold_argument_types(kep__ypnh, ybw__rxk))
                        nfugk__hxqr, hqsxc__iifj = inline_closure_call(func_ir,
                            bjdej__ydww.__globals__, block, i, bjdej__ydww,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((hqsxc__iifj[lcqkf__iyrhn].name,
                            kbxm__hoqz) for lcqkf__iyrhn, kbxm__hoqz in
                            pex__abyqp.value.locals.items() if lcqkf__iyrhn in
                            hqsxc__iifj)
                        break
    return szye__wyl


def udf_jit(signature_or_function=None, **options):
    augg__iomb = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=augg__iomb,
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
    for uaj__cyhki, (usd__xxvg, nfugk__hxqr) in enumerate(pm.passes):
        if usd__xxvg == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:uaj__cyhki + 1]
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
    fqvwl__mvsl = None
    bjidb__gprrp = None
    _locals = {}
    qgx__wrwd = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(qgx__wrwd, arg_types,
        kw_types)
    tkj__fbez = numba.core.compiler.Flags()
    vwx__xoss = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    xungh__ldf = {'nopython': True, 'boundscheck': False, 'parallel': vwx__xoss
        }
    numba.core.registry.cpu_target.options.parse_as_flags(tkj__fbez, xungh__ldf
        )
    abwxl__cge = TyperCompiler(typingctx, targetctx, fqvwl__mvsl, args,
        bjidb__gprrp, tkj__fbez, _locals)
    return abwxl__cge.compile_extra(func)
