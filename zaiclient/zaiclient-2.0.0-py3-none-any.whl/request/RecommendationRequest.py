import inspect
import types
from typing import List

class RecommendationRequest(object):
    
    def  __init__(self, limit: int, offset: int, recommendation_type: str, user_id: str = None, item_id: str = None, item_ids: List[str] = None) -> None:
        
        if not (limit >= 1 and limit <= 1_000_000):
            raise ValueError("Limit must be between 1 and 1000,000.")
            
        if not (offset >= 0 and offset <= 1_000_000):
            raise ValueError("Offset must be between 1 and 1000,000.")
            
        if not (len(recommendation_type) >= 1 and len(recommendation_type) <= 100):
            raise ValueError("Length of recommendation type must be between 1 and 100.")
            
        if user_id is not None:
            if not (len(user_id) >= 1 and len(user_id) <= 100):
                raise ValueError("Length of user id must be between 1 and 100.")

        if item_id is not None:
            if not (len(item_id) >= 1 and len(item_id) <= 100):
                raise ValueError("Length of item id must be between 1 and 100.")

        if item_ids is not None:
            if not (len(item_ids) >= 1 and len(item_ids) <= 1_000_000):
                raise ValueError("Length of item_ids must be between 1 and 1000,000.")
            if not all(isinstance(id, str) for id in item_ids):
                raise TypeError("Every element of item ids must be a string value.")
            if not all(len(id) >= 1 and len(id) <= 100 for id in item_ids):
                raise ValueError("Length of item id in item id list must be between 1 and 100.")
        
        self.user_id = user_id
        self.item_id = item_id
        self.item_ids = item_ids
        self.limit = limit
        self.offset = offset
        self.recommendation_type = recommendation_type

    def get_path(self, client_id: str) -> str:
        return ""
    
    def get_limit(self) -> int:
        return self.limit
    
    def get_offset(self) -> int:
        return self.offset

    def get_recommendation_type(self) -> str:
        return self.recommendation_type
    
class MultiMethod:
    '''
    Represents a single multimethod.
    '''
    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        '''
        Register a new method as a multimethod
        '''
        sig = inspect.signature(meth)

        # Build a type-signature from the method's annotations
        types = []
        for name, parm in sig.parameters.items():
            if name == 'self': 
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(
                    'Argument {} must be annotated with a type'.format(name)
                    )
            if not (isinstance(parm.annotation, type) or parm.annotation is None):
                raise TypeError(
                    'Argument {} annotation must be a type'.format(name)
                    )
            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth
            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        '''
        Call a method based on type signature of the arguments
        '''
        types = tuple(type(arg) if arg is not None else None for arg in args[1:])
        meth = self._methods.get(types, None)
        if meth:
            return meth(*args)
        else:
            raise TypeError('No matching method for types {}'.format(types))
        
    def __get__(self, instance, cls):
        '''
        Descriptor method needed to make calls work in a class
        '''
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self
    
class MultiDict(dict):
    '''
    Special dictionary to build multimethods in a metaclass
    '''
    def __setitem__(self, key, value):

        if key in self:
            # If key already exists, it must be a multimethod or callable
            current_value = self[key]
            if isinstance(current_value, MultiMethod):
                current_value.register(value)
            else:
                mvalue = MultiMethod(key)
                mvalue.register(current_value)
                mvalue.register(value)
                super().__setitem__(key, mvalue)
        else:
            super().__setitem__(key, value)

class MultipleMeta(type):
    '''
    Metaclass that allows multiple dispatch of methods
    '''
    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()