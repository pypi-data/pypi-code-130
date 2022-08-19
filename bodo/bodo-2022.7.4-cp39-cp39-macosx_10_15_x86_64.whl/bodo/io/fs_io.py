"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from fsspec.implementations.arrow import ArrowFile, ArrowFSWrapper, wrap_exceptions
from numba.core import types
from numba.extending import NativeValue, models, overload, register_model, unbox
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning, get_overload_constant_dict
from bodo.utils.utils import check_java_installation


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            tdf__tyb = self.fs.open_input_file(path)
        except:
            tdf__tyb = self.fs.open_input_stream(path)
    elif mode == 'wb':
        tdf__tyb = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, tdf__tyb, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr,
    types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
        (4) Wrong bucket region is used. Set AWS_DEFAULT_REGION variable with correct bucket region.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    ved__hos = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    qipj__fcju = False
    euaal__zbsrq = get_proxy_uri_from_env_vars()
    if storage_options:
        qipj__fcju = storage_options.get('anon', False)
    return S3FileSystem(anonymous=qipj__fcju, region=region,
        endpoint_override=ved__hos, proxy_options=euaal__zbsrq)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    ved__hos = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    qipj__fcju = False
    euaal__zbsrq = get_proxy_uri_from_env_vars()
    if storage_options:
        qipj__fcju = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=ved__hos, anonymous=
        qipj__fcju, proxy_options=euaal__zbsrq)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    stt__tuli = urlparse(path)
    if stt__tuli.scheme in ('abfs', 'abfss'):
        ogt__zkiv = path
        if stt__tuli.port is None:
            out__cbeh = 0
        else:
            out__cbeh = stt__tuli.port
        hctyo__lme = None
    else:
        ogt__zkiv = stt__tuli.hostname
        out__cbeh = stt__tuli.port
        hctyo__lme = stt__tuli.username
    try:
        fs = HdFS(host=ogt__zkiv, port=out__cbeh, user=hctyo__lme)
    except Exception as ufn__ktw:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            ufn__ktw))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        deyx__qqegn = fs.isdir(path)
    except gcsfs.utils.HttpError as ufn__ktw:
        raise BodoError(
            f'{ufn__ktw}. Make sure your google cloud credentials are set!')
    return deyx__qqegn


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [ztki__qtth.split('/')[-1] for ztki__qtth in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        stt__tuli = urlparse(path)
        kdwh__ldqdn = (stt__tuli.netloc + stt__tuli.path).rstrip('/')
        waxb__vvi = fs.get_file_info(kdwh__ldqdn)
        if waxb__vvi.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not waxb__vvi.size and waxb__vvi.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as ufn__ktw:
        raise
    except BodoError as lqjqh__axrh:
        raise
    except Exception as ufn__ktw:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ufn__ktw).__name__}: {str(ufn__ktw)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    xxjtf__sksw = None
    try:
        if s3_is_directory(fs, path):
            stt__tuli = urlparse(path)
            kdwh__ldqdn = (stt__tuli.netloc + stt__tuli.path).rstrip('/')
            znu__kbsw = pa_fs.FileSelector(kdwh__ldqdn, recursive=False)
            zmpok__pwqg = fs.get_file_info(znu__kbsw)
            if zmpok__pwqg and zmpok__pwqg[0].path in [kdwh__ldqdn,
                f'{kdwh__ldqdn}/'] and int(zmpok__pwqg[0].size or 0) == 0:
                zmpok__pwqg = zmpok__pwqg[1:]
            xxjtf__sksw = [mpvu__lhn.base_name for mpvu__lhn in zmpok__pwqg]
    except BodoError as lqjqh__axrh:
        raise
    except Exception as ufn__ktw:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ufn__ktw).__name__}: {str(ufn__ktw)}
{bodo_error_msg}"""
            )
    return xxjtf__sksw


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    stt__tuli = urlparse(path)
    pcfn__dglq = stt__tuli.path
    try:
        faxi__klhk = HadoopFileSystem.from_uri(path)
    except Exception as ufn__ktw:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            ufn__ktw))
    dvp__npt = faxi__klhk.get_file_info([pcfn__dglq])
    if dvp__npt[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not dvp__npt[0].size and dvp__npt[0].type == FileType.Directory:
        return faxi__klhk, True
    return faxi__klhk, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    xxjtf__sksw = None
    faxi__klhk, deyx__qqegn = hdfs_is_directory(path)
    if deyx__qqegn:
        stt__tuli = urlparse(path)
        pcfn__dglq = stt__tuli.path
        znu__kbsw = FileSelector(pcfn__dglq, recursive=True)
        try:
            zmpok__pwqg = faxi__klhk.get_file_info(znu__kbsw)
        except Exception as ufn__ktw:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(pcfn__dglq, ufn__ktw))
        xxjtf__sksw = [mpvu__lhn.base_name for mpvu__lhn in zmpok__pwqg]
    return faxi__klhk, xxjtf__sksw


def abfs_is_directory(path):
    faxi__klhk = get_hdfs_fs(path)
    try:
        dvp__npt = faxi__klhk.info(path)
    except OSError as lqjqh__axrh:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if dvp__npt['size'] == 0 and dvp__npt['kind'].lower() == 'directory':
        return faxi__klhk, True
    return faxi__klhk, False


def abfs_list_dir_fnames(path):
    xxjtf__sksw = None
    faxi__klhk, deyx__qqegn = abfs_is_directory(path)
    if deyx__qqegn:
        stt__tuli = urlparse(path)
        pcfn__dglq = stt__tuli.path
        try:
            xct__bkhza = faxi__klhk.ls(pcfn__dglq)
        except Exception as ufn__ktw:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(pcfn__dglq, ufn__ktw))
        xxjtf__sksw = [fname[fname.rindex('/') + 1:] for fname in xct__bkhza]
    return faxi__klhk, xxjtf__sksw


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    zhnm__qaho = urlparse(path)
    fname = path
    fs = None
    czsuf__wzg = 'read_json' if ftype == 'json' else 'read_csv'
    szy__rts = (
        f'pd.{czsuf__wzg}(): there is no {ftype} file in directory: {fname}')
    lwjsa__zsned = directory_of_files_common_filter
    if zhnm__qaho.scheme == 's3':
        snl__atd = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        mxpvm__veat = s3_list_dir_fnames(fs, path)
        kdwh__ldqdn = (zhnm__qaho.netloc + zhnm__qaho.path).rstrip('/')
        fname = kdwh__ldqdn
        if mxpvm__veat:
            mxpvm__veat = [(kdwh__ldqdn + '/' + ztki__qtth) for ztki__qtth in
                sorted(filter(lwjsa__zsned, mxpvm__veat))]
            pcuc__jzlu = [ztki__qtth for ztki__qtth in mxpvm__veat if int(
                fs.get_file_info(ztki__qtth).size or 0) > 0]
            if len(pcuc__jzlu) == 0:
                raise BodoError(szy__rts)
            fname = pcuc__jzlu[0]
        kxrvu__vhlh = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        dsl__hdnip = fs._open(fname)
    elif zhnm__qaho.scheme == 'hdfs':
        snl__atd = True
        fs, mxpvm__veat = hdfs_list_dir_fnames(path)
        kxrvu__vhlh = fs.get_file_info([zhnm__qaho.path])[0].size
        if mxpvm__veat:
            path = path.rstrip('/')
            mxpvm__veat = [(path + '/' + ztki__qtth) for ztki__qtth in
                sorted(filter(lwjsa__zsned, mxpvm__veat))]
            pcuc__jzlu = [ztki__qtth for ztki__qtth in mxpvm__veat if fs.
                get_file_info([urlparse(ztki__qtth).path])[0].size > 0]
            if len(pcuc__jzlu) == 0:
                raise BodoError(szy__rts)
            fname = pcuc__jzlu[0]
            fname = urlparse(fname).path
            kxrvu__vhlh = fs.get_file_info([fname])[0].size
        dsl__hdnip = fs.open_input_file(fname)
    elif zhnm__qaho.scheme in ('abfs', 'abfss'):
        snl__atd = True
        fs, mxpvm__veat = abfs_list_dir_fnames(path)
        kxrvu__vhlh = fs.info(fname)['size']
        if mxpvm__veat:
            path = path.rstrip('/')
            mxpvm__veat = [(path + '/' + ztki__qtth) for ztki__qtth in
                sorted(filter(lwjsa__zsned, mxpvm__veat))]
            pcuc__jzlu = [ztki__qtth for ztki__qtth in mxpvm__veat if fs.
                info(ztki__qtth)['size'] > 0]
            if len(pcuc__jzlu) == 0:
                raise BodoError(szy__rts)
            fname = pcuc__jzlu[0]
            kxrvu__vhlh = fs.info(fname)['size']
            fname = urlparse(fname).path
        dsl__hdnip = fs.open(fname, 'rb')
    else:
        if zhnm__qaho.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {zhnm__qaho.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        snl__atd = False
        if os.path.isdir(path):
            xct__bkhza = filter(lwjsa__zsned, glob.glob(os.path.join(os.
                path.abspath(path), '*')))
            pcuc__jzlu = [ztki__qtth for ztki__qtth in sorted(xct__bkhza) if
                os.path.getsize(ztki__qtth) > 0]
            if len(pcuc__jzlu) == 0:
                raise BodoError(szy__rts)
            fname = pcuc__jzlu[0]
        kxrvu__vhlh = os.path.getsize(fname)
        dsl__hdnip = fname
    return snl__atd, dsl__hdnip, kxrvu__vhlh, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    tlcf__mgjc = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            bjgk__hpei, mkv__kiyc = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = bjgk__hpei.region
        except Exception as ufn__ktw:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{ufn__ktw}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = tlcf__mgjc.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, filename_prefix, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, filename_prefix, is_parallel=False):

    def impl(path_or_buf, D, filename_prefix, is_parallel=False):
        rjdv__bvo = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        yez__lxq, gjugt__ddi = unicode_to_utf8_and_len(D)
        tdxi__byd = 0
        if is_parallel:
            tdxi__byd = bodo.libs.distributed_api.dist_exscan(gjugt__ddi,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), yez__lxq, tdxi__byd,
            gjugt__ddi, is_parallel, unicode_to_utf8(rjdv__bvo),
            unicode_to_utf8(filename_prefix))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    gek__rlmvl = get_overload_constant_dict(storage_options)
    tyjdd__sipo = 'def impl(storage_options):\n'
    tyjdd__sipo += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    tyjdd__sipo += f'    storage_options_py = {str(gek__rlmvl)}\n'
    tyjdd__sipo += '  return storage_options_py\n'
    mue__jvprs = {}
    exec(tyjdd__sipo, globals(), mue__jvprs)
    return mue__jvprs['impl']
