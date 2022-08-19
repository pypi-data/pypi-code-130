from typing import List, Union, TextIO, Any
import logging
import datetime
from dataclasses import fields
from xml.etree import ElementTree

from .main import Map, Device


logger = logging.getLogger(__name__)


def read(stream: TextIO) -> List[Map]:
    tree = ElementTree.parse(stream)
    el_root = tree.getroot()

    if _tag(el_root) != 'Maps':
        logger.warning(f'Root tag is "{_tag(el_root)}", expected "Maps"')

    maps = read_wmaps(el_root)
    return maps


def read_wmaps(el_root: ElementTree.Element) -> List[Map]:
    map_fields = [ff.name for ff in fields(Map)]
    maps = []
    for el_map in el_root:
        if _tag(el_map) != 'Map':
            logger.warning(f'Skipping map-level tag "{_tag(el_map)}"')
            continue

        wmap = Map()

        for key, val in el_map.attrib.items():
            if key in map_fields and key[0].isupper():
                setattr(wmap, key, val)
            else:
                wmap.misc[key] = val
        wmap.devices = read_devices(el_map)
        maps.append(wmap)
    return maps


def read_devices(el_map: ElementTree.Element) -> List[Device]:
    dev_fields = [ff.name for ff in fields(Device)]
    devices = []
    for el_device in el_map:
        if _tag(el_device) != 'Device':
            logger.warning(f'Skipping device-level tag "{_tag(el_device)}"')
            continue

        bin_type = el_device.attrib['BinType']
        null_bin: Union[int, str]
        if bin_type == 'Decimal':
            null_bin = int(el_device.attrib['NullBin'])
        else:
            null_bin = el_device.attrib['NullBin']

        device = Device(BinType=bin_type, NullBin=null_bin)

        val: Any
        for key, val in el_device.attrib.items():
            if key in ('BinType', 'NullBin'):
                continue

            if key in ('WaferSize', 'DeviceSizeX', 'DeviceSizeY', 'Orientation'):
                val = float(val)
            elif key in ('OriginLocation',):
                val = int(val)
            elif key == 'CreateDate':
                val = datetime.datetime.strptime(val + '000', '%Y%m%d%H%M%S%f')

            if key in dev_fields and key[0].isupper():
                setattr(device, key, val)
            else:
                device.misc[key] = val

        for el_entry in el_device:
            tag = _tag(el_entry)
            attrib = el_entry.attrib
            if tag == 'ReferenceDevice':
                if device.reference_xy is not None:
                    logger.warning('Duplicate ReferenceDevice entry; overwriting!')

                xy = (attrib.get('ReferenceDeviceX', None),
                      attrib.get('ReferenceDeviceY', None))

                if xy[0] is None or xy[1] is None:
                    logger.error('Malformed ReferenceDevice, ignoring!')
                    continue

                device.reference_xy = (int(xy[0]), int(xy[1]))
            elif tag == 'Bin':
                if 'BinCode' not in attrib:
                    logger.error(f'Bin without any associated BinCode, '
                                 f'with attributes {el_entry.attrib}')
                    continue

                if bin_type == 'Decimal':
                    bin_code = int(attrib['BinCode'])
                else:
                    bin_code = int(attrib['BinCode'])

                if bin_code in device.bin_pass:
                    logger.error(f'Bin code {bin_code} was repeated; ignoring later entry!')
                    continue

                device.bin_pass[bin_code] = attrib['BinQuality'].lower() == 'pass'
            elif tag == 'Data':
                data_strs = [read_row(rr) for rr in el_entry]
                data: Union[List[List[str]], List[List[int]]]
                if device.BinType == 'Decimal':
                    data = [[int(vv) for vv in rr] for rr in data_strs]
                else:
                    data = data_strs
                device.map = data
        devices.append(device)
    return devices


def read_row(el_row: ElementTree.Element) -> List[str]:
    assert _tag(el_row) == 'Row'

    row_stripped = (el_row.text or '').strip()
    if ' ' in row_stripped or '\t' in row_stripped:
        row_data = row_stripped.split()
    else:
        row_data = list(row_stripped)
    return row_data


def _tag(element: ElementTree.Element) -> str:
    '''
    Get the element's tag, excluding any namespaces.
    '''
    return element.tag.split('}')[-1]
