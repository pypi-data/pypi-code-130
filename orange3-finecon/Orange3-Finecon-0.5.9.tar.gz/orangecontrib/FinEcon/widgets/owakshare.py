from datetime import datetime, timedelta, date
from collections import OrderedDict

from AnyQt.QtCore import QDate
from AnyQt.QtWidgets import QDateEdit, QComboBox, QFormLayout

from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Output

from orangecontrib.timeseries import Timeseries
from Orange.data.pandas_compat import table_from_frame
import akshare as ak


class OWakshare(widget.OWWidget):
    name = 'A股交易数据'
    description = "从Akshare--东方财富 下载经济统计和金融交易数据"
    icon = 'icons/A股交易数据.svg'
    priority = 9

    class Outputs:
        time_series = Output("Time series", Timeseries)

    QT_DATE_FORMAT = 'yyyy-MM-dd'
    PY_DATE_FORMAT = '%Y-%m-%d'  
    AK_DATE_FROMAT = '%Y%m%d'   #akshare只接受 20200909 这样的字符串日期。
    MIN_DATE = date(1851, 1, 1)

    date_from = settings.Setting(
        (datetime.now().date() - timedelta(5 * 365)).strftime(PY_DATE_FORMAT))
    date_to = settings.Setting(datetime.now().date().strftime(PY_DATE_FORMAT))
    symbols = settings.Setting(['600857', '000088'])

    Adjust_Dict = {
        '不复权':'', 
        '前复权':'qfq', 
        '后复权':'hfq'
    }

    ADJUST_DICT = OrderedDict((
        ('不复权', ''),
        ('前复权','qfq'),
    ))

    want_main_area = False
    resizing_enabled = False

    class Error(widget.OWWidget.Error):
        download_error = widget.Msg('数据下载错误.\n'
                                    '断网了？股票代码错误？')

    def __init__(self):
        layout = QFormLayout()
        gui.widgetBox(self.controlArea, True, orientation=layout)

        self.combo = combo = QComboBox(
            editable=True, insertPolicy=QComboBox.InsertAtTop)
        combo.addItems(self.symbols)
        layout.addRow("股票代码:", self.combo)

        self.QPeriod = QPeriod =QComboBox()
        QPeriod.addItems(['daily', 'weekly', 'monthly'])
        QPeriod.setCurrentIndex(0)
        layout.addRow("数据频率:", self.QPeriod)

        minDate = QDate.fromString(self.MIN_DATE.strftime(self.PY_DATE_FORMAT),
                                   self.QT_DATE_FORMAT)
        date_from, date_to = (
            QDateEdit(QDate.fromString(date, self.QT_DATE_FORMAT),
                      displayFormat=self.QT_DATE_FORMAT, minimumDate=minDate,
                      calendarPopup=True)
            for date in (self.date_from, self.date_to))

        @date_from.dateChanged.connect
        def set_date_from(date):
            self.date_from = date.toString(self.QT_DATE_FORMAT)

        @date_to.dateChanged.connect
        def set_date_to(date):
            self.date_to = date.toString(self.QT_DATE_FORMAT)

        layout.addRow("起始日期:", date_from)
        layout.addRow("结束日期:", date_to)

        self.Adjust = Adjust = QComboBox()
        Adjust.addItems(tuple(self.Adjust_Dict.keys()))
        Adjust.setCurrentIndex(0)
        layout.addRow("复权方式:", Adjust)

        self.button = gui.button(
            self.controlArea, self, '下载数据', callback=self.download)

    def download(self):
        date_from = datetime.strptime(self.date_from, self.PY_DATE_FORMAT)
        date_from = date_from.strftime(self.AK_DATE_FROMAT)
        date_to = datetime.strptime(self.date_to, self.PY_DATE_FORMAT)
        date_to = date_to.strftime(self.AK_DATE_FROMAT)

        #  股票代码数据处理
        symbol = self.combo.currentText().strip().upper()
        self.combo.removeItem(self.combo.currentIndex())
        self.combo.insertItem(0, symbol)
        self.combo.setCurrentIndex(0)

        # 时间频率和复权数据
        period = self.QPeriod.currentText().strip().lower()
        adjust = self.Adjust_Dict[self.Adjust.currentText()]
        try:
            self.symbols.remove(symbol)
        except ValueError:
            pass
        self.symbols.insert(0, symbol)

        if not symbol:
            return

        self.Error.clear()
        with self.progressBar(3) as progress:
            try:
                progress.advance()
                self.button.setDisabled(True)
                df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=date_from, end_date=date_to, adjust=adjust)
                data = Timeseries.from_data_table(table_from_frame(df))
                data.name = symbol
                self.Outputs.time_series.send(data)
            except Exception as e:
                self.Error.download_error()
            finally:
                self.button.setDisabled(False)


if __name__ == "__main__":
    WidgetPreview(OWakshare).run()