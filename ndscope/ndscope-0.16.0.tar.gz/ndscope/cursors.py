# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
import pyqtgraph as pg

from . import util
from .const import LABEL_FILL, COLOR_MODE


def _calc_reset_values(r):
    return (
        (3*r[0] + r[1])/4,
        (r[0] + 3*r[1])/4,
    )


class TCursors(QtCore.QObject):
    __slots__ = [
        'T1', 'T2', 'diff',
    ]

    # the signalling here works differently than for the YCursor
    # class, which is all self contained.  for T cursors we want to
    # synchronize among all plots, so we create a single signal that
    # the scope can subscribe to, and then let the scope update the T
    # cursors in all the plots
    cursor_moved = Signal('PyQt_PyObject')

    def __init__(self, plot):
        super().__init__()
        self.plot = plot
        pen = pg.mkPen(style=Qt.DashLine)
        label_opts = {
            'position': 0,
            'anchors': [(0, 1), (1, 1)],
            'fill': LABEL_FILL,
        }
        self.T1 = pg.InfiniteLine(
            angle=90,
            pen=pen,
            movable=True,
            label='T1',
            labelOpts=label_opts,
        )
        self.T2 = pg.InfiniteLine(
            angle=90,
            pen=pen,
            movable=True,
            label='T2',
            labelOpts=label_opts,
        )
        self.T1._index = 'T1'
        self.T2._index = 'T2'
        self.T1.sigPositionChanged.connect(self._cursor_moved_slot)
        self.T2.sigPositionChanged.connect(self._cursor_moved_slot)
        self.diff = pg.InfiniteLine(
            angle=90,
            pen=pg.mkPen(None),
            label='diff',
            labelOpts={
                'position': 1,
                'anchors': [(0.5, 0), (0.5, 0)],
                'fill': LABEL_FILL,
            },
        )
        # always on top
        self.T1.setZValue(1)
        self.T2.setZValue(1)
        self.diff.setZValue(1)
        self.set_visible(False, False)

    def set_font(self, font):
        """set text label font"""
        for label in [self.T1.label, self.T2.label, self.diff.label]:
            label.textItem.setFont(font)

    def set_color_mode(self, mode):
        """set color mode"""
        fg = COLOR_MODE[mode]['fg']
        bg = COLOR_MODE[mode]['bg']
        for line in [self.T1, self.T2, self.diff]:
            line.label.fill = bg
            line.label.setColor(fg)
            line.pen.setColor(fg)

    def _cursor_moved_slot(self, line):
        value = line.value()
        # emit cursor signal for other plots
        self.cursor_moved.emit((line._index, value))
        # update labels
        line.label.setText('{}={}'.format(line._index, util.TDStr(value)))
        l0 = self.T1.value()
        l1 = self.T2.value()
        self.diff.setValue((l0 + l1)/2)
        vdiff = np.abs(l1 - l0)
        label = u'<table><tr><td rowspan="2" valign="middle">ΔT=</td><td>{}</td></tr><tr><td>{:g} Hz</td></tr></table></nobr>'.format(
            str(util.TDStr(vdiff)),
            1/vdiff,
        )
        self.diff.label.setHtml(label)

    def set_visible(self, t1=None, t2=None):
        """set cursor visibility

        Values should be True or False, or None to not change.

        """
        if t1 is not None:
            self.T1.setVisible(t1)
        if t2 is not None:
            self.T2.setVisible(t2)
        self.diff.setVisible(self.T1.isVisible() and self.T2.isVisible())

    def are_visible(self):
        """True if either cursor is visible"""
        return self.T1.isVisible() or self.T2.isVisible()

    def get_values(self):
        """get cursor values as a tuple"""
        return (self.T1.value(), self.T2.value())

    def set_values(self, t1=None, t2=None):
        """set cursor values

        Values should be floats.

        """
        if t1:
            self.T1.setValue(t1)
        if t2:
            self.T2.setValue(t2)

    def reset(self):
        """reset cursor values"""
        t, y = self.plot.viewRange()
        self.set_values(*_calc_reset_values(t))

    def export(self):
        """export cursors

        Value will be None or absent if the cursor is not visible.
        Use load_values() to load these values.

        """
        if self.T1.isVisible():
            if self.T2.isVisible():
                return (self.T1.value(), self.T2.value())
            else:
                return (self.T1.value(),)
        elif self.T2.isVisible():
            return (None, self.T2.value())
        return ()

    def load(self, cursors):
        """load cursors

        Load exported cursors.  If the tuple only includes one value,
        only Y1 will be turned on, if the tuple includes two values,
        but Y1 and Y2 will be turned on.

        """
        t1 = None
        t2 = None
        if len(cursors) == 1:
            t1 = cursors[0]
        elif len(cursors) == 2:
            t1, t2 = cursors
        else:
            raise ValueError("Only two T cursors supported.")
        self.set_values(t1, t2)
        self.set_visible(t1 is not None, t2 is not None)


class YCursors(QtCore.QObject):
    __slots__ = [
        'Y1', 'Y2', 'diff',
    ]

    def __init__(self, plot):
        super().__init__()
        self.plot = plot
        pen = pg.mkPen(style=Qt.DashLine)
        label_opts = {
            'position': 0,
            'anchors': [(0, 0), (0, 1)],
            'fill': LABEL_FILL,
        }
        self.Y1 = pg.InfiniteLine(
            angle=0,
            pen=pen,
            movable=True,
            label='Y1',
            labelOpts=label_opts,
        )
        self.Y2 = pg.InfiniteLine(
            angle=0,
            pen=pen,
            movable=True,
            label='Y2',
            labelOpts=label_opts,
        )
        self.Y1._index = 'Y1'
        self.Y2._index = 'Y2'
        self.Y1.sigPositionChanged.connect(self._cursor_moved_slot)
        self.Y2.sigPositionChanged.connect(self._cursor_moved_slot)
        self.diff = pg.InfiniteLine(
            angle=0,
            pen=pg.mkPen(None),
            label='diff',
            labelOpts={
                'position': 1,
                'anchors': [(1, 0.5), (1, 0.5)],
                'fill': LABEL_FILL,
            },
        )
        # always on top
        self.Y1.setZValue(1)
        self.Y2.setZValue(1)
        self.diff.setZValue(1)
        self.set_visible(False, False)
        # stored values, needed for when scale changes and cursor
        # positions need to be updated
        self.y1_val = self.Y1.value()
        self.y2_val = self.Y2.value()

    def set_font(self, font):
        """set text label font"""
        for label in [self.Y1.label, self.Y2.label, self.diff.label]:
            label.textItem.setFont(font)

    def set_color_mode(self, mode):
        """set color mode"""
        fg = COLOR_MODE[mode]['fg']
        bg = COLOR_MODE[mode]['bg']
        for line in [self.Y1, self.Y2, self.diff]:
            line.label.fill = bg
            line.label.setColor(fg)
            line.pen.setColor(fg)

    def _cursor_moved_slot(self, line):
        y1 = self.Y1.value()
        y2 = self.Y2.value()
        self.diff.setValue((y1 + y2)/2)
        self.y1_val = self.plot.y_pos_to_val(y1)
        self.y2_val = self.plot.y_pos_to_val(y2)
        self.Y1.label.setText(f'Y1={self.y1_val:g}')
        self.Y2.label.setText(f'Y2={self.y2_val:g}')
        vdiff = np.abs(self.y2_val - self.y1_val)
        label = u'ΔY={:g}'.format(vdiff)
        self.diff.label.setText(label)

    def set_visible(self, y1=None, y2=None):
        """set cursor visibility

        Value should be True or False, or None to not change.

        """
        if y1 is not None:
            self.Y1.setVisible(y1)
        if y2 is not None:
            self.Y2.setVisible(y2)
        self.diff.setVisible(self.Y1.isVisible() and self.Y2.isVisible())

    def are_visible(self):
        """True if either cursor is visible"""
        return self.Y1.isVisible() or self.Y2.isVisible()

    def get_values(self):
        """get cursor values as a tuple"""
        return (self.y1_val, self.y2_val)

    def set_values(self, y1=None, y2=None):
        """set cursor values

        Values should be floats.

        """
        if y1:
            y1 = self.plot.y_val_to_pos(y1)
            if y1 is not None:
                self.Y1.setValue(y1)
                #self.set_visible(y1=True)
            else:
                self.set_visible(y1=False)
        if y2:
            y2 = self.plot.y_val_to_pos(y2)
            if y2 is not None:
                self.Y2.setValue(y2)
                #self.set_visible(y2=True)
            else:
                self.set_visible(y2=False)

    def reset(self):
        """reset cursor values"""
        t, y = self.plot.viewRange()
        self.set_values(*_calc_reset_values(y))

    def redraw(self):
        """redraw the cursor lines

        Use when plot Y axis scale changed.

        """
        self.set_values(*self.get_values())

    def export(self):
        """export cursors

        Value will be None or absent if the cursor is not visible.
        Use load_values() to load these values.

        """
        y1, y2 = self.get_values()
        if self.Y1.isVisible():
            if self.Y2.isVisible():
                return (y1, y2)
            else:
                return (y1,)
        elif self.Y2.isVisible():
            return (None, y2)
        return ()

    def load(self, y_tuple):
        """load cursors

        Load exported cursors.  If the tuple only includes one value,
        only Y1 will be turned on, if the tuple includes two values,
        but Y1 and Y2 will be turned on.

        """
        y1 = None
        y2 = None
        if len(y_tuple) == 1:
            y1 = y_tuple[0]
        elif len(y_tuple) == 2:
            y1, y2 = y_tuple
        else:
            raise ValueError("Only two Y cursors supported.")
        self.set_values(y1, y2)
        self.set_visible(y1 is not None, y2 is not None)
