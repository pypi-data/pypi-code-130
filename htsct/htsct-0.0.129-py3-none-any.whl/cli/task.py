from argparse import ArgumentParser
from pathlib import Path
from random import choice
from shutil import move
from time import sleep
from htsct.utils.tools import search, Pipe


class CLICommand:
    """文件自动移动

    移动指定文件夹下的文件到当前文件夹并等待对应程序消耗文件后自动补充
    """

    @staticmethod
    def add_argments(parser: ArgumentParser):
        add = parser.add_argument
        add("--fileType", default=".cif", dest="fileType", help="自动管理的文件类型[default:.cif]")
        add("--folderNum", default=6, dest="folderNum", help="任务文件夹数量[default:]")
        add("--maxFile", default=1, dest="maxFile", help="单次最大排队文件[default:1]")
        add("--srcFolder", default="src", dest="srcFolder", help="存放资源文件夹[default:src]")
        add("--node", default=1, dest="node", help="提交的节点数[default:1]")
        add("--core", default=24, dest="core", help="提交的核数[default:24]")
        add("--file", default=None, dest="file", help="执行的python脚本文件[default:None]")

    @staticmethod
    def run(args, parser):
        fileType = args.fileType
        folderNum = int(args.folderNum)
        maxFile = int(args.maxFile)
        node = int(args.node)
        core = int(args.core)
        file = args.file
        src = Path(args.srcFolder)
        src.mkdir(exist_ok=True)
        for f in Path(".").iterdir():
            if f.is_file() and f.suffix == fileType:
                f.replace(src / f.name)

        task_folders = [str(i) for i in range(1, folderNum + 1)]
        for task_folder in task_folders:
            Path(task_folder).mkdir(exist_ok=True)
            command = f"htsct qsub --node {node} --core {core}{' --file ' + file if file else ''}"
            print(command)
            pipe = Pipe(command, task_folder)
            print(pipe.stdout, pipe.stderr)

        task_manager(fileType, src.__str__(), task_folders, maxFile)


def __task_manager(ftype, src_folder, task_folders: list, max_file):
    while True:
        src_files = list(search(src_folder, ftype))
        if src_files:
            for task_folder in task_folders:
                task_files = search(task_folder, ftype)
                length = len(list(task_files))
                if length < max_file:
                    src_file = choice(src_files)
                    move(src_file, task_folder)
                    break
        sleep(1)


def task_manager(ftype, src_folder, task_folders: list, max_file=3):
    """用于自动移动指定文件类型到指定目录
    :param ftype: 文件类型(后缀)
    :param src_folder: 源文件夹
    :param task_folders: 目标文件夹列表
    :param max_file: 最大移动数目
    """
    from threading import Thread
    t1 = Thread(target=__task_manager, args=[ftype, src_folder, task_folders, int(max_file)])
    t1.start()
