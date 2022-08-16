import arrow
from loguru import logger


class Validator:
    def __init__(self, data):
        self.instance = data["class"]
        self.max_days_old = data.get("max_days_old", None)
        self.max_periods_old = data.get("max_periods_old", None)
        self.data = data["data"]
        if "dataset" in data:
            self.dataset = data["dataset"] if data["dataset"] else []
        if "pep_analysis" in data:
            self.pep_analysis = data["pep_analysis"] if data["pep_analysis"] else []
        if "depth" in data:
            self.depth = data["depth"] if data["depth"] else None

    def banco_central_validator(self):
        logger.info("Running Banco Central validator")
        months_old = int(
            (
                arrow.utcnow().ceil("month")
                - arrow.get(self.data["prospect_date"]).floor("day")
            ).days
            / 30
        )
        return self.max_days_old is not None and months_old > self.max_periods_old

    def receita_federal_validator(self):
        logger.info("Running Receita Federal validator")
        if "emails_extended" in self.dataset:
            if not self.data["mail"]:
                return False
        if "phones_extended" in self.dataset:
            if not self.data["phone"]:
                return False
        if "addresses_extended" in self.dataset:
            if not self.data["address"]:
                return False
        if "activity_indicators" in self.dataset:
            if not self.data["employees_range"]:
                return False
        return True

    def qsa_validator(self):
        logger.info("Running QSA validator")
        qsa_persons = self.data["qsa_persons"]
        for person in qsa_persons:
            if self.pep_analysis and person.get("is_pep_anyway", None) is None:
                return False
        if self.depth and self.data.get("relationships", None) is None:
            return False
        return True

    def start(self):
        if self.instance == "receita_federal_pj":
            self.dataset = (
                self.enum_to_str(self.dataset)
                if isinstance(self.dataset, list)
                else self.dataset
            )
            return self.receita_federal_validator()
        elif self.instance == "qsa":
            return self.qsa_validator()
        elif self.instance == "banco_central":
            return self.banco_central_validator()
        return True

    def enum_to_str(self, arr):
        return [i.value for i in arr]
