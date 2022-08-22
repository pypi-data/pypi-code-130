import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', action="append", required=True)
parser.add_argument('-i', '--input', required=True)

def cli(argv):
    args = parser.parse_args(argv)

    print(args)

    return 0
