import argparse
import json
import os
from typing import List

import requests


def get_openapi_spec(url):
    """
    Get OpenAPI spec from url
    """

    try:
        response = requests.get(url)
        if response.status_code == 200:
            try:
                return response.json()
            except json.decoder.JSONDecodeError:
                print("Error: OpenAPI spec is not valid JSON ({url})".format(url=url))
    except requests.exceptions.RequestException as e:
        print("Error: Failed to get OpenAPI spec from url ({url})".format(url=url))
        print(e)

    return None


class MergeOpenAPI:
    def __init__(self, config_file: str):
        """
        Merge OpenAPI spec with info
        """

        with open(config_file, "r") as f:
            config: dict = json.load(f)
            assert isinstance(config, dict), "Invalid config file"

        self.spec = config["spec"]
        self._openapi_urls = config.get("openapi_urls", [])
        self._set_initial_data()

    def _set_initial_data(self):
        if "paths" not in self.spec:
            self.spec["paths"] = {}
        if "components" not in self.spec:
            self.spec["components"] = {}
        if "schemas" not in self.spec["components"]:
            self.spec["components"]["schemas"] = {}
        if "securitySchemes" not in self.spec["components"]:
            self.spec["components"]["securitySchemes"] = {}

    def merge_paths(self, spec: dict):
        """
        Merge paths
        """

        if "paths" in spec:
            self.spec["paths"].update(spec["paths"])

    def merge_components(self, spec: dict):
        """
        Merge components
        """

        if "schemas" in spec["components"]:
            self.spec["components"]["schemas"].update(spec["components"]["schemas"])
        if "securitySchemes" in spec["components"]:
            self.spec["components"]["securitySchemes"].update(
                spec["components"]["securitySchemes"]
            )

    def merge(self, openapi_urls: List[str]):
        for url in set(openapi_urls + self._openapi_urls):
            openapi_spec = get_openapi_spec(url)
            if openapi_spec:
                self.merge_paths(openapi_spec)
                self.merge_components(openapi_spec)

    def write(self, output_file: str):
        """
        Write spec to file
        """

        with open(output_file, "w") as f:
            json.dump(self.spec, f, indent=4, ensure_ascii=False)


def main():
    config_file = os.path.join(os.getcwd(), "merge_openapi.json")
    f = MergeOpenAPI(config_file)
    parser = argparse.ArgumentParser(description="Merge OpenAPI specs")
    try:
        parser.add_argument(
            "-o",
            "--output",
            dest="output_file",
            help="Output file (OpenAPI Spec)",
            default=os.path.join(os.getcwd(), "merged_openapi.json"),
        )
        parser.add_argument(
            "-u",
            "--url",
            dest="openapi_urls",
            help="OpenAPI spec url",
            action="append",
            default=[],
        )
        args = parser.parse_args()
        if os.path.isfile(args.output_file):
            print(
                "Error: Output file already exists ({output_file})".format(
                    output_file=args.output_file
                )
            )
            exit(1)

        print("Merging OpenAPI specs...")
        f.merge(args.openapi_urls)
        print("Writing OpenAPI spec to file...")
        f.write(args.output_file)
        print("Done")
    except argparse.ArgumentError as e:
        parser.error(e)


if __name__ == "__main__":
    main()
