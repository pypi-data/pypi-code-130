# config.py
# (C) 2020 Masato Kokubo
# since 1.2.0
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

import configparser
import os
import sys
import typing
from debugtrace import _print as pr

class Config(object):
    def __init__(self, config_path:str):
        self.config_path = config_path
        self._config_parser = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self._config_parser.read(self.config_path)
        else:
            self.config_path = '<No config file>'

        self.logger_name               = typing.cast(str , self._get_config_value('logger'                      , 'stderr'      ))
        self.logging_config_file       = typing.cast(str , self._get_config_value('logging_config_file'         , 'logging.conf'))
        self.logging_logger_name       = typing.cast(str , self._get_config_value('logging_logger_name'         , 'debugtrace'  ))
        self.logging_level             = typing.cast(str , self._get_config_value('logging_level'               , 'DEBUG'       )).upper()
        self.is_enabled                = typing.cast(bool, self._get_config_value('is_enabled'                  , True          ))
        self.enter_format              = typing.cast(str , self._get_config_value('enter_format'                , 'Enter {0} ({1}:{2})'     ))
        self.leave_format              = typing.cast(str , self._get_config_value('leave_format'                , 'Leave {0} ({1}:{2}) duration: {3}'))
        self.thread_boundary_format    = typing.cast(str , self._get_config_value('thread_boundary_format'      , '______________________________ {0} #{1} ______________________________')) # since 1.2.0
        self.maximum_indents           = typing.cast(int , self._get_config_value('maximum_indents'             , 32   ))
        self.indent_string             = typing.cast(str , self._get_config_value('indent_string'               , '| ' ))
        self.data_indent_string        = typing.cast(str , self._get_config_value('data_indent_string'          , '  ' ))
        self.limit_string              = typing.cast(str , self._get_config_value('limit_string'                , '...'))
        self.non_output_string         = typing.cast(str , self._get_config_value('non_output_string'           , '...'))
        self.cyclic_reference_string   = typing.cast(str , self._get_config_value('cyclic_reference_string'     , '*** Cyclic Reference ***'))
        self.varname_value_separator   = typing.cast(str , self._get_config_value('varname_value_separator'     , ' = '       ))
        self.key_value_separator       = typing.cast(str , self._get_config_value('key_value_separator'         , ': '        ))
        self.print_suffix_format       = typing.cast(str , self._get_config_value('print_suffix_format'         , ' ({1}:{2})'))
        self.count_format              = typing.cast(str , self._get_config_value('count_format'                , 'count:{}'  ))
        self.minimum_output_count      = typing.cast(int , self._get_config_value('minimum_output_count'        , 16          )) # 16 <- 5 since 1.2.0
        self.length_format             = typing.cast(str , self._get_config_value('length_format'               , 'length:{}' ))
        self.minimum_output_length     = typing.cast(int , self._get_config_value('minimum_output_length'       , 16          )) # 16 <- 5 since 1.2.0
        self.log_datetime_format       = typing.cast(str , self._get_config_value('log_datetime_format'         , '%Y-%m-%d %H:%M:%S.%f'))
        self.maximum_data_output_width = typing.cast(int , self._get_config_value('maximum_data_output_width'   , 70 ))
        self.bytes_count_in_line       = typing.cast(int , self._get_config_value('bytes_count_in_line'         , 16 ))
        self.collection_limit          = typing.cast(int , self._get_config_value('collection_limit'            , 128)) # 128 <- 512 since 1.2.0
        self.bytes_limit               = typing.cast(int , self._get_config_value('bytes_limit'                 , 256)) # 256 <- 8192 since 1.2.0
        self.string_limit              = typing.cast(int , self._get_config_value('string_limit'                , 256)) # 256 <- 8192 since 1.2.0
        self.reflection_nest_limit     = typing.cast(int , self._get_config_value('reflection_nest_limit'       , 4  ))

    def _get_config_value(self, key: str, fallback: object) -> object:
        """
        Gets the value related the key from debugtrace.ini file.

        Args:
            key (str): The key
            fallback (object): Value to return when the value related the key is undefined

        Returns:
            object: Value related the key
        """
        value = fallback
        try:
            if type(fallback) == bool:
                value = self._config_parser.getboolean('debugtrace', key, fallback=fallback)
            elif type(fallback) == int:
                value = self._config_parser.getint('debugtrace', key, fallback=fallback)
            else:
                value = self._config_parser.get('debugtrace', key, fallback=fallback)
                value = typing.cast(str, value).replace('\\s', ' ')

        except BaseException as ex:
            pr._print('debugtrace: (' + self.config_path + ') key: ' + key + ', error: '  + str(ex), sys.stderr)

        return value
