import unittest
from datetime import datetime

from devlibx_avro_helper.month_data import MonthDataAvroHelper


class TestingMonthDataAvroHelper(unittest.TestCase):

    def test_get_keys_for_month(self):
        date_time_str = '05/08/22 01:55:19'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
        helper = MonthDataAvroHelper()
        results = helper.get_keys_for_month(date_time_obj)
        print(results)
        self.assertEqual(5, len(results))
        self.assertEqual("8-1", results[0])
        self.assertEqual("8-2", results[1])
        self.assertEqual("8-3", results[2])
        self.assertEqual("8-4", results[3])
        self.assertEqual("8-5", results[4])

    def test_parsing(self):
        # Test 1
        base64Str = "AgIGNy01BAAAAAAC"
        helper = MonthDataAvroHelper()
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(2, result["days"]["7-5"], "It should be 2")

        base64Str = "AgoGNy0xAgY3LTICBjctMwIGNy00AgY3LTUKAAAAAAI="
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(1, result["days"]["7-1"], "It should be 1")
        self.assertEqual(1, result["days"]["7-2"], "It should be 1")
        self.assertEqual(1, result["days"]["7-3"], "It should be 1")
        self.assertEqual(1, result["days"]["7-1"], "It should be 1")
        self.assertEqual(5, result["days"]["7-5"], "It should be 1")
        self.assertEqual(5, len(result["days"]), "It should be 5")

    def test_process_and_return_aggregation_for_month(self):
        base64Str = "AgoGNy0xAgY3LTICBjctMwIGNy00AgY3LTUKAAAAAAI="
        helper = MonthDataAvroHelper()
        result = helper.process(base64Str)
        print(result)
        # Output = {'days': {'7-1': 1, '7-2': 1, '7-3': 1, '7-4': 1, '7-5': 5}, 'days_str': None, 'entity_id': None, 'sub_entity_id': None, 'version': 1}

        date_time_str = '05/07/22 01:55:19'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')

        # if you are looking for data for this month then use can use
        # helper.process_and_return_aggregation_for_this_month(base64Str)
        result = helper.process_and_return_aggregation_for_month(date_time_obj, base64Str)
        self.assertEqual(9, result, "result should be 9")
        # Output = 9


if __name__ == '__main__':
    unittest.main()
