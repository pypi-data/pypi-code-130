from _kymoknot_bindings import ffi, lib
from . import searchtype


class KnotEntry(object):

    #add here any fields from search_retval_t that should
    #be set as instance attribute after initialization
    # <instance>.attribute notation
    #if struct field is an array or a struct itself, provide proper marshalling
    fields = ["knot_ids", "start", "end", "length", "search_type"]

    def __init__(self, init_struct):

        if isinstance(init_struct, dict):
            for k in init_struct:
                if k in self.fields:
                    setattr(self, k, init_struct[k])
        else:
            for k in self.fields:

                attr = getattr(init_struct, k)

                if isinstance(attr, ffi.CData):
                    attr = ffi.string(attr, 128).decode("ascii")

                elif k == "search_type":
                    attr = searchtype.res_to_searchtype(attr)

                setattr(self, k, attr)

        return


    def __str__(self):
        return f"{self.knot_ids} {self.start} {self.end} {self.length} {self.search_type}"

    def __repr__(self):
        return self.__str__()


class TangleEntry(KnotEntry):

    fields = ["knot_ids", "start", "start_t2", "end", "end_t2", "length", "search_type"]

    def __str__(self):
        return f"{self.knot_ids} {self.start} {self.end} {self.start_t2} {self.end_t2} {self.length} {self.search_type}"

    def __repr__(self):
        return self.__str__()


def create_entry(entry):

    res = None

    stype = searchtype.res_to_searchtype(entry.search_type)

    if stype == searchtype.SearchType.TNG:
        res = TangleEntry(entry)

    else:
        res = KnotEntry(entry)

    return res


