# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from pathlib import Path
from warnings import warn

from pdkmaster import _util
from pdkmaster.io.spice.pyspice import PySpiceFactory

__all__ = ["pyspicefab", "pyspice_factory"]


pyspicefab = pyspice_factory = None
_file = Path(__file__)
_libfile = _file.parent.joinpath("models", "C4M.Sky130_all_lib.spice")
pyspicefab = pyspice_factory = PySpiceFactory(
    libfile=str(_libfile),
    corners=(
        "logic_tt", "logic_sf", "logic_ff", "logic_ss", "logic_fs",
        "io_tt", "io_sf", "io_ff", "io_ss", "io_fs",
        "diode_tt", "diode_sf", "diode_ff", "diode_ss", "diode_fs",
    ),
    conflicts={
        "logic_tt": ("logic_sf", "logic_ff", "logic_ss", "logic_fs"),
        "logic_sf": ("logic_tt", "logic_ff", "logic_ss", "logic_fs"),
        "logic_ff": ("logic_tt", "logic_sf", "logic_ss", "logic_fs"),
        "logic_ss": ("logic_tt", "logic_sf", "logic_ff", "logic_fs"),
        "logic_fs": ("logic_tt", "logic_sf", "logic_ff", "logic_ss"),
        "io_tt": ("io_sf", "io_ff", "io_ss", "io_fs"),
        "io_sf": ("io_tt", "io_ff", "io_ss", "io_fs"),
        "io_ff": ("io_tt", "io_sf", "io_ss", "io_fs"),
        "io_ss": ("io_tt", "io_sf", "io_ff", "io_fs"),
        "io_fs": ("io_tt", "io_sf", "io_ff", "io_ss"),
        "diode_tt": ("diode_sf", "diode_ff", "diode_ss", "diode_fs"),
        "diode_sf": ("diode_tt", "diode_ff", "diode_ss", "diode_fs"),
        "diode_ff": ("diode_tt", "diode_sf", "diode_ss", "diode_fs"),
        "diode_ss": ("diode_tt", "diode_sf", "diode_ff", "diode_fs"),
        "diode_fs": ("diode_tt", "diode_sf", "diode_ff", "diode_ss"),
    },
)
