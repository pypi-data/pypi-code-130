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
            rwf__owds = self.fs.open_input_file(path)
        except:
            rwf__owds = self.fs.open_input_stream(path)
    elif mode == 'wb':
        rwf__owds = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, rwf__owds, path, mode, block_size, **kwargs)


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
    dfyi__nki = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    awhwd__sxxe = False
    ubifz__oinc = get_proxy_uri_from_env_vars()
    if storage_options:
        awhwd__sxxe = storage_options.get('anon', False)
    return S3FileSystem(anonymous=awhwd__sxxe, region=region,
        endpoint_override=dfyi__nki, proxy_options=ubifz__oinc)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    dfyi__nki = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    awhwd__sxxe = False
    ubifz__oinc = get_proxy_uri_from_env_vars()
    if storage_options:
        awhwd__sxxe = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=dfyi__nki, anonymous
        =awhwd__sxxe, proxy_options=ubifz__oinc)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    lyvs__iqx = urlparse(path)
    if lyvs__iqx.scheme in ('abfs', 'abfss'):
        jnnv__eidhy = path
        if lyvs__iqx.port is None:
            fhbgo__gci = 0
        else:
            fhbgo__gci = lyvs__iqx.port
        siaa__qmw = None
    else:
        jnnv__eidhy = lyvs__iqx.hostname
        fhbgo__gci = lyvs__iqx.port
        siaa__qmw = lyvs__iqx.username
    try:
        fs = HdFS(host=jnnv__eidhy, port=fhbgo__gci, user=siaa__qmw)
    except Exception as jvlz__umjc:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            jvlz__umjc))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        uxvz__ifs = fs.isdir(path)
    except gcsfs.utils.HttpError as jvlz__umjc:
        raise BodoError(
            f'{jvlz__umjc}. Make sure your google cloud credentials are set!')
    return uxvz__ifs


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [fju__xpiri.split('/')[-1] for fju__xpiri in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        lyvs__iqx = urlparse(path)
        csw__nkvbp = (lyvs__iqx.netloc + lyvs__iqx.path).rstrip('/')
        plv__toqcs = fs.get_file_info(csw__nkvbp)
        if plv__toqcs.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not plv__toqcs.size and plv__toqcs.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as jvlz__umjc:
        raise
    except BodoError as wtxy__ppz:
        raise
    except Exception as jvlz__umjc:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jvlz__umjc).__name__}: {str(jvlz__umjc)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    fiaw__vxou = None
    try:
        if s3_is_directory(fs, path):
            lyvs__iqx = urlparse(path)
            csw__nkvbp = (lyvs__iqx.netloc + lyvs__iqx.path).rstrip('/')
            wxyv__sqxgx = pa_fs.FileSelector(csw__nkvbp, recursive=False)
            kbqix__glbs = fs.get_file_info(wxyv__sqxgx)
            if kbqix__glbs and kbqix__glbs[0].path in [csw__nkvbp,
                f'{csw__nkvbp}/'] and int(kbqix__glbs[0].size or 0) == 0:
                kbqix__glbs = kbqix__glbs[1:]
            fiaw__vxou = [cute__dsbp.base_name for cute__dsbp in kbqix__glbs]
    except BodoError as wtxy__ppz:
        raise
    except Exception as jvlz__umjc:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jvlz__umjc).__name__}: {str(jvlz__umjc)}
{bodo_error_msg}"""
            )
    return fiaw__vxou


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    lyvs__iqx = urlparse(path)
    rvv__tyt = lyvs__iqx.path
    try:
        vrj__jukuy = HadoopFileSystem.from_uri(path)
    except Exception as jvlz__umjc:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            jvlz__umjc))
    ngls__lwp = vrj__jukuy.get_file_info([rvv__tyt])
    if ngls__lwp[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not ngls__lwp[0].size and ngls__lwp[0].type == FileType.Directory:
        return vrj__jukuy, True
    return vrj__jukuy, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    fiaw__vxou = None
    vrj__jukuy, uxvz__ifs = hdfs_is_directory(path)
    if uxvz__ifs:
        lyvs__iqx = urlparse(path)
        rvv__tyt = lyvs__iqx.path
        wxyv__sqxgx = FileSelector(rvv__tyt, recursive=True)
        try:
            kbqix__glbs = vrj__jukuy.get_file_info(wxyv__sqxgx)
        except Exception as jvlz__umjc:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rvv__tyt, jvlz__umjc))
        fiaw__vxou = [cute__dsbp.base_name for cute__dsbp in kbqix__glbs]
    return vrj__jukuy, fiaw__vxou


def abfs_is_directory(path):
    vrj__jukuy = get_hdfs_fs(path)
    try:
        ngls__lwp = vrj__jukuy.info(path)
    except OSError as wtxy__ppz:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if ngls__lwp['size'] == 0 and ngls__lwp['kind'].lower() == 'directory':
        return vrj__jukuy, True
    return vrj__jukuy, False


def abfs_list_dir_fnames(path):
    fiaw__vxou = None
    vrj__jukuy, uxvz__ifs = abfs_is_directory(path)
    if uxvz__ifs:
        lyvs__iqx = urlparse(path)
        rvv__tyt = lyvs__iqx.path
        try:
            rhizt__wab = vrj__jukuy.ls(rvv__tyt)
        except Exception as jvlz__umjc:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rvv__tyt, jvlz__umjc))
        fiaw__vxou = [fname[fname.rindex('/') + 1:] for fname in rhizt__wab]
    return vrj__jukuy, fiaw__vxou


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    iybm__mud = urlparse(path)
    fname = path
    fs = None
    qjos__saese = 'read_json' if ftype == 'json' else 'read_csv'
    eaz__zau = (
        f'pd.{qjos__saese}(): there is no {ftype} file in directory: {fname}')
    nxddf__rnz = directory_of_files_common_filter
    if iybm__mud.scheme == 's3':
        pckw__wcy = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        lbszz__dzfg = s3_list_dir_fnames(fs, path)
        csw__nkvbp = (iybm__mud.netloc + iybm__mud.path).rstrip('/')
        fname = csw__nkvbp
        if lbszz__dzfg:
            lbszz__dzfg = [(csw__nkvbp + '/' + fju__xpiri) for fju__xpiri in
                sorted(filter(nxddf__rnz, lbszz__dzfg))]
            qvm__snc = [fju__xpiri for fju__xpiri in lbszz__dzfg if int(fs.
                get_file_info(fju__xpiri).size or 0) > 0]
            if len(qvm__snc) == 0:
                raise BodoError(eaz__zau)
            fname = qvm__snc[0]
        epyqr__amc = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        xjnuw__nkigw = fs._open(fname)
    elif iybm__mud.scheme == 'hdfs':
        pckw__wcy = True
        fs, lbszz__dzfg = hdfs_list_dir_fnames(path)
        epyqr__amc = fs.get_file_info([iybm__mud.path])[0].size
        if lbszz__dzfg:
            path = path.rstrip('/')
            lbszz__dzfg = [(path + '/' + fju__xpiri) for fju__xpiri in
                sorted(filter(nxddf__rnz, lbszz__dzfg))]
            qvm__snc = [fju__xpiri for fju__xpiri in lbszz__dzfg if fs.
                get_file_info([urlparse(fju__xpiri).path])[0].size > 0]
            if len(qvm__snc) == 0:
                raise BodoError(eaz__zau)
            fname = qvm__snc[0]
            fname = urlparse(fname).path
            epyqr__amc = fs.get_file_info([fname])[0].size
        xjnuw__nkigw = fs.open_input_file(fname)
    elif iybm__mud.scheme in ('abfs', 'abfss'):
        pckw__wcy = True
        fs, lbszz__dzfg = abfs_list_dir_fnames(path)
        epyqr__amc = fs.info(fname)['size']
        if lbszz__dzfg:
            path = path.rstrip('/')
            lbszz__dzfg = [(path + '/' + fju__xpiri) for fju__xpiri in
                sorted(filter(nxddf__rnz, lbszz__dzfg))]
            qvm__snc = [fju__xpiri for fju__xpiri in lbszz__dzfg if fs.info
                (fju__xpiri)['size'] > 0]
            if len(qvm__snc) == 0:
                raise BodoError(eaz__zau)
            fname = qvm__snc[0]
            epyqr__amc = fs.info(fname)['size']
            fname = urlparse(fname).path
        xjnuw__nkigw = fs.open(fname, 'rb')
    else:
        if iybm__mud.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {iybm__mud.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        pckw__wcy = False
        if os.path.isdir(path):
            rhizt__wab = filter(nxddf__rnz, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            qvm__snc = [fju__xpiri for fju__xpiri in sorted(rhizt__wab) if 
                os.path.getsize(fju__xpiri) > 0]
            if len(qvm__snc) == 0:
                raise BodoError(eaz__zau)
            fname = qvm__snc[0]
        epyqr__amc = os.path.getsize(fname)
        xjnuw__nkigw = fname
    return pckw__wcy, xjnuw__nkigw, epyqr__amc, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    tdbuk__lgexm = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            wcik__ctynu, susm__sqi = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = wcik__ctynu.region
        except Exception as jvlz__umjc:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{jvlz__umjc}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = tdbuk__lgexm.bcast(bucket_loc)
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
        pdor__hyv = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        zwgd__kvrqb, glt__iio = unicode_to_utf8_and_len(D)
        ufrmd__tgcd = 0
        if is_parallel:
            ufrmd__tgcd = bodo.libs.distributed_api.dist_exscan(glt__iio,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), zwgd__kvrqb, ufrmd__tgcd,
            glt__iio, is_parallel, unicode_to_utf8(pdor__hyv),
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
    aawva__hemdl = get_overload_constant_dict(storage_options)
    ezxj__fzf = 'def impl(storage_options):\n'
    ezxj__fzf += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    ezxj__fzf += f'    storage_options_py = {str(aawva__hemdl)}\n'
    ezxj__fzf += '  return storage_options_py\n'
    nsfv__tyfc = {}
    exec(ezxj__fzf, globals(), nsfv__tyfc)
    return nsfv__tyfc['impl']
