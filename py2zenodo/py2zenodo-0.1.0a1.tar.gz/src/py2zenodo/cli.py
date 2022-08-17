import argparse
import pathlib

from .py2zenodo import upload


def parse_args():
    parser = argparse.ArgumentParser(
        description="Python wrapper for Zenodo REST API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-f", "--files", nargs="+", help="Files to upload.")
    parser.add_argument("-t", "--token", required=True, help="Access token.")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    for filepath in map(pathlib.Path, args.files):
        upload(filepath, args.token)
