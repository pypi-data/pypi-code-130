#!/usr/bin/env python3

import struct
from ._command import BrotherESCPCommand

class CmdSetFeedAmount(BrotherESCPCommand):

    def __init__(self, feed=35):
        BrotherESCPCommand.__init__(self, b"id")
        self.feed = feed

    def compile(self):
        return struct.pack("<H", self.feed) # 2 bytes, little endian
