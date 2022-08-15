import os
try:
    from scandir import walk
except ImportError:
    from os import walk

from .compressed_filepath.types import *
from .compressed_filepath.iteration import IterationSet
from .compressed_filepath.tokenize import Tokenizer


def expand_filepath(filepath):
    """
    Expand user home and any env variables
    """

    filepath = os.path.expanduser(filepath)
    filepath = os.path.expandvars(filepath)
    return filepath


def walk_dir(directory, recursive=True, include=None, exclude=None):
    """
    Walk directory and return compressed filepaths
    """

    join = os.path.join
    abspath = os.path.abspath
    is_dir = os.path.isdir

    directory = expand_filepath(directory)

    if recursive:
        for relative_dir, _, files in walk(directory):
            filepaths = [abspath(join(relative_dir, filename)) for filename in files]
            for compressed in compress_filepaths(
                filepaths, include=include, exclude=exclude
            ):
                yield compressed
    else:
        filepaths = []
        for item in os.listdir(directory):
            item_path = abspath(join(directory, item))
            if not is_dir(item_path):
                filepaths.append(item_path)
                
        for compressed in compress_filepaths(
            filepaths, include=include, exclude=exclude
        ):
            yield compressed


def compress_filepaths(filepaths, include=None, exclude=None, cls=CompressedFilepath):
    return cls.compress(filepaths, include=include, exclude=exclude)


def expand_compressions(compressed_filepaths, cls=CompressedFilepath):
    return cls.expand_many(compressed_filepaths)


def get_human_readable(size, base=1024):
    """
    Give it bytes and it will convert that to human readable
    ** mainly for displaying to user **
    :param size: int(bytes)
    :return: str(human readable size)
    """

    if not isinstance(size, (int, float)):
        raise AssertionError('fs_util.get_human_readable function requires the size argument to be an int or float')

    size_types = ['B', 'KB', 'MB', 'GB', 'TB']

    for i, _ in enumerate(sorted(size_types, reverse=True)):
        i = len(size_types) - i
        if size > base ** i:
            return '{0:.2f} {1}'.format(size / float(base) ** i, size_types[i])

    return '{0:.2f} {1}'.format(float(size), 'B')


def mkdirs(path, mode, owner=-1, group=-1):
    assert isinstance(owner, int), 'the owner must be an int representing a uid'
    assert isinstance(group, int), 'the group must be an int representing a gid'
    s = path.split(os.sep)
    no_exists = []
    while not os.path.exists(path):
        no_exists.insert(0, s.pop())
        path = os.sep.join(s)
    new_path = path
    for x in no_exists:
        new_path = os.path.join(new_path, x)
        try:
            os.mkdir(new_path)
        except OSError as e:
            if 'errno 17' in str(e).lower():
                continue
            else:
                raise
        if isinstance(mode, int):
            os.chmod(new_path, mode)
        os.chown(new_path, owner, group)


def find_shared_folder(file_paths):
    """
    Given a list of filepaths, find the common directory
     --> (os.path.commonprefix will consider the whole string including filename)
    :param file_paths: list(str(filepath)s)
    :return: str(filepath)
    """
    file_paths = sorted(file_paths, key=lambda path: path.count('/'))

    dir_path = os.path.dirname(file_paths[0])
    while True:
        if all(p.startswith(dir_path) for p in file_paths):
            break
        dir_path = os.path.dirname(dir_path)

    return dir_path


def from_string(path_string, check_disk=True):
    """
    From a path string, decide the function to use and return CompressedFilepaths
    """
    return CompressedFilepath.from_string(path_string, check_disk=check_disk)
