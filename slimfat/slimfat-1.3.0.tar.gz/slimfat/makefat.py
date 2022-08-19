from io import SEEK_SET
from os import stat

from slimfat.structs_fat import FatArchStruct, FatHeaderStruct
from slimfat.structs_mach import MachHeaderBegin
from slimfat.util import align_int, executable_opener

def make_fat(output: str, input: list):
    HeaderCls = FatArchStruct
    align = 15
    endian = ">"

    align_bytes = pow(2, align)
    header_len = HeaderCls.packsize() * len(input)

    file_offsets = {}
    with open(output, "wb", opener=executable_opener) as outf:
        outf.write(FatHeaderStruct(endian=endian, magic=HeaderCls.magic(), nfat_arch=len(input)).pack())
        offset = align_int(header_len + outf.tell(), align_bytes)

        for bin in input:
            fstat = stat(bin)

            buf = None
            with open(bin, "rb") as binf:
                buf = binf.read(MachHeaderBegin.packsize())

            machHdr = MachHeaderBegin()
            machHdr.unpack(buf)

            hdr = HeaderCls(endian=endian, cputype=machHdr.cputype, cpusubtype=machHdr.cpusubtype, offset=offset, size=fstat.st_size, align=align)

            file_offsets[bin] = hdr.offset
            offset = align_int(offset + hdr.size, align_bytes)
            outf.write(hdr.pack())

        for bin in input:
            outf.seek(file_offsets[bin], SEEK_SET)
            with open(bin, "rb") as binf:
                outf.write(binf.read())
