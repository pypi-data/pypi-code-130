import pandas as pd
import requests
from fake_useragent import UserAgent
import threading
import time

match_types = {'Test': '1', 'ODI': '2', 'T20': '3', 'All': '11',
               'Test_Women': '8', 'ODI_Women': '9', 'T20_Women': '10',
               'Test_Youth': '20', 'ODI_Youth': '21', 'T20_Youth': '22'}


class espncricket:
    def __init__(self, data_type='batting', match_type='Test', view_type=''):
        self.data_type = data_type
        self.match_type = match_types[match_type]
        self.view_type = view_type
        self.template = 'results'
        self.result_set = pd.DataFrame()
        self.lock = threading.Lock()
        self.list_of_dataframes = []

    def build_url(self, page_num):
        return f"https://stats.espncricinfo.com/ci/engine/stats/index.html?" \
               f"type={self.data_type};" \
               f"class={self.match_type};" \
               f"view={self.view_type};" \
               f"template={self.template};" \
               f"page={page_num}"

    def get_url_object_with_agent(self, url):
        ua = UserAgent()
        header = {"User-Agent": str(ua.random)}
        return requests.get(url, headers=header).text

    def get_number_of_pages(self):
        url = self.build_url(page_num=1)
        url_object = self.get_url_object_with_agent(url)
        data = pd.read_html(url_object)
        return int(str(data[1][0]).split("\n")[0].split(" ")[7])

    def fetch_data(self, page_num):
        try:
            url = self.build_url(page_num=page_num)
            url_object = self.get_url_object_with_agent(url)
            data = pd.read_html(url_object)[2]
            if self.view_type in ['series', 'ground', 'host', 'opposition']:
                new_column_names = list(data.columns) + [self.view_type]
                data = pd.concat([data.iloc[::2].reset_index(drop=True),
                                  data.iloc[1::2].iloc[:, 0].reset_index(drop=True)], axis=1)
                data.columns = new_column_names
            self.list_of_dataframes[page_num - 1] = data
        except:
            self.fetch_data(page_num)

    def get_score(self, number_of_pages=99999):
        self.result_set = pd.DataFrame()
        number_of_pages = min(self.get_number_of_pages(), number_of_pages)
        self.list_of_dataframes = [pd.DataFrame() for _ in range(number_of_pages)]
        threads = [threading.Thread(target=self.fetch_data, args=(page_num + 1,)) for page_num in
                   range(number_of_pages)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        result = pd.concat(self.list_of_dataframes, axis=0, ignore_index=True)
        return result[[col for col in result.columns if 'Unnamed' not in col]]
