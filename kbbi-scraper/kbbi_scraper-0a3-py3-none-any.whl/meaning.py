class Meaning:
    def __init__(self, *args, **kwargs):
        self._word = kwargs['word'] if 'word' in kwargs else None
        self._meaning = kwargs['meaning'] if 'meaning' in kwargs else None
        self._symbols = kwargs['symbols'] if 'symbols' in kwargs else None

    def __str__(self):
        return self.word or ''
    
    @property
    def word(self):
        return self._word

    @property
    def meaning(self):
        return self._meaning

    @property
    def symbols(self):
        return self._symbols