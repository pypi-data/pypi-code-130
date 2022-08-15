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
        ttb__umkc = state
        gkt__buw = inspect.getsourcelines(ttb__umkc)[0][0]
        assert gkt__buw.startswith('@bodo.jit') or gkt__buw.startswith('@jit')
        avdgf__fua = eval(gkt__buw[1:])
        self.dispatcher = avdgf__fua(ttb__umkc)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    rru__jghw = MPI.COMM_WORLD
    while True:
        rsycv__zyo = rru__jghw.bcast(None, root=MASTER_RANK)
        if rsycv__zyo[0] == 'exec':
            ttb__umkc = pickle.loads(rsycv__zyo[1])
            for wlpom__fndrh, imfw__xcz in list(ttb__umkc.__globals__.items()):
                if isinstance(imfw__xcz, MasterModeDispatcher):
                    ttb__umkc.__globals__[wlpom__fndrh] = imfw__xcz.dispatcher
            if ttb__umkc.__module__ not in sys.modules:
                sys.modules[ttb__umkc.__module__] = pytypes.ModuleType(
                    ttb__umkc.__module__)
            gkt__buw = inspect.getsourcelines(ttb__umkc)[0][0]
            assert gkt__buw.startswith('@bodo.jit') or gkt__buw.startswith(
                '@jit')
            avdgf__fua = eval(gkt__buw[1:])
            func = avdgf__fua(ttb__umkc)
            jxm__yvwa = rsycv__zyo[2]
            rnipy__bbz = rsycv__zyo[3]
            fuod__zrv = []
            for gufs__eneyd in jxm__yvwa:
                if gufs__eneyd == 'scatter':
                    fuod__zrv.append(bodo.scatterv(None))
                elif gufs__eneyd == 'bcast':
                    fuod__zrv.append(rru__jghw.bcast(None, root=MASTER_RANK))
            jypq__mfeo = {}
            for argname, gufs__eneyd in rnipy__bbz.items():
                if gufs__eneyd == 'scatter':
                    jypq__mfeo[argname] = bodo.scatterv(None)
                elif gufs__eneyd == 'bcast':
                    jypq__mfeo[argname] = rru__jghw.bcast(None, root=
                        MASTER_RANK)
            pow__xbzb = func(*fuod__zrv, **jypq__mfeo)
            if pow__xbzb is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(pow__xbzb)
            del (rsycv__zyo, ttb__umkc, func, avdgf__fua, jxm__yvwa,
                rnipy__bbz, fuod__zrv, jypq__mfeo, pow__xbzb)
            gc.collect()
        elif rsycv__zyo[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    rru__jghw = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        jxm__yvwa = ['scatter' for hqy__xub in range(len(args))]
        rnipy__bbz = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        zot__lqj = func.py_func.__code__.co_varnames
        cmm__upo = func.targetoptions

        def get_distribution(argname):
            if argname in cmm__upo.get('distributed', []
                ) or argname in cmm__upo.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        jxm__yvwa = [get_distribution(argname) for argname in zot__lqj[:len
            (args)]]
        rnipy__bbz = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    nodu__ccl = pickle.dumps(func.py_func)
    rru__jghw.bcast(['exec', nodu__ccl, jxm__yvwa, rnipy__bbz])
    fuod__zrv = []
    for jyhk__iuwt, gufs__eneyd in zip(args, jxm__yvwa):
        if gufs__eneyd == 'scatter':
            fuod__zrv.append(bodo.scatterv(jyhk__iuwt))
        elif gufs__eneyd == 'bcast':
            rru__jghw.bcast(jyhk__iuwt)
            fuod__zrv.append(jyhk__iuwt)
    jypq__mfeo = {}
    for argname, jyhk__iuwt in kwargs.items():
        gufs__eneyd = rnipy__bbz[argname]
        if gufs__eneyd == 'scatter':
            jypq__mfeo[argname] = bodo.scatterv(jyhk__iuwt)
        elif gufs__eneyd == 'bcast':
            rru__jghw.bcast(jyhk__iuwt)
            jypq__mfeo[argname] = jyhk__iuwt
    xvc__cxb = []
    for wlpom__fndrh, imfw__xcz in list(func.py_func.__globals__.items()):
        if isinstance(imfw__xcz, MasterModeDispatcher):
            xvc__cxb.append((func.py_func.__globals__, wlpom__fndrh, func.
                py_func.__globals__[wlpom__fndrh]))
            func.py_func.__globals__[wlpom__fndrh] = imfw__xcz.dispatcher
    pow__xbzb = func(*fuod__zrv, **jypq__mfeo)
    for oyiz__zwezd, wlpom__fndrh, imfw__xcz in xvc__cxb:
        oyiz__zwezd[wlpom__fndrh] = imfw__xcz
    if pow__xbzb is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        pow__xbzb = bodo.gatherv(pow__xbzb)
    return pow__xbzb


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
