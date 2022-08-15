import unittest

from roseta import trans_cup


class TestCup(unittest.TestCase):
    def setUp(self) -> None:
        self.cup_data = {
            "32a": [(82, "cm"), (0.82, "m")],
            "c36": [(96, "cm"), (0.96, "m")],
            "40c": [(106, "cm"), (1.06, "m")],
            "c42": [(111, "cm"), (1.11, "m")],
            "E48": [(130, "cm"), (1.3, "m")],
            "85B": [(99, "cm"), (0.99, "m")],
            "95F": [(117, "cm"), (1.17, "m")],
            "c80": [(96, "cm"), (0.96, "m")],
            "H110": [(136, "cm"), (1.36, "m")],
            "105g": [(129, "cm"), (1.29, "m")],
            "三十二a": [(82, "cm"), (0.82, "m")],
            "c三十六": [(96, "cm"), (0.96, "m")],
            "四十c": [(106, "cm"), (1.06, "m")],
            "c四十二": [(111, "cm"), (1.11, "m")],
            "E四十八": [(130, "cm"), (1.3, "m")],
            "八十五B": [(99, "cm"), (0.99, "m")],
            "九十五F": [(117, "cm"), (1.17, "m")],
            "c八十": [(96, "cm"), (0.96, "m")],
            "H一百一十": [(136, "cm"), (1.36, "m")],
            "一百零五g": [(129, "cm"), (1.29, "m")],
            "三二a": [(82, "cm"), (0.82, "m")],
            "c三六": [(96, "cm"), (0.96, "m")],
            "四零c": [(106, "cm"), (1.06, "m")],
            "c四二": [(111, "cm"), (1.11, "m")],
            "E四八": [(130, "cm"), (1.3, "m")],
            "八五B": [(99, "cm"), (0.99, "m")],
            "九五F": [(117, "cm"), (1.17, "m")],
            "c八零": [(96, "cm"), (0.96, "m")],
            "H一一零": [(136, "cm"), (1.36, "m")],
            "一零五g": [(129, "cm"), (1.29, "m")],
        }

    def test_trans_cup(self) -> None:
        for key, value in self.cup_data.items():
            self.assertEqual(trans_cup(key),  value[0])  # default unit: cm
            self.assertEqual(trans_cup(key, unit="cm"), value[0])
            self.assertEqual(trans_cup(key, unit="m"), value[1])


if __name__ == "__main__":
    unittest.main()
