import os

import argeasy
import tabulate

from .__init__ import __version__
from .counter import count_directory
from .counter import count_file


def get_total_lines(result: list) -> int:
    total_lines = 0

    for path, lines in result:
        total_lines += int(lines)

    return total_lines


def main() -> int:
    parser = argeasy.ArgEasy(
        name='pylcount',
        description='Python file line counter',
        version=__version__
    )

    parser.add_argument(
        'count',
        ('Count lines of file/directory. '
         'The next argument must be the file path.')
    )

    parser.add_flag('--ext', 'Count lines with specific extensions', action='append')
    parser.add_flag('--ignore', 'Skip such files', action='append')

    args = parser.parse()

    if args.count:
        filepath = args.count
        ignore_list = args.ignore or []
        ext_list = args.ext or []

        if os.path.isdir(filepath):
            result = count_directory(filepath, ignore=ignore_list, ext=ext_list)
        elif os.path.isfile(filepath):
            result = count_file(filepath)
        else:
            print('\033[31merror: the specified path is not a known directory or file.\033[m')
            return 1

        if result:
            print(tabulate.tabulate(result, headers=['File', 'Lines'], tablefmt='orgtbl'))
        else:
            print('\033[31merror: this file cannot be counted\033[m')
            return 1

        total_lines = get_total_lines(result)
        print(f'\nTotal number of lines: {total_lines}')

        return 0
