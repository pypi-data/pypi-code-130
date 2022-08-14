#!/usr/bin/env python3

from ._command import BrotherESCPCommand


class CmdStatusInformationRequest(BrotherESCPCommand):

    def __init__(self):
        BrotherESCPCommand.__init__(self, b"iS")

    def compile(self):
        return b""
