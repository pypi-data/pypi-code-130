# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

import gi
gi.require_versions({'GdkPixbuf': "2.0", 'Gtk': "3.0"})
from gi.repository import GdkPixbuf, Gtk
import os

from varuploader.config import VARISCITE_LOGO_PATH

license = (f"Redistribution and use in source and binary forms, with or without\n"
           f"modification, are permitted provided that the following conditions are met:\n\n"
           f"1. Redistributions of source code must retain the above copyright notice, this\n"
           f"list of conditions and the following disclaimer.\n\n"
           f"2. Redistributions in binary form must reproduce the above copyright notice,\n"
           f"this list of conditions and the following disclaimer in the documentation\n"
           f"and/or other materials provided with the distribution.\n\n"
           f"3. Neither the name of the copyright holder nor the names of its\n"
           f"contributors may be used to endorse or promote products derived from\n"
           f"this software without specific prior written permission.\n\n"
           f"THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\"\n"
           f"AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE\n"
           f"IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE\n"
           f"DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE\n"
           f"FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL\n"
           f"DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR\n"
           f"SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER\n"
           f"CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,\n"
           f"OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE\n"
           f"OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n")

class MenuBar(Gtk.MenuBar):
    def __init__(self, parent):
        super().__init__()
        item_about = Gtk.MenuItem.new_with_label('About')
        item_about.connect('activate', self.on_about, parent)

        menu_help = Gtk.Menu.new()
        menu_help.append(item_about)

        item_help = Gtk.MenuItem.new_with_label('Help')
        item_help.set_submenu(menu_help)

        self.new()
        self.append(item_help)

    def on_about(self, menu, parent):
        authors = ["Alifer Moraes", "Diego Dorta"]
        dialog = Gtk.AboutDialog(parent=parent)
        logo = GdkPixbuf.Pixbuf.new_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), VARISCITE_LOGO_PATH))
        if logo != None:
            dialog.set_logo(logo)
        else:
            print("A GdkPixbuf Error has occurred.")
        dialog.set_name("VarUploader")
        dialog.set_version("0.1 - Beta")
        dialog.set_copyright("(C) 2022 Variscite LTD")
        dialog.set_comments("Recovery SD Card Uploader Tool")
        dialog.set_license(license)
        dialog.set_website("https://github.com/dorta/var-uploader")
        dialog.set_website_label("VarUploader on Github")
        dialog.set_authors(authors)
        dialog.connect("response", self.on_about_dialog_button_clicked)
        dialog.run()

    def on_about_dialog_button_clicked(self, dialog, response):
        dialog.destroy()
