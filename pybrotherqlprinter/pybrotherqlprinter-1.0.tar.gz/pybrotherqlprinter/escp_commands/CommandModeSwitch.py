#!/usr/bin/env python3

from ._command import BrotherESCPCommand


class CmdCommandModeSwitch(BrotherESCPCommand):

    MODE_ESCP = 0
    MODE_RASTER = 1

    def __init__(self, mode):
        BrotherESCPCommand.__init__(self, b"ia")
        self.mode = mode

    def compile(self):
        return bytes([self.mode]) 
