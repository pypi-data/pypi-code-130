import os
import sys
import argparse

from .api import walk_dir, get_human_readable


def ls(args):

    summary = {
        'files': 0,
        'size': 0,
    }

    for compressed_path in walk_dir(
        args.directory, 
        recursive=args.recursive, 
        include=args.include, 
        exclude=args.exclude
    ):
        output = compressed_path.format(args.format)

        if args.size:
            size = compressed_path.size()
            if args.summary:
                    summary['size'] += size
            if args.human_readable:
                size = get_human_readable(size)
            output = '{:<15}{}'.format(size, output)

        if args.summary:
            summary['files'] += len(compressed_path)

        print(output)

    if args.summary:
        if args.human_readable:
            summary['size'] = get_human_readable(summary.get('size'))
        print('files: {files}, size: {size}'.format(**summary))


def main():
    
    description = """"""

    parser = argparse.ArgumentParser(
        description=description, 
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers()
    ls_subparser = subparsers.add_parser(
        'ls', 
        help='List a directory recursively and get files in a compressed format'
    )
    ls_subparser.add_argument(
        dest='directory', 
        help="(see above)",
        nargs='?',
        default=os.getcwd()
    )
    ls_subparser.add_argument(
        '-i', 
        '--include', 
        nargs='*',
        help='list of regexes to include'
    )
    ls_subparser.add_argument(
        '-e', 
        '--exclude', 
        nargs='*',
        help='list of regexes to exclude'
    )
    ls_subparser.add_argument(
        '-s', 
        '--size',
        action='store_true',
        help='size in bytes'
    )
    ls_subparser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='Recurse through directories'
    )
    ls_subparser.add_argument(
        '-m', 
        '--human_readable',
        action='store_true',
        help='human readable size'
    )
    ls_subparser.add_argument(
        '-f', 
        '--format',
        help='choose iteration set format'
    )
    ls_subparser.add_argument( 
        '--summary',
        action='store_true',
        help='summarize the list'
    )
    ls_subparser.set_defaults(func=ls)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(2)
        
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
