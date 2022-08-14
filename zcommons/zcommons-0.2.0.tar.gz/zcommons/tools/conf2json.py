import argparse
import configparser
import json

from zcommons.config_dict import ConfigDict


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="convert config key-value pairs to json")
    parser.add_argument("input", metavar="N", type=str, nargs="+", help="input config files")
    parser.add_argument("--output", "-o", type=str, required=False, help="output json file, default is stdout")
    parser.add_argument("--allow-no-value", "--allow_no_value", action="store_true")
    parser.add_argument("--delimiters", type=str, required=False, default=None)
    parser.add_argument("--comment-prefixes", "--comment_prefixes", type=str, required=False, default=None)

    return parser.parse_args(args)


def main(args):
    cd = ConfigDict()
    for filepath in args.input:
        cp = configparser.ConfigParser()
        cp.read(filepath)
        for k, sec in cp.items():
            if k == "DEFAULT":
                if len(sec) != 0:
                    cd.update(ConfigDict(dict(sec)))
                continue
            else:
                cd.update(ConfigDict({
                    k: dict(sec)
                }))
    if args.output is None or args.output == "":
        print(json.dumps(dict(cd), indent=4))
    else:
        with open(args.output, "w") as f:
            f.write(json.dumps(dict(cd), indent=4))


def cli_main(args=None):
    args = parse_args(args)
    main(args)

if __name__ == "__main__":
    cli_main()
