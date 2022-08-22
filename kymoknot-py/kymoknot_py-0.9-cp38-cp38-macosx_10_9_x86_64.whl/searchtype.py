from enum import Enum


#search types

class SearchType(Enum):
    BU  = 0
    TD  = 1
    UNS = 2
    TNG = 3


class UndefinedSearchType(Exception):
    pass


def encode_search_type(search_type):

    res = [0 for i in range(4)]
    all_types = list(SearchType)

    for s in search_type:
        if s in all_types:
            res[s.value] = 1
        else:
            raise UndefinedSearchType

    return res


def res_to_searchtype(res):

    conv = {
            0 : SearchType.BU,
            1 : SearchType.TD,
            2 : SearchType.UNS,
            3 : SearchType.TNG,
        }

    search_type = conv.get(res)
    if res is None:
        raise UndefinedSearchType

    return search_type


