import unittest
from package import module


class TestClass(unittest.TestCase):
    def setUp(self):
        self.instance = module.CorDate()
        self.test_date = '19880416'

    def tearDown(self):
        del self.instance

    def test_get_correct_array(self):
        res = self.instance.get_correct_array(self.test_date)
        self.assertEqual(res, ['19880416'])
        
    def test_get_correct_one(self):
        res = self.instance.get_correct_one(self.test_date)
        self.assertEqual(res, '19880416')

    def test_load_date_dictionary(self):
        res = self.instance.load_date_dictionary()
        self.assertEqual(res, True)

    def test_look_up_array(self):
        self.instance.load_date_dictionary()
        res = self.instance.look_up_array(self.test_date)
        self.assertEqual(res[0].term, '19880416')

    def test_look_up_one(self):
        self.instance.load_date_dictionary()
        res = self.instance.look_up_one(self.test_date)
        self.assertEqual(res.term, '19880416')