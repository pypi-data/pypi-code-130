# Copyright (C) 2022 Panther Labs Inc
#
# Panther Enterprise is licensed under the terms of a commercial license available from
# Panther Labs Inc ("Panther Commercial License") by contacting contact@runpanther.com.
# All use, distribution, and/or modification of this software, whether commercial or non-commercial,
# falls under the Panther Commercial License to the extent it is permitted.

# coding=utf-8
# *** WARNING: generated file
import ast
import typing
import unittest
import inspect
from . import detection

__all__ = ["PantherPythonFilterTestCase"]


class PantherPythonFilterTestCase(unittest.TestCase):
    @staticmethod
    def _parseFilterFunc(pfilter: detection.PythonFilter) -> typing.Any:
        func_src = inspect.getsource(pfilter.func)
        sourcefile = inspect.getsourcefile(pfilter.func) or ""
        root_ast = ast.parse(func_src, filename=sourcefile, mode="exec")

        ns = dict(typing=typing)
        exec(ast.unparse(root_ast), ns)
        func: typing.Callable[..., bool] = ns[pfilter.func.__name__]  # type: ignore
        return func

    def _callParsedFilterFunc(
        self, pfilter: detection.PythonFilter, obj: typing.Any
    ) -> typing.Any:
        func = self._parseFilterFunc(pfilter)
        return func(obj, pfilter.params)

    def assertFilterIsValid(self, test_filter: detection.PythonFilter) -> None:
        self.assertIsInstance(
            test_filter,
            detection.PythonFilter,
            "filter is not an instance of PythonFilter",
        )

        try:
            func = self._parseFilterFunc(test_filter)
        except BaseException as err:
            self.fail(f"unable to parse func value: {err}")

        self.assertTrue(callable(func), "parsed filter is not callable")

    def assertFilterMatches(
        self, test_filter: detection.PythonFilter, obj: typing.Any
    ) -> None:
        unparsed_result = test_filter.func(obj, test_filter.params)
        self.assertTrue(unparsed_result)

        parsed_result = self._callParsedFilterFunc(test_filter, obj)
        self.assertEqual(
            unparsed_result,
            parsed_result,
            "result from parsed version of filter does not match unparsed result",
        )

    def assertFilterNotMatches(
        self, test_filter: detection.PythonFilter, obj: typing.Any
    ) -> None:
        unparsed_result = test_filter.func(obj, test_filter.params)
        self.assertFalse(unparsed_result)

        parsed_result = self._callParsedFilterFunc(test_filter, obj)
        self.assertEqual(
            unparsed_result,
            parsed_result,
            "result from parsed version of filter does not match unparsed result",
        )
