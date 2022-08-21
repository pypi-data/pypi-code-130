import time, os, zipfile, json, requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import zq_cv, zq_http, zq_const

class selenium_tools_class():
    def __init__(self, **kw):
        self.By = By
        self.Keys = Keys

        chrome_path = kw.get('chrome_path', zq_const.const_merage_env_ins_dir('Google/Chrome/Application/chrome.exe')) # 浏览器路径
        chrome_driver_path = kw.get('chrome_driver_path', zq_const.const_merage_env_ins_dir('chromedriver_win_91.exe')) #浏览器调试路径
        chrome_zip_path = kw.get('chrome_zip_path', zq_const.const_merage_env_pkg_dir('Google.zip')) #浏览器包装地址
        chrome_hide_run = kw.get('chrome_hide_run', False) # 是否隐藏运行
        chrome_wait_time = kw.get('chrome_wait_time', 10) # 等待时间
        chrome_web = kw.get('chrome_web', False) #同步浏览处理
        chrome_web_wait = kw.get('chrome_web_wait', False) #等待浏览处理
        chrome_cookies = kw.get('chrome_cookies', None) #cookies
        chrome_url = kw.get('chrome_url', None) #默认打开地址
        chrome_open_new = kw.get('chrome_open_new', False) #默认打开地址

        self.web = chrome_web
        if not self.web:
            options = webdriver.ChromeOptions()
            # 详细参数：https://peter.sh/experiments/chromium-command-line-switches/
            options.add_argument('--log-level=3')
            options.add_argument('--no-sandbox') # 以最高权限运行
            options.add_argument('--use-system-clipboard') # 允许操作剪切板
            options.add_argument('--allow-silent-push') #允许不显示通知的 Web 推送通知
            # options.add_argument(r'user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data_Backup') #将登录态带入
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')

            options.add_argument("--enable-javascript")
            if chrome_hide_run:
                options.add_argument('--headless') ## 浏览器不提供可视化页面
                # options.headless = True
            options.add_experimental_option('excludeSwitches',['enable-automation'])
            # 禁用浏览器弹窗
            prefs = {
                'profile.default_content_setting_values' : {
                    'notifications' : 2  
                }
            }
            options.add_experimental_option('prefs',prefs)
            options.binary_location = chrome_path

            # 准备环境,解压浏览器包装
            if not os.path.exists(chrome_path):
                r = zipfile.is_zipfile(chrome_zip_path)
                if r:     
                    fz = zipfile.ZipFile(chrome_zip_path, 'r')
                    for file in fz.namelist():
                        fz.extract(file, './env')
                else:
                    print('这不是一个正规的zip压缩包')
            self.web = webdriver.Chrome(options=options, executable_path=chrome_driver_path, chrome_options=options)
        self.web.maximize_window()
        self.web.set_page_load_timeout(chrome_wait_time)
        self.web.set_script_timeout(chrome_wait_time)
        self.web_wait = chrome_web_wait
        self.curr_window_handle = None
        if not self.web_wait:
            self.web_wait = WebDriverWait(self.web, chrome_wait_time)
        if chrome_cookies:
            self.web_add_cookies(chrome_cookies)
        if chrome_url:
            self.curr_window_handle = self.web_open_url(chrome_url, self.curr_window_handle, open_new=chrome_open_new)
    
    def web_add_cookies(self, cookies):
        ''' 添加cookies '''
        try:
            if cookies:
                for i in cookies:
                    if 'expiry' in i:
                        i.pop('expiry')
                    self.web.add_cookie(i)
        except:
            pass
    
    def web_switch_to_window(self, window_name):
        if window_name and window_name in self.web.window_handles:
            self.web.switch_to.window(window_name)

    def web_open_url(self, url, window_handle=None, open_new=False):
        ''' 打开地址 '''
        if open_new: # 新开窗口
            js='window.open("%s");'%url
            self.web.execute_script(js)
            window_handle = self.web.window_handles[-1]
            self.web_switch_to_window(window_handle)
        else: # 不新开,永远用第一个, 或者传进来的哪一个
            window_handle = window_handle if window_handle else self.web.window_handles[0]
            self.web_switch_to_window(window_handle)
            self.web.get(url)
        return self.web.current_window_handle
    
    def web_close(self, window_handle=None):
        if window_handle:
            self.web_switch_to_window(window_handle)
        self.web.close()

    def web_refresh(self):
        ''' 刷新网页 '''
        self.web.refresh()

    def web_refresh_window(self, window_handle):
        ''' 刷新网页 '''
        self.web_switch_to_window(window_handle)
        self.web_refresh()

    def web_get_cookies(self):
        ''' 获取cookies '''
        return self.web.get_cookies()

    def web_switch_to_frame(self, name):
        ''' 主窗切换到frame '''
        self.web.switch_to.frame(name)

    def web_switch_to_default_content(self):
        ''' frame切换到主窗 '''
        self.web.switch_to.default_content()

    def web_get_requests_get(self, url):
        ''' 获取带浏览器cookies的requests模拟 '''
        requestCookies = {}
        cookies = self.web_get_cookies()
        for i in cookies:
            if 'expiry' in i:
                i.pop('expiry')
            requestCookies[i['name']] = i['value']
        return requests.get(url, cookies=requestCookies)


    def web_get_requests_post(self, url, data):
        ''' 获取带浏览器cookies的requests模拟 '''
        requestCookies = {}
        cookies = json.dumps(self.web_get_cookies())
        for i in cookies:
            if 'expiry' in i:
                i.pop('expiry')
            requestCookies[i['name']] = i['value']
        return requests.post(url, cookies=requestCookies, data=data)

    def web_node_is_hidden(self, id, idValue, index=0):
        ''' web 节点是否属于隐藏节点 '''
        return self.web_node_get_attribute(id, idValue, 'hidden', index) == 'true'

    def web_wait_node_is_hidden(self, id, idValue):
        ''' web 节点是否属于隐藏节点 '''
        return self.web_wait_node_get_attribute(id, idValue, 'hidden') == 'true'

    def web_node_get_attribute(self, id, idValue, attrName='textContent', index=0):
        ''' web 获取属性 '''
        element = self.web_node_find_element(id, idValue, index)
        if element:
            return element.get_attribute(attrName)
        else:
            return None

    def web_wait_node_get_attribute(self, id, idValue, attrName='textContent'):
        ''' web 等待出现 获取属性 '''
        element = self.web_wait_node_element(id, idValue)
        if element:
            return element.get_attribute(attrName)
        else:
            return None

    def web_node_find_elements(self, id, idValue):
        ''' web 多个获取 '''
        return self.web.find_elements(id, idValue)

    def web_node_find_element(self, id, idValue, index=0):
        ''' web 直接获取 '''
        elements = self.web_node_find_elements(id, idValue)
        if len(elements) <= index:
            return None
        return elements[index]

    def web_node_element_send_key(self, id, idValue, content, index=0):
        ''' web 直接获取 '''
        try:
            element = self.web_node_find_element(id, idValue, index)
            if not element:
                return False
            element.send_keys(content)
            return True
        except:
            return False

    def web_node_element_has(self, id, idValue):
        ''' web 是否存在 节点 '''
        elements = self.web_node_find_elements(id, idValue)
        return not len(elements) == 0
    
    
    def web_node_element_has_by_element(self, parent_element, id, idValue):
        ''' web 是否存在 节点 '''
        elements = parent_element.find_elements(id, idValue)
        return not len(elements) == 0

    def web_node_find_elements_click(self, id, idValue, indexs=0, endSleep=1, startSleep=0):
        ''' web 多个直接点击 '''
        try:
            time.sleep(startSleep)
            elements = self.web_node_find_elements( id, idValue)
            if len(elements) == 0:
                return False
            if isinstance(indexs, list) or isinstance(indexs, tuple):
                for index in indexs:
                    if index < len(elements):
                        elements[index].click()
                        time.sleep(endSleep)
            else:
                if indexs < len(elements):
                    elements[indexs].click()
                    time.sleep(endSleep)
            return True
        except:
            return False


    def web_wait_node_element(self, id, idValue):
        ''' web 等待出现 '''
        try:
            return self.web_wait.until(EC.presence_of_element_located((id, idValue)))
        except:
            return None

    def web_wait_node_element_click(self, id, idValue):
        ''' web 等待出现 点击 '''
        try:
            element = self.web_wait_node_element(id, idValue)
            if not element:
                return False
            element.click()
            return True
        except:
            return False

    def web_wait_node_element_send_keys(self, id, idValue, *content):
        ''' web 等待出现 发送值 '''
        try:
            element = self.web_wait_node_element(id, idValue)
            if not element:
                return False
            element.send_keys(content)
            return True
        except:
            return False

    def web_node_action_chains_drag(self, slider, tracks):
        ActionChains(self.web).click_and_hold(slider).perform()
        for x in tracks:
            ActionChains(self.web).move_by_offset(xoffset=x,yoffset=0).perform()
        # ActionChains(self.web).move_by_offset(xoffset=offset,yoffset=0).perform()
        ActionChains(self.web).release().perform()

    def web_node_action_chains_click_and_hold(self, element, sleep):
        '''鼠标长按下'''
        ActionChains(self.web).click_and_hold(element).perform()
        time.sleep(sleep)
        ActionChains(self.web).release().perform()

    def web_node_action_chains_click(self, element):
        '''鼠标按下'''
        self.web_node_action_chains_click_and_hold(element, 0)

    def web_node_action_chains_key_down(self, key, element, sleep):
        '''
        按下输入
        '''
        ActionChains(self.web).key_down(key, element).perform()
        time.sleep(sleep)
        ActionChains(self.web).key_up(key, element).perform()
    
    def web_node_action_chains_move_to(self, element):
        ''' 隐藏按钮需要移动上去才能操作，否则 element not interactable '''
        ActionChains(self.web).move_to_element(element).perform()
