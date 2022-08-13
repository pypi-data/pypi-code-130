import argparse
from urldt.__version__ import __version__


parser = argparse.ArgumentParser(
    prog='urldt',
    description="""check if URL is available."""
)

parser.add_argument(
    '-f', '--file',
    action='store',
    type=str,
    help="""The csv file that contain the targets."""
)

parser.add_argument(
    '-o', '--output',
    action='store',
    type=str,
    help="""Output the result of detecting."""
)

parser.add_argument(
    '-q', '--quiet',
    action='store_true',
    help="""Not output the result to terminal."""
)

parser.add_argument(
    '-v', '--version',
    action='version',
    version='%(prog)s '+__version__
)
