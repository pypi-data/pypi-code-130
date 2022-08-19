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
    sqmtn__jmnw = MPI.COMM_WORLD
    alhb__vlubm = sqmtn__jmnw.Get_rank()
    vmbo__vct = get_host_ranks()
    ktxi__avl = get_nodes_first_ranks()
    if alhb__vlubm in ktxi__avl:
        try:
            epcy__vat = get_num_gpus(framework)
        except Exception as gvyqg__kvrmv:
            epcy__vat = gvyqg__kvrmv
        syn__omors = create_subcomm_mpi4py(ktxi__avl)
        kfh__rgwd = syn__omors.gather(epcy__vat)
        if alhb__vlubm == 0:
            gpu_ranks = []
            xqwgo__uexyr = None
            for pyw__eckx, ceanm__gtqps in enumerate(vmbo__vct.values()):
                mmix__wemr = kfh__rgwd[pyw__eckx]
                if isinstance(mmix__wemr, Exception):
                    xqwgo__uexyr = mmix__wemr
                    break
                if mmix__wemr == 0:
                    continue
                usg__mkeg = len(ceanm__gtqps) // mmix__wemr
                for qip__kxkvy, kuk__spoyk in enumerate(ceanm__gtqps):
                    if qip__kxkvy % usg__mkeg == 0:
                        uqn__onuih = qip__kxkvy / usg__mkeg
                        if uqn__onuih < mmix__wemr:
                            gpu_ranks.append(kuk__spoyk)
            if xqwgo__uexyr:
                sqmtn__jmnw.bcast(xqwgo__uexyr)
                raise xqwgo__uexyr
            else:
                sqmtn__jmnw.bcast(gpu_ranks)
    if alhb__vlubm != 0:
        gpu_ranks = sqmtn__jmnw.bcast(None)
        if isinstance(gpu_ranks, Exception):
            gvyqg__kvrmv = gpu_ranks
            raise gvyqg__kvrmv
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
    vigmm__cae = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        syn__omors = MPI.COMM_WORLD.Split(color=0 if vigmm__cae in
            gpu_ranks else MPI.UNDEFINED, key=vigmm__cae)
        if syn__omors != MPI.COMM_NULL:
            hvd.init(comm=syn__omors)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                acp__bsi = tf.config.experimental.list_physical_devices('GPU')
                for biw__qocb in acp__bsi:
                    tf.config.experimental.set_memory_growth(biw__qocb, True)
                tf.config.experimental.set_visible_devices(acp__bsi[hvd.
                    local_rank()], 'GPU')
    else:
        if vigmm__cae == 0:
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
        zmg__gwsog = 17
        sqmtn__jmnw = MPI.COMM_WORLD
        nnk__ejvyk = MPI.Get_processor_name()
        bmz__jak = get_host_ranks()[nnk__ejvyk]
        assert_dl_initialized()
        if bodo.get_rank() == bmz__jak[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for alhb__vlubm in bmz__jak[1:]:
                sqmtn__jmnw.isend(1, dest=alhb__vlubm, tag=zmg__gwsog)
        else:
            while True:
                glih__reata = MPI.Status()
                qnqm__uem = sqmtn__jmnw.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    glih__reata)
                if qnqm__uem:
                    assert glih__reata.source == bmz__jak[0]
                    assert glih__reata.tag == zmg__gwsog
                    sqmtn__jmnw.recv(source=0, tag=zmg__gwsog)
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
