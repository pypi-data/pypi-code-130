# -*- coding: utf-8 -*-

# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from magorder.stdsi import StdSIMagnitudeUnit


def test_simple_std_si_magnitude():
    mag = StdSIMagnitudeUnit("m")
    assert mag.transform(100) == 100
    assert mag.transform(0.1, "km") == 100
    assert mag.transform(100_000_000, "µm") == 100
    assert mag.transform(100_000_000_000_000_000_000_000_000.0, "ym") == 100
    assert mag.transform(0.0000000000000000000001, "Ym", 3) == 100

def test_std_si_magnitude_aliases():
    mag = StdSIMagnitudeUnit("m")
    assert mag.transform(100_000_000, "µm") == 100
    assert mag.transform(100_000_000, "um") == 100

def test_simple_std_si_magnitude_bounds():
    mag = StdSIMagnitudeUnit("m", lower="p", upper="T")
    assert mag.transform(100) == 100
    assert mag.transform(0.1, "km") == 100
    assert mag.transform(100_000_000, "µm") == 100

    with pytest.raises(ValueError):
        assert mag.transform(100_000_000_000_000_000_000_000_000.0, "ym") == 100
        assert mag.transform(0.0000000000000000000001, "Ym") == 100

def test_from_std_si_magnitude():
    mag = StdSIMagnitudeUnit("m")
    assert mag.transform(1, "km") == 1000
