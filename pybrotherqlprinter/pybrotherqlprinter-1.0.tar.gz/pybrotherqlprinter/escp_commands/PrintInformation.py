#!/usr/bin/env python3

import struct
from ._command import BrotherESCPCommand
from ..labels import FormFactor


class CmdPrintInformation(BrotherESCPCommand):

    """Declares information to the printer about the page being printed."""


    def __init__(self, label, image, is_starting_page=True):
        BrotherESCPCommand.__init__(self, b"iz")

        n1 = 0x02 | 0x04 | 0x08
        n2 = 0x0A if label.form_factor == FormFactor.ENDLESS else 0x0B
        n3 = label.size[0]
        n4 = label.size[1]

        n5n8 = struct.pack("<L", image.size[1])
        n9 = 0 if is_starting_page else 1
        n10 = 0

        self.__data = bytes([n1, n2, n3, n4]) + n5n8 + bytes([n9, n10])


    def compile(self):
        return self.__data 
