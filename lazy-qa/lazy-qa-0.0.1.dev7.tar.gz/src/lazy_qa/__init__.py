__version__ = '0.0.2'
try:
    #from ._lazy_qa import longest  # noqa
    import csv_builder
    import database_mysql
    import database_postgresql
    import json_builder
    import list_manipulation
    import request_builder
    import string_manipulation
    import yaml_manipulation
except ImportError:
    def longest(args):
        return max(args, key=len)
