import unittest
from Orange.widgets.tests.base import WidgetTest

from orangecontrib.finecon.widgets.pyjulia import OWPyJuliaScript


class ExampleTests(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)


class TestMyWidget(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(OWPyJuliaScript)

    def test_addition(self):
        self.assertEqual(1 + 1, 2)
