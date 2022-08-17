#! /usr/bin/env python3
"""This module get the title and h1 tags of the website."""


import sys
import argparse
from typing import Any, Union
import requests
import validators
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString


def get_title_tag(code: str) -> Union[str, None]:
    """Get the title tag of the site.

    code: the HTML code.
    """
    soup: BeautifulSoup = BeautifulSoup(code, 'html.parser')
    title: Tag | NavigableString | None = soup.find('title')

    if title:
        return str(title)

    return None


def get_heading_tag(code: str) -> Union[str, None]:
    """Get the first h1 tag of the site.

    code: the HTML code.
    """
    soup: BeautifulSoup = BeautifulSoup(code, 'html.parser')
    heading: Tag | NavigableString | None = soup.find('h1')

    if heading:
        return str(heading)

    return None


def fetch_html_code(url: str) -> str:
    """Fetch the HTML code.

    url: the website url
    """
    if not validators.url(url):
        sys.exit('Incorrect url')

    try:
        result: Any = requests.get(url, timeout=10)

        if result.status_code == 200:
            return result.text

        # result.status_code is 404
        sys.exit('Page not found')

    except requests.exceptions.RequestException as err:
        sys.exit(err)


def create_parser_args() -> argparse.Namespace:
    """Convert argument strings to objects and assign them as
    attributes of the namespace.

    Return the populated namespace.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Get the title and heading 1 of the site'
    )

    parser.add_argument('url', help='The website URL')

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '--title',
        action='store_true',
        help='The website title'
    )

    group.add_argument(
        '--heading',
        action='store_true',
        help='The website heading 1'
    )

    return parser.parse_args()


def get_title(url: str) -> Union[str, None]:
    """Get the title of the web page."""
    html_code: str = fetch_html_code(url)

    return get_title_tag(html_code)


def get_heading(url: str) -> Union[str, None]:
    """Get the heading 1 of the web page."""
    html_code: str = fetch_html_code(url)

    return get_heading_tag(html_code)


def main():
    """Get the title and heading 1 of the web page entered by the user."""
    args: argparse.Namespace = create_parser_args()

    html_code: str = fetch_html_code(args.url)

    # If the user entered only URL
    if not args.title and not args.heading:
        print(get_title_tag(html_code))
        print(get_heading_tag(html_code))

    # If the user has entered the URL and title
    if args.title:
        print(get_title_tag(html_code))

    # If the user has entered the URL and heading
    if args.heading:
        print(get_heading_tag(html_code))
