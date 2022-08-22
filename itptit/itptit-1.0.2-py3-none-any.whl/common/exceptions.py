from typing import (
    Optional as _Optional,
    Sequence as _Sequence
)
from ._stdout import format as _format

'''
Exceptions that may happen in all the code.
'''


class HlightException(Exception):
    '''
    Base exception.
    '''

    def __init__(self,
                 msg: _Optional[str] = None,
                 screen: _Optional[str] = None,
                 stacktrace: _Optional[_Sequence[str]] = None) -> None:
        if msg is None:
            msg = '...'
        msg = _format.formating(msg, _format.RED)
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self) -> str:
        exception_msg = "\n"

        def label(lb: str):
            return _format.formating(" +) " + lb + ": ", _format.BOLD, _format.DARKCYAN)
        exception_msg += label('Message') + "%s\n" % self.msg
        if self.screen:
            exception_msg += label('Screenshot') + "Available via screen\n"
        if self.stacktrace:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += label('Stacktrace') + "\n%s" % stacktrace
        return exception_msg


class FailedToCreateTestCaseException(HlightException):
    '''
    Thrown when a test case creation process has an error.
    '''

    def __init__(self,
                 filename: str = None,
                 error: _Optional[str] = None,
                 screen: _Optional[str] = None,
                 stacktrace: _Optional[_Sequence[str]] = None) -> None:
        msg = f'Failed to create "{filename}"' + \
            (': ' + error if error else '!')
        super().__init__(msg, screen, stacktrace)


class WrongFileExtensionException(HlightException):
    '''
    Thrown when no files with the set extension exist.
    '''

    def __init__(self,
                 file_ets: _Optional[str] = None,
                 screen: _Optional[str] = None,
                 stacktrace: _Optional[_Sequence[str]] = None) -> None:
        msg = f'No files with the set extension exist (extension: ".{file_ets}").'
        super().__init__(msg, screen, stacktrace)


class TypeException(HlightException):
    '''
    Thrown when actual type is not expected type.
    '''


class InvalidArgumentValueException(HlightException):
    '''
    Thrown when an argument value is invalid.
    '''


class MissingFileException(HlightException):
    '''
    Thrown when the requested file is missing.
    '''


class JudgeException(HlightException):
    '''
    Base exception for judging.
    '''


class CompileError(JudgeException):
    '''
    Thrown when compilation fails.
    '''


class RunTimeError(JudgeException):
    '''
    Thrown when an error occurs during run time.
    '''


class InvalidReturn(JudgeException):
    '''
    Thrown when the running program throws an exception.
    '''


class TimeLimitExceeded(JudgeException):
    '''
    Thrown when program's runtime exceeds the execution time permitted.
    '''
