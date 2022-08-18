from zeep import xsd


class MutatieRegel:
    def __init__(
        self,
        bedrag_invoer: str,
        bedrag_excl_btw: str,
        bedrag_btw: str,
        bedrag_incl_btw: str,
        btw_code: str,
        btw_percentage: str,
        tegenrekening_code: str,
    ):
        self.bedrag_invoer = bedrag_invoer
        self.bedrag_excl_btw = bedrag_excl_btw
        self.bedrag_btw = bedrag_btw
        self.bedrag_incl_btw = bedrag_incl_btw
        self.btw_code = btw_code
        self.btw_percentage = btw_percentage
        self.tegenrekening_code = tegenrekening_code

    def export(self):
        return dict(
            BedragInvoer=self.bedrag_invoer,
            BedragExclBTW=self.bedrag_excl_btw,
            BedragBTW=self.bedrag_btw,
            BedragInclBTW=self.bedrag_incl_btw,
            BTWCode=self.btw_code,
            BTWPercentage=self.btw_percentage,
            TegenrekeningCode=self.tegenrekening_code,
            KostenplaatsID=xsd.SkipValue,
        )
