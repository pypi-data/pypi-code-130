# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import sys

import click
import requests
import ipaddress

DEFAULT_SERVER_URLS = [
    "https://zencore.cn/ipinfo",
    "https://sr1.zencore.cn/ipinfo",
    "https://sr2.zencore.cn/ipinfo",
]

def get_outgoing_ip(server_urls=None):
    if not server_urls:
        server_urls = DEFAULT_SERVER_URLS
    for url in server_urls:
        try:
            response = requests.get(url)
        except Exception:
            continue
        if response.status_code == 200 and response.content:
            try:
                ipaddress.IPv4Address(response.text)
                return response.text
            except:
                pass
            try:
                ipaddress.IPv6Address(response.text)
                return response.text
            except:
                pass
    return None

@click.command()
@click.option("--url", required=False, multiple=True, help="Server url. Can apply multiple times.")
@click.option("-q", "--quiet", is_flag=True, help="Don't show error information.")
def main(url, quiet):
    server_urls = url
    ip = get_outgoing_ip(server_urls)
    if ip:
        print(ip)
        sys.exit(0)
    else:
        if not quiet:
            print("get outgoing ip failed...", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
