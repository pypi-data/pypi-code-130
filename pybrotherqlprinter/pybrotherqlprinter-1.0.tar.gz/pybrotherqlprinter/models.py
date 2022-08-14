#!/usr/bin/env python3

class PrinterModel:

    def __init__(self, name, code, bytes_per_row, offset_right_adjust=0):
        self.name = name
        self.code = code
        self.bytes_per_row = bytes_per_row
        self.offset_right_adjust = offset_right_adjust




_ALL_MODELS = [
    PrinterModel("QL-1100", "4C", bytes_per_row=162, offset_right_adjust=44),
]


def find_printer(code):
    found = _ALL_MODELS
    if code:
        found = [e for e in found if e.code == code]
    return found[0]
