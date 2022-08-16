"""
Exceptions
"""


class CsvParamsDataFileNotFound(FileNotFoundError):
    """
    File Not Found
    """


class CsvParamsDataFileInaccessible(IOError):
    """
    Cannot Access the File
    """


class CsvParamsDataFileInvalid(ValueError):
    """
    CSV Data is somehow invalid
    """
