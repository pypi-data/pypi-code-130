from .tables import Query

class Loader(Query):
    def __init__(self, ticker, fact):
        super().__init__()
        self.ticker = ticker
        self.fact = fact
        
    def fact(self):
        return self.xtag(self.ticker, self.fact)