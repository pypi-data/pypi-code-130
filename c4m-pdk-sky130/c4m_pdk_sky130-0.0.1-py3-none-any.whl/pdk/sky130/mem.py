# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import cast

from pdkmaster.technology import primitive as _prm
from pdkmaster.design import library as _lbry
from pdkmaster.io import klayout as _klio
from c4m.flexmem import SP6TSpecification, SP6TFactory, DP8TSpecification, DP8TFactory

from . import pdkmaster as _pdk, stdcell as _std

__all__ = ["Sky130SP6TFactory", "Sky130DP8TFactory", "memlib"]


_prims = _pdk.tech.primitives

class Sky130SP6TFactory(SP6TFactory):
    spec: SP6TSpecification = SP6TSpecification(
        nmos=cast(_prm.MOSFET, _prims.nfet_01v8_sc), pmos=cast(_prm.MOSFET, _prims.pfet_01v8),
        stdcelllib=_std.stdcelllib,
        pu_l=0.15, pu_w=0.42, pd_l=0.15, pd_w=0.36, pg_l=0.15, pg_w=0.36,
        precharge_w=0.42, colmux_w=4.00, writedrive_w=3.90,
        wldrive_nmos_w=0.50, wldrive_pmos_w=1.00,
        prbound=cast(_prm.Auxiliary, _prims.prBoundary),
    )

    def __init__(self, *, lib: _lbry.Library):
        super().__init__(lib=lib, spec=self.spec)

class Sky130DP8TFactory(DP8TFactory):
    spec: DP8TSpecification = DP8TSpecification(
        nmos=cast(_prm.MOSFET, _prims.nfet_01v8_sc), pmos=cast(_prm.MOSFET, _prims.pfet_01v8),
        stdcelllib=_std.stdcelllib,
        pu_l=0.15, pu_w=0.42, pd_l=0.15, pd_w=0.36, pg_l=0.17, pg_w=0.36,
        precharge_w=0.42, colmux_w=4.00, writedrive_w=3.90,
        wldrive_nmos_w=0.50, wldrive_pmos_w=1.00,
        prbound=cast(_prm.Auxiliary, _prims.prBoundary),
    )

    def __init__(self, *, lib: _lbry.Library):
        super().__init__(lib=lib, spec=self.spec)

memlib = _lbry.Library(
    name="MemLib",
    tech=_pdk.tech, cktfab=_pdk.cktfab, layoutfab=_pdk.layoutfab,
)
# SP
_fab = Sky130SP6TFactory(lib=memlib)
# WIP: generate cells
_fab.block(address_groups=(3, 4, 2), word_size=64, we_size=8, cell_name="Block_512x64_8WE").layout
# DP
_fab = Sky130DP8TFactory(lib=memlib)
_fab.block(address_groups=(3, 4, 2), word_size=64, we_size=8, cell_name="Block_512x64_8WE").layout

_klio.merge(memlib)
