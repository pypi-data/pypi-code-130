class ValueNotOfSupportedType(Exception):
    def __init__(self, error):
        return super().__init__(error)


class ConflictingDataDetected(Exception):
    def __init__(self, error):
        return super().__init__(error)
