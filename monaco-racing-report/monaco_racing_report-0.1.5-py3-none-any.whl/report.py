import argparse
import pathlib
import print_report

parser = argparse.ArgumentParser()

parser.add_argument('--files', type=pathlib.Path, required=True, help='Input a folder_path')
parser.add_argument('--asc', action='store_true')
parser.add_argument('--desc', action='store_true')
parser.add_argument('--driver', type=str, help="Input a driver's name surname")


def select_action(args):
    print(args)
    if args.driver and args.files:
        return print_report.show_statistic(args.driver, args.files)
    elif args.files and args.asc:
        return print_report.print_report_cli(True, args.files)
    elif args.files and args.desc:
        return print_report.print_report_cli(False, args.files)
    elif args.files:
        return print_report.print_report_cli(None, args.files)


if __name__ == "__main__":
    args = parser.parse_args()
    print(select_action(args))
