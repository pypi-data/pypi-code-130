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
    name = '财务报表及指标'
    description = "从Akshare--下载A股财务报表和财务指标数据。"
    icon = 'icons/财务数据.svg'
    priority = 9

    class Outputs:
        time_series = Output("Time series", Timeseries)


    symbols = settings.Setting(['600857', '000088'])

    Fin_DICT = OrderedDict((
        ('资产负债表-新浪', lambda stk:ak.stock_financial_report_sina(stock=stk, symbol="资产负债表")),
        ('利润表-新浪', lambda stk:ak.stock_financial_report_sina(stock=stk, symbol="利润表")),
        ('现金流量表-新浪', lambda stk:ak.stock_financial_report_sina(stock=stk, symbol="现金流量表")),
        ('资产负债表-东财', lambda stk:ak.stock_balance_sheet_by_report_em(symbol=('SH'+stk if  stk.startswith('6') else 'SZ'+stk))),
        ('利润表-东财', lambda stk:ak.stock_profit_sheet_by_report_em(symbol=('SH'+stk if  stk.startswith('6') else 'SZ'+stk))),
        ('利润表-年-东财', lambda stk:ak.stock_profit_sheet_by_yearly_em(symbol=('SH'+stk if  stk.startswith('6') else 'SZ'+stk))),
        ('现金流量表-东财', lambda stk:ak.stock_cash_flow_sheet_by_report_em(symbol=('SH'+stk if  stk.startswith('6') else 'SZ'+stk))),
        ('财务摘要-新浪', lambda stk:ak.stock_financial_abstract(stock=stk)),
        ('财务指标-新浪', lambda stk:ak.stock_financial_analysis_indicator(symbol=stk)),
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

        self.Idx = Idx =QComboBox()
        Idx.addItems(self.Fin_DICT.keys())
        Idx.setCurrentIndex(0)
        layout.addRow("类型:", self.Idx)

        self.button = gui.button(
            self.controlArea, self, '下载数据', callback=self.download)

    def download(self):
        #  股票代码数据处理
        symbol = self.combo.currentText().strip().upper()
        self.combo.removeItem(self.combo.currentIndex())
        self.combo.insertItem(0, symbol)
        self.combo.setCurrentIndex(0)

        # 时间频率和复权数据
        idx_fun = self.Fin_DICT[self.Idx.currentText()]
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
                df = idx_fun(symbol)
                data = Timeseries.from_data_table(table_from_frame(df))
                data.name = symbol
                self.Outputs.time_series.send(data)
            except Exception as e:
                self.Error.download_error()
            finally:
                self.button.setDisabled(False)


if __name__ == "__main__":
    WidgetPreview(OWakshare).run()