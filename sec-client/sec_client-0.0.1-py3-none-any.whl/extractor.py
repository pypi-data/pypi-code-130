from utils import handlers
from utils import nodupes


class Extractor:
    def __init__(self, call) -> None:
        self.call = call

    def __extract_years(self, entries):
        return nodupes([entry["fy"] for entry in entries])

    def __extract_values(self, entries):
        return nodupes([entry["val"] for entry in entries])

    def __extract_entries(self, form="10-K"):
        return [entry for entry in self.call if entry["form"] == form and "frame" not in entry]

    def extract(self, form="10-K"):
        entries = self.__extract_entries(form=form)
        values = self.__extract_values(entries)
        years = self.__extract_years(entries)

        return handlers.years(values, years)


def extract(call, form="10-K"):
    return Extractor(call).extract(form=form)
