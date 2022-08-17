class Result:
    def __init__(self, valid: bool, val):
        if valid:
            self._value = val
            self._error = None
        else:
            self._value = None
            self._error = val

        self.valid = valid

    @classmethod
    def ok(cls, value):
        return cls(True, value)

    @classmethod
    def fail(cls, error):
        return cls(False, error)

    @property
    def value(self):
        assert self.valid, "Try to unwrap invalid result."
        return self._value

    @property
    def error(self):
        assert not self.valid, "Try to unwrap the error of a valid result."
        return self._error

    def __bool__(self):
        return self.valid
