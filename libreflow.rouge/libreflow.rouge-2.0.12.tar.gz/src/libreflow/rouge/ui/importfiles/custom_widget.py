from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from .shot_list import ShotList

STYLESHEET = '''
    QPushButton:disabled {
        background-color: rgba(255, 255, 255, 0);
        color: rgba(255, 255, 255, 50);
    }'''


class DragDropWidget(QtWidgets.QWidget):

    def __init__(self, custom_widget):
        super(DragDropWidget, self).__init__(custom_widget)
        self.custom_widget = custom_widget

        self.setAcceptDrops(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.frame = QtWidgets.QFrame()
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setStyleSheet('''
            background-color: #2b2b2b;
            border: 1px solid #22222b;
        ''')

        self.asset = QtWidgets.QWidget()
        asset_lo = QtWidgets.QVBoxLayout()
        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'file')))
        pixmap = icon.pixmap(QtCore.QSize(128, 128))
        self.icon_lbl = QtWidgets.QLabel('')
        self.icon_lbl.setPixmap(pixmap)
        self.label = QtWidgets.QLabel('Drop your files here')

        asset_lo.addWidget(self.icon_lbl, 0, QtCore.Qt.AlignCenter)
        asset_lo.addWidget(self.label, 1, QtCore.Qt.AlignCenter)
        self.asset.setLayout(asset_lo)
        
        glo = QtWidgets.QGridLayout()
        glo.setContentsMargins(0,0,0,0)
        glo.addWidget(self.frame, 0, 0, 3, 0)
        glo.addWidget(self.asset, 1, 0, QtCore.Qt.AlignCenter)
        self.setLayout(glo)

    def sizeHint(self):
        return QtCore.QSize(800, 493)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.custom_widget.add_files(links)
        else:
            event.ignore()


class ImportFilesWidget(CustomPageWidget):

    def build(self):
        self.setStyleSheet(STYLESHEET)

        self.reset_list()

        self.shot_list = ShotList(self)
        self.shots_count = QtWidgets.QLabel(self.shot_list.get_shots_count())
        self.dragdrop = DragDropWidget(self)
        
        self.button_settings = QtWidgets.QPushButton('Settings')
        if self.check_user_status() != 'Admin':
            self.button_settings.setEnabled(False)

        self.button_browse = QtWidgets.QPushButton('Browse')
        self.checkbox_selectall = QtWidgets.QCheckBox('Select all')
        self.checkbox_selectall.setEnabled(False)
        self.import_feedback = QtWidgets.QLabel('')
        self.button_import = QtWidgets.QPushButton('Import')

        if self.shot_list.topLevelItemCount() == 0:
            self.shot_list.hide()
            self.button_import.setEnabled(False)
        else:
            self.dragdrop.hide()
        
        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.shots_count, 0, 0, 1, 6)
        glo.addWidget(self.shot_list, 1, 0, 1, 6)
        glo.addWidget(self.dragdrop, 1, 0, 1, 6)
        glo.addWidget(self.button_settings, 2, 0)
        glo.addWidget(self.button_browse, 2, 1)
        glo.addWidget(self.checkbox_selectall, 2, 2)
        glo.addWidget(self.import_feedback, 2, 4, QtCore.Qt.AlignRight)
        glo.addWidget(self.button_import, 2, 5)
        glo.setColumnStretch(2, 3)
        self.setLayout(glo)
    
        # Install callbacks
        # self.button_settings.clicked.connect(self._on_button_settings_clicked)
        self.button_browse.clicked.connect(self._on_button_browse_clicked)
        self.checkbox_selectall.stateChanged.connect(self._on_checkbox_selectall_state_changed)
        self.button_import.clicked.connect(self._on_button_import_clicked)

    def reset_list(self):
        return self.session.cmds.Flow.call(
            self.oid, 'clear_list', {}, {}
        )

    def refresh_shots_count(self):
        return self.shots_count.setText(self.shot_list.get_shots_count())

    def check_user_status(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_user_status', {}, {}
        )

    def get_shots(self):
        return self.session.cmds.Flow.get_mapped_oids(self.oid + '/shots_map')
    
    def get_shot_files(self, shot):
        return self.session.cmds.Flow.get_mapped_oids(shot + '/files_map')

    def remove_shot(self, name):
        return self.session.cmds.Flow.call(
            self.oid + '/shots_map', 'remove', [name], {}
        )

    def add_files(self, paths):
        # Error list:
        # file = unknown file
        # kitsu = shot not found on kitsu
        # init = shot needs to be init
        # rtk = waiting a retake file and not a base file
        # pack_only = single pack folder
        # dir_name = wrong dir name
        # dir_empty = dir is empty
        # no_track = only one version of the file can be created
        # overwrite = file will be overwrite
        # not_match = plas file_name don't have the same as dir
        # no_valid_files = after listdir, no valid files has been found
        # not_all_files = can't create because not all files has been found

        self.button_import.setEnabled(False)
        self.import_feedback.setText('Waiting...')
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        check_files = self.session.cmds.Flow.call(
            self.oid, 'check_files', [paths], {}
        )

        if check_files != {'files': [], 'shots': []}:
            # Dialog when incorrect files
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)

            body = '''<b>Warning</b><br><br>
            Some files/shots can\'t be imported.<br><br>
            '''

            for f in check_files['files']:
                display_error = ''
                if f['error'] == 'file':
                    display_error = 'Unknown file'
                if f['error'] == 'kitsu':
                    display_error = 'Shot not found in Kitsu'
                if f['error'] == 'rtk':
                    display_error = 'Shot needs a retake file, not a base file'
                if f['error'] == 'init':
                    display_error = 'Shot needs to be initialized'
                if f['error'] == 'pack_only':
                    display_error = 'You should send the shot folder'
                if f['error'] == 'dir_name':
                    display_error = 'No target for this directory name'
                body = body + '''
                - {name} : {error}<br>
                '''.format(name=f['name'], error=display_error)
            
            body = body + '''
            <br>
            '''

            for s in check_files['shots']:
                if s['error'] == '':
                    body = body + '''
                    - {name}<br>
                    '''.format(name=s['shot'])
                else:
                    shot_display_error = ''
                    if s['error'] == 'kitsu':
                        shot_display_error = 'Not found in Kitsu'
                    if s['error'] == 'init':
                        shot_display_error = 'Shot needs to be initialized'
                    if s['error'] == 'dir_empty':
                        shot_display_error = 'Folder is empty'
                    if s['error'] == 'no_valid_files':
                        shot_display_error = 'Has no valid files'
                    if s['error'] == 'not_all_files':
                        shot_display_error = 'Missing necessary files'
                    body = body + '''
                    - {name} : {error}<br>
                    '''.format(name=s['shot'], error=shot_display_error)

                for f in s['files']:
                    display_error = ''
                    if f['error'] == 'file':
                        display_error = 'Unknown file'
                    if f['error'] == 'no_track':
                        display_error = 'Only one version of this file can be created'
                    if f['error'] == 'overwrite':
                        display_error = 'This file will be overwritten if imported'
                        self.shot_list.overwrite.append(s['shot'])
                    if f['error'] == 'not_match':
                        display_error = 'File name is not equal as folder'
                    if f['error'] == 'rtk':
                        display_error = 'Retake file is needed, not a base file'
                    if f['error'] == 'init':
                        display_error = 'Base file is needed, not a retake'
                    body = body + '''
                    &nbsp;&nbsp;&nbsp;&nbsp;- {name} : {error}<br>
                    '''.format(name=f['name'], error=display_error)

            msg.setText(body)

            msg.setWindowTitle('libreflow')
            msg.setWindowIcon(
                resources.get_icon(('icons.gui', 'kabaret_icon'))
            )
            msg.exec_()

        if self.get_shots() != []:
            if self.shot_list.isVisible() == False:
                self.shot_list.show()
                self.dragdrop.hide()
                self.checkbox_selectall.setCheckState(QtCore.Qt.Checked)
                self.button_import.setEnabled(True)
        
            self.shot_list.refresh()
        
        self.import_feedback.setText('')

    def _on_button_browse_clicked(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setStyleSheet('''
            QLineEdit:focus {
                border: none;
                padding: 0px;
                padding-left: 2px;
            }
        ''')
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)

        file_view = dialog.findChild(QtWidgets.QListView, 'listView')
        if file_view:
            file_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            file_view.setSelectionRectVisible(True)
        f_tree_view = dialog.findChild(QtWidgets.QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        if dialog.exec():
            paths = dialog.selectedFiles()
            self.add_files(paths)

    def _on_checkbox_selectall_state_changed(self, state):
        for i in range(self.shot_list.topLevelItemCount()):
            state = QtCore.Qt.CheckState(state)
            self.shot_list.topLevelItem(i).setCheckState(0, state)

    def _on_button_import_clicked(self):
        shots = []
        for i in range(self.shot_list.topLevelItemCount()):
            shot_item = self.shot_list.topLevelItem(i)

            if shot_item.checkState(0) == QtCore.Qt.Checked:
                shots.append(shot_item.text(0))
        
        if self.shot_list.overwrite != []:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText('''<b>Warning</b><br>Some files will be overwritten''')
            msg.setInformativeText('Are you sure to import?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setWindowTitle('libreflow')
            msg.setWindowIcon(
                resources.get_icon(('icons.gui', 'kabaret_icon'))
            )
            ret = msg.exec_()
            
            if ret == QtWidgets.QMessageBox.No:
                return

        self.button_import.setEnabled(False)
        self.import_feedback.setText('Importing...')
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        
        self.session.cmds.Flow.call(
            self.oid, 'import_shot_files', [shots], {}
        )

        self.shot_list.refresh()

        self.import_feedback.setText('Completed')