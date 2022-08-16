#!/usr/bin/env python3
# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

import gi
gi.require_version('Gtk',  "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Box):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._image = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        main_box.set_margin_left(100)
        main_box.set_margin_right(100)
        self.add(main_box)

        box = Gtk.Box()
        main_box.pack_start(box, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        new_release_button = Gtk.Button.new_with_label("Create a new release")
        new_release_button.connect("clicked", self.on_new_release_clicked)
        hbox.pack_start(new_release_button, True, True, 0)

        edit_release_button = Gtk.Button.new_with_label("Edit an existing release")
        edit_release_button.connect("clicked", self.on_edit_release_clicked)
        edit_release_button.set_sensitive(False)
        hbox.pack_start(edit_release_button, True, True, 0)

        remove_release_button = Gtk.Button.new_with_label("Remove an existing release")
        remove_release_button.connect("clicked", self.on_remove_release_clicked)
        remove_release_button.set_sensitive(False)
        hbox.pack_start(remove_release_button, True, True, 0)
        main_box.pack_start(hbox, False, True, 0)

        box = Gtk.Box()
        main_box.pack_start(box, True, True, 0)

    def on_new_release_clicked(self, button):
        self._parent.new_release_window.show_all()
        self.hide()

    def on_edit_release_clicked(self, button):
        """
            TODO
        """
        print("Edit release")

    def on_remove_release_clicked(self, button):
        """
            TODO
        """
        print("Remove release")
