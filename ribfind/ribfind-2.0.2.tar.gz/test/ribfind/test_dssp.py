#!/usr/bin/env python3

from ribfind.dssp import DSSPContigReader
from ribfind.model import Loop, Strand, Helix, Sheet
import unittest


class TestDSSP(unittest.TestCase):
    def assertEqualRecord(self, this_dssp_record, that_dssp_record):
        self.assertEqual(type(this_dssp_record), type(that_dssp_record))
        self.assertEqual(this_dssp_record.start, that_dssp_record.start)
        self.assertEqual(this_dssp_record.stop, that_dssp_record.stop)
        self.assertEqual(this_dssp_record.chain_id, that_dssp_record.chain_id)
        if isinstance(this_dssp_record, Strand):
            self.assertEqual(this_dssp_record.sheet_id, that_dssp_record.sheet_id)

    def assertEqualRecords(self, these_records, those_records):
        self.assertEqual(len(these_records), len(those_records))
        for this, that in zip(these_records, those_records):
            self.assertEqualRecord(this, that)

    def test_parse_model(self):
        reader = DSSPContigReader()
        model = reader.parse_model("test/data/model/model.dssp")
        self.assertEqual(len(model.rigid_bodies()), 13)

    def test_parse_records(self):
        reader = DSSPContigReader()
        model = reader.parse_model("test/data/model/model.dssp")
        contigs = [m for m in model.models if not isinstance(m, Sheet)]
        expected = [
            Loop("A", 3, 6),
            Helix("A", 6, 14),
            Loop("A", 14, 15),
            Helix("A", 15, 23),
            Loop("A", 23, 34),
            Strand("A", 34, 43, "A"),
            Loop("A", 43, 50),
            Helix("A", 50, 65),
            Loop("A", 65, 69),
            Strand("A", 69, 73, "A"),
            Loop("A", 73, 87),
            Strand("A", 87, 95, "A"),
            Loop("A", 95, 96),
            Helix("A", 96, 109),
            Loop("A", 109, 130),
            Strand("A", 130, 136, "A"),
            Loop("A", 136, 139),
            Strand("A", 139, 141, "C"),
            Loop("A", 141, 145),
            Strand("A", 145, 147, "C"),
            Loop("A", 147, 155),
            Strand("A", 155, 162, "A"),
            Loop("A", 162, 166),
            Helix("A", 166, 177),
            Loop("A", 177, 183),
            Loop("B", 4, 6),
            Helix("B", 6, 14),
            Loop("B", 14, 15),
            Helix("B", 15, 24),
            Loop("B", 24, 34),
            Strand("B", 34, 44, "D"),
            Loop("B", 44, 52),
            Helix("B", 52, 65),
            Loop("B", 65, 69),
            Strand("B", 69, 73, "D"),
            Loop("B", 73, 87),
            Strand("B", 87, 95, "D"),
            Loop("B", 95, 96),
            Helix("B", 96, 109),
            Loop("B", 109, 131),
            Strand("B", 131, 136, "D"),
            Loop("B", 136, 152),
            Strand("B", 152, 162, "D"),
            Loop("B", 162, 166),
            Helix("B", 166, 177),
            Loop("B", 177, 183),
        ]
        self.assertEqualRecords(expected, contigs)
