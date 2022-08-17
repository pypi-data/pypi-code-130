import argparse

DESCRIPTION = 'Compares two configuration files and shows a difference.'


def run(): 
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    parser.add_argument('-f', '--format', help='set format of output')
    args = parser.parse_args()
    return args
