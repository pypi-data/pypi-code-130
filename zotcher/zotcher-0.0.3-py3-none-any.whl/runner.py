import io
import sys
import json
import pathlib
import datetime
import argparse

import requests

from .utils import *
from .constants import *
from . import __version__
from .payload import Payload
from .configurator import Config


def setup_configurator(configurator: argparse.ArgumentParser):

    configurator.add_argument(
        "infile", type=argparse.FileType("r"), help="file with a NodeJS fetch to parse"
    )
    configurator.add_argument(
        "-o",
        "--outfile",
        default="config.json",
        help="output file to store config data",
    )


def setup_fetcher(fetcher: argparse.ArgumentParser):

    fetcher.add_argument(
        "-u",
        "--url",
        type=valid_url,
        default=DEFAULT_URL,
        help="Zomato endpoint to send payload",
    )
    fetcher.add_argument(
        "-D",
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help="number of days to fetch data for",
    )
    fetcher.add_argument(
        "-o",
        "--offset",
        type=int,
        default=0,
        help="offset to start from (default: 0)",
    )
    fetcher.add_argument(
        "-n",
        "--number",
        type=int,
        default=20,
        help="number of orders to fetch in a batch (default 20)",
    )
    fetcher.add_argument(
        "outfile",
        help="output file to store response data",
    )
    fetcher.add_argument(
        "-d",
        "--end-date",
        type=valid_date,
        default=datetime.datetime.now().strftime(DATE_FORMAT),
        help='end date to fetch orders 10 days prior to (default: today, format: "YYYY-MM-DD")',
    )
    fetcher.add_argument(
        "-c",
        "--config-file",
        type=pathlib.Path,
        default=pathlib.Path(DEFAULT_CONFIG_FILE),
        help="path to JSON config file (default config.json)",
    )


def run_config(infile: io.TextIOWrapper, outfile: str):
    config = Config.from_node_fetch(infile.read())
    with open(outfile, "w+") as f:
        f.write(config.to_json())
    infile.close()


def run_fetch(
    url: str,
    days: int,
    offset: int,
    number: int,
    outfile: str,
    end_date: str,
    config_file: pathlib.Path,
):

    config = Config.from_config_file(config_file)
    payload = Payload(
        days=days,
        count=number,
        offSet=offset,
        end_date=end_date,
        res_ids=config.res_ids,
    )

    with requests.Session() as session, open(outfile, "w+") as of:

        # begin json list
        of.write("[")

        session.headers.update(config.headers)
        session.cookies.update(config.cookies)

        while True:
            response = session.post(url, data=payload.to_json())

            if not response.ok:
                sys.stderr.write(f"error: {response.status_code} {response.reason}")
                continue

            resp_data: dict = response.json()

            if new_orders := resp_data.get("orders"):
                for idx, order in enumerate(new_orders):
                    of.write(json.dumps(order, indent=2))
                    if idx != len(new_orders) - 1:
                        of.write(",")

            if len(new_orders) < payload.count:
                break
            else:
                of.write(",")

            payload.offSet += len(new_orders)

        of.write("]")


def run():

    parser = argparse.ArgumentParser(
        description="a CLI to interact with the (unofficial) Zomato Partner API"
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    subparsers = parser.add_subparsers(required=True, dest="command")

    configurator = subparsers.add_parser(
        "config",
        aliases=["c"],
        help="generate a config file",
        description="generate a config file",
    )
    fetcher = subparsers.add_parser(
        "fetch",
        aliases=["f"],
        help="fetches data from the API",
        description="fetches data from the API",
    )

    setup_fetcher(fetcher)
    setup_configurator(configurator)

    args = vars(parser.parse_args())

    spinner = AsyncSpinner()
    spinner.start()

    command = args.pop("command", "").lower()
    command_funcs = {
        "f": run_fetch,
        "c": run_config,
        "fetch": run_fetch,
        "config": run_config,
    }

    runner = command_funcs.get(command)

    if runner:
        runner(**args)
    else:
        parser.print_help()

    spinner.stop()
