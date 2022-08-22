"""
IPython magic module.
:author: András Aszódi
:date: 2020-11-03
"""

# Implementation note: the class is based on the IPython manual
# See https://ipython.readthedocs.io/en/stable/config/custommagics.html

from sys import stderr

from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.getipython import get_ipython

from .harness import Harness

# -- Classes --

@magics_class
class TestMagic(Magics):
    """
    Defines magics to run a piece of code wrapped in a unit test harness.
    """

    def __init__(self, tests=None):
        """
        Initialiser. Registers the created instance with IPython.
        :param tests: If `None`, then no tests are registered (this is the default).
            If a dictionary containing test name - expected value pairs or the name
            of a JSON file corresponding to such a dictionary, then
            they are registered using the `register_tests()` method.
        """
        # Set up this TestMagic instance as an IPython magic
        super().__init__(None)
        ipython = get_ipython()
        ipython.register_magics(self)

        # Test names and expected values
        self._tests = {}
        self.register_tests(tests)

    def register_test(self, testname, expvalue):
        """
        Registers a test (stores the expected value)
        :param testname: The name of the test
        :param expvalue: The expected value coming from the test
        """
        self._tests[testname] = expvalue

    def register_tests(self, tests):
        """
        Convenience method to register many tests at once.
        Invokes the `register_test()` method on all key-value pairs provided in `tests`
        :param tests: Either a dictionary with test name - expected value pairs,
            or the name of a JSON file from which such a dictionary can be `load`-ed.
        Errors are swallowed silently.
        """
        # local function
        def reg_from_dir(t):
            for testname, expvalue in t.items():
                self.register_test(testname, expvalue)

        try:
            if isinstance(tests, str):
                import json
                with open(tests) as inf:
                    reg_from_dir(json.load(inf))
            elif isinstance(tests, dict):
                reg_from_dir(tests)
            else:
                pass
        except Exception as err:
            print(f"ERROR: {str(err)} in 'register_tests', ignored")

    @cell_magic
    def testexpr(self, testname, cell):
        """
        IPython 'cell magic' to wrap a piece of code (sequence of expressions)
        in a unit test harness and have it run.
        Usage within an IPython cell:
        +-------------------------+
        | %%testexpr testname     |
        | Python code line        |
        | ... more code lines ... |
        +-------------------------+

        :param testname: Identifies the test harness to be used.
        :param cell: Contents of the cell (the Python code lines)
        :return: The value of the last expression of the cell contents or None
        """
        # Create a Harness instance and test what's in the cell
        harness = Harness()
        ok = harness.test_expr(self._tests[testname], cell)
        if ok:
            print("Test passed :-)")
        else:
            # JupyterLab will print this with a red background
            print("Test failed :-(", file=stderr)
        return harness.last



