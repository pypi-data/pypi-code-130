# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

import gi
gi.require_version('Gtk',  "3.0")
from gi.repository import GLib, Gtk
import os
from pathlib import Path
from threading import Thread
from time import sleep

import yaml

from varuploader.config import MX8_YAML_CHANGELOG_FILES
from varuploader.config import VAR_SYSTEM_ON_MODULES
from varuploader.ftp import connect_ftp
from varuploader.ftp import retrieve_remote_file
from varuploader.ftp import stor_remote_file
from varuploader.utils import calculate_sha224_hash
from varuploader.utils import check_image_file_extension
from varuploader.utils import get_current_date
from varuploader.utils import get_file_size
from varuploader.utils import get_som_folder_path
from varuploader.utils import get_release_name


class NewReleaseWindow(Gtk.Box):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._image = None
        self._module = None
        self._os = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        self.add(main_box)

        box = Gtk.Box()
        main_box.pack_start(box, True, True, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_left(100)
        vbox.set_margin_right(100)

        label = Gtk.Label()
        label.set_text("Recovery SD card")
        vbox.pack_start(label, False, True, 0)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Select a Recovery SD card...")
        self.entry.set_editable(False)
        vbox.pack_start(self.entry, False, True, 0)

        info_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        os_label = Gtk.Label(label="Select OS:")
        hbox.pack_start(os_label, True, True, 0)

        yocto_check_button = Gtk.CheckButton(label="Yocto")
        yocto_check_button.connect("toggled", self.on_check_button_toggled, "yocto")
        yocto_check_button.set_active(True)
        hbox.pack_start(yocto_check_button, True, True, 0)

        b2qt_check_button = Gtk.CheckButton(label="B2Qt")
        b2qt_check_button.connect("toggled", self.on_check_button_toggled, "b2qt")
        b2qt_check_button.set_sensitive(False)
        hbox.pack_start(b2qt_check_button, True, True, 0)

        debian_check_button = Gtk.CheckButton(label="Debian")
        debian_check_button.connect("toggled", self.on_check_button_toggled, "debian")
        debian_check_button.set_sensitive(False)
        hbox.pack_start(debian_check_button, True, True, 0)

        info_hbox.pack_start(hbox, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        modules_label = Gtk.Label(label="Select module:")

        modules_combo = Gtk.ComboBoxText()
        modules_combo.set_entry_text_column(0)
        modules_combo.connect("changed", self.on_module_combo_changed)
        for module in VAR_SYSTEM_ON_MODULES:
            modules_combo.append_text(module)

        modules_combo.set_active(0)

        hbox.pack_start(modules_label, True, True, 0)
        hbox.pack_start(modules_combo, True, True, 0)
        info_hbox.pack_start(hbox, True, True, 0)
        vbox.pack_start(info_hbox, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        open_file_button = Gtk.Button.new_with_label("Open")
        open_file_button.connect("clicked", self.on_open_clicked, self._parent)
        hbox.pack_start(open_file_button, True, True, 0)

        self.new_release_button = Gtk.Button.new_with_label("Create Release")
        self.new_release_button.connect("clicked", self.on_create_release_clicked)
        self.new_release_button.set_sensitive(False)
        hbox.pack_start(self.new_release_button, True, True, 0)

        vbox.pack_start(hbox, True, True, 0)
        main_box.pack_start(vbox, False, True, 0)

        box = Gtk.Box()
        main_box.pack_start(box, True, True, 0)

    def on_open_clicked(self, button, parent):
        dialog = Gtk.FileChooserDialog(title="Please choose a file", parent=parent,
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        while(True):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                image = dialog.get_filename()
                if not check_image_file_extension(image):
                    dialog.destroy()
                    invalid_image_dialog = InvalidImageDialog(self._parent)
                    response = invalid_image_dialog.run()
                    if response == Gtk.ResponseType.OK:
                        pass

                    invalid_image_dialog.destroy()
                    break
                self._image = image
                self.entry.set_text(image)
                self.new_release_button.set_sensitive(True)
                parent.con.remove(parent.release_window)
                parent.release_window = ReleaseWindow(parent, image, self._module, self._os)
                parent.con.add(parent.release_window)
                parent.con.show()
                parent.show()
                dialog.destroy()
                break

    def on_create_release_clicked(self, button):
        self._parent.release_window.show_all()
        self.hide()

    def on_check_button_toggled(self, checkbutton, os):
        if checkbutton.get_active():
            self._os = os
        else:
            checkbutton.set_active(True)

    def on_module_combo_changed(self, combo):
        module = combo.get_active_text()
        if module:
            self._module = module


class ReleaseWindow(Gtk.Box):
    def __init__(self, parent, file_path=None, module=None, os=None):
        super().__init__()
        self._parent = parent
        self._date = get_current_date("%m/%d/%Y")
        self._file_path = file_path
        self._module = module
        self._os = os
        self._file_sha224 = None if not file_path else calculate_sha224_hash(file_path)
        self._file_size = None if not file_path else get_file_size(file_path)
        self._ftp_path = None if not file_path else get_som_folder_path(module, os)
        self._info = {"Release Date": self._date, "Yocto Version": None, "Yocto Release": None,
                      "Android Version": None, "Android Release": None, "Upload Path": self._ftp_path,
                      "Image SHA224": self._file_sha224, "Image Size": self._file_size}
        self._info_example = {"Release Date": "", "Yocto Version": "(e.g., v1.0)", "Yocto Release": "(e.g., Hardknott 5.10.72_2.2.1)",
                              "Android Version": "(e.g., v1.0)", "Android Release": "(e.g., 11.0.0_1.0.0)", "Upload Path": "", "Image SHA224": "", "Image Size": ""}

        path = self._info["Upload Path"]
        self._changelog = None if not path else MX8_YAML_CHANGELOG_FILES[Path(path).parts[0]]

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        main_box.set_margin_left(20)
        main_box.set_margin_right(20)
        self.add(main_box)

        back_button = Gtk.Button.new_with_label("Back")
        back_button.connect("clicked", self.on_back_clicked)

        notebook = Gtk.Notebook()
        notebook.set_hexpand(True)
        notebook.set_vexpand(True)

        self.release_page = ReleasePage(self._info, self._info_example)
        self.changelog_page = ChangelogPage()
        self.sources_page = SourcesPage()

        add_notebook_page(notebook, self.release_page, "Release")
        add_notebook_page(notebook, self.changelog_page, "Changelog")
        add_notebook_page(notebook, self.sources_page, "Sources")

        export_release_button = Gtk.Button.new_with_label("Export Release")
        export_release_button.connect("clicked", self.on_export_release_clicked)

        main_box.pack_start(back_button, False, True, 5)
        main_box.pack_start(notebook, True, True, 5)
        main_box.pack_start(export_release_button, False, True, 5)

    def _export_yml(self):
        self.release_page.write_release_entries()
        self.changelog_page.write_changelog_entries()
        self.sources_page.write_sources_entries()

        return {'Release': self.release_page.release_dict,
                'Changes': self.changelog_page.changelog_dict,
                'Sources': self.sources_page.sources_dict}

    def on_back_clicked(self, button):
        self._parent.main_window.show_all()
        self.hide()

    def on_export_release_clicked(self, button):
        yaml_dict = self._export_yml()
        file_name = get_release_name(self._module, yaml_dict)
        ftp = None

        confirmation_dialog = ConfirmationDialog(self._parent, yaml_dict, file_name)
        confirmation_response = confirmation_dialog.run()

        if confirmation_response == Gtk.ResponseType.OK:
            login_dialog = LoginDialog(confirmation_dialog)
            ftp = None

            while not ftp:
                login_response = login_dialog.run()

                if login_response == Gtk.ResponseType.OK:
                    ftp = login_dialog.get_ftp()
                    if ftp:
                        thread = Thread(target=login_dialog.upload_to_ftp,
                                        args=(yaml_dict, self._changelog,
                                              self._info["Upload Path"],
                                              self._file_path, file_name))
                        thread.daemon = True
                        thread.start()
                else:
                    login_dialog.destroy()
                    break

        confirmation_dialog.destroy()


class ConfirmationDialog(Gtk.Dialog):
    def __init__(self, parent, yaml_dict, file_name):
        super().__init__(title="Release Changelog Preview", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        window_size = parent.get_size()
        self.set_default_size(*window_size)

        sw = Gtk.ScrolledWindow()
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        label_box = Gtk.Box()

        yaml_dump = yaml.dump(yaml_dict, Dumper=IndentDumper,
                              sort_keys=False).replace("  ", "\t")

        label = Gtk.Label(label=f"File Name: {file_name}\n\n{yaml_dump}")
        label_box.pack_start(label, False, True, 10)
        sw.add(label_box)

        box = self.get_content_area()
        box.add(sw)
        self.show_all()


class InvalidImageDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Invalid Image", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        label = Gtk.Label(label="Invalid image. Please select a valid one.")

        box = self.get_content_area()
        box.set_margin_left(50)
        box.set_margin_right(50)
        box.add(label)
        self.show_all()


class LoginDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Login", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        window_size = parent.get_size()
        self.set_default_size(*window_size)

        self._ftp = None
        self._error_msg = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        credentials_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        credentials_box.set_hexpand(True)
        credentials_box.set_vexpand(True)
        credentials_box.set_margin_left(10)
        credentials_box.set_margin_right(10)
        credentials_box.set_margin_top(10)

        label = Gtk.Label(label="Enter FTP credentials")
        credentials_box.pack_start(label, False, True, 0)

        username_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        username_label =  Gtk.Label(label="Username:\t")
        self.username_entry = Gtk.Entry()
        username_hbox.pack_start(username_label, False, True, 0)
        username_hbox.pack_start(self.username_entry, True, True, 0)
        credentials_box.pack_start(username_hbox, False, True, 0)

        passwd_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        passwd_label =  Gtk.Label(label="Password:\t")
        self.passwd_entry = Gtk.Entry()
        self.passwd_entry.set_visibility(False)
        passwd_hbox.pack_start(passwd_label, False, True, 0)
        passwd_hbox.pack_start(self.passwd_entry, True, True, 0)
        credentials_box.pack_start(passwd_hbox, False, True, 0)

        self.error_label = Gtk.Label(label="")
        credentials_box.pack_start(self.error_label, False, True, 0)

        progress_box = Gtk.Box(spacing=10)
        self.progress_label = Gtk.Label(label="Progress:")
        progress_box.pack_start(self.progress_label, False, True, 0)

        main_box.pack_start(credentials_box, True, True, 10)
        main_box.pack_start(progress_box, True, True, 10)

        box = self.get_content_area()
        box.add(main_box)
        self.show_all()

    def set_progress_message(self, msg):
        self.progress_label.set_text(f"{self.progress_label.get_text()}\n{msg}")

    def get_ftp(self):
        self.error_label.set_text("Connecting...")
        self._ftp, self._error_msg = connect_ftp(ftp_user_name=self.username_entry.get_text(),
                                                 ftp_passwd=self.passwd_entry.get_text())

        if not self._ftp:
            self.error_label.set_text(str(self._error_msg))

        return self._ftp

    def upload_to_ftp(self, yaml_dict, changelog, ftp_path, file_path, file_name):
        GLib.idle_add(self.error_label.set_text, "")
        GLib.idle_add(self.set_progress_message, f"Downloading {changelog} from ftp")
        retrieved_file = retrieve_remote_file(self.get_ftp(), changelog,
                                              os.path.join("General",ftp_path))
        GLib.idle_add(self.set_progress_message, f"{changelog} saved at {retrieved_file}")

        with open(retrieved_file, 'a') as f:
            yaml.dump(yaml_dict, f,  Dumper=IndentDumper, default_flow_style=False,
                    explicit_start=True, sort_keys=False)

        GLib.idle_add(self.set_progress_message, f"Uploading {changelog} to ftp")
        uploaded = stor_remote_file(self.get_ftp(), changelog, retrieved_file,
                                    os.path.join("General",ftp_path))
        if uploaded:
            GLib.idle_add(self.set_progress_message,
                          f"{changelog} uploaded successfully")
            GLib.idle_add(self.set_progress_message, f"Uploading {file_name}")
            uploaded = stor_remote_file(self.get_ftp(), file_name, file_path,
                                        os.path.join("General",ftp_path))
            if uploaded:
                GLib.idle_add(self.set_progress_message,
                              f"{file_name} uploaded successfully")
            else:
                GLib.idle_add(self.set_progress_message,
                              f"{file_name} upload failed")
        else:
            GLib.idle_add(self.set_progress_message, f"{changelog} upload failed")
        GLib.idle_add(self.set_progress_message, "Completed")
        sleep(5)
        self.destroy()


class ReleasePage(Gtk.Box):
    def __init__(self, release_info, release_example):
        super().__init__()
        self._release_info = release_info
        self._release_example = release_example
        self.release_entries = []
        self.release_dict = {}

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_hexpand(True)
        vbox.set_vexpand(True)
        vbox.set_margin_left(10)
        vbox.set_margin_right(10)
        vbox.set_margin_top(5)
        self.add(vbox)

        for info in self._release_info:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            label = Gtk.Label(label=f"{info:14}\t")
            entry = Gtk.Entry()
            if self._release_info[info]:
                entry.set_text(self._release_info[info])
                entry.set_editable(False)
            else:
                entry.set_placeholder_text(f"Add {info.lower()}... {self._release_example[info]}")
            self.release_entries.append(entry)
            hbox.pack_start(label, False, True, 0)
            hbox.pack_start(entry, True, True, 0)
            vbox.pack_start(hbox, False, True, 0)

    def write_release_entries(self):
        for info, entry in zip(self._release_info, self.release_entries):
            self.release_dict[info] = entry.get_text()


class ChangelogPage(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.changelog_dict = {}

        notebook = Gtk.Notebook()
        notebook.set_hexpand(True)
        notebook.set_vexpand(True)
        self.add(notebook)

        self.yocto_page = self.UpdatesPage()
        self.android_page = self.UpdatesPage()

        add_notebook_page(notebook, self.yocto_page, "Yocto")
        add_notebook_page(notebook, self.android_page, "Android")

    def write_changelog_entries(self):
        self.changelog_dict["Yocto"] = self.yocto_page.write_updates_entries()
        self.changelog_dict["Android"] = self.android_page.write_updates_entries()

    class UpdatesPage(Gtk.Box):
        def __init__(self):
            super().__init__()
            self.updates_entries = {}
            self.updates_dict =  {}

            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.main_box.set_hexpand(True)
            self.main_box.set_vexpand(True)
            self.main_box.set_margin_left(10)
            self.main_box.set_margin_right(10)
            self.main_box.set_margin_top(5)
            self.add(self.main_box)

            self.sw_vbox = []

            self.add_changelog_section("U-Boot", 0)
            self.add_changelog_section("Linux", 1)

        def add_changelog_section(self, target, pos):
            self.updates_entries[target] = []
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            vbox.set_hexpand(True)
            vbox.set_vexpand(True)

            header_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label(label=f"{target} Changelog")
            add_button = Gtk.Button.new_with_label("Add New")
            add_button.connect("clicked", self.on_add_button_clicked, target, pos)
            header_hbox.pack_start(label, True, True, 0)
            header_hbox.pack_start(add_button, False, False, 0)
            vbox.pack_start(header_hbox, False, True, 0)

            sw = Gtk.ScrolledWindow()
            vbox.pack_start(sw, True, True, 0)
            sw_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            sw.add(sw_vbox)
            self.sw_vbox.append(sw_vbox)
            self.main_box.pack_start(vbox, True, True, 0)

        def write_updates_entries(self):
            for target, updates_list in self.updates_entries.items():
                self.updates_dict[target] = []

                for update in updates_list:
                    self.updates_dict[target].append(update.get_text())

                if not updates_list:
                    self.updates_dict[target] = ['No changes']

            return self.updates_dict

        def on_add_button_clicked(self, button, target, pos):
            sw_hbox =  Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            sw_hbox.set_margin_left(10)
            sw_hbox.set_margin_right(10)
            entry = Gtk.Entry()
            entry.set_placeholder_text("Add changelog...")
            self.updates_entries[target].append(entry)
            rm_button = Gtk.Button.new_with_label("Remove")
            rm_button.connect("clicked", self.on_rm_button_clicked, sw_hbox, entry, target, pos)
            sw_hbox.pack_start(entry, True, True, 0)
            sw_hbox.pack_start(rm_button, False, False, 0)
            self.sw_vbox[pos].pack_start(sw_hbox, False, True, 0)
            self.show_all()

        def on_rm_button_clicked(self, button, widget, entry, target, pos):
            self.updates_entries[target].remove(entry)
            self.sw_vbox[pos].remove(widget)
            self.show_all()


class SourcesPage(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.sources_dict = {}

        notebook = Gtk.Notebook()
        notebook.set_hexpand(True)
        notebook.set_vexpand(True)
        self.add(notebook)

        self.yocto_page = self.RepoPage("meta-variscite-imx")
        self.android_page = self.RepoPage("MX6x-Android")

        add_notebook_page(notebook, self.yocto_page, "Yocto")
        add_notebook_page(notebook, self.android_page, "Android")

    def write_sources_entries(self):
        self.sources_dict["Yocto"] = self.yocto_page.write_repo_entries()
        self.sources_dict["Android"] = self.android_page.write_repo_entries()

    class RepoPage(Gtk.Box):
        def __init__(self, meta):
            super().__init__()
            self.repo_entries = {}
            self.repo_dict = {}
            self._meta = meta

            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.main_box.set_hexpand(True)
            self.main_box.set_vexpand(True)
            self.main_box.set_margin_left(10)
            self.main_box.set_margin_right(10)
            self.main_box.set_margin_top(5)
            self.add(self.main_box)

            self._add_source_section('U-Boot')
            self._add_source_section('Linux')
            self._add_source_section(self._meta)

        def _add_source_section(self, target):
            self.repo_entries[target] = {}
            self.repo_dict[target] = {}

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            vbox.set_hexpand(True)
            vbox.set_vexpand(True)

            label = Gtk.Label(label=f"{target} Source")
            vbox.pack_start(label, False, True, 0)

            source_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)

            self._add_subsection('Git Repository', target, source_vbox)
            self._add_subsection('Git Branch', target, source_vbox)
            self._add_subsection('Git Commit ID', target, source_vbox)

            vbox.pack_start(source_vbox, True, True, 0)
            self.main_box.pack_start(vbox, True, True, 0)

        def _add_subsection(self, subsection, target, source_vbox):
            source_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label(label=f"{subsection:>16}\t")
            entry = Gtk.Entry()
            entry.set_placeholder_text(f"Add {subsection.lower()}...")
            self.repo_entries[target][subsection] = entry
            source_hbox.pack_start(label, False, False, 0)
            source_hbox.pack_start(entry, True, True, 0)
            source_vbox.pack_start(source_hbox, False, True, 0)

        def write_repo_entries(self):
            for target in self.repo_entries:
                for subsection in self.repo_entries[target]:
                    self.repo_dict[target][subsection] = self.repo_entries[target][subsection].get_text()

            return self.repo_dict


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


def add_notebook_page(notebook, page_object, page_name):
    page = page_object
    notebook.append_page(page)
    notebook.set_tab_label_text(page, page_name)
