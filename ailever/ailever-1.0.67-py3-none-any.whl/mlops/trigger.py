from .evaluation import classification

from functools import wraps
import pandas



 
def integrated_trigger(train, validation, inference, target='target', refresh=False, save=False):
    assert isinstance(train, pandas.DataFrame)
    assert isinstance(validation, pandas.DataFrame)
    assert isinstance(inference, pandas.DataFrame)
    assert isinstance(target, (str, tuple, list))
    
    # type casting
    if isinstance(target, str):
        target = [target]
    elif isinstance(target, tuple):
        target = list(target)
    else:
        pass
    
    return None



class Train:
    def __init__(self, *args, **kwargs): # args: (, ), kwargs: {objective='for equip'}
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, func):
        @wraps(func)        
        def wrapper(*args, **kwargs): # args: (model,) kwargs: {}
            model = args[0]
            model = func(*args, **kwargs) 
            print('working')
            return model
        return wrapper
    

@Train(objective='for equip')
def equip(model):
    if sys._getframe(0).f_code.co_name == 'cls_trigger':
        setattr(model, 'cls_trigger', integrated_trigger)
    elif sys._getframe(0).f_code.co_name == 'reg_trigger':
        setattr(model, 'reg_trigger', integrated_trigger)
    else:
        raise NotImplementedError()
    return model
