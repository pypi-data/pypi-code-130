#!/usr/bin/env python3

from PIL import Image, ImageOps
from ._command import BrotherGenericCommand
from ..labels import Label, FormFactor

class CmdRasterImageTransfer(BrotherGenericCommand):

    def __init__(self, image, label_type, printer_model):
        assert isinstance(image, Image.Image)
        assert isinstance(label_type, Label)
        assert image.size[0] == printer_model.bytes_per_row * 8 
        BrotherGenericCommand.__init__(self)
        self.image = image
        self.bytes_per_row = printer_model.bytes_per_row

    def __image_to_instructions(self, image):
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image = image.convert("1")
        image = ImageOps.invert(image)
        image_bytes = bytes(image.tobytes(encoder_name='raw'))
        row_length = self.bytes_per_row

        output = b""
        for start in range(0, len(image_bytes), row_length):
            row_bytes = image_bytes[start:start+row_length]
            row_bytes_length = len(row_bytes)
            output += b'\x67\x00' + bytes([row_bytes_length])
            output += row_bytes 
        return output

    def __bytes__(self):
        return self.__image_to_instructions(self.image) 
