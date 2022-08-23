import pytest

import numpy as np

from ..data import DataBuffer


# 10 seconds of 1000 Hz data
DATA = np.sin(np.arange(10000))
SAMPLE_RATE = 1000
#GPS_START = 1341014418
GPS_START = 10


def gen_tarray(samples, sample_rate, gps_start):
    # FIXME: why is this:
    step = 1/sample_rate
    return np.arange(samples) * step + gps_start
    # not the same as this:
    # return np.arange(samples) / sample_rate + gps_start


def test_data_buffer_create():
    raw = DATA[2000:3000]
    gps_start = GPS_START+2
    data = DataBuffer('FOO', 'raw', 'raw', raw, SAMPLE_RATE, gps_start)
    assert data.gps_start == gps_start
    assert data.gps_end == gps_start + 1
    assert data.range == (gps_start, gps_start+1)
    assert len(data) == len(raw)
    assert data.tlen == len(raw) / SAMPLE_RATE
    assert np.array_equal(data.tarray, gen_tarray(1000, SAMPLE_RATE, gps_start))
    assert data['raw'].data == raw


def test_data_add_left():
    data = DataBuffer('FOO', 'raw', 'raw', DATA[2000:3000], SAMPLE_RATE, GPS_START+2)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[1000:2500], SAMPLE_RATE, GPS_START+1)
    data.add_data(data1)
    assert data.gps_start == GPS_START + 1
    assert data.gps_end == GPS_START + 3
    assert len(data) == 2000
    assert data.tlen == 2000 / SAMPLE_RATE
    assert np.array_equal(data.tarray, gen_tarray(2000, SAMPLE_RATE, GPS_START+1))
    assert data['raw'].data == DATA[1000:3000]


def test_data_add_left_miss():
    data = DataBuffer('FOO', 'raw', 'raw', DATA[2000:3000], SAMPLE_RATE, GPS_START+2)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[1000:1500], SAMPLE_RATE, GPS_START+1)
    with pytest.raises(AssertionError) as excinfo:
        data.add_data(data1)
    assert "is less than start" in str(excinfo.value)


def test_data_add_right():
    data = DataBuffer('FOO', 'raw', 'raw', DATA[2000:3000], SAMPLE_RATE, GPS_START+2)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[2500:4000], SAMPLE_RATE, GPS_START+2.5)
    data.add_data(data1)
    assert data.gps_start == GPS_START + 2
    assert data.gps_end == GPS_START + 4
    assert len(data) == 2000
    assert data.tlen == 2000 / SAMPLE_RATE
    assert np.array_equal(data.tarray, gen_tarray(2000, SAMPLE_RATE, GPS_START+2))
    assert data['raw'].data == DATA[2000:4000]


def test_data_add_right_miss():
    data = DataBuffer('FOO', 'raw', 'raw', DATA[2000:3000], SAMPLE_RATE, GPS_START+2)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[3500:4500], SAMPLE_RATE, GPS_START+3.5)
    with pytest.raises(AssertionError) as excinfo:
        data.add_data(data1)
    assert "is greater than end" in str(excinfo.value)


def test_data_add_center():
    raw = DATA[2000:3000]
    data = DataBuffer('FOO', 'raw', 'raw', raw, SAMPLE_RATE, GPS_START+2)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[2200:2800], SAMPLE_RATE, GPS_START+2.2)
    data.add_data(data1)
    assert data.gps_start == 12
    assert data.gps_end == 13
    assert len(data) == len(raw)
    assert data.tlen == len(raw) / SAMPLE_RATE
    assert np.array_equal(data.tarray, gen_tarray(1000, SAMPLE_RATE, 12))
    assert data['raw'].data == raw


def test_data_add_super():
    data = DataBuffer('FOO', 'raw', 'raw', DATA[2000:3000], SAMPLE_RATE, 12)
    data1 = DataBuffer('FOO', 'raw', 'raw', DATA[1000:4000], SAMPLE_RATE, 11)
    data.add_data(data1)
    assert data.gps_start == 11
    assert data.gps_end == 14
    assert len(data) == 3000
    assert data.tlen == 3000 / SAMPLE_RATE
    assert data['raw'].data == DATA[1000:4000]
