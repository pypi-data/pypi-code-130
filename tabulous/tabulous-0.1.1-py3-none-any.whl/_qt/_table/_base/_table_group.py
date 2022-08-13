from __future__ import annotations
from typing import TYPE_CHECKING
from qtpy import QtWidgets as QtW, QtGui
from qtpy.QtCore import Qt, Signal

if TYPE_CHECKING:
    from ._table_base import QBaseTable, _QTableViewEnhanced

# Wrapper widgets that can be used to wrap a QTableView


class QTableGroup(QtW.QSplitter):
    """Split view of two tables."""

    focusChanged = Signal(int)

    def __init__(self, tables: list[QBaseTable], orientation=Qt.Orientation.Horizontal):
        super().__init__(orientation)
        self.setChildrenCollapsible(False)

        self._tables: list[QBaseTable] = []
        for i, table in enumerate(tables):
            view_copy = table._qtable_view.copy(link=True)
            view_copy.focusedSignal.connect(
                lambda: self.focusChanged.emit(self.focusedIndex())
            )
            self.addWidget(view_copy)
            self.setStretchFactor(i, 1)
            self._tables.append(table)

    def copy(self) -> QTableGroup:
        """Make a copy of this widget."""
        copy = self.__class__(self.tables, self.orientation())
        return copy

    @property
    def tables(self) -> list[QBaseTable]:
        """List of tables."""
        return self._tables.copy()

    def pop(self, index: int = -1) -> QBaseTable:
        """Pop a table from the group."""
        if index < 0:
            index += self.count()
        out = self._tables.pop(index)
        table = self.widget(index)  # this is a copy
        table.setParent(None)
        table.deleteLater()
        return out

    def tableIndex(self, table: QBaseTable) -> int:
        """Return the index of a table in the group."""
        model = table.model()
        for t in self.tables:
            if t.model() is model:
                return t
        raise ValueError("Table not found.")

    def focusedIndex(self) -> int:
        """Return the index of the currently focused table."""
        for i in range(self.count()):
            if self.tableHasFocus(i):
                return i
        return -1

    def setFocusedIndex(self, index: int) -> None:
        """Set the focused widget to the table at index."""
        for i in range(self.count()):
            if i != index:
                self.widget(i).setBackgroundRole(QtGui.QPalette.ColorRole.Dark)
            else:
                self.widget(i).setBackgroundRole(QtGui.QPalette.ColorRole.Light)
        return self.widget(index).setFocus()

    def focusedTable(self) -> QBaseTable | None:
        """Return the currently focused table widget."""
        i = self.focusedIndex()
        if i < 0:
            return None
        return self.tables[i]

    def tableHasFocus(self, index: int) -> bool:
        """True if the table at index has focus."""
        return self.widget(index).hasFocus()

    def __eq__(self, other: QTableGroup) -> bool:
        if not isinstance(other, QTableGroup):
            return False
        # NOTE: This should be safe. Table groups derived from the same ancestor
        # will always have exclusively the same set of tables.
        return self._tables[0].model() is other._tables[0].model()

    if TYPE_CHECKING:

        def widget(self, index: int) -> _QTableViewEnhanced:
            ...
