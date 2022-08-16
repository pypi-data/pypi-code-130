from os.path import join, dirname
import os
import sys
import tempfile
from plotly.io import to_html
import plotly.graph_objs as go

from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import OWWidget, Input, Output

from AnyQt.QtWidgets import QTreeWidget, \
    QWidget, QPushButton, QListView, QVBoxLayout
from AnyQt.QtGui import QIcon

from Orange.widgets.utils.itemmodels import VariableListModel
#from orangecontrib.finecon.widgets.utls.echarts import Echarts
from Orange.data import Table, Domain, DiscreteVariable, Variable, \
    ContinuousVariable
    
from orangecontrib.timeseries import Timeseries
from Orange.data.pandas_compat import table_from_frame
import akshare as ak

class OWLineChartEcharts(OWWidget):
    name = '异常收益AR'
    description = "下载股票交易数据，计算异常收益AR."
    icon = 'icons/misc.svg'
    priority = 90

    class Inputs:
        data = Input("Data", Table)
    class Outputs:
        time_series = Output("Time series", Timeseries)

    attrs = settings.Setting({})  # Maps data.name -> [attrs]

    # 设置输入数据:股票代码，事件日，自然日还是股票交易日，前排除时长，后排除时长，时间前期，时间后期
    attr_x = ''
    attr_y = ''

    def __init__(self):
        self.data = None
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html',delete=False)
        # A model for displaying python list like objects in Qt item view classes
        # 用于表示下拉框数据列表的模型
        self.varmodel = VariableListModel(parent=self)
        
        vbox = gui.vBox(self)
        # 从输入数据字段列表选取x轴的下拉框
        self.cb_attr_x = gui.comboBox(vbox, self, 'attr_x',
                     label='x轴:',
                     orientation='horizontal',
                     model=self.varmodel,
                     sendSelectedValue=True)
        # 从输入数据字段列表选取y轴的下拉框
        self.cb_attr_y = gui.comboBox(vbox, self, 'attr_y',
                     label='y轴:',
                     orientation='horizontal',
                     model=self.varmodel,
                     sendSelectedValue=True)
        # 按钮
        self.draw_button = QPushButton('绘制折线图', self)
        self.draw_button.clicked.connect(self.linechart_plot)
        # 在控制区域放置控制部件
        self.controlArea.layout().addWidget(vbox)
        self.controlArea.layout().addWidget(self.draw_button)
        # 创建Echarts部件
        self.chart = None #Echarts(self)
        # 在显示区域放置Echarts部件
        self.mainArea.layout().addWidget(self.chart)

    def set_figure(self, fig=None):
        self.tmp_file.seek(0)
        if fig is None:
            fig=go.Figure()
        fig.update_xaxes()
        
    def linechart_plot(self):
        # Echarts的参数选项
        options = {
            'xAxis': {
                'data': self.data.get_column_view(self.attr_x)[0].tolist(),
            },
            'yAxis': {
                'scale': 'true'
            },
            'dataZoom': [
                {
                    'type': 'inside'
                },
            ],
            'series': [{
                'symbolSize': 10,
                'data': self.data.get_column_view(self.attr_y)[0].tolist(),
                'type': 'line'
            }]
        };
        # 绘制图形
        self.chart.chart(options=options)

    @Inputs.data
    def set_data(self, data):
        new_data = None if data is None else data
        if new_data is not None and self.data is not None \
                and new_data.domain == self.data.domain:
            self.data = new_data
            for config in self.configs:
                config.selection_changed()
            return

        self.data = data = None if data is None else data
        if data is None:
            self.varmodel.clear()
            self.chart.clear()
            return

        self.varmodel.wrap([var for var in data.domain.variables
                            if var.is_continuous])

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from orangecontrib.timeseries import ARIMA, VAR

    a = QApplication([])
    ow = OWLineChartEcharts()

    table = Table("iris")
    ow.set_data(table)

    ow.show()
    a.exec()