from collections import OrderedDict

from AnyQt.QtWidgets import QComboBox, QFormLayout

from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.widgets import widget, gui
from Orange.widgets.widget import Output

from orangecontrib.timeseries import Timeseries
from Orange.data.pandas_compat import table_from_frame
import akshare as ak


class OWMacroUSA(widget.OWWidget):
    name = '美国宏观数据'
    description = "从 Akshare下载美国经济统计数据"
    icon = 'icons/美国宏观.svg'
    priority = 9

    class Outputs:
        time_series = Output("Time series", Timeseries)


    Macro_DICT = OrderedDict((
        ('美国GDP',     ak.macro_usa_gdp_monthly),
        ('美国CPI',   ak.macro_usa_cpi_monthly),
        ('美国核心CPI',      ak.macro_china_fdi),
        ('美国个人支出',      ak.macro_usa_personal_spending),
        ('美国零售销售',      ak.macro_usa_retail_sales),
        ('美国进口物价指数',      ak.macro_usa_import_price),
        ('美国出口价格指数',      ak.macro_usa_export_price),
        ('LMCI',      ak.macro_usa_lmci),
        ('美国失业率',      ak.macro_usa_unemployment_rate),
        ('美国挑战者企业裁员人数',      ak.macro_usa_job_cuts),
        ('美国非农就业人数',      ak.macro_usa_non_farm),
        ('美国ADP就业人数',      ak.macro_usa_adp_employment),
        ('美国核心PCE物价指数',      ak.macro_usa_core_pce_price),
        ('美国实际个人消费支出',      ak.macro_usa_real_consumer_spending),
        ('美国贸易帐',      ak.macro_usa_trade_balance),
        ('美国经常帐',      ak.macro_usa_current_account),
        ('贝克休斯钻井报告',      ak.macro_usa_rig_count),
        ('美国PPI',      ak.macro_usa_ppi),
        ('美国核心PPI',      ak.macro_usa_core_ppi),
        ('美国API原油库存',      ak.macro_usa_api_crude_stock),
        ('美国Markit制造业PMI初值',      ak.macro_usa_pmi),
        ('美国ISM制造业PMI',      ak.macro_usa_ism_pmi),
        ('美国工业产出',      ak.macro_usa_industrial_production),
        ('美国耐用品订单',      ak.macro_usa_durable_goods_orders),
        ('美国工厂订单',      ak.macro_usa_factory_orders),
        ('美国Markit服务业PMI',      ak.macro_usa_services_pmi),
        ('美国商业库存',      ak.macro_usa_business_inventories),
        ('美国ISM非制造业PMI',      ak.macro_usa_ism_non_pmi),
        ('美国NAHB房产市场指数',      ak.macro_usa_nahb_house_market_index),
        ('美国新屋开工总数',      ak.macro_usa_house_starts),
        ('美国新屋销售总数',      ak.macro_usa_new_home_sales),
        ('美国营建许可总数',      ak.macro_usa_building_permits),
        ('美国成屋销售总数',      ak.macro_usa_exist_home_sales),
        ('美国FHFA房价指数',      ak.macro_usa_house_price_index),
        ('美国S&P/CS20座大城市房价指数',      ak.macro_usa_spcs20),
        ('美国成屋签约销售指数',      ak.macro_usa_pending_home_sales),
        ('未决房屋销售',      ak.macro_usa_phs),
        ('美国谘商会消费者信心指数',      ak.macro_usa_cb_consumer_confidence),
        ('美国NFIB小型企业信心指数',      ak.macro_usa_nfib_small_business),
        ('美国密歇根大学消费者信心指数',      ak.macro_usa_michigan_consumer_sentiment),
        ('美国EIA原油库存',      ak.macro_usa_eia_crude_rate),
        ('美国初请失业金人数',      ak.macro_usa_initial_jobless),
        ('美国原油产量',      ak.macro_usa_crude_inner),
    ))


    want_main_area = False
    resizing_enabled = False

    class Error(widget.OWWidget.Error):
        download_error = widget.Msg('数据下载错误.\n'
                                    '断网了？代码错误？')

    def __init__(self):
        layout = QFormLayout()
        gui.widgetBox(self.controlArea, True, orientation=layout)

        self.MacroIdx = MacroIdx =QComboBox()
        MacroIdx.addItems(self.Macro_DICT.keys())
        MacroIdx.setCurrentIndex(0)
        layout.addRow("宏观经济指标:", self.MacroIdx)


        self.button = gui.button(
            self.controlArea, self, '下载数据', callback=self.download)

    def download(self):
        # 
        MacroIdx = self.MacroIdx.currentText()
        self.Error.clear()

        with self.progressBar(3) as progress:
            try:
                progress.advance()
                self.button.setDisabled(True)
                df = self.Macro_DICT[MacroIdx]()
                data = Timeseries.from_data_table(table_from_frame(df))
                data.name = MacroIdx
                self.Outputs.time_series.send(data)
            except Exception as e:
                self.Error.download_error()
            finally:
                self.button.setDisabled(False)


if __name__ == "__main__":
    WidgetPreview(OWMacroUSA).run()