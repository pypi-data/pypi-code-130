#!/usr/bin/env python3

class BrotherGenericCommand:

    def __bytes__(self):
        raise NotImplementedError("Must override this.")

    def __repr__(self):
        return "[BrotherESCPCommand: %s]" % self.__class__.__name__


class BrotherESCPCommand(BrotherGenericCommand):

    def __init__(self, leading_bytes):
        BrotherGenericCommand.__init__(self)
        self.leading_bytes = leading_bytes

    def compile(self):
        raise NotImplementedError("Must override this.")

    def __bytes__(self):
        data = self.compile()
        assert type(data) == bytes
        ret = b"\x1B" + self.leading_bytes + data
        print(repr(self), "\t", " ".join([hex(e)[2:].rjust(2, "0") for e in ret]))
        return ret
