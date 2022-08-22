from dataclasses import field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import List, Union
from unittest import TestCase

from src.compysitions import Compysition, EnumEncodingSetting, TypeAssignmentException


class TestCompysition(TestCase):
    def test_encode_basic(self):
        class TestClass(Compysition):
            index: int = 0
            index2: int = 1
            val: str = "test"
            val2: str = None

        sample_dict = {"index": 3, "val": "test2"}

        encoded = TestClass().from_dict(sample_dict)
        # assert that what came out of the dict was set
        self.assertEqual(sample_dict["index"], encoded.index)
        self.assertEqual(sample_dict["val"], encoded.val)
        # assert defaults
        self.assertEqual(encoded.index2, 1)
        self.assertIsNone(encoded.val2)

    def test_encode_decode_with_subclass(self):
        class TestSubclass(Compysition):
            index: int = 3

        class TestClass(Compysition):
            index: int = 1
            val: str = "thisisavalue"
            sub: TestSubclass = None

        sample_dict = {"index": 13, "val": "test", "sub": {"index": 4}}
        encoded = TestClass().from_dict(sample_dict)
        self.assertEqual(sample_dict["index"], encoded.index)
        self.assertEqual(sample_dict["val"], encoded.val)
        self.assertIsInstance(encoded.sub, Compysition)
        self.assertIsInstance(encoded.sub, TestSubclass)
        self.assertEqual(sample_dict["sub"]["index"], encoded.sub.index)
        self.assertDictEqual(sample_dict, encoded.to_dict())

    def test_with_iterable(self):
        class TestSubclass(Compysition):
            index: int = 3

        class TestClass(Compysition):
            index: int = 0
            collection: List[TestSubclass] = field(default_factory=list)

        sample_dict = {"index": 13, "collection": [{"index": 4}, {"index": 16}]}

        encoded = TestClass().from_dict(sample_dict)
        self.assertEqual(encoded.index, 13)
        self.assertIsInstance(encoded.collection, list)
        self.assertEqual(len(encoded.collection), 2)
        self.assertTrue(
            all(isinstance(obj, TestSubclass) for obj in encoded.collection)
        )
        self.assertDictEqual(sample_dict, encoded.to_dict())

    def test_with_enum(self):
        class TestEnum(IntEnum):
            TESTNAME = 0
            TESTNAME2 = 1

        class TestClassValueSetting(Compysition):
            test_1: TestEnum = None
            test_2: TestEnum = None
            test_3: TestEnum = None

        class TestClassNameSetting(Compysition):
            test_1: TestEnum = None
            test_2: TestEnum = None
            test_3: TestEnum = None

            @staticmethod
            def _enum_encoding_setting():
                return EnumEncodingSetting.NAME

        test_value = {"test_1": 0, "test_2": 1}
        test_name = {"test_1": "TESTNAME", "test_2": "TESTNAME2"}

        encoded_value = TestClassValueSetting().from_dict(test_value)
        encoded_name = TestClassNameSetting().from_dict(test_name)

        self.assertEqual(encoded_value.test_1, TestEnum.TESTNAME)
        self.assertEqual(encoded_value.test_2, TestEnum.TESTNAME2)
        self.assertEqual(encoded_name.test_2, TestEnum.TESTNAME2)
        self.assertEqual(encoded_name.test_2, TestEnum.TESTNAME2)

        self.assertDictEqual(test_value, encoded_value.to_dict())
        self.assertDictEqual(test_name, encoded_name.to_dict())

    def test_with_datetime(self):
        class TestClass(Compysition):
            test_date: datetime = None
            test_date2: datetime = None

        now = datetime.utcnow()
        sample_data = {
            "test_date": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "test_date2": (now - timedelta(seconds=10)).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
        }

        encoded = TestClass().from_dict(sample_data)
        self.assertEqual(encoded.test_date, now)
        self.assertEqual(encoded.test_date2, now - timedelta(seconds=10))

        self.assertDictEqual(encoded.to_dict(), sample_data)

    def test_datetime_custom_encode_function(self):
        epoch = datetime(1970, 1, 1)

        class TestClass(Compysition):
            test_date: datetime = None
            test_date2: datetime = None
            test_date3: datetime = None

            @staticmethod
            def _encode_datetime(dt: datetime) -> Union[str, int, float]:
                return (dt - epoch).total_seconds()

        # note a custom decode may be desired as well in the case of non-utc time
        # or a string encoding that does not conform to ISO-8601

        now = datetime.utcnow()
        now_epoch = (now - epoch).total_seconds()
        sample_data = {"test_date": now_epoch, "test_date2": now_epoch - 10}

        encoded = TestClass().from_dict(sample_data)
        self.assertEqual(encoded.test_date, now)
        self.assertEqual(encoded.test_date2, now - timedelta(seconds=10))

        self.assertDictEqual(encoded.to_dict(), sample_data)

    def test_init(self):
        class TestClass(Compysition):
            test_str: str = None
            test_int: int = 0

        test_obj = TestClass(test_str="hello")
        self.assertEqual(test_obj.test_str, "hello")
        self.assertEqual(test_obj.test_int, 0)

    def test_init_with_invalid_type_assignment(self):
        class TestClass(Compysition):
            test_str: str = None

        with self.assertRaises(TypeAssignmentException):
            TestClass(test_str=1500)
