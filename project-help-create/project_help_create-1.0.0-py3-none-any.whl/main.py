import argparse
from src.projhc import utils

parser = argparse.ArgumentParser(description='projhc')
# parser.add_argument('-p', '--print', help='Prints the supplied argument', default='A random string')

parser.add_argument('-f', '--framework',
                    help='choose framework to setup: "django"',
                    default='framework')

parser.add_argument('-d', '--directory',
                    help='directory for your project (default is .)',
                    default='.')

args = parser.parse_args()

if args.framework == 'django':
    if args.directory != '':
        utils.setup_django_project(args.directory)
    else:
        utils.setup_django_project()

# if __name__ == '__main__':
#     pass
