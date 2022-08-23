from backtrader.sizers import FixedSize


class AztSizer(FixedSize):
    params = dict(
        stake=100
    )
