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
    nhhld__eot = MPI.COMM_WORLD
    xsgen__tkx = nhhld__eot.Get_rank()
    jlauj__jsq = get_host_ranks()
    wpycz__tla = get_nodes_first_ranks()
    if xsgen__tkx in wpycz__tla:
        try:
            kjffu__epxvn = get_num_gpus(framework)
        except Exception as ywgf__ntfwp:
            kjffu__epxvn = ywgf__ntfwp
        dfqm__iokwz = create_subcomm_mpi4py(wpycz__tla)
        hykmr__eqj = dfqm__iokwz.gather(kjffu__epxvn)
        if xsgen__tkx == 0:
            gpu_ranks = []
            sfuzy__zgffv = None
            for ljms__vtp, pest__lwch in enumerate(jlauj__jsq.values()):
                nqxi__saqcr = hykmr__eqj[ljms__vtp]
                if isinstance(nqxi__saqcr, Exception):
                    sfuzy__zgffv = nqxi__saqcr
                    break
                if nqxi__saqcr == 0:
                    continue
                nrq__wvklt = len(pest__lwch) // nqxi__saqcr
                for xkp__xelu, lnagl__qbrl in enumerate(pest__lwch):
                    if xkp__xelu % nrq__wvklt == 0:
                        xmnk__fkvd = xkp__xelu / nrq__wvklt
                        if xmnk__fkvd < nqxi__saqcr:
                            gpu_ranks.append(lnagl__qbrl)
            if sfuzy__zgffv:
                nhhld__eot.bcast(sfuzy__zgffv)
                raise sfuzy__zgffv
            else:
                nhhld__eot.bcast(gpu_ranks)
    if xsgen__tkx != 0:
        gpu_ranks = nhhld__eot.bcast(None)
        if isinstance(gpu_ranks, Exception):
            ywgf__ntfwp = gpu_ranks
            raise ywgf__ntfwp
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
    wpqjl__vqkb = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        dfqm__iokwz = MPI.COMM_WORLD.Split(color=0 if wpqjl__vqkb in
            gpu_ranks else MPI.UNDEFINED, key=wpqjl__vqkb)
        if dfqm__iokwz != MPI.COMM_NULL:
            hvd.init(comm=dfqm__iokwz)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                utadm__omzk = tf.config.experimental.list_physical_devices(
                    'GPU')
                for llba__cgpiz in utadm__omzk:
                    tf.config.experimental.set_memory_growth(llba__cgpiz, True)
                tf.config.experimental.set_visible_devices(utadm__omzk[hvd.
                    local_rank()], 'GPU')
    else:
        if wpqjl__vqkb == 0:
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
        iopo__wxp = 17
        nhhld__eot = MPI.COMM_WORLD
        iqld__jgqag = MPI.Get_processor_name()
        gmpz__mik = get_host_ranks()[iqld__jgqag]
        assert_dl_initialized()
        if bodo.get_rank() == gmpz__mik[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for xsgen__tkx in gmpz__mik[1:]:
                nhhld__eot.isend(1, dest=xsgen__tkx, tag=iopo__wxp)
        else:
            while True:
                htf__frdz = MPI.Status()
                grbfv__jrkm = nhhld__eot.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    htf__frdz)
                if grbfv__jrkm:
                    assert htf__frdz.source == gmpz__mik[0]
                    assert htf__frdz.tag == iopo__wxp
                    nhhld__eot.recv(source=0, tag=iopo__wxp)
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
