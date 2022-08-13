from urldt.cli import parser
from urldt.scanner import Scanner
from urldt.utils import read_targets, write_result


args = parser.parse_args()


def main():
    scanner = Scanner()

    if not args.file:
        print('targets information file is needed!')
        exit(1)
    else:
        scanner.input_file = args.file

    if args.quiet:
        scanner.is_quiet = args.quiet

    if args.output:
        scanner.output_file = args.output

    scanner.run()


if __name__ == '__main__':
    main()
