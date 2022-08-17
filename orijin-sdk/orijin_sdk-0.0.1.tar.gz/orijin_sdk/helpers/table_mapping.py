class Map:
    def __init__(self, oldID, newID):
        self.oldID = oldID
        self.newID = newID

def find_new_id(map: list[Map], oldID):
    filtered = [ x for x in map if x.oldID == oldID ]
    if len(filtered) == 0: return
    if len(filtered) > 1: raise Exception("Error: oldID was uploaded multiple times, this should never happen!")
    return filtered[0].newID

def list_map_to_table(map: list[Map]):
    rtn = list[list[str]]()
    
    for entry in map:
        rtn.append([entry.oldID, entry.newID])
    
    return rtn