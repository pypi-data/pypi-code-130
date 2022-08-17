import requests
import logging


class Engine(object):
    def __init__(self):
        # Initialize the Engine's constants
        self.crawler_head = {'user-agent': 'Mozilla/5.0'}   # The headers of xueqiu website
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"   # The format of the log message
        self.date_format = "%m%d/%Y %H:%M:%S %p"    # The format of date

        # Set the engine's logging settings
        logging.basicConfig(filename='./log.log', level=logging.DEBUG, format=self.log_format, datefmt=self.date_format)

        # Initialize the engine's session
        self.session = requests.Session()
        self.session.get("https://xueqiu.com/", headers=self.crawler_head)

        logging.log(logging.INFO, "Successfully created session")

    def get_html_text(self, url, param=None):
        try:
            r = self.session.get(url, headers=self.crawler_head, params=param, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except requests.exceptions.HTTPError as e:   # HTTPError
            logging.log(logging.ERROR, "HTTPError: for url " + url, e)
            print("HTTPError: for url " + url)
            return ""
        except Exception as e:  # Other Exceptions
            logging.log(logging.ERROR, "Exception: " + str(e))
            print("Exception: " + str(e))
            return ""
