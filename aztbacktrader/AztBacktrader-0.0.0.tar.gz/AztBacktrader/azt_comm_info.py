from backtrader import CommInfoBase


class AztCommInfo(CommInfoBase):
    def getvaluesize(self, size, price):
        return abs(size) * price

    def getoperationcost(self, size, price):
        return abs(size) * price

    pass
