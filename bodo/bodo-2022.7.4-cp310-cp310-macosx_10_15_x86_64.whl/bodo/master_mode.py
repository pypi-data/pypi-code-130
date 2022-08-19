import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        dqe__itgw = state
        jqi__wvzzr = inspect.getsourcelines(dqe__itgw)[0][0]
        assert jqi__wvzzr.startswith('@bodo.jit') or jqi__wvzzr.startswith(
            '@jit')
        enj__vnij = eval(jqi__wvzzr[1:])
        self.dispatcher = enj__vnij(dqe__itgw)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    yown__tibar = MPI.COMM_WORLD
    while True:
        vanfu__xcam = yown__tibar.bcast(None, root=MASTER_RANK)
        if vanfu__xcam[0] == 'exec':
            dqe__itgw = pickle.loads(vanfu__xcam[1])
            for blfd__wnw, crgsk__fgt in list(dqe__itgw.__globals__.items()):
                if isinstance(crgsk__fgt, MasterModeDispatcher):
                    dqe__itgw.__globals__[blfd__wnw] = crgsk__fgt.dispatcher
            if dqe__itgw.__module__ not in sys.modules:
                sys.modules[dqe__itgw.__module__] = pytypes.ModuleType(
                    dqe__itgw.__module__)
            jqi__wvzzr = inspect.getsourcelines(dqe__itgw)[0][0]
            assert jqi__wvzzr.startswith('@bodo.jit') or jqi__wvzzr.startswith(
                '@jit')
            enj__vnij = eval(jqi__wvzzr[1:])
            func = enj__vnij(dqe__itgw)
            ulb__blof = vanfu__xcam[2]
            itguk__zux = vanfu__xcam[3]
            xov__ldod = []
            for mxjb__ugbkm in ulb__blof:
                if mxjb__ugbkm == 'scatter':
                    xov__ldod.append(bodo.scatterv(None))
                elif mxjb__ugbkm == 'bcast':
                    xov__ldod.append(yown__tibar.bcast(None, root=MASTER_RANK))
            ltfy__hujv = {}
            for argname, mxjb__ugbkm in itguk__zux.items():
                if mxjb__ugbkm == 'scatter':
                    ltfy__hujv[argname] = bodo.scatterv(None)
                elif mxjb__ugbkm == 'bcast':
                    ltfy__hujv[argname] = yown__tibar.bcast(None, root=
                        MASTER_RANK)
            ydjci__kzc = func(*xov__ldod, **ltfy__hujv)
            if ydjci__kzc is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(ydjci__kzc)
            del (vanfu__xcam, dqe__itgw, func, enj__vnij, ulb__blof,
                itguk__zux, xov__ldod, ltfy__hujv, ydjci__kzc)
            gc.collect()
        elif vanfu__xcam[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    yown__tibar = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        ulb__blof = ['scatter' for hqmz__zxf in range(len(args))]
        itguk__zux = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        glc__apzym = func.py_func.__code__.co_varnames
        nckae__xxn = func.targetoptions

        def get_distribution(argname):
            if argname in nckae__xxn.get('distributed', []
                ) or argname in nckae__xxn.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        ulb__blof = [get_distribution(argname) for argname in glc__apzym[:
            len(args)]]
        itguk__zux = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    dazx__htc = pickle.dumps(func.py_func)
    yown__tibar.bcast(['exec', dazx__htc, ulb__blof, itguk__zux])
    xov__ldod = []
    for azbod__dukoa, mxjb__ugbkm in zip(args, ulb__blof):
        if mxjb__ugbkm == 'scatter':
            xov__ldod.append(bodo.scatterv(azbod__dukoa))
        elif mxjb__ugbkm == 'bcast':
            yown__tibar.bcast(azbod__dukoa)
            xov__ldod.append(azbod__dukoa)
    ltfy__hujv = {}
    for argname, azbod__dukoa in kwargs.items():
        mxjb__ugbkm = itguk__zux[argname]
        if mxjb__ugbkm == 'scatter':
            ltfy__hujv[argname] = bodo.scatterv(azbod__dukoa)
        elif mxjb__ugbkm == 'bcast':
            yown__tibar.bcast(azbod__dukoa)
            ltfy__hujv[argname] = azbod__dukoa
    olqve__duof = []
    for blfd__wnw, crgsk__fgt in list(func.py_func.__globals__.items()):
        if isinstance(crgsk__fgt, MasterModeDispatcher):
            olqve__duof.append((func.py_func.__globals__, blfd__wnw, func.
                py_func.__globals__[blfd__wnw]))
            func.py_func.__globals__[blfd__wnw] = crgsk__fgt.dispatcher
    ydjci__kzc = func(*xov__ldod, **ltfy__hujv)
    for lsh__rtyi, blfd__wnw, crgsk__fgt in olqve__duof:
        lsh__rtyi[blfd__wnw] = crgsk__fgt
    if ydjci__kzc is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        ydjci__kzc = bodo.gatherv(ydjci__kzc)
    return ydjci__kzc


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
