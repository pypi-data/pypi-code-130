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


class OWMarkitIndex(widget.OWWidget):
    name = '股票市场指数'
    description = "从Akshare--下载A股市场指数。"
    icon = 'icons/市场指数.svg'
    priority = 9

    class Outputs:
        time_series = Output("Time series", Timeseries)


    symbols = settings.Setting(['sh000919', 'sz399552'])

    Mkt_DICT = OrderedDict((
        ('实时行情指数',  lambda stk:ak.stock_zh_index_spot()),
        ('历史指数-新浪', lambda stk:ak.stock_zh_index_daily(symbol=stk)),
        ('历史指数-腾讯', lambda stk:ak.stock_zh_index_daily_tx(symbol=stk)),
    ))

    want_main_area = False
    resizing_enabled = False

    class Error(widget.OWWidget.Error):
        download_error = widget.Msg('数据下载错误.\n'
                                    '断网了？股票代码错误？')

    def __init__(self):
        layout = QFormLayout()
        gui.widgetBox(self.controlArea, True, orientation=layout)

        self.Idx = Idx =QComboBox()
        Idx.addItems(self.Mkt_DICT.keys())
        Idx.setCurrentIndex(0)
        layout.addRow("  类型:  ", self.Idx)

        self.combo = combo = QComboBox(
            editable=True, insertPolicy=QComboBox.InsertAtTop)
        combo.addItems(self.symbols)
        layout.addRow("指数代码:", self.combo)

        
        self.button = gui.button(
            self.controlArea, self, '下载数据', callback=self.download)

    def download(self):
        #  股票代码数据处理
        symbol = self.combo.currentText().strip().lower()
        self.combo.removeItem(self.combo.currentIndex())
        self.combo.insertItem(0, symbol)
        self.combo.setCurrentIndex(0)

        # 时间频率和复权数据
        mkt_fun = self.Mkt_DICT[self.Idx.currentText()]
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
                df = mkt_fun(symbol)
                data = Timeseries.from_data_table(table_from_frame(df))
                data.name = symbol
                self.Outputs.time_series.send(data)
            except Exception as e:
                self.Error.download_error()
            finally:
                self.button.setDisabled(False)


if __name__ == "__main__":
    WidgetPreview(OWMarkitIndex).run()