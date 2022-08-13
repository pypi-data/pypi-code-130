from base64 import urlsafe_b64encode
import requests

from distutils.file_util import write_file
from urldt.utils import read_targets, write_result
from urldt.url_asset import URLAsset


class Scanner:
    def __init__(self, input_file: str = None, output_file: str = None, is_quiet: bool = None,
                 targets: list = None, results: list = None, ) -> None:
        self._input_file = input_file
        self.output_file = output_file
        self.targets = targets
        self.results = results
        self.is_quiet = is_quiet
        self.url_asset: URLAsset = None

    @property
    def input_file(self):
        '''targets information will be load automatically.'''
        return self._input_file

    @input_file.setter
    def input_file(self, filename: str):
        self._input_file = filename
        csv_header, self.targets = read_targets(filename)
        self.url_asset = URLAsset(csv_header)

    def is_available(self, url: str) -> bool:
        '''check if url  is available'''
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False

    def run(self) -> list:
        '''find available targets'''
        available_urls = list()
        amount = len(self.targets)

        try:
            cnt = 1
            for info in self.targets:
                url = info[self.url_asset.url_index]
                title = info[self.url_asset.title_index]
                if self.is_available(url):
                    print(f'已检查: {cnt}/{amount}, {url}, {title}, 存活')
                    available_urls.append([url, title])
                cnt += 1

        except KeyboardInterrupt:
            print('Process terminated!')

        if self.output_file:
            write_result(self.output_file, available_urls)

        return available_urls
