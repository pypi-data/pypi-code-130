import argparse
import pathlib

from JCompile import compiler

parser = argparse.ArgumentParser(description="compile json file")
parser.add_argument(
    "template_path", type=pathlib.Path, help="path of template json file"
)
parser.add_argument(
    "context_path", type=pathlib.Path, help="path of context json file"
)
parser.add_argument("save_path", type=pathlib.Path, help="path of save file")


def run():
    args = parser.parse_args()
    com_ = compiler.JsonCompiler.from_file(
        template_path=args.template_path, context_path=args.context_path
    )
    com_.to_file(save_path=args.save_path)


if __name__ == "__main__":
    run()
