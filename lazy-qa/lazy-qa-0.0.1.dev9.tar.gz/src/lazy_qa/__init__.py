__version__ = '0.0.3'
try:
    #from ._lazy_qa import longest  # noqa
    from .csv_builder import *
    from .database_mysql import *
    from .database_postgresql import *
    from .json_builder import *
    from .list_manipulation import *
    from .request_builder import *
    from .string_manipulation import *
    from .yaml_manipulation import *

except ImportError:
    def longest(args):
        return max(args, key=len)
