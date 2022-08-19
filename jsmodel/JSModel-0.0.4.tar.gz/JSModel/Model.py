import re
from typing import Iterator, Any, List, Tuple
class ParseModel:
    __slots__=("_obj","json_data",)
    def __init__(self,obj:Any):
        self._obj=obj
        self.json_data=None
    ##get item
    def get(self,key) -> Any:
        return getattr(self._obj,key)
    ## keys function to attract list of items
    def keys(self) -> List[Any]:
        return list(self)
    ### return values of all keys
    def values(self) -> List[Any]:
        return [self[i] for i in self]
    ## return items Iterator
    def items(self) -> Iterator[Tuple[str,Any]]:
        for i in self:
            yield i, self.get(i)
    def __contains__(self, item:Any) -> bool:
        return item in self.keys()
    ## I have to write magic iter in order to get the dictionary of the self
    def __iter__(self) -> Iterator[str]:
        for name in dir(self._obj):
            if not name.startswith('_'):
                yield name
    def data(self,json_data):
        self.json_data=json_data


    def attract_value(self,input_data,v):

        if isinstance(v,list):
            for index,element in enumerate(v):
                if index==0:
                    data=input_data[element]
                else:
                    data=data[element]
            return data
        elif isinstance(v,str):
            return input_data[v]

        else:
            ## pass for now
            pass

    def parse(self,null_value:Any=None,error_if_null:bool=False) ->Iterator[Any]:
        json_build={}
        for json_data in self.json_data:
            for key,value in self.items():
                    try:
                        get_data=self.attract_value(json_data,value)
                        json_build[key]=get_data
                    except (KeyError,TypeError) as e:

                        if error_if_null == False:
                            if null_value==None:
                                json_build[key]="None"
                            else:
                                json_build[key]=null_value
                        elif error_if_null ==True:
                            raise (e)
            yield json_build

