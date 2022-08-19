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
            godk__iaxvr = self.fs.open_input_file(path)
        except:
            godk__iaxvr = self.fs.open_input_stream(path)
    elif mode == 'wb':
        godk__iaxvr = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, godk__iaxvr, path, mode, block_size, **kwargs)


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
    rys__iuk = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    ybsft__tmnm = False
    wgnz__rjuqu = get_proxy_uri_from_env_vars()
    if storage_options:
        ybsft__tmnm = storage_options.get('anon', False)
    return S3FileSystem(anonymous=ybsft__tmnm, region=region,
        endpoint_override=rys__iuk, proxy_options=wgnz__rjuqu)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    rys__iuk = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    ybsft__tmnm = False
    wgnz__rjuqu = get_proxy_uri_from_env_vars()
    if storage_options:
        ybsft__tmnm = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=rys__iuk, anonymous=
        ybsft__tmnm, proxy_options=wgnz__rjuqu)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    tbx__ord = urlparse(path)
    if tbx__ord.scheme in ('abfs', 'abfss'):
        dnpf__zyi = path
        if tbx__ord.port is None:
            hxxt__rlr = 0
        else:
            hxxt__rlr = tbx__ord.port
        wuhn__tzhsw = None
    else:
        dnpf__zyi = tbx__ord.hostname
        hxxt__rlr = tbx__ord.port
        wuhn__tzhsw = tbx__ord.username
    try:
        fs = HdFS(host=dnpf__zyi, port=hxxt__rlr, user=wuhn__tzhsw)
    except Exception as kknva__vif:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            kknva__vif))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        xnuhc__vzism = fs.isdir(path)
    except gcsfs.utils.HttpError as kknva__vif:
        raise BodoError(
            f'{kknva__vif}. Make sure your google cloud credentials are set!')
    return xnuhc__vzism


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [bxnp__hiwfj.split('/')[-1] for bxnp__hiwfj in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        tbx__ord = urlparse(path)
        lfcd__kefnl = (tbx__ord.netloc + tbx__ord.path).rstrip('/')
        hzuxx__geyrl = fs.get_file_info(lfcd__kefnl)
        if hzuxx__geyrl.type in (pa_fs.FileType.NotFound, pa_fs.FileType.
            Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not hzuxx__geyrl.size and hzuxx__geyrl.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as kknva__vif:
        raise
    except BodoError as gmiir__hvg:
        raise
    except Exception as kknva__vif:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(kknva__vif).__name__}: {str(kknva__vif)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    nmut__nda = None
    try:
        if s3_is_directory(fs, path):
            tbx__ord = urlparse(path)
            lfcd__kefnl = (tbx__ord.netloc + tbx__ord.path).rstrip('/')
            xjvs__aer = pa_fs.FileSelector(lfcd__kefnl, recursive=False)
            wct__ebq = fs.get_file_info(xjvs__aer)
            if wct__ebq and wct__ebq[0].path in [lfcd__kefnl, f'{lfcd__kefnl}/'
                ] and int(wct__ebq[0].size or 0) == 0:
                wct__ebq = wct__ebq[1:]
            nmut__nda = [abkm__lwotl.base_name for abkm__lwotl in wct__ebq]
    except BodoError as gmiir__hvg:
        raise
    except Exception as kknva__vif:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(kknva__vif).__name__}: {str(kknva__vif)}
{bodo_error_msg}"""
            )
    return nmut__nda


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    tbx__ord = urlparse(path)
    rbitf__annwf = tbx__ord.path
    try:
        lgfbx__nyeza = HadoopFileSystem.from_uri(path)
    except Exception as kknva__vif:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            kknva__vif))
    pbzez__bmctg = lgfbx__nyeza.get_file_info([rbitf__annwf])
    if pbzez__bmctg[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not pbzez__bmctg[0].size and pbzez__bmctg[0].type == FileType.Directory:
        return lgfbx__nyeza, True
    return lgfbx__nyeza, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    nmut__nda = None
    lgfbx__nyeza, xnuhc__vzism = hdfs_is_directory(path)
    if xnuhc__vzism:
        tbx__ord = urlparse(path)
        rbitf__annwf = tbx__ord.path
        xjvs__aer = FileSelector(rbitf__annwf, recursive=True)
        try:
            wct__ebq = lgfbx__nyeza.get_file_info(xjvs__aer)
        except Exception as kknva__vif:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rbitf__annwf, kknva__vif))
        nmut__nda = [abkm__lwotl.base_name for abkm__lwotl in wct__ebq]
    return lgfbx__nyeza, nmut__nda


def abfs_is_directory(path):
    lgfbx__nyeza = get_hdfs_fs(path)
    try:
        pbzez__bmctg = lgfbx__nyeza.info(path)
    except OSError as gmiir__hvg:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if pbzez__bmctg['size'] == 0 and pbzez__bmctg['kind'].lower(
        ) == 'directory':
        return lgfbx__nyeza, True
    return lgfbx__nyeza, False


def abfs_list_dir_fnames(path):
    nmut__nda = None
    lgfbx__nyeza, xnuhc__vzism = abfs_is_directory(path)
    if xnuhc__vzism:
        tbx__ord = urlparse(path)
        rbitf__annwf = tbx__ord.path
        try:
            tpka__nxwbr = lgfbx__nyeza.ls(rbitf__annwf)
        except Exception as kknva__vif:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rbitf__annwf, kknva__vif))
        nmut__nda = [fname[fname.rindex('/') + 1:] for fname in tpka__nxwbr]
    return lgfbx__nyeza, nmut__nda


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ver__qhz = urlparse(path)
    fname = path
    fs = None
    ill__hfmy = 'read_json' if ftype == 'json' else 'read_csv'
    tcvd__itsxj = (
        f'pd.{ill__hfmy}(): there is no {ftype} file in directory: {fname}')
    dxxgl__iiyt = directory_of_files_common_filter
    if ver__qhz.scheme == 's3':
        xasz__kiasz = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        xpcp__een = s3_list_dir_fnames(fs, path)
        lfcd__kefnl = (ver__qhz.netloc + ver__qhz.path).rstrip('/')
        fname = lfcd__kefnl
        if xpcp__een:
            xpcp__een = [(lfcd__kefnl + '/' + bxnp__hiwfj) for bxnp__hiwfj in
                sorted(filter(dxxgl__iiyt, xpcp__een))]
            kqdi__ctn = [bxnp__hiwfj for bxnp__hiwfj in xpcp__een if int(fs
                .get_file_info(bxnp__hiwfj).size or 0) > 0]
            if len(kqdi__ctn) == 0:
                raise BodoError(tcvd__itsxj)
            fname = kqdi__ctn[0]
        uwpfr__nlapn = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        anuy__pkve = fs._open(fname)
    elif ver__qhz.scheme == 'hdfs':
        xasz__kiasz = True
        fs, xpcp__een = hdfs_list_dir_fnames(path)
        uwpfr__nlapn = fs.get_file_info([ver__qhz.path])[0].size
        if xpcp__een:
            path = path.rstrip('/')
            xpcp__een = [(path + '/' + bxnp__hiwfj) for bxnp__hiwfj in
                sorted(filter(dxxgl__iiyt, xpcp__een))]
            kqdi__ctn = [bxnp__hiwfj for bxnp__hiwfj in xpcp__een if fs.
                get_file_info([urlparse(bxnp__hiwfj).path])[0].size > 0]
            if len(kqdi__ctn) == 0:
                raise BodoError(tcvd__itsxj)
            fname = kqdi__ctn[0]
            fname = urlparse(fname).path
            uwpfr__nlapn = fs.get_file_info([fname])[0].size
        anuy__pkve = fs.open_input_file(fname)
    elif ver__qhz.scheme in ('abfs', 'abfss'):
        xasz__kiasz = True
        fs, xpcp__een = abfs_list_dir_fnames(path)
        uwpfr__nlapn = fs.info(fname)['size']
        if xpcp__een:
            path = path.rstrip('/')
            xpcp__een = [(path + '/' + bxnp__hiwfj) for bxnp__hiwfj in
                sorted(filter(dxxgl__iiyt, xpcp__een))]
            kqdi__ctn = [bxnp__hiwfj for bxnp__hiwfj in xpcp__een if fs.
                info(bxnp__hiwfj)['size'] > 0]
            if len(kqdi__ctn) == 0:
                raise BodoError(tcvd__itsxj)
            fname = kqdi__ctn[0]
            uwpfr__nlapn = fs.info(fname)['size']
            fname = urlparse(fname).path
        anuy__pkve = fs.open(fname, 'rb')
    else:
        if ver__qhz.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ver__qhz.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        xasz__kiasz = False
        if os.path.isdir(path):
            tpka__nxwbr = filter(dxxgl__iiyt, glob.glob(os.path.join(os.
                path.abspath(path), '*')))
            kqdi__ctn = [bxnp__hiwfj for bxnp__hiwfj in sorted(tpka__nxwbr) if
                os.path.getsize(bxnp__hiwfj) > 0]
            if len(kqdi__ctn) == 0:
                raise BodoError(tcvd__itsxj)
            fname = kqdi__ctn[0]
        uwpfr__nlapn = os.path.getsize(fname)
        anuy__pkve = fname
    return xasz__kiasz, anuy__pkve, uwpfr__nlapn, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    slmd__wfwjf = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            lrh__bhy, raqd__vvu = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = lrh__bhy.region
        except Exception as kknva__vif:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{kknva__vif}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = slmd__wfwjf.bcast(bucket_loc)
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
        xgnr__glc = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        ufy__gtcqc, svksr__zkwqm = unicode_to_utf8_and_len(D)
        cpk__dsm = 0
        if is_parallel:
            cpk__dsm = bodo.libs.distributed_api.dist_exscan(svksr__zkwqm,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), ufy__gtcqc, cpk__dsm,
            svksr__zkwqm, is_parallel, unicode_to_utf8(xgnr__glc),
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
    luw__jikp = get_overload_constant_dict(storage_options)
    tqsz__zwzd = 'def impl(storage_options):\n'
    tqsz__zwzd += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    tqsz__zwzd += f'    storage_options_py = {str(luw__jikp)}\n'
    tqsz__zwzd += '  return storage_options_py\n'
    vaxvh__zpo = {}
    exec(tqsz__zwzd, globals(), vaxvh__zpo)
    return vaxvh__zpo['impl']
