#!/usr/bin/env python3

from twine.commands.upload import upload
from twine.settings import Settings
from argparse import ArgumentParser
import os


def main():

    parser = ArgumentParser()
    parser.add_argument(
        "--official", action="store_true", help="Upload to the official PyPI repository"
    )
    args = parser.parse_args()
    os.system("python -m build")

    upload(
        upload_settings=Settings(repository_name="pypi" if args.official else "testpypi"),
        dists=["dist/*"],
    )


if __name__ == "__main__":
    main()
