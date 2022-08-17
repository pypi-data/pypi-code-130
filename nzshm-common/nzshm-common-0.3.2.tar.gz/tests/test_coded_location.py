import pytest
import unittest

from nzshm_common.location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
import random

GRID_02 = load_grid('NZ_0_2_NB_1_1')
LOCS = [CodedLocation(loc[0], loc[1], 0.001) for loc in GRID_02[20:50]]


def test_coded_location_is_hashable():
    c = CodedLocation(-45.2, 175.2, 0.1)
    s = set()
    s.add(c)
    assert c in s


class CodedLocationResampling(unittest.TestCase):
    def test_get_nearest_hazard_for_an_arbitrary_location(self):
        gridloc = random.choice(LOCS)
        print(f'gridloc {gridloc}')

        off_lat = round(gridloc.lat + random.randint(0, 9) * 0.01, 3)
        off_lon = round(gridloc.lon + random.randint(0, 9) * 0.01, 3)
        somewhere_off_grid = CodedLocation(off_lat, off_lon, 0.001)

        nearest_grid = somewhere_off_grid.downsample(0.2)

        print(f'somewhere_off_grid {somewhere_off_grid}')
        print(f'nearest_grid {nearest_grid}')

        self.assertEqual(gridloc, nearest_grid.resample(0.001))
        self.assertEqual(gridloc, nearest_grid.downsample(0.001))
        self.assertEqual(gridloc.code, nearest_grid.downsample(0.001).code)

        self.assertEqual(gridloc, CodedLocation(nearest_grid.lat, nearest_grid.lon, 0.001))
        self.assertTrue(CodedLocation(nearest_grid.lat, nearest_grid.lon, 0.001) in LOCS)


oh_point_five_expected = [
    (-45.27, 171.1, '-45.5~171.0'),
    (-45.23, 171.1, '-45.0~171.0'),
    (-45.27, 171.4, '-45.5~171.5'),
    (-45.27, 171.8, '-45.5~172.0'),
    (-41.3, 174.783, '-41.5~175.0'),  # WLG
]


@pytest.mark.parametrize("lat,lon,expected", oh_point_five_expected)
def test_coded_location_equality(lat, lon, expected):
    c0 = CodedLocation(lat, lon, 0.5)
    c1 = CodedLocation(lat, lon, 0.5)
    assert c0 == c1


@pytest.mark.parametrize("lat,lon,expected", oh_point_five_expected)
def test_downsample_default_oh_point_five_no_downsampking_required(lat, lon, expected):
    print(f"lat {lat} lon {lon} -> {expected}")
    assert CodedLocation(lat, lon, 0.5).code == expected


@pytest.mark.parametrize("lat,lon,expected", oh_point_five_expected)
def test_downsample_default_oh_point_five(lat, lon, expected):
    print(f"lat {lat} lon {lon} -> {expected}")
    c = CodedLocation(lat, lon, 0.5)
    assert c.downsample(0.5).code == expected


@pytest.mark.parametrize(
    "lat,lon,expected",
    [
        (-45.27, 171.1, '-45.0~171.0'),
        (-45.23, 171.1, '-45.0~171.0'),
        (-45.77, 171.4, '-46.0~171.0'),
        (-45.27, 171.8, '-45.0~172.0'),
        (-41.3, 174.78, '-41.0~175.0'),  # WLG
    ],
)
def test_downsample_one_point_oh(lat, lon, expected):
    c = CodedLocation(lat, lon, 1.0)
    assert c.downsample(1.0).code == expected


@pytest.mark.parametrize(
    "lat,lon,expected",
    [
        (-45.27, 171.1, '-45.3~171.1'),
        (-45.239, 171.13, '-45.2~171.1'),
        (-45.27, 171.4, '-45.3~171.4'),
        (-45.27, 171.8, '-45.3~171.8'),
        (-41.333, 174.78, '-41.3~174.8'),  # WLG
    ],
)
def test_downsample_oh_point_one(lat, lon, expected):
    c = CodedLocation(lat, lon, 0.1)
    assert c.downsample(0.1).code == expected


@pytest.mark.parametrize(
    "lat,lon,expected",
    [
        (-45.27, 171.111, '-45.25~171.10'),
        (-45.239, 171.73, '-45.25~171.75'),
        (45.126, 171.4, '45.15~171.40'),
        (-45.27, 171.03, '-45.25~171.05'),
        (-41.333, 174.78, '-41.35~174.80'),  # WLG
    ],
)
def test_downsample_oh_point_oh_five(lat, lon, expected):
    c = CodedLocation(lat, lon, 0.05)
    assert c.downsample(0.05).code == expected
