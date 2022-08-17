"""This module define unittest for dissect_site module."""


import argparse
import unittest
from typing import TypeVar, Union
from unittest import mock
import requests
from requests.models import Response

from dissect_site.dissect_site import (
    create_parser_args,
    fetch_html_code,
    get_heading_tag,
    get_title_tag,
    get_heading,
    get_title,
    main
)


DST = TypeVar('DST', bound='DissectSiteTest')


class DissectSiteTest(unittest.TestCase):
    """Check out the process of get the title and h1 tags
    of a user-entered site.
    """

    def setUp(self: DST) -> None:
        """Mock the HTML code."""
        self.code_with_title = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>The title tag</title>
                </head>
                <body>
                    <p>This is a paragraph.</p>
                </body>
            </html>
        """
        self.code_with_heading = """
            <!DOCTYPE html>
            <html>
                <body>
                    <h1>This is a heading</h1>
                    <p>This is a paragraph.</p>
                </body>
            </html>
        """
        self.code_with_title_and_heading = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>The title tag</title>
                </head>
                <body>
                    <h1>This is a heading</h1>
                    <p>This is a paragraph.</p>
                </body>
            </html>
        """

    def test_the_html_code_have_the_title(self: DST) -> None:
        """Should return title if present in HTML code."""
        title: Union[str, None] = get_title_tag(self.code_with_title)

        self.assertEqual(title, '<title>The title tag</title>')

    def test_the_html_code_without_title(self: DST) -> None:
        """Should return None if there is no title in the HTML code."""
        title: Union[str, None] = get_title_tag(self.code_with_heading)

        self.assertIsNone(title)

    def test_the_html_code_have_the_heading_tag(self: DST) -> None:
        """Should return heading if present in HTML code."""
        heading: Union[str, None] = get_heading_tag(self.code_with_heading)

        self.assertEqual(heading, '<h1>This is a heading</h1>')

    def test_the_html_code_without_heading_tag(self: DST) -> None:
        """Should return None if there is no heading in the HTML code."""
        heading: Union[str, None] = get_heading_tag(self.code_with_title)

        self.assertIsNone(heading)

    def test_call_exit_if_invalid_url(self: DST) -> None:
        """Should call sys.exit if invalid URL."""
        with mock.patch('sys.exit') as exit_mock:
            fetch_html_code('htpp://example.com')
            self.assertTrue(exit_mock.called)

    @mock.patch('dissect_site.dissect_site.requests.get')
    def test_call_exit_if_timeout_when_fetch_data(
        self: DST,
        mock_requests: mock.MagicMock
    ) -> None:
        """Should call sys.exit if timeout when fetching HTML code."""
        mock_requests.side_effect = requests.exceptions.Timeout()

        with mock.patch('sys.exit') as exit_mock:
            fetch_html_code('https://www.google.com.vn')
            self.assertTrue(exit_mock.called)

    @mock.patch('dissect_site.dissect_site.requests.get')
    def test_call_exit_if_stutus_code_other_200(
        self: DST,
        mock_requests: mock.MagicMock
    ) -> None:
        """Should call sys.exit if timeout when fetching HTML code."""
        mock_requests.status_code.return_value = 404

        with mock.patch('sys.exit') as exit_mock:
            fetch_html_code('https://www.google.com.vn')
            self.assertTrue(exit_mock.called)

    @mock.patch('dissect_site.dissect_site.requests.get')
    def test_call_exit_if_stutus_code_is_200(
        self: DST,
        mock_requests: mock.MagicMock
    ) -> None:
        """Should return the HTML if status code is 200."""
        mock_request_data = mock.Mock(spec=Response)
        mock_request_data.status_code = 200
        mock_request_data.encoding = 'UTF-8'
        mock_request_data.apparent_encoding = 'utf-8'
        mock_request_data.text = self.code_with_title_and_heading

        mock_requests.return_value = mock_request_data

        html_code: str = fetch_html_code('https://www.google.com.vn')

        self.assertEqual(html_code, self.code_with_title_and_heading)

    def test_false_to_create_parser_args(self: DST) -> None:
        """Should call sys.exit when call create_parser_args without url."""
        with mock.patch('sys.exit') as exit_mock:
            create_parser_args()
            self.assertTrue(exit_mock.called)

    @mock.patch('dissect_site.dissect_site.fetch_html_code')
    def test_get_title(
        self: DST,
        mock_fetch_html_code: mock.MagicMock
    ) -> None:
        """Should return the title of the site"""
        mock_fetch_html_code.return_value = self.code_with_title
        url: str = 'https://www.google.com'
        title: Union[str, None] = get_title(url)
        self.assertEqual(title, '<title>The title tag</title>')

    @mock.patch('dissect_site.dissect_site.fetch_html_code')
    def test_get_heading(
        self: DST,
        mock_fetch_html_code: mock.MagicMock
    ) -> None:
        """Should return the title of the site"""
        mock_fetch_html_code.return_value = self.code_with_heading
        url: str = 'https://www.google.com'
        heading: Union[str, None] = get_heading(url)
        self.assertEqual(heading, '<h1>This is a heading</h1>')

    @mock.patch('builtins.print')
    @mock.patch('dissect_site.dissect_site.fetch_html_code')
    @mock.patch('dissect_site.dissect_site.create_parser_args')
    def test_print_title_and_heading(
        self: DST,
        mock_create_parser_args: mock.MagicMock,
        mock_fetch_html_code: mock.MagicMock,
        mock_print: mock.MagicMock,
    ) -> None:
        """Should print the title and heading."""
        mock_create_parser_args.return_value = argparse.Namespace(
            url='https://www.google.com',
            title=False,
            heading=False
        )

        mock_fetch_html_code.return_value = self.code_with_title_and_heading
        main()
        mock_print.assert_has_calls([
            mock.call('<title>The title tag</title>'),
            mock.call('<h1>This is a heading</h1>'),
        ])

    @mock.patch('builtins.print')
    @mock.patch('dissect_site.dissect_site.fetch_html_code')
    @mock.patch('dissect_site.dissect_site.create_parser_args')
    def test_print_title(
        self: DST,
        mock_create_parser_args: mock.MagicMock,
        mock_fetch_html_code: mock.MagicMock,
        mock_print: mock.MagicMock,
    ) -> None:
        """Should print the title."""
        mock_create_parser_args.return_value = argparse.Namespace(
            url='https://www.google.com',
            title=True,
            heading=False
        )

        mock_fetch_html_code.return_value = self.code_with_title
        main()
        mock_print.assert_called_with('<title>The title tag</title>')

    @mock.patch('builtins.print')
    @mock.patch('dissect_site.dissect_site.fetch_html_code')
    @mock.patch('dissect_site.dissect_site.create_parser_args')
    def test_print_heading(
        self: DST,
        mock_create_parser_args: mock.MagicMock,
        mock_fetch_html_code: mock.MagicMock,
        mock_print: mock.MagicMock,
    ) -> None:
        """Should print the heading."""
        mock_create_parser_args.return_value = argparse.Namespace(
            url='https://www.google.com',
            title=False,
            heading=True
        )

        mock_fetch_html_code.return_value = self.code_with_heading
        main()
        mock_print.assert_called_with('<h1>This is a heading</h1>')
