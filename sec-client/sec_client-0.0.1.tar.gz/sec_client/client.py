from .dumper import Dumper
from .loader import Loader


class SecClient:
    def __init__(self):
        pass

    def call_fact(self, ticker, fact_):
        load = Loader(ticker, fact_)
        fact = load.fact()

        if len(fact) > 1:
            return [(_.value, _.year) for _ in fact]

        dump = Dumper(ticker, fact_)
        dump.fact()
        return dump.extracted
    
