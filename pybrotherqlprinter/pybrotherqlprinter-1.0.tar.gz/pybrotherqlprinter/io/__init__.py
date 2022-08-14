#!/usr/bin/env python

from builtins import str
import glob, os, time, select
from ..escp_commands._command import BrotherGenericCommand

class PrinterIOLinuxKernel:

    @staticmethod
    def list():
        return glob.glob("/dev/usb/lp*")

    def __init__(self, dev_path):
        self.dev_path = dev_path

    def __enter__(self, *args, **kvargs):
        self.dev = open(self.dev_path, "rb+")
        #os.open(self.dev_path, os.O_RDWR)
        return self

    def __exit__(self, *args, **kvargs):
        #os.close(self.dev)
        self.dev.close()

    def read(self, timeout=5, length=1024):
        data = b''
        start = time.time()
        while (not data) and (time.time() - start < timeout):
            result, _, _ = select.select([self.dev], [], [], 0)
            if self.dev in result:
                data += self.dev.read(length) #os.read(self.dev, length)
            if data: break
            time.sleep(0.001)
        if not data:
            # one last try if still no data:
            return self.dev.read(length) #os.read(self.dev, length)
        else:
            return data

    def write(self, data):
        if isinstance(data, BrotherGenericCommand):
            data = bytes(data)
        #os.write(self.dev, data)
        self.dev.write(data)
        self.dev.flush()
