class ParseException(Exception):
    pass


class DocumentNotDefinedException(ParseException):
    message = 'Call to get_absolute_path without document parameter and no document set.'


class FileNotLoadedException(ParseException):
    message = 'Could not load file'


class IndentationException(ParseException):
    message = 'Indentation not a multiple of two'


class VariableNotDefinedException(ParseException):
    message = 'Variable not defined'


class TranslationNotDefinedException(ParseException):
    message = 'Translation not defined'


class NotFoundException(ParseException):
    message = 'Route can not be resolved'
