#!/usr/bin/env python3

from PIL import Image
from ._command import BrotherGenericCommand

class CmdPrint(BrotherGenericCommand):

    def __init__(self, is_last_page=True):
        BrotherGenericCommand.__init__(self)
        self.is_last_page = is_last_page

    def __bytes__(self):
        return b"\x1A" if self.is_last_page else b"\x0C"
