#!/usr/bin/env python3

from PIL import Image
from .labels import Label, FormFactor
from .models import PrinterModel 


def adapt_image(image, printer_model, label):

    assert isinstance(printer_model, PrinterModel)
    assert isinstance(label, Label)
    
    if label.form_factor == FormFactor.ENDLESS:

        if image.size[0] != label.dots_printable[0]:
            hsize = int(
                label.dots_printable[0] / image.size[0] * image.size[1])
            image = image.resize(
                (label.dots_printable[0], hsize), 
                Image.ANTIALIAS
            )

        device_pixel_width = printer_model.bytes_per_row * 8
        if image.size[0] < device_pixel_width:
            new_im = Image.new(
                image.mode,
                (device_pixel_width, image.size[1]),
                (255,)*len(image.mode)
            )
            new_im.paste(
                image,
                (device_pixel_width\
                 - image.size[0] - printer_model.offset_right_adjust, 0)
            )
            image = new_im
    else:
        # resize the image to fit the printable area
        raise Exception("Not implemented yet.")

    return image



