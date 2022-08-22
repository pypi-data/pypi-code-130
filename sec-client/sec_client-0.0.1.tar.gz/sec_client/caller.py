from .base import BaseClient


class Caller(BaseClient):
    def __init__(self, ticker):
        super().__init__(ticker)

    def get_fact(self, fact):
        return self.call_gaap()[fact]["units"]["USD"]

