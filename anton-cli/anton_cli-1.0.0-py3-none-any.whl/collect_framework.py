from collections import Counter
from functools import lru_cache


@lru_cache(maxsize=500, typed=False)
def split_letters(input_text):
    if not isinstance(input_text, str):
        raise TypeError('Text must be only str type!')
    result = Counter(Counter(input_text).values())[1]
    return result


def read_from_file(file_path):
    with open(f'anton_cli/{file_path}', "r") as file:
        string = file.read().splitlines()
        return [split_letters(el) for el in string]
