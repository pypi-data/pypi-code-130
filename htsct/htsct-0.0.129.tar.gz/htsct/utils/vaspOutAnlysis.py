from pathlib import Path


class VaspOutAnalysis:
    def __init__(self, fn=""):
        self.__filename = Path(fn)
        if "OUTCAR" != self.__filename.name:
            self.__filename = self.__filename / "OUTCAR"
        self.errors = []
        self.warnings = []

    def is_converge(self):
        with open(self.__filename) as fd:
            for line in fd:
                if "reached required accuracy" in line:
                    return True
            return False

    def error_collection(self):
        errors = ""
        with open(self.__filename) as fd:
            for line in fd:
                if "Error" in line or "error" in line or "failed" in line:
                    errors += line
            if errors:
                return errors
            return ""

    def warning_collection(self):
        warnings = ""
        with open(self.__filename) as fd:
            for line in fd:
                if "WARNING" in line or "Warning" in line:
                    warnings += line
            if warnings:
                return warnings
            return ""
