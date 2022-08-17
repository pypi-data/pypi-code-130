#!/usr/bin/env python3
from gendiff import run_gendiff, cli


def main():
    args = cli.run()
    run_gendiff.start(args)


if '__name__' == '__main__':
    main()
