import textwrap
from argparse import ArgumentParser
from os import system
from pathlib import Path

from htsct.utils.tools import Pipe


class CLICommand:
    """bandDecomposedCharge
    """

    @staticmethod
    def add_argments(parser: ArgumentParser):
        add = parser.add_argument
        add("--node", default=1, dest="node")
        add("--core", default=24, dest="core")
        add("--file", default=None, dest="file", help="执行的python脚本文件")
        # add("--path", default=None, dest="path", help="提交脚本路径")

    @staticmethod
    def run(args, parser):
        node = args.node
        core = args.core
        file = args.file
        # path = args.path
        Path("run").unlink(missing_ok=True)
        if not file:
            script = textwrap.dedent(f"""
                        from htsct import qsub, band_high_throughput
                        if __name__ == "__main__":
                            qsub({node}, {core})
                            band_high_throughput()""").lstrip()
            with open("qsub.py", "w+") as fd:
                fd.write(script)
            pipe = Pipe("python qsub.py\n", ".")
            print(pipe.stdout, pipe.stderr)
        else:
            system(f"python {file}\n")
