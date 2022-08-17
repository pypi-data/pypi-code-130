from pytest_extensions.comparators import FuncComparator

startswith = FuncComparator(str.startswith)
endswith = FuncComparator(str.endswith)

class contains:
    def __init__(self, match):
        self.match = match
        self.last_comparison = None

    def __repr__(self):
        return f"{repr(self.match)} in {repr(self.last_comparison)}"

    def __eq__(self, other):
        self.last_comparison = other
        return self.match in other
