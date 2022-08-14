# -*- coding: utf-8 -*-

# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from magorder.data import SIDataMagnitudeUnit, IECDataMagnitudeUnit


def test_si_data():
    mags = SIDataMagnitudeUnit("b")
    assert mags.transform(1, "kb") == 1000
    assert mags.transform(1, "Gb:kb") == 1_000_000


def test_iec_data():
    mags = IECDataMagnitudeUnit("b")
    assert mags.transform(1, "Kib") == 1024
    assert mags.transform(4096, "Mib:Gib") == 4


def test_iec_data_legacy():
    mags = IECDataMagnitudeUnit("bps", legacy=True)
    assert mags.transform(1, "Kibps") == 1024
    assert mags.transform(4096, "Mibps:Gibps") == 4
    assert mags.transform(1, "Kbps") == 1024
    assert mags.transform(8192, "Mbps:Gbps") == 8


def test_iec_data_case_insensitive():
    mags = IECDataMagnitudeUnit("bps", case=False)
    assert mags.transform(1, "kibps") == 1024
    assert mags.transform(4096, "mibps:Gibps") == 4
    assert mags.transform(1, "Kibps") == 1024
    assert mags.transform(8192, "Mibps:gibps") == 8
