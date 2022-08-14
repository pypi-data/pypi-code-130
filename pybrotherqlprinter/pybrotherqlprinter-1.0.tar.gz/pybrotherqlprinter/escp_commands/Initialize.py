#!/usr/bin/env python3

from ._command import BrotherESCPCommand


class CmdInitialize(BrotherESCPCommand):

    def __init__(self):
        BrotherESCPCommand.__init__(self, b"@")

    def compile(self):
        return b""
