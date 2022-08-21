import zq_selenium, time, zq_http
from selenium.webdriver.common.by import By
class tts_youdao_web_class:
    def __init__(self):
        self.selenium_tools = zq_selenium.selenium_tools_class()
        self.selenium_tools.web_open_url('https://ai.youdao.com/product-tts.s')
        self.selenium_tools.web_wait_node_element_click(By.ID, 'customSelectBtnText')
        time.sleep(1)
        self.selenium_tools.web_node_find_elements_click(By.CLASS_NAME, 'anchorColor', 2)

    def tts_youdao_req(self, save, text):
            self.selenium_tools.web_wait_node_element_click(By.ID, 'clearInput')
            self.selenium_tools.web_wait_node_element_send_keys(By.ID, 'inputText', text)
            self.selenium_tools.web_wait_node_element_click(By.ID, 'syntheticBtn')
            audio_src = self.selenium_tools.web_wait_node_get_attribute(By.ID, 'jp_audio_0', 'src')
            if zq_http.http_download(audio_src, save):
                print('下载语音成功:%s'%save)
            else:
                print('下载语音洗白:%s'%save)