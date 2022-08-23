import os
import sys
import traceback

from yangke.web.pyecharts.app import start_ws_serve, update_port_in_html
from PyQt5.QtCore import pyqtSignal


def start_pyecharts_server(port=5000, callback=None):
    """
    开启pyecharts后台服务，
    :param port:
    :param callback: 服务端接收到前端画面返回的信息后，调用的函数
    :return:
    """
    os.chdir(os.path.dirname(__file__))  # 改变当前工作路径

    try:
        update_port_in_html(port)
        start_ws_serve(port=port, callback=callback)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    start_pyecharts_server(5000)
