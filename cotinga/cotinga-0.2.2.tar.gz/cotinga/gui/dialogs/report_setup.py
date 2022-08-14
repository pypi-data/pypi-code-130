# -*- coding: utf-8 -*-

# Cotinga helps maths teachers creating worksheets
# and managing pupils' progression.
# Copyright 2018-2022 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Cotinga.

# Cotinga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Cotinga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Cotinga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
try:
    gi.require_version('Gtk', '3.0')
except ValueError:
    raise
else:
    from gi.repository import Gtk

from cotinga.core import doc_setup
from cotinga.core.constants import REPORT_MIN_COLWIDTH, REPORT_MAX_COLWIDTH
from cotinga.core.constants import REPORT_MIN_TABLES, REPORT_MAX_TABLES
from cotinga.core.constants import REPORT_MIN_MAXROWS, REPORT_MAX_MAXROWS
from cotinga.gui.core import Sharee

__all__ = ['ReportSetupDialog']


class ReportSetupDialog(Gtk.Dialog, Sharee):

    def __init__(self, db, status, prefs, recollections, parentw):
        Sharee.__init__(self, db, status, prefs, recollections)
        Gtk.Dialog.__init__(self, self.tr('Report setup'), parentw, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_size_request(350, 200)
        self.box = self.get_content_area()
        self.layout = Gtk.Grid()
        self.layout.set_column_spacing(10)
        self.layout.set_row_spacing(5)
        reportsetup = doc_setup.load()['report']

        label1 = Gtk.Label(self.tr('Date format'))
        label1.set_margin_top(10)
        label1.set_margin_left(5)
        self.datefmt = Gtk.Entry()
        self.datefmt.set_editable(True)
        self.datefmt.set_margin_top(10)
        self.datefmt.set_text(reportsetup['date_fmt'])

        label2 = Gtk.Label(self.tr('Columns width (cm)'))
        label2.set_margin_left(5)
        self.colwidths = Gtk.SpinButton()
        self.colwidths.set_numeric(True)
        self.colwidths.set_snap_to_ticks(True)
        self.colwidths.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.colwidths.set_digits(1)
        self.colwidths.set_increments(0.1, 1)
        self.colwidths.set_range(REPORT_MIN_COLWIDTH, REPORT_MAX_COLWIDTH)
        self.colwidths.set_value(reportsetup['col_width'])

        label3 = Gtk.Label(self.tr('Maximum number of rows per table'))
        label3.set_margin_left(5)
        self.max_rows = Gtk.SpinButton()
        self.max_rows.set_numeric(True)
        self.max_rows.set_snap_to_ticks(True)
        self.max_rows.set_update_policy(
            Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.max_rows.set_digits(0)
        self.max_rows.set_increments(1, 1)
        self.max_rows.set_range(REPORT_MIN_MAXROWS, REPORT_MAX_MAXROWS)
        self.max_rows.set_value(reportsetup['max_rows'])

        label4 = Gtk.Label(self.tr('Maximum number of tables per page'))
        label4.set_margin_left(5)
        self.tables_store = Gtk.ListStore(str)
        for v in range(REPORT_MIN_TABLES, REPORT_MAX_TABLES + 1):
            self.tables_store.append([str(v)])
        self.max_tables = Gtk.ComboBox.new_with_model(self.tables_store)
        # self.max_tables.props.margin_bottom = 5
        self.max_tables.set_id_column(0)
        # self.max_tables.set_entry_text_column(0)
        txt_rend = Gtk.CellRendererText()
        self.max_tables.pack_start(txt_rend, True)
        self.max_tables.add_attribute(txt_rend, 'text', 0)
        active_entry = int(reportsetup['max_tables']) - REPORT_MIN_TABLES
        self.max_tables.set_active(active_entry)

        self.layout.attach(label1, 0, 0, 1, 1)
        self.layout.attach_next_to(self.datefmt, label1,
                                   Gtk.PositionType.RIGHT, 1, 1)
        self.layout.attach_next_to(label2, label1,
                                   Gtk.PositionType.BOTTOM, 1, 1)
        self.layout.attach_next_to(self.colwidths, label2,
                                   Gtk.PositionType.RIGHT, 1, 1)
        self.layout.attach_next_to(label3, label2,
                                   Gtk.PositionType.BOTTOM, 1, 1)
        self.layout.attach_next_to(self.max_rows, label3,
                                   Gtk.PositionType.RIGHT, 1, 1)
        self.layout.attach_next_to(label4, label3,
                                   Gtk.PositionType.BOTTOM, 1, 1)
        self.layout.attach_next_to(self.max_tables, label4,
                                   Gtk.PositionType.RIGHT, 1, 1)

        self.box.add(self.layout)
        self.show_all()
