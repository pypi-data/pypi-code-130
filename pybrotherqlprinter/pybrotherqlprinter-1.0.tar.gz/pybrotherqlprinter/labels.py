#!/usr/bin/env python3

from enum import IntEnum

class FormFactor(IntEnum):
    """
    Enumeration representing the form factor of a label.
    The labels for the Brother QL series are supplied either as die-cut (pre-sized), or for more flexibility the
    continuous label tapes offer the ability to vary the label length.
    """
    #: rectangular die-cut labels
    DIE_CUT = 1
    #: endless (continouse) labels
    ENDLESS = 2
    #: round die-cut labels
    ROUND_DIE_CUT = 3

class Label:

    def __init__(
        self,
        name,
        size,
        form_factor,
        dots_total,
        dots_printable,
        offset_right,
        feed_margin=0
    ):
        self.name = name
        self.size = size
        self.form_factor = form_factor
        self.dots_total = dots_total
        self.dots_printable = dots_printable
        self.offset_right = offset_right
        self.feed_margin = feed_margin

    def __repr__(self):
        return "<Label %s>" % self.name


        
_ALL_LABELS = [
    Label("12",     ( 12,   0), FormFactor.ENDLESS,       ( 142,    0), ( 106,    0),  29 , feed_margin=35),
    Label("29",     ( 29,   0), FormFactor.ENDLESS,       ( 342,    0), ( 306,    0),   6 , feed_margin=35),
    Label("38",     ( 38,   0), FormFactor.ENDLESS,       ( 449,    0), ( 413,    0),  12 , feed_margin=35),
    Label("50",     ( 50,   0), FormFactor.ENDLESS,       ( 590,    0), ( 554,    0),  12 , feed_margin=35),
    Label("54",     ( 54,   0), FormFactor.ENDLESS,       ( 636,    0), ( 590,    0),   0 , feed_margin=35),
    Label("62",     ( 62,   0), FormFactor.ENDLESS,       ( 732,    0), ( 696,    0),  12 , feed_margin=35),
    Label("102",    (102,   0), FormFactor.ENDLESS,       (1200,    0), (1164,    0),  12 , feed_margin=35),
    Label("103",    (104,   0), FormFactor.ENDLESS,       (1224,    0), (1200,    0),  12 , feed_margin=35),
    Label("17x54",  ( 17,  54), FormFactor.DIE_CUT,       ( 201,  636), ( 165,  566),   0 ),
    Label("17x87",  ( 17,  87), FormFactor.DIE_CUT,       ( 201, 1026), ( 165,  956),   0 ),
    Label("23x23",  ( 23,  23), FormFactor.DIE_CUT,       ( 272,  272), ( 202,  202),  42 ),
    Label("29x42",  ( 29,  42), FormFactor.DIE_CUT,       ( 342,  495), ( 306,  425),   6 ),
    Label("29x90",  ( 29,  90), FormFactor.DIE_CUT,       ( 342, 1061), ( 306,  991),   6 ),
    Label("39x90",  ( 38,  90), FormFactor.DIE_CUT,       ( 449, 1061), ( 413,  991),  12 ),
    Label("39x48",  ( 39,  48), FormFactor.DIE_CUT,       ( 461,  565), ( 425,  495),   6 ),
    Label("52x29",  ( 52,  29), FormFactor.DIE_CUT,       ( 614,  341), ( 578,  271),   0 ),
    Label("62x29",  ( 62,  29), FormFactor.DIE_CUT,       ( 732,  341), ( 696,  271),  12 ),
    Label("62x100", ( 62, 100), FormFactor.DIE_CUT,       ( 732, 1179), ( 696, 1109),  12 ),
    Label("102x51", (102,  51), FormFactor.DIE_CUT,       (1200,  596), (1164,  526),  12 ),
    Label("102x152",(102, 153), FormFactor.DIE_CUT,       (1200, 1804), (1164, 1660),  12 ),
    # size 103 has media width 104
    Label("103x164",(104, 164), FormFactor.DIE_CUT,       (1224, 1941), (1200, 1822),  12 ),
    Label("d12",    ( 12,  12), FormFactor.ROUND_DIE_CUT, ( 142,  142), (  94,   94), 113 ),
    Label("d24",    ( 24,  24), FormFactor.ROUND_DIE_CUT, ( 284,  284), ( 236,  236),  42 ),
    Label("d58",    ( 58,  58), FormFactor.ROUND_DIE_CUT, ( 688,  688), ( 618,  618),  51 ),
]

def get_label(name):
    x = [e for e in _ALL_LABELS if e.name == name]
    if x: return x[0]
    return None

def find_label(width=None, length=None, form_factor=None):
    found = _ALL_LABELS
    if form_factor:
        found = [e for e in found if e.form_factor == form_factor]
    if width:
        found = [e for e in found if e.size[0] == width]
    if length:
        found = [e for e in found if e.size[1] == length]
    return found
