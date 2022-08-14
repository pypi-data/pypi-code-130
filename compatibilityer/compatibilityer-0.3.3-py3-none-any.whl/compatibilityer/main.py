from typing import Type

from compatibilityer.convert import convert_dir
from compatibilityer.converter import Converter

import argparse
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("dir", type=Path, help="directory to convert")
    parser.add_argument("output_dir", type=Path, help="directory to output converted files")

    args = parser.parse_args()
    dir_, output_dir = args.dir, args.output_dir
    dir_: Path
    output_dir: Path

    excludes = []

    if output_dir in dir_.glob("**/*"):
        excludes.append(output_dir)

    excludes = ["--exclude", *map(str, excludes)] if excludes else []

    subprocess.run(["rsync", "-a", dir_, output_dir, *excludes], check=True)
    convert_dir(output_dir, Converter)


if __name__ == '__main__':
    main()
