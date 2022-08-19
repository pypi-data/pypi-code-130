from typing import Sequence, Tuple, List, TextIO, Union
import logging
import math
from dataclasses import fields
from xml.etree import ElementTree

from .main import Map, Device


logger = logging.getLogger(__name__)


# Hack to directly pass through <![CDATA[...]]>
def _escape_cdata(text):
    if text.startswith('<![CDATA[') and text.endswith(']]>'):
        return text
    else:
        return _original_escape_cdata(text)


_original_escape_cdata = ElementTree._escape_cdata      # type: ignore
ElementTree._escape_cdata = _escape_cdata               # type: ignore
####


def write(maps: Sequence[Map], stream: TextIO) -> None:
    el_root = ElementTree.Element('Maps')

    for wmap in maps:
        write_wmap(wmap, el_root)

    tree = ElementTree.ElementTree(element=el_root)
    ElementTree.indent(tree)
    tree.write(stream)


def write_wmap(wmap: Map, el_root: ElementTree.Element) -> None:
    el_map = ElementTree.SubElement(el_root, 'Map')

    write_devices(wmap.devices, el_map)

    map_fields = [ff.name for ff in fields(wmap)]
    for field in map_fields:
        if field[0].isupper():
            val = getattr(wmap, field)
            if val is None:
                continue
            el_map.set(field, val)
    for key, value in wmap.misc.items():
        if key[0].isupper() and key in map_fields:
            continue
        el_map.set(key, value)


def write_devices(devices: Sequence[Device], el_map: ElementTree.Element) -> None:
    for device in devices:
        el_device = ElementTree.SubElement(el_map, 'Device')

        # ReferenceDevice
        if device.reference_xy is not None:
            el_ref = ElementTree.SubElement(el_device, 'ReferenceDevice')
            el_ref.set('ReferenceDeviceX', str(device.reference_xy[0]))
            el_ref.set('ReferenceDeviceY', str(device.reference_xy[1]))

        # Row data prep
        if device.map is None:
            raise Exception(f'No _data for device pformat({device})')

        is_decimal = device.BinType == 'Decimal'
        row_texts, bin_length = prepare_data(device.map, decimal=is_decimal)

        # Bins
        if not device.bin_pass:
            logger.warning('No bins were provided!')

        bin_counts = device.bin_counts()

        for bin_code, passed in device.bin_pass.items():
            el_bin = ElementTree.SubElement(el_device, 'Bin')
            if is_decimal:
                el_bin.set('BinCode', str(bin_code).zfill(bin_length))
            else:
                el_bin.set('BinCode', str(bin_code))
            el_bin.set('BinQuality', 'Pass' if passed else 'Fail')
            el_bin.set('BinCount', str(bin_counts[bin_code]))

        for row_text in row_texts:
            el_row = ElementTree.SubElement(el_device, 'Row')
            el_row.text = f'<![CDATA[{row_text}]]>'

        # Device attribs
        dev_fields = [ff.name for ff in fields(device)]
        for field in dev_fields:
            if field[0].isupper():
                val = getattr(device, field)
                if val is None:
                    continue

                if field in ('WaferSize', 'DeviceSizeX', 'DeviceSizeY', 'Orientation'):
                    val = f'{val:g}'
                elif field in ('OriginLocation',):
                    val = f'{val:d}'
                elif field == 'CreateDate':
                    val = val.strftime('%Y%m%d%H%M%S%f')[:-3]
                elif field == 'NullBin' and device.BinType == 'Decimal':
                    val = f'{val:d}'

                el_device.set(field, val)

        for key, value in device.misc.items():
            if key[0].isupper() and key in dev_fields:
                continue
            el_device.set(key, value)


def prepare_data(data: List[List[Union[str, int]]], decimal: bool) -> Tuple[List[str], int]:
    is_char = isinstance(data[0][0], str)

    if is_char:
        char_len = len(data[0][0])
    else:
        max_value = max(max(rr) for rr in data)
        max_digits = math.ceil(math.log10(max_value))

    row_texts = []
    for row in data:
        if is_char and char_len == 1:
            row_text = ''.join(row)
        elif is_char:
            row_text = ' '.join(row) + ' '
        else:
            row_text = ' '.join(str(vv).zfill(max_digits) for vv in row) + ' '
        row_texts.append(row_text)

    if is_char:
        return row_texts, char_len
    else:
        return row_texts, max_digits
