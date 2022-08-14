from dataclasses import dataclass
from typing import Optional
from .enums import OnError, MatchByColumnName

from .bases import SQL
from .exceptions import KnownSnowflakeLimitation

@dataclass
class CopyOptions(SQL):
    on_error: OnError
    purge: bool = False
    return_failed_only: bool = False
    enforcelength: bool = False
    truncatecolumns: bool = False
    force: bool = False
    load_uncertain_files: bool = False
    match_by_column_name: Optional[MatchByColumnName] = None
    size_limit: Optional[int] = None

    def __post_init__(self) -> None:
        if self.size_limit:
            if self.size_limit < 0:
                raise KnownSnowflakeLimitation('SIZE_LIMIT must be a positive number of bytes')

    @property
    def sql(self) -> str:
        copy_options_string = ''

        internals = self.__dict__

        for key, value in internals.items():
            if value:
                if type(value) == bool:
                    val = str(value).lower()
                elif type(value) in [OnError, MatchByColumnName]:
                    val = f"'{value.value}'"
                elif type(value) == str:
                    val = f"'{value}'"
                else:
                    val = value
                
                copy_options_string = f'{copy_options_string} {key.upper()} = {val}' 
        
        return f'COPY_OPTIONS = ( {copy_options_string.strip()} )'