#!/usr/bin/env python3

"""Generates a print job with commands."""

import sys
from PIL import Image
from .io import PrinterIOLinuxKernel
from .escp_commands import *
from .labels import find_label, FormFactor
from .models import find_printer
from .image_adapter import adapt_image


class Job:

    def __init__(self, printer):
        self.printer = printer
        
        printer.write(CmdClearJob())
        printer.write(CmdInitialize())

        printer.write(CmdStatusInformationRequest())
        resp = printer.read(timeout=3)

        if not resp:
            raise Exception("No response from printer.")

        resp = StatusInformationResponse(resp)
        print(repr(resp))

        printer_model = find_printer(code=resp.printer_code)
        label = find_label(
            width=resp.media_width,
            form_factor=FormFactor.ENDLESS if resp.is_continous_media else None,
            length=resp.media_length,
        ) 

        if len(label) != 1:
            raise Exception("Cannot determine label type.")

        label = label[0]

        self.label_type = label
        self.printer_model = printer_model

    def print(self, image):
        image = adapt_image(
            image,
            printer_model=self.printer_model,
            label=self.label_type
        )

        cmdlist = [
            CmdCommandModeSwitch(mode=CmdCommandModeSwitch.MODE_RASTER),
            CmdPrintInformation(self.label_type, image, is_starting_page=True),
            CmdSetEachMode(auto_cut=True),
            CmdSetExpandedMode(cut_at_end=True, hires=False),
            CmdSetFeedAmount(self.label_type.feed_margin),
            CmdRasterImageTransfer(
                image,
                label_type=self.label_type,
                printer_model=self.printer_model
            ),
            CmdPrint(),
        ]

        for cmd in cmdlist: self.printer.write(cmd)

        resp = self.printer.read(timeout=3)
        if resp:
            resp = StatusInformationResponse(resp)
            print(repr(resp))
            return resp
        return None
