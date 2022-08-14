import unittest

from compatibilityer.converter import Converter
from compatibilityer.convert import convert

import ast
from textwrap import dedent


class TestConverter(unittest.TestCase):
    def assertEqualCode(self, actual, expected):
        self.assertEqual(ast.unparse(ast.parse(actual)), ast.unparse(ast.parse(expected)))

    def test_converter(self):
        code = dedent("""\
        from typing import TypeAlias, List

        def test(a: int, b) -> list[int] | None:
            return [a]
        """)
        expected = dedent("""\
        from typing import List

        def test(a: 'int', b) -> 'list[int] | None':
            return [a]
        """)

        self.assertEqualCode(convert(code), expected)

    def test_none_import(self):
        code = dedent("""\
        from typing import Self
        """)
        expected = dedent("""\
        """)  # None

        self.assertEqualCode(convert(code), expected)

    def test_type_alias(self):
        code = dedent("""\
        from typing import TypeAlias
        
        a: TypeAlias = list[int]

        l: a = [1, 2, 3]
        """)
        expected = dedent("""\
        a: 'TypeAlias' = 'list[int]'

        l: 'a' = [1, 2, 3]
        """)

        self.assertEqualCode(convert(code), expected)

    def test_str_annotation(self):
        code = dedent("""\
        a: 'list[int]' = [1, 2, 3]
        """)
        expected = dedent("""\
        a: '\\'list[int]\\'' = [1, 2, 3]
        """)

        self.assertEqualCode(convert(code), expected)

    def test_match(self):
        # ToDo
        pass
