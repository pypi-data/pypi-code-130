#!/usr/bin/env python3
import glob
import os
import errno
import argparse


def list(path):
    q = os.path.join(path, '*')
    namelen = 0
    dirs = []
    files = []
    for file in glob.glob(q):
        namelen = max(namelen, len(file.replace(path, '')))
        if os.path.isdir(file):
            dirs.append(file)
        else:
            files.append(file)

    for file in sorted(dirs) + sorted(files):
        if file.endswith('uevent'):
            continue

        if not os.path.isfile(file):
            print(file[len(path):])
            continue

        display = file[len(path):].ljust(namelen + 2, '.')
        try:
            with open(file, 'r') as handle:
                data = handle.read().strip()
            print(display, data)
        except OSError as e:
            if e.errno in errno.errorcode:
                print(display, f'[-{errno.errorcode[e.errno]}]')
            else:
                print(display, e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', default='.', nargs='?', help='Directory to open')
    args = parser.parse_args()
    list(args.path)


if __name__ == '__main__':
    main()
