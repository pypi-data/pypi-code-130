#!/usr/bin/env python3

from ._command import BrotherESCPCommand

class CmdSetEachMode(BrotherESCPCommand):

    def __init__(self, auto_cut=True):
        BrotherESCPCommand.__init__(self, b"iM")
        self.mode = 0b1000000 if auto_cut else 0b000000

    def compile(self):
        return bytes([self.mode])
