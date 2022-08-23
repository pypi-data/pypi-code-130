"""
__author__ = 'Qrp'
__desc__ = 'selenium底层操作封装'
"""
# 封装 driver, do_find, do_send_keys, wait_visible,
import time

from selenium import webdriver
from util.log_util import logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

class Base:
    _BASE_URL = ""

    def __init__(self, base_driver=None,host=None):
        """初始化driver 如果存在，复用driver ，如果不存在 创建一个driver"""
        if base_driver:
            # 复用driver
            logger.info("复用driver")
            self.driver = base_driver
        else:
            # 为None
            # 创建一个driver
            # 第一步：创建一个driver实例变量
            logger.info("创建driver")
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            self.driver.implicitly_wait(5)

        if not self.driver.current_url.startswith("http"):
            # 不以http 开头则打开_base_url
            self._BASE_URL = host + "/portal/admin/#/login"
            self.driver.get(self._BASE_URL)

    def do_find(self, by, value=None):
        logger.info(f"查找元素{by, value}")
        """查找单个元素"""
        if value:
            return self.driver.find_element(by, value)
        else:
            # (By.ID,"")
            return self.driver.find_element(*by)

    def do_finds(self, by, value=None):
        """查找多个元素"""
        # (By.ID,"")
        if value:
            return self.driver.find_elements(by, value)
        else:
            return self.driver.find_elements(*by)

    def do_send_keys(self, text, by, value=None):
        logger.info(f"输入内容{text}")
        """输入文本"""
        ele = self.do_find(by, value)
        ele.clear()
        ele.send_keys(text)

    def explicit_wait(self,seconds,by):
        logger.info(f"等待秒数{seconds},等待可点击元素{by}")
        """目前只写了显示等待元素可点击"""
        WebDriverWait(self.driver,seconds).until(expected_conditions.element_to_be_clickable(by))

    def operation_table(self,table_location):
        """
        表格操作，以二维数组形式返回表格中所有的值
        :param table_location: 定位表格的方法
        :return:以二维数组形式返回表格中所有内容
        """
        logger.info(f"表格定位地址为{table_location}")
        _TABLE = (table_location)
        tb_list = self.driver.find_element(*_TABLE).find_elements(By.TAG_NAME, "tr")
        arr_list = []
        for tr in tb_list:
            arr = tr.text.split("\n")
            arr_list.append(arr)
        logger.info(f"表格内容为：{arr_list}")
        return arr_list

    def operation_ul_li(self,ul_location,li_value):
        lis = self.do_finds(By.XPATH,ul_location)
        for li in lis:
            if li_value in li.text:
                li.click()
                break


    def close_driver(self):
        time.sleep(3)
        self.driver.quit()
