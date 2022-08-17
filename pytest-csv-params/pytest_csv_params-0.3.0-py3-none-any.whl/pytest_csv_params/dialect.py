"""
CSV Dialects
"""
import csv


class CsvParamsDefaultDialect(csv.Dialect):  # pylint: disable=too-few-public-methods
    """
    Basic CSV Dialect for most Tests
    """

    delimiter = ","
    doublequote = True
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    strict = True
    skipinitialspace = True
