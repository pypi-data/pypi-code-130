from argparse import ArgumentParser
from shutil import copy

from htsct.constants import HTS_HOME
from htsct.utils.resources import files as packageFiles


class CLICommand:
    """初始化配置文件，设置环境变量

    说明：
        1.在$HOME下导出.htsct.toml配置文件
    """

    @staticmethod
    def add_argments(parser: ArgumentParser):
        pass

    @staticmethod
    def run(args, parser):
        print("正在初始化设置...")
        copy_statics()


def copy_statics():
    print("Start initialize...")
    HTS_HOME.mkdir(parents=True, exist_ok=True)
    files = packageFiles("htsct.statics").iterdir()
    for file in files:
        try:
            print(f"Copy '{file}' to '{HTS_HOME}'", end=" ... ")
            copy(file, HTS_HOME)
            print("done")
        except Exception as e:
            print(e)
