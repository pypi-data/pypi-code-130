from dataclasses import dataclass
from typing import List, Union, Optional

from .copy_options import CopyOptions, OnError
from .locations import ExternalStage, InternalStage, ExternalLocation
from .table import Table
from .file_format import AVROFileFormat, CSVFileFormat, DefinedFileFormat, FileFormat, JSONFileFormat, ORCFileFormat, ParquetFileFormat, XMLFileFormat
from .bases import SQL
from .exceptions import KnownSnowflakeLimitation, NotImplemented
from .enums import ValidationMode

@dataclass
class StandardCopyCommand(SQL):
    stage: Union[ExternalStage, InternalStage, ExternalLocation]
    table: Table
    file_format: Optional[Union[
        DefinedFileFormat, 
        CSVFileFormat, 
        JSONFileFormat, 
        AVROFileFormat, 
        ORCFileFormat, 
        ParquetFileFormat, 
        XMLFileFormat
    ]] = None
    copy_options: Optional[CopyOptions] = None
    force: bool = False
    filenames: Optional[List[str]] = None
    pattern: Optional[str] = None
    validation_mode: Optional[ValidationMode] = None

    def validate(self) -> None:
        '''
        There's an argument to just let it generate statements that will fail and let the user debug via the Snowflake
        errors that are returned, but I don't really like that
        '''
        if self.copy_options:
            if self.copy_options.match_by_column_name:
                if self.validation_mode:
                    raise KnownSnowflakeLimitation('MATCH_BY_COLUMN_NAME is not compatible with a VALIDATION_MODE')
                if self.file_format not in (FileFormat.JSON, FileFormat.AVRO, FileFormat.ORC, FileFormat.PARQUET):
                    raise KnownSnowflakeLimitation(f'MATCH_BY_COLUMN_NAME only supports: {",".join([FileFormat.JSON, FileFormat.AVRO, FileFormat.ORC, FileFormat.PARQUET])}') # type: ignore

            if self.file_format in (FileFormat.JSON, FileFormat.AVRO, FileFormat.ORC, FileFormat.PARQUET, FileFormat.XML) and self.copy_options.on_error not in [OnError.CONTINUE]:
                raise KnownSnowflakeLimitation(f'These file formats only supports: {OnError.CONTINUE} and these that are currently not support by this project: SKIP_FILE_<num> and SKIP_FILE_<num>%')

        '''
        Block for things that aren't yet implemented
        '''
        if type(self.stage) != ExternalStage:
            raise NotImplemented('Currently the stage may only be an ExternalStage')

        if self.file_format:
            if self.file_format.ff_type != FileFormat.CSV:
                raise NotImplemented('Currently the only file format available is the CSVFileFormat')
        

    @property
    def sql(self) -> str:
        self.validate()
        
        sql = f'''
            COPY INTO {self.table.fullname}
            FROM @{self.stage.fullname}
        '''

        if self.filenames:
            sql = f'''
                {sql}
                FILENAMES = ( '{"', '".join(self.filenames)}' )
            '''

        if self.pattern:
            sql = f'''
                {sql}
                PATTERN = '{self.pattern}'
            '''

        if self.file_format:
            sql = f'''
                {sql} 
                {self.file_format.sql}
            '''

        if self.copy_options:
            sql = f'''
                {sql}
                {self.copy_options.sql} 
            '''

        if self.validation_mode:
            sql = f'''
                {sql}
                VALIDATION_MODE = '{self.validation_mode.value}'
            '''

        if self.force:
            sql = f'''
                {sql}
                FORCE = true
            '''

        return sql


@dataclass
class TransformationCopyCommand:
    pass