"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    dawz__nfu = MPI.COMM_WORLD
    yfo__daqf = dawz__nfu.Get_rank()
    ptoao__uxofz = get_host_ranks()
    qlj__wwyl = get_nodes_first_ranks()
    if yfo__daqf in qlj__wwyl:
        try:
            uzyt__yvdar = get_num_gpus(framework)
        except Exception as oqcw__pdcrp:
            uzyt__yvdar = oqcw__pdcrp
        amkr__joxl = create_subcomm_mpi4py(qlj__wwyl)
        ydx__ahkn = amkr__joxl.gather(uzyt__yvdar)
        if yfo__daqf == 0:
            gpu_ranks = []
            odxdc__hfry = None
            for srjx__natmw, wlzw__uyxn in enumerate(ptoao__uxofz.values()):
                yilnl__nrqf = ydx__ahkn[srjx__natmw]
                if isinstance(yilnl__nrqf, Exception):
                    odxdc__hfry = yilnl__nrqf
                    break
                if yilnl__nrqf == 0:
                    continue
                iuku__hvcp = len(wlzw__uyxn) // yilnl__nrqf
                for xioe__occkm, ximzg__glqvr in enumerate(wlzw__uyxn):
                    if xioe__occkm % iuku__hvcp == 0:
                        bgyax__qwbpq = xioe__occkm / iuku__hvcp
                        if bgyax__qwbpq < yilnl__nrqf:
                            gpu_ranks.append(ximzg__glqvr)
            if odxdc__hfry:
                dawz__nfu.bcast(odxdc__hfry)
                raise odxdc__hfry
            else:
                dawz__nfu.bcast(gpu_ranks)
    if yfo__daqf != 0:
        gpu_ranks = dawz__nfu.bcast(None)
        if isinstance(gpu_ranks, Exception):
            oqcw__pdcrp = gpu_ranks
            raise oqcw__pdcrp
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    kgi__dbi = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        amkr__joxl = MPI.COMM_WORLD.Split(color=0 if kgi__dbi in gpu_ranks else
            MPI.UNDEFINED, key=kgi__dbi)
        if amkr__joxl != MPI.COMM_NULL:
            hvd.init(comm=amkr__joxl)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                gpy__mzx = tf.config.experimental.list_physical_devices('GPU')
                for rra__cqgvp in gpy__mzx:
                    tf.config.experimental.set_memory_growth(rra__cqgvp, True)
                tf.config.experimental.set_visible_devices(gpy__mzx[hvd.
                    local_rank()], 'GPU')
    else:
        if kgi__dbi == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        xtm__sqlx = 17
        dawz__nfu = MPI.COMM_WORLD
        lpct__sqlcs = MPI.Get_processor_name()
        vxx__gmtl = get_host_ranks()[lpct__sqlcs]
        assert_dl_initialized()
        if bodo.get_rank() == vxx__gmtl[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for yfo__daqf in vxx__gmtl[1:]:
                dawz__nfu.isend(1, dest=yfo__daqf, tag=xtm__sqlx)
        else:
            while True:
                fba__qrgol = MPI.Status()
                qac__nzwst = dawz__nfu.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    fba__qrgol)
                if qac__nzwst:
                    assert fba__qrgol.source == vxx__gmtl[0]
                    assert fba__qrgol.tag == xtm__sqlx
                    dawz__nfu.recv(source=0, tag=xtm__sqlx)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
