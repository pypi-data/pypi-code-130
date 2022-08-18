"""
:Project: Cruncher
:Contents: utils.py
:copyright: © 2019-2022 Daniel Morell
:license: MIT, see LICENSE for more details.
:Author: Daniel Morell
"""
# Standard Library Imports

# Package Imports

# Local Imports

UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


def friendly_data_units(data, unit, digits=5):
    """
    Turns large number of byte units into larger units for easier reading.

    :param data: Integer|Float: The number of bytes.
    :param unit: String: The byte unit ['B', 'KB', 'MB', 'GB', 'TB'].
    :param digits: Integer: The number of decimal digits to round to.
    :return: 2 Tuple: New data quantity and unit string.
    """
    unit_num = UNITS.index(unit)
    if data > 1000 and len(UNITS) >= (unit_num + 1):
        unit = UNITS[unit_num + 1]
        data = data / 1000
        data, unit = friendly_data_units(data, unit)
    if digits:
        n = 5 - len(str(data).split('.')[0])
        if n > 3:
            n = 3
        data = round(data, n)
    return data, unit


def calculate_temperature_change(degree: int = 0) -> tuple:
    """
    Turns a degree in a range from -100 to 100 into a RGB color conversion.

    Negative degrees cool the image (increase blues)

    Positive degrees heat the image (increase reds)

    :param degree: Integer: The intended color temperature change
    """
    degree = min(100, degree) if degree >= 0 else max(-100, degree)
    red = 255 if degree > 1 else round(255 - (abs(degree) / 100 * 255))
    green = 255 if degree == 0 else round(255 - (abs(degree) / 100 * 255))
    blue = 255 if degree < 1 else round(255 - (abs(degree) / 100 * 255))
    return red, green, blue
