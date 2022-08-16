from collections import OrderedDict

from AnyQt.QtWidgets import QComboBox, QFormLayout

from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.widgets import widget, gui
from Orange.widgets.widget import Output

from orangecontrib.timeseries import Timeseries
from Orange.data.pandas_compat import table_from_frame
import akshare as ak


class OWMacroCN(widget.OWWidget):
    name = '中国宏观数据'
    description = "从 Akshare--东方财富 下载经济统计数据"
    icon = 'icons/中国宏观.svg'
    priority = 9

    class Outputs:
        time_series = Output("Time series", Timeseries)


    Macro_DICT = OrderedDict((
        ('中国宏观杠杆率',     ak.macro_cnbs),
        ('企业商品价格指数',   ak.macro_china_qyspjg),
        ('外商直接投资',      ak.macro_china_fdi),
        ('社会融资规模增量',      ak.macro_china_shrzgm),
        ('LPR',      ak.macro_china_lpr),
        ('GDP—年',      ak.macro_china_gdp_yearly),
        ('CPI—月',      ak.macro_china_cpi_monthly),
        ('PPI—年',      ak.macro_china_ppi_yearly),
        ('出口—美元—年',      ak.macro_china_exports_yoy),
        ('进口—美元—年',      ak.macro_china_imports_yoy),
        ('贸易帐—美元—年',      ak.macro_china_trade_balance),
        ('工业增加值',      ak.macro_china_gyzjz),
        ('规模以上工业增加值',      ak.macro_china_industrial_production_yoy),
        ('官方制造业PMI',      ak.macro_china_pmi_yearly),
        ('财新制造业PMI终值',      ak.macro_china_cx_pmi_yearly),
        ('财新服务业PMI',      ak.macro_china_cx_services_pmi_yearly),
        ('官方非制造业PMI',      ak.macro_china_non_man_pmi),
        ('外汇储备-亿美元',      ak.macro_china_fx_reserves_yearly),
        ('M2',      ak.macro_china_m2_yearly),
        ('新房价指数',      ak.macro_china_new_house_price),
        ('企业景气及企业家信心指数',      ak.macro_china_enterprise_boom_index),
        ('全国税收收入',      ak.macro_china_national_tax_receipts),
        ('银行理财产品发行数量',      ak.macro_china_bank_financing),
        ('原保险保费收入',      ak.macro_china_insurance_income),
        ('手机出货量',      ak.macro_china_mobile_number),
        ('菜篮子产品批发价格指数',      ak.macro_china_vegetable_basket),
        ('农产品批发价格总指数',      ak.macro_china_agricultural_product),
        ('农副指数',      ak.macro_china_agricultural_index),
        ('能源指数',      ak.macro_china_energy_index),
        ('大宗商品价格',      ak.macro_china_commodity_price_index),
        ('费城半导体指数',      ak.macro_global_sox_index),
        ('义乌小商品指数-电子元器件',      ak.macro_china_yw_electronic_index),
        ('建材指数',      ak.macro_china_construction_index),
        ('建材价格指数',      ak.macro_china_construction_price_index),
        ('物流景气指数',      ak.macro_china_lpi_index),
        ('原油运输指数',      ak.macro_china_bdti_index),
        ('超灵便型船运价指数',      ak.macro_china_bsi_index),
        ('新增信贷',      ak.macro_china_new_financial_credit),
        ('CPI',      ak.macro_china_cpi),
        ('GDP',      ak.macro_china_gdp),
        ('PPI',      ak.macro_china_ppi),
        ('采购经理人指数',      ak.macro_china_pmi),
        ('城镇固定资产投资',      ak.macro_china_gdzctz),
        ('海关进出口增减情况',      ak.macro_china_hgjck),
        ('财政收入',      ak.macro_china_czsr),
        ('外汇贷款',      ak.macro_china_whxd),
        ('本外币存款',      ak.macro_china_wbck),
        ('货币净投放与净回笼',      ak.macro_china_hb),
        ('央行公开市场操作',      ak.macro_china_gksccz),
        ('新债发行',      ak.macro_china_bond_public),
        ('消费者信心指数',      ak.macro_china_xfzxx),
        ('存款准备金率',      ak.macro_china_reserve_requirement_ratio),
        ('社会消费品零售总额',      ak.macro_china_consumer_goods_retail),
        ('全社会用电分类情况表',      ak.macro_china_society_electricity ),
        ('全社会客货运输量',      ak.macro_china_society_traffic_volume ),
        ('邮电业务基本情况',      ak.macro_china_postal_telecommunicational ),
        ('国际旅游外汇收入构成',      ak.macro_china_international_tourism_fx ),
        ('民航客座率及载运率',      ak.macro_china_passenger_load_factor ),
        ('航贸运价指数',      ak.macro_china_freight_index ),
        ('央行货币当局资产负债',      ak.macro_china_central_bank_balance ),
        ('保险业经营情况',      ak.macro_china_insurance ),
        ('货币供应量',      ak.macro_china_supply_of_money ),
        ('FR007利率互换曲线',      ak.macro_china_swap_rate ),
        ('央行黄金和外汇储备',      ak.macro_china_foreign_exchange_gold ),
        ('商品零售价格指数',      ak.macro_china_retail_price_index ),
        ('国房景气指数',      ak.macro_china_real_estate ),
        ('外汇和黄金储备',      ak.macro_china_fx_gold ),
        ('中国货币供应量',      ak.macro_china_money_supply ),
        ('全国股票交易统计表',      ak.macro_china_stock_market_cap ),
        ('SHIBOR',      ak.macro_china_shibor_all ),
        ('人民币香港银行同业拆息',      ak.macro_china_hk_market_info ),
        ('人民币汇率中间价',      ak.macro_china_rmb),
        ('深圳融资融券报告',      ak.macro_china_market_margin_sz),
        ('上海融资融券报告',      ak.macro_china_market_margin_sh),
        ('上海黄金交易所报告',      ak.macro_china_au_report),
        ('全国综合电煤价格指数',      ak.macro_china_ctci),
        ('各价区电煤价格指数',      ak.macro_china_ctci_detail),
        ('历史电煤价格指数',      ak.macro_china_ctci_detail_hist),
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
    WidgetPreview(OWMacroCN).run()