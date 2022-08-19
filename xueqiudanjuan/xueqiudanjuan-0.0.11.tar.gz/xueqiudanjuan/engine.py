import requests


class Engine(object):
    def __init__(self):
        # Initialize the Engine's constants
        self.crawler_head = {'user-agent': 'Mozilla/5.0'}   # The headers of xueqiu website
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"   # The format of the log message
        self.date_format = "%m%d/%Y %H:%M:%S %p"    # The format of date

        # Initialize the engine's session
        self.session = requests.Session()
        self.session.get("https://xueqiu.com/", headers=self.crawler_head)

    def get_html_text(self, url, param=None):
        try:
            r = self.session.get(url, headers=self.crawler_head, params=param, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except requests.exceptions.HTTPError as e:   # HTTPError
            print("HTTPError: for url " + url)
            return ""
        except Exception as e:  # Other Exceptions
            print("Exception: " + str(e))
            return ""
