from abc import ABCMeta, abstractmethod


class Exchange(metaclass=ABCMeta):

    def __init__(self, market):
        self.market = market

    @abstractmethod
    def get_contract_sizes(self):
        raise NotImplementedError

    @abstractmethod
    def get_balance(self, ticker):
        raise NotImplementedError

    @abstractmethod
    def post_market_order(self, ticker, side, open_close, amount):
        raise NotImplementedError


class CcxtExchange(Exchange):

    def __init__(self, market):
        super().__init__(market)
        self.ccxt_inst = None

    def get_contract_sizes(self):
        raise NotImplementedError

    def get_balance(self, ticker):
        """
        :param ticker: <String> Ticker name. ex) 'USDT', 'BTC'
        :return: <Int> Balance amount
        """
        return self.ccxt_inst.fetch_balance()[ticker]['total']

    def post_market_order(self, ticker, side, open_close, amount):
        raise NotImplementedError
