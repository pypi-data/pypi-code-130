from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources

from libreflow.baseflow.runners import CHOICES_ICONS
from ...resources.icons import gui


class LabelIcon(QtWidgets.QLabel):

    def __init__(self, icon=None):
        QtWidgets.QLabel.__init__(self, '')

        icon = QtGui.QIcon(resources.get_icon(icon))
        pixmap = icon.pixmap(QtCore.QSize(16, 16))
        self.setPixmap(pixmap)
        self.setAlignment(QtCore.Qt.AlignVCenter)


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, value, dialog_widget):
        QtWidgets.QLineEdit.__init__(self)
        self.dialog_widget = dialog_widget
    
        if value != None:
            self.setText(value)

        self.editingFinished.connect(self.on_text_finish_edit)
         
    def on_text_finish_edit(self):
        if not self.text():
            self.setProperty('error', True)
            self.setStyleSheet('''
                QLineEdit {
                    border-color: red;
                }
                QToolTip {
                    background-color: #ffaaaa;
                    color: black;
                    border-color: red;
                }
            ''')
            error = '!!!\nERROR: Comment must not be empty.'
            self.setToolTip(error)
            return self.dialog_widget.refresh_buttons()
        
        self.setProperty('error', False)
        self.setStyleSheet('')
        self.setToolTip('')
        self.dialog_widget.refresh_buttons()


class EditFileComment(QtWidgets.QDialog):

    def __init__(self, tree, item):
        super(EditFileComment, self).__init__(tree)
        self.tree = tree
        self.custom_widget = tree.parent()
        self.item = item

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFixedSize(500, 0)

        self.lo = QtWidgets.QVBoxLayout(self)
        self.lo.setContentsMargins(20,20,20,20)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Window))
        self.setPalette(palette)

        self.content_lo = QtWidgets.QGridLayout()

        self.content_lo.addWidget(LabelIcon(('icons.flow', 'input')), 0, 0, QtCore.Qt.AlignVCenter)
        self.content_lo.addWidget(QtWidgets.QLabel('Comment'), 0, 1, QtCore.Qt.AlignVCenter)
        self.comment = LineEdit(self.item.toolTip(1), self)
        self.content_lo.addWidget(self.comment, 0, 2, QtCore.Qt.AlignVCenter)

        self.content_lo.setAlignment(QtCore.Qt.AlignTop)

        # Buttons
        self.button_lo = QtWidgets.QHBoxLayout()
        self.button_lo.addStretch()

        self.button_action = QtWidgets.QPushButton('Add')
        if self.comment.text() != '':
            self.button_action.setText('Edit')
        else:
            self.button_action.setEnabled(False)
        self.button_cancel = QtWidgets.QPushButton('Cancel')

        self.button_action.clicked.connect(self._on_action_button_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_button_clicked)

        self.button_cancel.setAutoDefault(False)
        
        self.button_lo.addWidget(self.button_action)
        self.button_lo.addWidget(self.button_cancel)

        self.lo.addLayout(self.content_lo)
        self.lo.addLayout(self.button_lo)
        
        self.setLayout(self.lo)

    def sizeHint(self):
        return QtCore.QSize(500, 0)

    def refresh_buttons(self):
        for i in reversed(range(self.content_lo.count())):
            widget = self.content_lo.itemAt(i).widget()
            if widget:
                if widget.property('error') == True:
                    return self.button_action.setEnabled(False)
        
        return self.button_action.setEnabled(True)
    
    def _on_action_button_clicked(self):
        self.custom_widget.session.cmds.Flow.set_value(self.item.shot_file + '/file_comment', self.comment.text())
        self.tree.refresh()
        self.close()

    def _on_cancel_button_clicked(self):
        self.close()


class FileItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, item, shot_file):
        super(FileItem, self).__init__(item)
        self.tree = tree
        self.custom_widget = tree.parent()
        self.shot_file = shot_file

        self.refresh()

    def buttons(self):
        widget = QtWidgets.QWidget()
        lo = QtWidgets.QHBoxLayout(widget)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        button_edit_comment = QtWidgets.QPushButton(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'comment-lines'))), ''
        )
        button_edit_comment.setStyleSheet('qproperty-iconSize: 13px; padding: 2px;')
        button_edit_comment.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        button_edit_comment.clicked.connect(lambda checked=False, x=self: self._on_comment_button_clicked(x))
            
        lo.addStretch()
        lo.addWidget(button_edit_comment)

        return widget

    def refresh(self):
        self.setText(0, self.custom_widget.session.cmds.Flow.get_value(self.shot_file + '/file_name'))
        self.setIcon(0, self.get_file_icon(self.custom_widget.session.cmds.Flow.get_value(self.shot_file + '/file_format')))

        comment = self.custom_widget.session.cmds.Flow.get_value(self.shot_file + '/file_comment')
        self.setIcon(1, QtGui.QIcon())
        self.setToolTip(1, '')
        if comment != '':
            self.setIcon(1, self.get_icon(('icons.gui', 'speech-bubbles-comment-option')))
            self.setToolTip(1, comment)
        
        self.setText(2, self.custom_widget.session.cmds.Flow.get_value(self.shot_file + '/file_target'))
        self.setText(3, self.custom_widget.session.cmds.Flow.get_value(self.shot_file + '/rev_version'))

        self.tree.setItemWidget(self, 4, self.buttons())

    @staticmethod
    def get_file_icon(extension=None):
        if extension == '':
            return QtGui.QIcon(resources.get_icon(('icons.gui', 'folder-white-shape')))
        else:
            return QtGui.QIcon(resources.get_icon(CHOICES_ICONS.get(extension, ('icons.gui', 'text-file-1'))))

    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))

    def _on_comment_button_clicked(self, item):
        dialog = EditFileComment(self.tree, self)
        dialog.exec()


class ShotListItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, shot):
        super(ShotListItem, self).__init__(tree)
        self.tree = tree
        self.custom_widget = tree.parent()
        self.shot = shot
        self.status = self.custom_widget.session.cmds.Flow.get_value(self.shot + '/shot_status')

        self.refresh()
    
    def refresh(self):
        files = self.custom_widget.get_shot_files(self.shot)
        shot_name = self.custom_widget.session.cmds.Flow.get_value(self.shot + '/shot_name')
        if files == []:
            self.custom_widget.remove_shot(shot_name)
            return self.tree.takeTopLevelItem(self.tree.indexFromItem(self).row())

        for shot_file in files:
            FileItem(self.tree, self, shot_file)

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(0, QtCore.Qt.Checked)
        self.setExpanded(True)
        
        self.setText(0, shot_name)
        if self.new_shot() == True:
            self.setIcon(1, self.get_icon(('icons.gui', 'plus-black-symbol')))
            self.setToolTip(1, 'Shot will be created in libreflow')
        
        self.paint()

    def new_shot(self):
        return self.custom_widget.session.cmds.Flow.get_value(self.shot + '/new_shot')

    def paint(self):
        for i in range(self.treeWidget().header().count()):
            brush = QtGui.QBrush(QtGui.QColor(70, 70, 70))
            self.setBackground(i, brush)
    
    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))


class ShotList(QtWidgets.QTreeWidget):

    def __init__(self, custom_widget):
        super(ShotList, self).__init__(custom_widget)
        self._custom_widget = custom_widget
        self.overwrite = []

        self.setStyleSheet("QTreeWidget::item { height: 25px }")

        self.setAcceptDrops(True)
        self.setHeaderLabels(self.get_columns())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        self.refresh(True)

        self.header().setStretchLastSection(True)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 170)
        self.setColumnWidth(2, 240)
        self.setColumnWidth(3, 60)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def get_columns(self):
        return ('Source file', '', 'Target', 'Version', '')
    
    def sizeHint(self):
        return QtCore.QSize(800, 500)
    
    def refresh(self, init=None):
        self.blockSignals(True)
        self.clear()

        shots = self._custom_widget.get_shots()

        for shot in shots:
            ShotListItem(self, shot)

        if init is None:
            if self.topLevelItemCount() == 0:
                self._custom_widget.checkbox_selectall.setCheckState(QtCore.Qt.Unchecked)
                self._custom_widget.checkbox_selectall.setEnabled(False)
                self._custom_widget.button_import.setEnabled(False)
                self._custom_widget.dragdrop.show()
                self._custom_widget.shot_list.hide()
            else:
                self._custom_widget.checkbox_selectall.setEnabled(True)
                self._custom_widget.button_import.setEnabled(True)
            self._custom_widget.refresh_shots_count()
        self.blockSignals(False)

    def get_shots_count(self):
        count = self.topLevelItemCount()
        if count > 1:
            return str(count) + " shots"
        if count == 1:
            return str(count) + " shot"
        return str(0) + " shots"

    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))

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
            self._custom_widget.add_files(links)
        else:
            event.ignore()

    def _on_remove_comment_action_clicked(self, item):
        self._custom_widget.session.cmds.Flow.set_value(item.shot_file + '/file_comment', '')
        item.refresh()

    def _on_remove_file_action_clicked(self, item):
        name = self._custom_widget.session.cmds.Flow.call(
            item.shot_file, 'name', {}, {}
        )
        self._custom_widget.session.cmds.Flow.call(
            item.parent().shot + '/files_map', 'remove', [name], {}
        )
        if name == 'pack':
            for shot in self.overwrite:
                if item.parent().text(0) == shot:
                    self.overwrite.remove(shot)
        self.refresh()

    def _on_remove_all_files_action_clicked(self, item):
        self._custom_widget.session.cmds.Flow.call(
            item.shot + '/files_map', 'clear', {}, {}
        )
        for shot in self.overwrite:
            if item.text(0) == shot:
                self.overwrite.remove(shot)
        self.refresh()

    def _on_context_menu(self, event):
        item = self.itemAt(event)
        column = self.currentColumn()

        if item is None:
            return

        context_menu = QtWidgets.QMenu(self)

        if item.childCount() != 0:
            remove_all_files = context_menu.addAction(self.get_icon(('icons.gui', 'remove-symbol')), 'Remove Shot')
        
            remove_all_files.triggered.connect(
                lambda checked=False, x=item: self._on_remove_all_files_action_clicked(x)
            )
        else:
            if item.toolTip(1) != '':
                remove_comment = context_menu.addAction(self.get_icon(('icons.gui', 'speech-bubbles-comment-option')), 'Remove Comment')
                remove_comment.triggered.connect(
                    lambda checked=False, x=item: self._on_remove_comment_action_clicked(x)
                )

            if item.parent().status == 'init':
                optional_init = self._custom_widget.session.cmds.Flow.get_value(item.shot_file + '/optional_init')
                if optional_init == True:
                    remove_file = context_menu.addAction(self.get_icon(('icons.gui', 'remove-symbol')), 'Remove File')
                    remove_file.triggered.connect(
                        lambda checked=False, x=item: self._on_remove_file_action_clicked(x)
                    )
            if item.parent().status == 'rtk':
                optional_new_rev = self._custom_widget.session.cmds.Flow.get_value(item.shot_file + '/optional_new_rev')
                if optional_new_rev == True:
                    remove_file = context_menu.addAction(self.get_icon(('icons.gui', 'remove-symbol')), 'Remove File')
                    remove_file.triggered.connect(
                        lambda checked=False, x=item: self._on_remove_file_action_clicked(x)
                    )

        if context_menu.isEmpty() != True:
            context_menu.exec_(self.mapToGlobal(event))