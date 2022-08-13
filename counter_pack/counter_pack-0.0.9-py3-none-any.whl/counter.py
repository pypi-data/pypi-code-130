import argparse
from argparse import Namespace
from collections import Counter
from functools import lru_cache

from counter_paсk.custom_exceptions import OpenFileException


def argument_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--string', type=str, help="some string for count unique characters")
    arg_parser.add_argument('-f', '--file', type=str, help="some file for count unique characters")
    return arg_parser


@lru_cache
def count_unique_characters_from_string(original_string: str) -> int:
    assert isinstance(original_string, str), 'Argument should be string type!'
    counter_dict = Counter(''.join(original_string.split()))
    unique_list = [value for value in counter_dict.values() if value == 1]
    return len(unique_list)


def open_file(file_path: str) -> str:
    try:
        with open(file_path) as f:
            return f.read()
    except IOError as err:
        raise OpenFileException(f'{err.args[1]}')


def count_unique_characters_from_file(file_path: str) -> int:
    assert isinstance(file_path, str), 'Argument should be string type!'
    data = open_file(file_path)
    return count_unique_characters_from_string(data)


def count_depending_on_arguments(arguments: Namespace) -> int:
    num_characters = None
    if arguments.file:
        num_characters = count_unique_characters_from_file(arguments.file)
    elif arguments.string:
        num_characters = count_unique_characters_from_string(arguments.string)
    return num_characters


def main():
    try:
        parser = argument_parser()
        return count_depending_on_arguments(parser.parse_args())
    except OpenFileException as e:
        print('Oops!', e)


if __name__ == '__main__':
    print(main())
