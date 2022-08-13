import os
import subprocess
import warnings
from functools import wraps
from hashlib import md5
from inspect import getattr_static
from os.path import join
from pathlib import Path
from re import Pattern, match
from shutil import copy
from subprocess import Popen
from typing import List, Union, Iterator

from ase.io.cif import CIFBlock, parse_block
from ase.io.cif_unicode import format_unicode


class Pipe:
    def __init__(self, command, current_directory, encoding="utf-8"):
        self.command = command
        self.current_directory = current_directory
        self.encoding = encoding
        self.stdout = ""
        self.stderr = ""
        self.pipe()

    def pipe(self):
        popen = Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                      cwd=self.current_directory)
        stdout, stderr = popen.communicate()
        if stdout:
            self.stdout = stdout.decode(self.encoding)
            return
        if stderr:
            self.stderr = stderr.decode(self.encoding)


def copyFile(src_dir, target_dir, file):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    src = join(src_dir, file)
    copy(src, target_dir)


def search(fp, target, exclude=None, recursion=False):
    """
    Search files.
    :param fp: file path.
    :param target: target filename or keywords.
    :param exclude: exclude filename or keywords.
    :param recursion: Whether to recursively search
    :return: a generator
    """
    abs_fp = os.path.abspath(fp)
    items = os.listdir(abs_fp)
    for item in items:
        item_fp = os.path.join(abs_fp, item)
        if os.path.isdir(item_fp) and recursion:
            for tmp in search(item_fp, target, exclude, recursion):
                yield tmp
        elif exclude:
            if target in item and exclude not in item:
                yield item_fp
        elif target in item:
            yield item_fp


def md5_hex(file: Union[str, Path]):
    """计算16进制的md5值
    """
    return md5(Path(file).read_bytes()).hexdigest()


def matchList(li: list, pattern: Union[str, Pattern], return_type="str"):
    """匹配列表中符合条件的第一列
    """
    for i in li:
        if match(pattern, i):
            if return_type == "str":
                return i
            elif return_type == "Match":
                return match(pattern, i)
    return ""


def matchManyList(li: list, patterns: List[Union[str, Pattern]]):
    return [matchList(li, pattern) for pattern in patterns]


def method_register(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        if getattr_static(cls, func.__name__, None):
            msg = 'Error method name REPEAT, {} has exist'.format(func.__name__)
            raise NameError(msg)
        else:
            setattr(cls, func.__name__, wrapper)
        return func

    return decorator


def parse_cif_ase(s) -> Iterator[CIFBlock]:
    """Parse a CIF file using ase CIF parser."""

    data = format_unicode(s)
    lines = [e for e in data.split('\n') if len(e) > 0]
    lines = [''] + lines[::-1]  # all lines (reversed)

    while lines:
        line = lines.pop().strip()
        if not line or line.startswith('#'):
            continue

        yield parse_block(lines, line)


def parse_cif_ase_string(s):
    return list(parse_cif_ase(s))[0].get_atoms()
