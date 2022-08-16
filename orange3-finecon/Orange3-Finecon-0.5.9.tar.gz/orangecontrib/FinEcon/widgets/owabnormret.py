from cProfile import label
from datetime import datetime, timedelta, date
import sys

from math import sin, cos, pi

import os
import tempfile
import numpy as np
import pandas as pd

from AnyQt.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem,
    QGraphicsEllipseItem, QLabel, QGridLayout)
from AnyQt.QtGui import QColor, QPainter, QPixmap
from AnyQt.QtCore import Qt, QSize
from AnyQt.QtCore import QDate
from AnyQt.QtWidgets import QDateEdit, QComboBox, QFormLayout


import Orange.data
from Orange.statistics import contingency, distribution

from Orange.widgets import widget, gui
from Orange.widgets.settings import DomainContextHandler, ContextSetting, \
    Setting
from Orange.widgets.utils.itemmodels import DomainModel
from Orange.widgets.widget import Input, Output

import eventstudy as es
from Orange.data.io import FileFormat
from Orange.data.pandas_compat import table_from_frame, table_to_frame


# SCALE = 200


class OWAbnormalRet(widget.OWWidget):
    name = "异常收益AR"
    description = "自动下载股票交易数据，计算给定窗口期的超额收益。"
    keywords = ["pie chart", "chart", "visualisation"]
    icon = "icons/misc.svg"
    priority = 700

    class Inputs:
        data = Input("Stk & Mkt Data", Orange.data.Table)
        #ff = Input('FamaFrench', Orange.data.Table)
        #event = Input('EnentRecord', Orange.data.Table)
        
    class Outputs:
        es_result = Output("事件研究结果", Orange.data.Table)
        
        
    class Error(widget.OWWidget.Error):
        download_error = widget.Msg('数据下载错误.\n'
                                    '断网了？股票代码错误？')

    # settingsHandler = DomainContextHandler()
    # graph_name = "scene"
    
    is_price = Setting(True)
    log_return = Setting(True)
    window_start = Setting(-2)
    window_end = Setting(30)
    event_date = Setting('20200910')

    def __init__(self):
        super().__init__()
        self.dataset = None
        self.es_model = es.Single
        self.security_ticker = None
        self.market_ticker = None

        self.varlist = DomainModel(
            valid_types=Orange.data.Variable, separators=False)
        cb = gui.comboBox(
            self.controlArea, self, "security_ticker", box='公司股票代码：',
            model=self.varlist, callback=self.update_scene, contentsLength=12)        

        #cs = gui.comboBox(
        #    self.controlArea, self, "market_ticker", box="市场指数：",
        #    model=self.varlist, callback=self.update_scene)
        
        gui.lineEdit(
            self.controlArea, self, 'event_date', box = '事件时间：',
            tooltip='字符串表示的事件时间'
        )

        box = gui.vBox(self.controlArea, '事件窗口：')
        gui.spin(
            box, self, 'window_start',
            -100, 100, label='事件窗口开始:',
            controlWidth=60, alignment=Qt.AlignRight,
            callback=self.update_scene)
        
        gui.spin(
            box, self, 'window_end',
            0, 1000, label='事件窗口结束:',
            controlWidth=60, alignment=Qt.AlignRight,
            callback=self.update_scene)
        
        self.price_checkbox = gui.checkBox(
            self.controlArea, self, "is_price", "输入的为股票价格指数", box=True,
            callback=self.update_scene)
        
        self.logret_checkbox = gui.checkBox(
            self.controlArea, self, "log_return", "取对数收益", box=True,
            callback=self.update_scene)
        
        gui.rubber(self.controlArea)
        gui.widgetLabel(
            gui.hBox(self.controlArea, box=True),
            """为单只股票计算事件异常收益；
            也可以输入多只股票的事件日期，一次计算多只
            """)

        # self.scene = QGraphicsScene()
        # self.view = QGraphicsView(self.scene)
        # self.view.setRenderHints(
        #    QPainter.Antialiasing | QPainter.TextAntialiasing |
        #    QPainter.SmoothPixmapTransform)
        # self.mainArea.layout().addWidget(self.view)
        # self.mainArea.setMinimumWidth(400)
  
    # def sizeHint(self):
    #     return QSize(200, 150)  # Horizontal size is regulated by mainArea

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None and (
                not bool(dataset) or not len(dataset.domain.variables)):
            dataset = None
        self.closeContext()
        self.dataset = dataset
        self.is_prcice = None
        self.log_return = None
        domain = dataset.domain if dataset is not None else None
        self.varlist.set_domain(domain)
        #self.time_vars.set_domain(domain)
        if dataset is not None:
            self.select_default_variables(domain)
            self.openContext(self.dataset)
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv',delete=True) as fp:
            ext = os.path.splitext(fp.name)[1]
            writer = FileFormat.writers.get(ext)
            writer.write(fp.name, self.dataset, False)
            self.es_model.import_returns(fp.name, is_price=self.is_price, log_return=self.log_return)  

    def select_default_variables(self, domain):
        if len(self.varlist) > len(domain.class_vars):
            first_attr = self.time_vars[len(domain.class_vars)]
        else:
            first_attr = None
        if len(self.varlist):
            self.security_ticker, self.market_ticker = self.varlist[0], first_attr
        else:
            self.security_ticker, self.market_ticker = self.market_ticker, None

    def update_scene(self):
        #self.scene.clear()
        if self.security_ticker is None:
            return
        self.es_model.constant_mean(
            security_ticker=self.security_ticker,
            event_date=self.event_date,
            event_window=(self.window_start,self.window_end),
            estimation_size=300,
        )
        result = table_from_frame(self.es_model.results())
        self.Outputs.es_result.send(result)


def main(argv=None):
    from AnyQt.QtWidgets import QApplication
    if argv is None:
        argv = sys.argv
    argv = list(argv)
    app = QApplication(argv)
    filename = "heart_disease"
    data = Orange.data.Table(filename)
    w = OWAbnormalRet()
    w.show()
    w.raise_()
    w.set_data(data)
    w.handleNewSignals()
    rval = app.exec_()
    w.set_data(None)
    w.handleNewSignals()
    w.saveSettings()
    return rval


if __name__ == "__main__":
    sys.exit(main())