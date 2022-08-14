class BArray():

    # RootHandler
    class RootHandler():
        roots = None
        def __init__(self):
            self.roots = [
                ["SORTED" , False],
                # Changing Type can cause unsafe behavior
                ["TYPE", "None"],
                ["LENGTH", 0],
                ["FORCE_LENGTH", True],
                ["FORCE_TYPE", True],
                # Only Enable for Experimental Behavior, can cause unsafe activity
                ["EXPERIMENTAL", False],
                # Only Enable for Experimental Behavior, can cause unsafe activity
                ["MODE_UNSAFE", False],
                ["DICT_TYPE_HANDLER_USEAGE", None]
            ]

    # RootObject
    class RootObject(RootHandler):

        _refference = {
            'int':0,
            'str':'',
            'float':0.0,
            'boolean':False,
            'complex':0 + 0j
        }

        def __init__(self):
            super().__init__()
        
        def root(self, root:str):
            length = len(self.roots)
            for i in range(length-1):
                if self.roots[i][0] == root:
                    return self.roots[i][1]

        def setRoot(self, rootEdit:str, flagValue) -> None:
            root = rootEdit.upper()
            # print(root)
            length = len(self.roots)
            x = None
            for i in range(length):
                if self.roots[i][0] == root:
                    x = i
            if x != None and (type(self.roots[x][1]) == type(flagValue)):
                self.roots[x][1] = flagValue
            else:
                if x == 7:
                    self.roots[x][1] = self._refference.get(self.roots[1][1])
                else:
                    print("Root DNE or flag value cannot be specified type.")
    
    class RootChecker():
        LENGTH = None
        FORCE_LENGTH = None
        FORCE_TYPE = None
        DICT_TYPE_HANDLER_USEAGE = None
        roots = None

        def __init__(self, rootObjRoots : list):
            self.roots = rootObjRoots
            self.setUpChecker()            

        def setUpChecker(self):
            self.LENGTH = self.roots[2][1]
            self.FORCE_LENGTH = self.roots[3][1]
            self.FORCE_TYPE = self.roots[4][1]
            self.DICT_TYPE_HANDLER_USEAGE = self.roots[7][1]

    # Holding Array
    _holding = []

    # Makes the Root Object Accessible
    rootObject = RootObject()
    rootChecker = None

    _refference = {
        'int':0,
        'str':'',
        'float':0.0,
        'boolean':False,
        'complex':0 + 0j
    }

    def __init__(self, type: str, len: int):
        self.rootObject.roots[1][1] = type
        self.rootObject.roots[2][1] = len
        self.rootObject.roots[7][1] = self._refference.get(type)
        self.make()
        self.rootChecker = self.RootChecker(self.rootObject.roots)
        
    def make(self) -> None:
        if self.rootObject.roots[1][1] in self._refference:
            self._holding = [self._refference.get(self.rootObject.roots[1][1])] * self.rootObject.roots[2][1]
        else:
            print("Type Cannot Exist in BArray, Destrcting Object")
            del self
            del rootObject

    def __len__(self):
        return self.rootObject.roots[2][1]
    
    def __repr__(self):
        return self._holding
    
    def __str__(self):
        return str(self.__repr__())
    
    def preserve(self, filename:str) -> None:
        f = open(filename, 'x')
        for element in self._holding:
            f.write(str(element) + " // ")
        f.close()
    
    def set(self, data, index : int = None) -> None:
        indx = -1 if index is None else index
        if type(data) is list:
            self.__setHoldingList(data)
        if type(data) is not list:
            self.__setHoldingSingle(data, indx)
    
    def __setHoldingList(self, l) -> None:
    # Only LEN AND TYPE FORCED
        if self.rootChecker.FORCE_LENGTH == True and len(l) != self.rootObject.roots[2][1]:
            print("Size Incompatible with CURR_LENGTH")
            pass
        if self.rootChecker.FORCE_LENGTH == True and self.rootChecker.FORCE_TYPE == True:
            if len(l) == self.rootObject.roots[2][1]:
                self._holding = []
                for index in l:
                    if type(index) == type(self.rootChecker.DICT_TYPE_HANDLER_USEAGE):
                        self._holding.append(index)
                    else:
                        self._holding.append(None)
                        self.rootObject.roots[6][1] = True
                        print("Array Switced to MODE_UNSAFE as BArray Encounted Unexpected Value While Parsing")
        elif self.rootChecker.FORCE_LENGTH == True and self.rootChecker.FORCE_TYPE == False:
            if len(l) == self.rootObject.roots[2][1]:
                self._holding = l
        elif self.rootChecker.FORCE_LENGTH == False and self.rootChecker.FORCE_TYPE == True:
            for index in l:
                    if type(index) == type(self.rootChecker.DICT_TYPE_HANDLER_USEAGE):
                        self._holding.append(index)
                    else:
                        self._holding.append(None)
                        self.rootObject.roots[6][1] = True
                        print("Array Switced to MODE_UNSAFE as BArray Encounted Unexpected Value While Parsing")
        elif self.rootChecker.FORCE_LENGTH == False and self.rootChecker.FORCE_TYPE == False:
            for index in l:
                self._holding.append(index)
    
    def __setHoldingSingle(self, l, index) -> None:
        if self.rootChecker.FORCE_LENGTH == True and self.rootChecker.FORCE_TYPE == True:
            if type(l) != type(self.rootChecker.DICT_TYPE_HANDLER_USEAGE):
                print("Not Valid")
                pass
            if self._holding[-1] != None and (self.rootChecker.LENGTH != 0):
                
                if (len(self._holding) == self.rootChecker.LENGTH):
                    print("Deleting Last Index to Conserve CURR_LENGTH")
                    self._holding.pop(-1)
                else: 
                    pass
                if index == -1:
                    self._holding.append(l)
                else:
                    self._holding.insert(index, l)
            elif self._holding[-1] == None:
                self._holding.pop(-1)
                if index == -1:
                    self._holding.append(l)
                else:
                    self._holding.insert(index, l)
        elif self.rootChecker.FORCE_LENGTH == True and self.rootChecker.FORCE_TYPE == False:
            if self._holding[-1] != None and (self.rootChecker.LENGTH != 0):
                if (len(self._holding) == self.rootChecker.LENGTH):
                    print("Deleting Last Index to Conserve CURR_LENGTH")
                    self._holding.pop(-1)
                else: 
                    pass
                if index == -1:
                    self._holding.append(l)
                else:
                    self._holding.insert(l, index)
            elif self._holding[-1] == None:
                self._holding.pop(-1)
                if index == -1:
                    self._holding.append(l)
                else:
                    self._holding.insert(index, l)
        elif self.rootChecker.FORCE_LENGTH == False and self.rootChecker.FORCE_TYPE == True:
            if type(l) != type(self.rootChecker.DICT_TYPE_HANDLER_USEAGE):
                print("Not Valid")
                pass
            if index == -1:
                self._holding.append(l)
            else:
                self._holding.insert(index, l)
        elif self.rootChecker.FORCE_LENGTH == False and self.rootChecker.FORCE_TYPE == False:
            if index == -1:
                self._holding.append(l)
            else:
                self._holding.insert(index, l)

    def __update(self, rootName, rootValue) -> None:
        self.rootObject.setRoot(rootName, rootValue)
        self.rootChecker.setUpChecker()
   
    def update_EXP(self, rootName, rootValue) -> None:
        print(
            "Use of this Method has switched the BArray to Experimental Mode. This can cause unsafe activity."
            " To disable this warnning flag the disable_warning function for this array."
            )
        self.__update("Experimental", True)
        self.__update(rootName, rootValue)

    def type(self, type: str) -> None:
        self.__update("Type", type)
        self.__update("FORCE_TYPE", False)
        self.__update("DICT_TYPE_HANDLER_USEAGE", self._refference.get(self.rootObject.roots[1][1]))
