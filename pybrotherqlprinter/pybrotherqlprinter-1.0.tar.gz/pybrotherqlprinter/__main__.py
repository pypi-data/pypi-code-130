#!/usr/bin/env python3

import sys
from PIL import Image
from .io import PrinterIOLinuxKernel
from .job import Job

printer_list = PrinterIOLinuxKernel.list()

if len(printer_list) < 1:
    print("No printer found.")
    exit()


image = Image.open(sys.argv[1])



with PrinterIOLinuxKernel(printer_list[0]) as printer:
    job = Job(printer)
    job.print(image)
