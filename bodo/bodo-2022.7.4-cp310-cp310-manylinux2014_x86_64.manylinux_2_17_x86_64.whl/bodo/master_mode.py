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
        cghl__coeo = state
        acwtp__jmn = inspect.getsourcelines(cghl__coeo)[0][0]
        assert acwtp__jmn.startswith('@bodo.jit') or acwtp__jmn.startswith(
            '@jit')
        xngni__cmewx = eval(acwtp__jmn[1:])
        self.dispatcher = xngni__cmewx(cghl__coeo)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    neor__dxj = MPI.COMM_WORLD
    while True:
        saef__kgfsc = neor__dxj.bcast(None, root=MASTER_RANK)
        if saef__kgfsc[0] == 'exec':
            cghl__coeo = pickle.loads(saef__kgfsc[1])
            for nmwe__kdia, amcj__sdl in list(cghl__coeo.__globals__.items()):
                if isinstance(amcj__sdl, MasterModeDispatcher):
                    cghl__coeo.__globals__[nmwe__kdia] = amcj__sdl.dispatcher
            if cghl__coeo.__module__ not in sys.modules:
                sys.modules[cghl__coeo.__module__] = pytypes.ModuleType(
                    cghl__coeo.__module__)
            acwtp__jmn = inspect.getsourcelines(cghl__coeo)[0][0]
            assert acwtp__jmn.startswith('@bodo.jit') or acwtp__jmn.startswith(
                '@jit')
            xngni__cmewx = eval(acwtp__jmn[1:])
            func = xngni__cmewx(cghl__coeo)
            gzlu__qfh = saef__kgfsc[2]
            fcpcf__uke = saef__kgfsc[3]
            siluw__ridw = []
            for xjr__yhmv in gzlu__qfh:
                if xjr__yhmv == 'scatter':
                    siluw__ridw.append(bodo.scatterv(None))
                elif xjr__yhmv == 'bcast':
                    siluw__ridw.append(neor__dxj.bcast(None, root=MASTER_RANK))
            ftkpz__aozg = {}
            for argname, xjr__yhmv in fcpcf__uke.items():
                if xjr__yhmv == 'scatter':
                    ftkpz__aozg[argname] = bodo.scatterv(None)
                elif xjr__yhmv == 'bcast':
                    ftkpz__aozg[argname] = neor__dxj.bcast(None, root=
                        MASTER_RANK)
            nhgo__iasx = func(*siluw__ridw, **ftkpz__aozg)
            if nhgo__iasx is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(nhgo__iasx)
            del (saef__kgfsc, cghl__coeo, func, xngni__cmewx, gzlu__qfh,
                fcpcf__uke, siluw__ridw, ftkpz__aozg, nhgo__iasx)
            gc.collect()
        elif saef__kgfsc[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    neor__dxj = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        gzlu__qfh = ['scatter' for flw__viol in range(len(args))]
        fcpcf__uke = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        zcms__zwgnl = func.py_func.__code__.co_varnames
        gpsqy__jmy = func.targetoptions

        def get_distribution(argname):
            if argname in gpsqy__jmy.get('distributed', []
                ) or argname in gpsqy__jmy.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        gzlu__qfh = [get_distribution(argname) for argname in zcms__zwgnl[:
            len(args)]]
        fcpcf__uke = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    uoh__edll = pickle.dumps(func.py_func)
    neor__dxj.bcast(['exec', uoh__edll, gzlu__qfh, fcpcf__uke])
    siluw__ridw = []
    for jok__rhq, xjr__yhmv in zip(args, gzlu__qfh):
        if xjr__yhmv == 'scatter':
            siluw__ridw.append(bodo.scatterv(jok__rhq))
        elif xjr__yhmv == 'bcast':
            neor__dxj.bcast(jok__rhq)
            siluw__ridw.append(jok__rhq)
    ftkpz__aozg = {}
    for argname, jok__rhq in kwargs.items():
        xjr__yhmv = fcpcf__uke[argname]
        if xjr__yhmv == 'scatter':
            ftkpz__aozg[argname] = bodo.scatterv(jok__rhq)
        elif xjr__yhmv == 'bcast':
            neor__dxj.bcast(jok__rhq)
            ftkpz__aozg[argname] = jok__rhq
    xta__lnf = []
    for nmwe__kdia, amcj__sdl in list(func.py_func.__globals__.items()):
        if isinstance(amcj__sdl, MasterModeDispatcher):
            xta__lnf.append((func.py_func.__globals__, nmwe__kdia, func.
                py_func.__globals__[nmwe__kdia]))
            func.py_func.__globals__[nmwe__kdia] = amcj__sdl.dispatcher
    nhgo__iasx = func(*siluw__ridw, **ftkpz__aozg)
    for vgg__hro, nmwe__kdia, amcj__sdl in xta__lnf:
        vgg__hro[nmwe__kdia] = amcj__sdl
    if nhgo__iasx is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        nhgo__iasx = bodo.gatherv(nhgo__iasx)
    return nhgo__iasx


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
