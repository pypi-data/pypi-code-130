from enum import Enum

class StandardCompression(Enum):
    AUTO = 'AUTO'
    GZIP = 'GZIP'
    BZ2 = 'BZ2'
    ZSTD = 'ZSTD'
    DEFLATE = 'DEFLATE'
    RAW_DEFLATE = 'RAW_DEFLATE'
    NONE = 'NONE'

class ParquetCompression(Enum):
    AUTO = 'AUTO'
    SNAPPY = 'SNAPPY'
    NONE = 'NONE'

class FileFormat(Enum):
    CSV = 'CSV'
    JSON = 'JSON'
    AVRO = 'AVRO'
    ORC = 'ORC'
    PARQUET = 'Parquet'
    XML = 'XML'

class ValidationMode(Enum):
    '''
    Not supporting RETURN_<n>_ROWS for now
    '''
    RETURN_ALL_ERRORS = 'RETURN_ALL_ERRORS'
    RETURN_ERRORS = 'RETURN_ERRORS'

class OnError(Enum):
    '''
    There are 2 options that aren't going to be initially supported: SKIP_FILE_<num> and 'SKIP_FILE_<num>%'
    '''
    CONTINUE = 'CONTINUE'
    SKIP_FILE = 'SKIP_FILE'
    ABORT_STATEMENT = 'ABORT_STATEMENT'

class MatchByColumnName(Enum):
    CASE_SENSITIVE = 'CASE_SENSITIVE'
    CASE_INSENSITIVE = 'CASE_INSENSITIVE'
    NONE = 'NONE'

class ExternalStorage(Enum):
    S3 = 's3'
    GCS = 'gcs'
    AZURE = 'azure'

class ExternalPathConfig(Enum):
    S3 = 's3'
    GCS = 'gcs'
    AZURE = 'azure'

class Credentials(Enum):
    S3 = 's3'
    GCS = 'gcs'
    AZURE = 'azure'

class Encryption(Enum):
    S3 = 's3'
    gcs = 'gcs'
    AZURE = 'azure'