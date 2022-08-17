import sys
import json
import pathlib
import dataclasses

from .constants import *


@dataclasses.dataclass
class Config:
    """
    Config object to store headers, cookies, and any
    data other than the payload to be sent to the Zomato API.
    """

    res_ids: list[int]
    headers: dict[str, str]
    cookies: dict[str, str]

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=2)

    @classmethod
    def from_config_file(
        cls, config_file: pathlib.Path = pathlib.Path(DEFAULT_CONFIG_FILE)
    ) -> "Config":

        try:
            with open(config_file) as f:
                data = json.load(f)

            res_ids = data["res_ids"]
            headers = data["headers"]
            cookies = data["cookies"]

            return cls(res_ids, headers, cookies)
        except (KeyError, json.JSONDecodeError):
            sys.stderr.write("error: invalid config file")
            sys.exit(1)
        except FileNotFoundError:
            sys.stderr.write(f'error: config file "{config_file}" not found')
            sys.exit(1)

    @classmethod
    def from_node_fetch(cls, node_fetch: str) -> "Config":
        """
        Generate a config from a NodeJS fetch request. Record as
        POST request to the fetch-order-by-states endpoint, right
        click the request and select "Copy as Node.js fetch".

        Pass the copied fetch function into this function and a
        config dictionary will be generated.
        """

        lbrace_idx, rbrace_idx = node_fetch.find("{"), node_fetch.rfind("}")
        fetch_options = json.loads(node_fetch[lbrace_idx : rbrace_idx + 1])

        fetch_headers = fetch_options["headers"]
        fetch_body = json.loads(fetch_options["body"])

        res_ids = fetch_body["res_ids"]
        headers = DEFAULT_HEADERS | {
            "x-zomato-csrft": fetch_headers["x-zomato-csrft"],
            "x-zomato-trace-id": fetch_headers["x-zomato-trace-id"],
        }

        return cls(res_ids, headers, cls._prepare_cookies(fetch_headers["cookie"]))

    @staticmethod
    def _prepare_cookies(compressed_cookies: str) -> dict:
        """Prepares auth cookies for the request"""
        cookies: dict[str, str] = {}
        raw_cookie_list: list[str] = compressed_cookies.split("; ")

        for cookie in raw_cookie_list:
            sep_idx = cookie.find("=")
            key, value = cookie[:sep_idx], cookie[sep_idx + 1 :]
            if key == "locus":
                continue
            cookies[key] = value

        return cookies
