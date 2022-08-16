import os
import example_demo.setting as setting


class UrlSourceBase(object):
    def __init__(self, work_path=os.getcwd(), **kwargs):
        self.work_path = work_path
        self.init_work_path()
    # 初始化运行目录
    def init_work_path(self):
        cwd_path = os.getcwd()
        if cwd_path != self.work_path:
            setting.reload_setting(self.work_path)
