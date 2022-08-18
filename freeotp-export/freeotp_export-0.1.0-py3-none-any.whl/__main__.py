#!/usr/bin/env python3

from __future__ import annotations

from base64 import b32encode
import json
import logging
from sys import argv
from typing import Any, Dict
from urllib.parse import urlencode, urlunparse
import xml.etree.ElementTree as ET

import qrcode


logging.basicConfig()  # level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def process_file(filename: str):
    LOGGER.debug("Loading file %r", filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    token_order = None
    entries = {}
    for entry in root.iter("string"):
        name = entry.attrib["name"]
        LOGGER.debug("Loading %r...", name)
        data = json.loads(entry.text)
        if name == "tokenOrder":
            token_order = data
            continue
        LOGGER.debug("Parsed data: %r", data)
        entries[name] = data

    for name in token_order:
        print_entry(name, entries.pop(name))
    for name, data in entries.items():
        print_entry(name, data)


def print_entry(name: str, data: Dict[str, Any]):
    print(name)
    try:
        uri = parse_entry(name, data)
    except Exception as e:
        print("Couldn't parse entry:", e)
        return

    print(uri)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(uri)
    qr.make(fit=True)
    qr.print_ascii()
    print("\n\n")


def parse_entry(name: str, data: str) -> str:
    secret = b32encode(bytes([x + 256 & 255 for x in data["secret"]])).rstrip(b"=")

    params = {
        "secret": secret,
        "issuer": data["issuerExt"],
    }
    if data["algo"] != "SHA1":
        params["algorithm"] = data["algo"]
    if data["digits"] != 6:
        params["digits"] = data["digits"]
    if data["type"].lower == "hotp":
        params["counter"] = data["counter"]
    if data["period"] != 30:
        params["period"] = data["period"]

    uri = urlunparse(
        (
            "otpauth",
            data["type"].lower(),
            name,
            "",
            urlencode(params),
            "",
        )
    )
    return uri


def main():
    if len(argv) < 2:
        print("Usage: {} tokens.xml".format(argv[0]))
        exit(1)
    file = argv[1]

    process_file(file)


if __name__ == "__main__":
    main()
