from sec_edgar_api import EdgarClient
from fake_useragent import UserAgent
from .tables import Query

query = Query()


class BaseClient:
    def __init__(self, ticker):
        ua = UserAgent()
        edgar = EdgarClient(ua.ie)

        cik = query.cik(ticker)
        self.ticker = ticker
        self.__enter = edgar.get_company_facts(cik)

        # self.tags_gaap = {ticker: list(self.call_gaap())}
        # self.tags_dei = {ticker: list(self.call_dei())}

    def __base_call(self, taxonomy):
        return self.__enter["facts"][taxonomy]

    def call_gaap(self):
        return self.__base_call("us-gaap")

    def call_dei(self):
        return self.__base_call("dei")
