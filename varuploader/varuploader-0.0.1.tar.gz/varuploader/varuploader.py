#!/usr/bin/env python3

# Copyright 2022 Variscite LTD
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os

from varuploader.config import *
from varuploader.menubar import MenuBar
from varuploader.release import NewReleaseWindow
from varuploader.release import ReleaseWindow
from varuploader.welcome import MainWindow


class VarUploaderGUI(Gtk.Window):
    def __init__(self):
        super(VarUploaderGUI, self).__init__(title=WINDOW_T)
        self.set_default_size(WINDOW_W, WINDOW_H)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        menu_bar = MenuBar(self)
        main_box.pack_start(menu_bar, False, False, 0)

        self.con = Gtk.Box()
        main_box.pack_start(self.con, True, True, 0)
        self.show_all()

        self.main_window = MainWindow(self)
        self.new_release_window = NewReleaseWindow(self)
        self.release_window = ReleaseWindow(self)

        self.con.add(self.main_window)
        self.con.add(self.new_release_window)
        self.con.add(self.release_window)
        self.con.show()


def main():
    os.makedirs(CACHEDIR, exist_ok=True)
    app = VarUploaderGUI()
    app.connect('delete-event', Gtk.main_quit)
    app.show()
    app.main_window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
