#!/usr/bin/python
# -*- coding:utf-8 -*-

"""将方法快速实现为一个命令行工具

假设在 main.py 有个方法 add 需要运行在终端，仅需要用装饰器 command 包裹

    @command(
        a="加数",
        b="被加数",
        n="可变长参数,其他被加数",
        name="姓名"
    )
    def add(a: int, b: float, *n: float, name: str = "无名"):
        print(name, a+b+sum(n))

    add.console()


在终端运行 python main.py --help 则会输出以下内容:

    usage: command.py [-h] [--name NAME] a b [n ...]

    positional arguments:
    a            加数 (int)
    b            被加数 (float)
    n            可变长参数,其他被加数 (float)

    optional arguments:
    -h, --help   show this help message and exit
    --name NAME  姓名 (str default 无名)

"""

__author__ = "WeiFeng Tu"
__status__ = "Pre-Alpha"
__version__ = "0.0.1"
__date__ = "2022-08-23"
__all__ = (
    "command",
)


from functools import wraps
from inspect import getfullargspec
from argparse import ArgumentParser
from re import split


class MyArgumentParser(ArgumentParser):
    __helps = {}

    def load_helps_from_func(self, func):
        flag = False
        self.description = self.description or ""
        for rawline in func.__doc__.split("\n"):
            line = rawline.strip("\r\t\n ")
            if flag:
                if line:
                    arg, help = line.split(":", maxsplit=1)
                    self.__helps[arg.strip("\r\t\n ")] = help.strip("\r\t\n ")
                else:
                    return
            elif line.startswith("Args:"):
                flag = True
            else:
                self.description += rawline

    def set_helps(self, helps):
        self.__helps = helps

    def add_argument(self, *args, **kwargs):
        arg = kwargs.get("dest", args[0]).strip("-")
        if arg != "h":
            type = kwargs.get("type")
            default = kwargs.get("default")
            help = ""
            if type:
                help = type.__name__
            if default is not None:
                help += f" default {default}"
            kwargs["help"] = f'{self.__helps.get(arg, "")} ({help})'
        return super().add_argument(*args, **kwargs)


def command(**helps):

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        def wrapped_console():
            argspec = getfullargspec(f)

            def parse():
                parser = MyArgumentParser()
                parser.set_helps(helps)

                for i, arg in enumerate(argspec.args):
                    type = argspec.annotations.get(arg)

                    if argspec.defaults:
                        j = i - len(argspec.args) + len(argspec.defaults)
                        if j >= 0:
                            parser.add_argument(
                                arg, nargs="?", default=argspec.defaults[j], type=type)
                        else:
                            parser.add_argument(arg, type=type)
                    else:
                        parser.add_argument(arg, type=type)

                if argspec.varargs:
                    type = argspec.annotations.get(argspec.varargs)
                    parser.add_argument(argspec.varargs, nargs="*", type=type)
                if argspec.kwonlydefaults:
                    for k, v in argspec.kwonlydefaults.items():
                        type = argspec.annotations.get(k)
                        parser.add_argument(f"--{k}", default=v, type=type)
                if argspec.varkw:
                    type = argspec.annotations.get(argspec.varkw)
                    parser.add_argument(
                        f"--{argspec.varkw}", nargs="*", type=type)
                args = parser.parse_args()
                return args

            args = parse()

            def get_kw():
                kw = {}
                if argspec.varkw:
                    for i in getattr(args, argspec.varkw) or []:
                        k, v = split(r"=", i, maxsplit=1)
                        kw[k] = v
                return kw

            def get_default_kw():
                default_kw = {}
                if argspec.kwonlydefaults:
                    for arg in argspec.kwonlydefaults.keys():
                        default_kw[arg] = getattr(args, arg)
                return default_kw

            def get_varargs():
                if argspec.varargs:
                    return getattr(args, argspec.varargs)
                return []

            def get_args():
                return [getattr(args, arg) for arg in argspec.args]

            return wrapped(*get_args(),
                           *get_varargs(),
                           **get_default_kw(),
                           **get_kw())

        wrapped.console = wrapped_console

        return wrapped
    return wrapper


def main():

    @command(
        a="加数",
        b="被加数",
        n="可变长参数,其他被加数",
        name="姓名"
    )
    def add(a: int, b: float, *n: float, name: str = "无名"):
        print(name, a+b+sum(n))

    add.console()


if __name__ == "__main__":
    main()
