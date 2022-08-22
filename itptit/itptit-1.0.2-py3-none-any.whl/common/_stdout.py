from io import (
    TextIOWrapper,
    BytesIO
)
import sys


class format:
    '''
    Change format for stdout text.
    '''
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'

    @staticmethod
    def formating(text: str, *fm: str) -> str:
        '''
        Return a string has been formated with the given formatting.
        '''
        return ''.join([*fm]) + text + format.END

    @staticmethod
    def color(r: int, g: int, b: int) -> str:
        '''
        Return a string which is ANSI code of a color.
        '''
        return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b)


class cursor:
    '''
    Control the stdout cursor.
    '''
    @staticmethod
    def up(n: int = 1):
        '''
        Move up n lines.
        '''
        stdout.print(f'\033[{n}A')

    @staticmethod
    def down(n: int = 1):
        '''
        Move down n lines.
        '''
        stdout.print(f'\033[{n}B')

    @staticmethod
    def next(n: int = 1):
        '''
        Move next n chars.
        '''
        stdout.print(f'\033[{n}C')

    @staticmethod
    def back(n: int = 1):
        '''
        Move back n chars.
        '''
        stdout.print(f'\033[{n}D')

    @staticmethod
    def move_to(x, y):
        stdout.print(f'\033[{x};{y}H')

    @staticmethod
    def clear_lines(n: int = 0):
        '''
        Clear n lines.
        '''
        stdout.print(f'\r\033[K')
        for i in range(n):
            cursor.up()
            stdout.print(f'\r\033[K')

    @staticmethod
    def del_line(left_to_right=True):
        '''
        Delete chars from left to right.
        '''
        if left_to_right:
            stdout.print('\033[0K')
        else:
            stdout.print('\033[1K')


class stdout:
    @staticmethod
    def print(*args):
        print(*args, end='')

    @staticmethod
    def get(func, *args, **kwargs) -> str:
        '''
        Get stdout's content of a function call.
        '''
        old_stdout = sys.stdout
        sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)
        wrapper = sys.stdout
        func(*args, **kwargs)
        wrapper.seek(0)
        output = wrapper.read()
        sys.stdout = old_stdout
        wrapper.close()
        return output