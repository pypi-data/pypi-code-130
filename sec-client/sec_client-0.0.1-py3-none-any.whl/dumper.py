from .caller import Caller
from .extractor import extract
from .tables.inputs import Inserter, Updater

insert = Inserter()
update = Updater()

class Dumper(Caller):
    def __init__(self, ticker, fact):
        super().__init__(ticker)        
        call = self.get_fact(fact)
        self.extracted = extract(call)
        
        self.fact = fact
        
    def fact(self):
        [insert.value(
            self.ticker, self.fact, value, year) for value, year in self.extracted]
        