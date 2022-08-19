"""DSSP parser"""
from ribfind.model import ProteinModel, Strand, Loop, Helix


class DSSPContigReader:
    """A DSSP file parser.

    Call 'parse_model' to generate a 'Model' object.
    """

    RESIDUE_NUM_FIELD = 1
    CHAIN_ID_FIELD = 2
    STRUCT_FIELD = 4

    def __init__(self):
        self.model = ProteinModel()
        self.lines = None

    def _eat_header(self):
        """Eat all the lines which are at the beginning of the DSSP file. We are
        only interested in everything that comes after the line beginning with
        '#' character."""
        while self.lines[0].split()[0] != "#":
            self.lines.pop(0)
        self.lines.pop(0)

    def _get_sse(self):
        line = self.lines[0]
        fields = line.split()
        if fields[DSSPContigReader.RESIDUE_NUM_FIELD] == "!*":
            return "F"
        if fields[1] == "!":
            return "U"
        struct = fields[DSSPContigReader.STRUCT_FIELD]
        if struct in ("H"):
            return "H"
        if struct in ("E"):
            return "S"
        return "L"

    def _get_res(self):
        line = self.lines[0]
        fields = line.split()
        return int(fields[DSSPContigReader.RESIDUE_NUM_FIELD])

    def _get_chain(self):
        line = self.lines[0]
        fields = line.split()
        return fields[DSSPContigReader.CHAIN_ID_FIELD]

    def _get_sheet_id(self):
        line = self.lines[0]
        return str(line[33:34])

    def _finished(self):
        return len(self.lines) == 0

    def _parse_helix(self):
        res_start = res_end = self._get_res()
        chain = self._get_chain()
        while True:
            if self._finished() or self._get_sse() != "H":
                self.model.add_contig(Helix(chain, res_start, res_end + 1))
                return
            res_end = self._get_res()
            self._next_line()

    def _parse_strand(self):
        res_start = res_end = self._get_res()
        chain = self._get_chain()
        sheet_id = self._get_sheet_id()
        while True:
            if (
                self._finished()
                or self._get_sse() != "S"
                or self._get_sheet_id() not in (sheet_id, " ")
            ):
                self.model.add_contig(Strand(chain, res_start, res_end + 1, sheet_id))
                return
            res_end = self._get_res()
            self._next_line()

    def _parse_loop(self):
        res_start = res_end = self._get_res()
        chain = self._get_chain()
        while True:
            if self._finished() or self._get_sse() != "L":
                self.model.add_contig(Loop(chain, res_start, res_end + 1))
                return
            res_end = self._get_res()
            self._next_line()

    def _next_line(self):
        self.lines.pop(0)

    def _parse_entry(self):
        sse = self._get_sse()
        if sse in ("H"):
            self._parse_helix()
        elif sse in ("S"):
            self._parse_strand()
        elif sse in ("F", "U"):
            # Switching to next chain
            self._next_line()
        else:
            self._parse_loop()

    def parse_model(self, dssp_file):
        """TODO"""
        with open(dssp_file, encoding="utf8") as file:
            self.lines = file.readlines()
            self._eat_header()
            while len(self.lines) > 0:
                self._parse_entry()
        self.lines = None
        return self.model
