from .bases import Namespaced, SQL, FileFormatType
from .exceptions import SchemaRequired
from .enums import FileFormat, StandardCompression, ParquetCompression
from typing import Optional, List
from dataclasses import dataclass

class DefinedFileFormat(Namespaced, SQL, FileFormatType):
    def __init__(self, file_format_name: str, schema: Optional[str] = None, database: Optional[str] = None) -> None:
        self.file_format_name = file_format_name
        self.schema = schema
        self.database = database

        if database and not schema:
            raise SchemaRequired('Database name provided but schema missing')

    @property
    def fullname(self) -> str:
        '''
        So long as this class raises on init that a schema is required if a database is provided
        then this is safe to do
        '''
        name = self.file_format_name

        if self.schema:
            name = f'{self.schema}.{name}'

        if self.database:
            name = f'{self.database}.{name}'

        return name

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        pass

'''
For all of these options types classes, they're probably going to want to have mostly Optional arguments set to None,
then when generating the SQL those options would be omitted and therefore fall back on the Snowflake defaults. If this
isn't done, then this codebase would want to try and maintain the expected default behaviour of Snowflake, which is probably
a bad idea
'''

@dataclass
class CSVFileFormat(SQL, FileFormatType):
    compression: StandardCompression
    record_delimiter: Optional[str] = None
    field_delimiter: Optional[str] = None
    skip_header: Optional[int] = None
    skip_blank_lines: bool = False
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    timestamp_format: Optional[str] = None
    binary_format: Optional[str] = None
    escape: Optional[str] = None
    escape_unenclosed_field: Optional[str] = None
    trim_space: bool = False
    field_optionally_enclosed_by: Optional[str] = None
    null_if: Optional[List[str]] = None
    error_on_column_count_mismatch: bool = False
    replace_invalid_characters: bool = False
    empty_field_as_null: bool = False
    skip_byte_order_mark: bool = False
    encoding: Optional[str] = None

    @property
    def sql(self) -> str:
        file_format_string = ''

        internals = self.__dict__

        for key, value in internals.items():
            if value:
                if type(value) == bool:
                    val = str(value).lower()
                elif type(value) == list:
                    '''
                    Only going to consider List[str] for now
                    '''
                    val = f'''( '{"', '".join(value)}' )'''
                elif type(value) == StandardCompression:
                    val = f"'{value.value}'"
                elif type(value) == str:
                    val = f"'{value}'"
                else:
                    val = value
                
                file_format_string = f'{file_format_string} {key.upper()} = {val}' 

        return f'FILE_FORMAT = ( {file_format_string.strip()} )'

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.CSV

@dataclass
class JSONFileFormat(SQL):
    compression: StandardCompression
    date_format: str
    time_format: str
    timestamp_format: str
    binary_format: str
    trim_space: bool
    null_if: List[str]
    enable_octal: bool
    allow_duplicate: bool
    strip_outer_array: bool
    strip_null_values: bool
    replace_invalid_characters: bool
    ignore_utf8_errors: bool
    skip_byte_order_mark: bool

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.JSON

@dataclass
class AVROFileFormat(SQL):
    compression: StandardCompression
    trim_space: bool
    null_if: List[str]

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.AVRO

@dataclass
class ORCFileFormat(SQL):
    trim_space: bool
    null_if: List[str]

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.ORC

@dataclass
class ParquetFileFormat(SQL):
    compression: ParquetCompression
    binarty_as_text: bool
    trim_space: bool
    null_if: List[str]

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.PARQUET

@dataclass
class XMLFileFormat(SQL):
    compression: StandardCompression
    ignore_utf8_errors: bool
    preserve_space: bool
    strip_outer_element: bool
    disable_snowflake_data: bool
    disable_auto_convert: bool
    skip_byte_order_mark: bool

    @property
    def sql(self) -> str:
        pass

    @property
    def ff_type(self) -> FileFormat:
        return FileFormat.XML

