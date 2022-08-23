import weakref
from contextlib import contextmanager

from qtpy import QtCore, QtGui, QtWidgets

from ._qt import load_ui
from .const import CHANNEL_REGEXP, CHANNEL_RE


AxisCtrlTemplate, __ = load_ui('axisCtrlTemplate.ui')

class AxisCtrlMenuItem(QtWidgets.QMenu, AxisCtrlTemplate):
    def __init__(self, title, mainmenu):
        super().__init__(title, mainmenu)
        self.setupUi(self)
        self.minText.setValidator(QtGui.QDoubleValidator())
        self.maxText.setValidator(QtGui.QDoubleValidator())

    @property
    def _controls(self):
        return [
            self.manualRadio,
            self.minText,
            self.maxText,
            self.autoRadio,
            self.autoPercentSpin,
            self.logModeCheck,
        ]

    def blockSignals(self, block):
        for c in self._controls:
            c.blockSignals(block)

    @contextmanager
    def signal_blocker(self):
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)


class MouseModeMenuItem(QtWidgets.QMenu):
    def __init__(self, title, mainmenu):
        super().__init__(title, mainmenu)
        group = QtWidgets.QActionGroup(self)
        self.pan = QtWidgets.QAction("pan/zoom", self)
        self.rect = QtWidgets.QAction("zoom box", self)
        self.addAction(self.pan)
        self.addAction(self.rect)
        self.pan.setCheckable(True)
        self.rect.setCheckable(True)
        self.pan.setActionGroup(group)
        self.rect.setActionGroup(group)


class CursorWidget(QtWidgets.QWidget):
    def __init__(self, check1, check2):
        super().__init__()
        self._c1 = QtWidgets.QCheckBox(check1)
        self._c1.setToolTip(f"enable {check1} cursor")
        self._c2 = QtWidgets.QCheckBox(check2)
        self._c2.setToolTip(f"enable {check2} cursor")
        setattr(self, check1, self._c1)
        setattr(self, check2, self._c2)
        self.reset = QtWidgets.QPushButton("reset")
        self.reset.setToolTip("reset cursor positions")
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self._c1)
        self.layout.addWidget(self._c2)
        self.layout.addWidget(self.reset)
        self.setLayout(self.layout)


# this is lifted from the pqtgraph.ViewBoxMenu module
class NDScopePlotMenu(QtWidgets.QMenu):
    def __init__(self, plot):
        QtWidgets.QMenu.__init__(self)
        # keep weakref to view to avoid circular reference (don't know
        # why, but this prevents the ViewBox from being collected)
        self.plot = weakref.ref(plot)
        self.view = weakref.ref(plot.getViewBox())
        self.viewMap = weakref.WeakValueDictionary()

        loc = self.plot().loc
        title = f"plot {loc}"
        self.setTitle(title)
        self.addLabel(title)
        self.addSeparator()

        self.viewAll = QtWidgets.QAction("view all data", self)
        self.viewAll.triggered.connect(self.autoRange)
        self.addAction(self.viewAll)

        self.resetT0 = QtWidgets.QAction("reset t0 to point", self)
        self.resetT0.triggered.connect(self.reset_t0)
        self.addAction(self.resetT0)

        self.yAxisUI = AxisCtrlMenuItem("Y axis scale", self)
        self.yAxisUI.manualRadio.clicked.connect(self.yManualClicked)
        self.yAxisUI.minText.editingFinished.connect(self.yRangeTextChanged)
        self.yAxisUI.maxText.editingFinished.connect(self.yRangeTextChanged)
        self.yAxisUI.autoRadio.clicked.connect(self.yAutoClicked)
        self.yAxisUI.autoPercentSpin.valueChanged.connect(self.yAutoSpinChanged)
        self.yAxisUI.logModeCheck.stateChanged.connect(self.yLogModeToggled)
        self.addMenu(self.yAxisUI)

        self.mouseModeUI = MouseModeMenuItem("mouse mode", self)
        self.mouseModeUI.pan.triggered.connect(self.setMouseModePan)
        self.mouseModeUI.rect.triggered.connect(self.setMouseModeRect)
        self.addMenu(self.mouseModeUI)

        self.addLabel()

        self.addSection("T cursors")
        self.t_cursor_widget = CursorWidget('T1', 'T2')
        self.t_cursor_action = QtWidgets.QWidgetAction(self)
        self.t_cursor_action.setDefaultWidget(self.t_cursor_widget)
        self.t_cursor_widget.T1.stateChanged.connect(self.update_t1_cursor)
        self.t_cursor_widget.T2.stateChanged.connect(self.update_t2_cursor)
        self.t_cursor_widget.reset.clicked.connect(self.reset_t_cursors)
        self.addAction(self.t_cursor_action)

        self.addSection("Y cursors")
        self.y_cursor_widget = CursorWidget('Y1', 'Y2')
        self.y_cursor_action = QtWidgets.QWidgetAction(self)
        self.y_cursor_action.setDefaultWidget(self.y_cursor_widget)
        self.y_cursor_widget.Y1.stateChanged.connect(self.update_y1_cursor)
        self.y_cursor_widget.Y2.stateChanged.connect(self.update_y2_cursor)
        self.y_cursor_widget.reset.clicked.connect(self.reset_y_cursors)
        self.addAction(self.y_cursor_action)

        self.addLabel()
        self.addSection("add/modify/remove channels")
        self.addLabel()

        self.openChannelSelectDialogButton = self.addButton("set channel list/parameters")
        self.openChannelSelectDialogButton.clicked.connect(self.channel_select_dialog)

        self.addChannelEntry = QtWidgets.QLineEdit()
        self.addChannelEntry.setMinimumSize(300, 24)
        self.addChannelEntry.setPlaceholderText("enter channel to add")
        self.addChannelEntry.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(CHANNEL_REGEXP)))
        self.addChannelEntry.textChanged.connect(self.validate_add)
        self.addChannelEntry.returnPressed.connect(self.add_channel)
        self.addChannelEntry.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        acea = QtWidgets.QWidgetAction(self)
        acea.setDefaultWidget(self.addChannelEntry)
        self.addAction(acea)

        self.addChannelButton = self.addButton("add channel to plot")
        self.addChannelButton.setEnabled(False)
        self.addChannelButton.clicked.connect(self.add_channel)

        self.addLabel()

        self.removeChannelList = QtWidgets.QComboBox()
        self.removeChannelList.setMinimumSize(200, 26)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        # self.removeChannelList.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        rcl = QtWidgets.QWidgetAction(self)
        rcl.setDefaultWidget(self.removeChannelList)
        self.addAction(rcl)

        self.addLabel()
        self.addSection("add/remove plots")
        self.addLabel()

        self.newPlotRowButton = self.addButton("add plot to row")
        self.newPlotRowButton.clicked.connect(self.new_plot_row)

        self.newPlotColButton = self.addButton("add plot to column")
        self.newPlotColButton.clicked.connect(self.new_plot_col)

        self.addLabel()

        self.removePlotButton = self.addButton("remove plot")
        self.removePlotButton.clicked.connect(self.remove_plot)

        self.setContentsMargins(10, 10, 10, 10)

        self.view().sigStateChanged.connect(self.viewStateChanged)

    ##########

    def addLabel(self, label=''):
        ql = QtWidgets.QLabel()
        ql.setText(label)
        ql.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        qla = QtWidgets.QWidgetAction(self)
        qla.setDefaultWidget(ql)
        self.addAction(qla)

    def addButton(self, label):
        button = QtWidgets.QPushButton(label)
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(button)
        self.addAction(action)
        return button

    ##########

    def viewStateChanged(self):
        if self.yAxisUI.minText.isVisible():
            self.updateState()

    def updateState(self):
        # something about the viewbox has changed. update the axis
        # menu GUI

        state = self.view().getState(copy=False)

        # update the yAxisUI
        # block signals in the widget while we update the values
        with self.yAxisUI.signal_blocker():
            # index 1 in state is y axis
            i = 1
            tr = tuple(map(self.plot().y_pos_to_val, state['targetRange'][i]))
            self.yAxisUI.minText.setText("%0.5g" % tr[0])
            self.yAxisUI.maxText.setText("%0.5g" % tr[1])
            if state['autoRange'][i] is not False:
                self.yAxisUI.autoRadio.setChecked(True)
                if state['autoRange'][i] is not True:
                    self.yAxisUI.autoPercentSpin.setValue(int(state['autoRange'][i]*100))
            else:
                self.yAxisUI.manualRadio.setChecked(True)
            self.yAxisUI.logModeCheck.setChecked(state['logMode'][i])

        if state['mouseMode'] == self.view().PanMode:
            self.mouseModeUI.pan.setChecked(True)
        else:
            self.mouseModeUI.rect.setChecked(True)

        self.t_cursor_widget.T1.setChecked(self.plot().t_cursors.T1.isVisible())
        self.t_cursor_widget.T2.setChecked(self.plot().t_cursors.T2.isVisible())

        self.y_cursor_widget.Y1.setChecked(self.plot().y_cursors.Y1.isVisible())
        self.y_cursor_widget.Y2.setChecked(self.plot().y_cursors.Y2.isVisible())

    def popup(self, pos):
        self.updateState()

        plot = self.plot()

        ppos = plot.vb.mapSceneToView(pos)
        self.pos = (ppos.x(), ppos.y())

        # update remove channels list
        self.update_channel_list()

        # see if there's a channel in the clipboard
        clipboard = QtWidgets.QApplication.clipboard().text(
            mode=QtGui.QClipboard.Selection)
        clipboard = clipboard.strip()
        if CHANNEL_RE.match(clipboard):
            # if we have a channel add it to the label
            self.addChannelEntry.setText(clipboard)
        else:
            self.addChannelEntry.setText('')

        self.removeChannelList.setEnabled(len(plot.channels) > 0)

        QtWidgets.QMenu.popup(self, pos)

    ##########

    def autoRange(self):
        # don't let signal call this directly--it'll add an unwanted argument
        self.view().autoRange()

    def reset_t0(self):
        self.plot()._reset_t0(self.pos[0])

    ##########

    def update_channel_list(self):
        channels = list(self.plot().channels.keys())
        self.removeChannelList.currentIndexChanged.disconnect(self.remove_channel)
        self.removeChannelList.clear()
        ls = ['remove channel'] + channels
        self.removeChannelList.addItems(ls)
        self.removeChannelList.insertSeparator(1)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)

    def validate_add(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            if channel in self.plot().channels:
                self.addChannelEntry.setStyleSheet("background: #87b5ff;")
                self.addChannelButton.setEnabled(False)
            else:
                self.addChannelEntry.setStyleSheet("font-weight: bold; background: #90ff8c;")
                self.addChannelButton.setEnabled(True)
        else:
            self.addChannelEntry.setStyleSheet('')
            self.addChannelButton.setEnabled(False)

    def channel_select_dialog(self):
        self.plot()._select_channel_menu()
        self.close()

    def add_channel(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            self.plot()._add_channel_menu(channel)
        self.close()

    def remove_channel(self, *args):
        self.removeChannelList.currentIndexChanged.disconnect(self.remove_channel)
        channel = str(self.removeChannelList.currentText())
        self.plot().remove_channel(channel)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        self.close()

    def new_plot_row(self):
        self.new_plot('row')

    def new_plot_col(self):
        self.new_plot('col')

    def new_plot(self, rowcol):
        channel = str(self.addChannelEntry.text())
        kwargs = {}
        if CHANNEL_RE.match(channel):
            kwargs['channels'] = [{channel: None}]
        self.plot().new_plot_request.emit(
            (self.plot(), rowcol, kwargs),
        )
        self.close()

    def remove_plot(self):
        self.plot().remove_plot_request.emit(self.plot())
        self.close()

    ##########

    def setMouseModePan(self):
        self.view().setLeftButtonAction('pan')

    def setMouseModeRect(self):
        self.view().setLeftButtonAction('rect')

    def yMouseToggled(self, b):
        self.view().setMouseEnabled(y=b)

    def yManualClicked(self):
        self.view().enableAutoRange(self.view().YAxis, False)

    def yRangeTextChanged(self):
        self.yAxisUI.manualRadio.setChecked(True)
        range_1 = float(self.yAxisUI.minText.text())
        range_2 = float(self.yAxisUI.maxText.text())
        self.plot().set_y_range((range_1, range_2))

    def yAutoClicked(self):
        val = self.yAxisUI.autoPercentSpin.value() * 0.01
        self.view().enableAutoRange(self.view().YAxis, val)

    def yAutoSpinChanged(self, val):
        self.yAxisUI.autoRadio.setChecked(True)
        self.view().enableAutoRange(self.view().YAxis, val*0.01)

    def yAutoPanToggled(self, b):
        self.view().setAutoPan(y=b)

    def yVisibleOnlyToggled(self, b):
        self.view().setAutoVisible(y=b)

    def yInvertToggled(self, b):
        self.view().invertY(b)

    def yLogModeToggled(self, state):
        self.plot().set_log_mode(state == QtCore.Qt.Checked)

    def update_t1_cursor(self):
        self.plot().enable_t_cursors().set_visible(
            t1=self.t_cursor_widget.T1.isChecked(),
        )

    def update_t2_cursor(self):
        self.plot().enable_t_cursors().set_visible(
            t2=self.t_cursor_widget.T2.isChecked(),
        )

    def reset_t_cursors(self):
        self.plot().t_cursors.reset()

    def update_y1_cursor(self):
        self.plot().enable_y_cursors().set_visible(
            y1=self.y_cursor_widget.Y1.isChecked(),
        )

    def update_y2_cursor(self):
        self.plot().enable_y_cursors().set_visible(
            y2=self.y_cursor_widget.Y2.isChecked(),
        )

    def reset_y_cursors(self):
        self.plot().y_cursors.reset()
