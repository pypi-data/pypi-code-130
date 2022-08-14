#!/usr/bin/env python3

from ._command import BrotherESCPCommand

class CmdSetExpandedMode(BrotherESCPCommand):

    def __init__(self, cut_at_end=True, hires=False):
        BrotherESCPCommand.__init__(self, b"iK")
        self.mode = 0x00 | (
            (bool(cut_at_end) << 3) |
            (bool(hires) << 6)
        )

    def compile(self):
        return bytes([self.mode])
