class GlobalDict():
    inst = {}

    def __new__(cls):
        inited = True
        if not cls.inst.get(inited):
            inited = False
            cls.inst.update({False: object.__new__(cls)})
        return cls.inst.get(inited)

    def __init__(self) -> None:
        if False in GlobalDict.inst:
            self.repdict = {}
            GlobalDict.inst = {True: self}

    def __getitem__(self, key):
        if key in self.repdict:
            return self.repdict.get(key)
        else:
            raise KeyError

    def __setitem__(self, key, value):
        try:
            self.repdict[key] = value
        except TypeError as te:
            return te

    def setdefault(self, key, default):
        return self.repdict.setdefault(key, default)
