from .evaluation import classification

import sys
from functools import wraps
import pandas


 
class TrainScenario:
    def __init__(self, *args, **kwargs): # args: (, ), kwargs: {objective='for equip'}
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def trigger(*args, **kwargs): # args: (model,) kwargs: {}
            model = func(*args, **kwargs)
            return model
        return trigger


class Trigger:
    def __init__(self, model):
        self.__model__ = model

    def __call__(self, train, validation, inference, predict=lambda x:x, predict_proba=lambda x:x, fit=lambda x:x, target=list(), refresh=False, save=False):
        assert isinstance(train, pandas.DataFrame)
        assert isinstance(validation, pandas.DataFrame)
        assert isinstance(inference, pandas.DataFrame)
        assert isinstance(target, (str, tuple, list))
        assert callable(predict), 'The predict object is Not Callable. It must be type of callable object.'
        assert callable(predict_proba), 'The predict_proba object is Not Callable. It must be type of callable object.'
        assert callable(fit), 'The fit object is Not Callable. It must be type of callable object.'
        assert isinstance(refresh, bool)
        assert isinstance(save, (bool, str))
        
        return self

    def cls_trigger(self, train, validation, inference, predict=lambda x:x, predict_proba=lambda x:x, fit=lambda x:x, target=list(), refresh=False, save=False):
        assert isinstance(train, pandas.DataFrame)
        assert isinstance(validation, pandas.DataFrame)
        assert isinstance(inference, pandas.DataFrame)
        assert isinstance(target, (str, tuple, list))
        assert callable(predict), 'The predict object is Not Callable. It must be type of callable object.'
        assert callable(predict_proba), 'The predict_proba object is Not Callable. It must be type of callable object.'
        assert callable(fit), 'The fit object is Not Callable. It must be type of callable object.'
        assert isinstance(refresh, bool)
        assert isinstance(save, (bool, str))

        return self

    def reg_trigger(self, train, validation, inference, predict=lambda x:x, predict_proba=lambda x:x, fit=lambda x:x, target=list(), refresh=False, save=False):
        assert isinstance(train, pandas.DataFrame)
        assert isinstance(validation, pandas.DataFrame)
        assert isinstance(inference, pandas.DataFrame)
        assert isinstance(target, (str, tuple, list))
        assert callable(predict), 'The predict object is Not Callable. It must be type of callable object.'
        assert callable(predict_proba), 'The predict_proba object is Not Callable. It must be type of callable object.'
        assert callable(fit), 'The fit object is Not Callable. It must be type of callable object.'
        assert isinstance(refresh, bool)
        assert isinstance(save, (bool, str))

        return self

    @property
    def model(self):
        return self.__model__


@TrainScenario()
def equip(model):
    trigger = Trigger(model)
    setattr(model, 'reg_trigger', reg_trigger)
    setattr(model, 'cls_trigger', cls_trigger)
    return model

