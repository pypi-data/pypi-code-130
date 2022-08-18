import argparse
from print_report import show_statistic, print_report_cli

parser = argparse.ArgumentParser()

parser.add_argument(
    "--files",
    type=str,
    help="Input a folder_path",
)

parser.add_argument(
    '--driver',
    type=str,
    help="Input a driver",
)


def select_action(args):
    if args.driver and args.files:
        return show_statistic(args.driver, args.files)
    elif args.files:
        slice_index = args.files.rfind('-') - 1
        return print_report_cli(args.files[slice_index:], args.files[:slice_index])


if __name__ == "__main__":
    args = parser.parse_args()
    print(select_action(args))
