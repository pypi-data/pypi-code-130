from .evaluation import classification as cls_evaluate
from ..logging_system import logger

import sys
from functools import wraps
from copy import deepcopy
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


    def cls_trigger(self, train, validation, inference, predict=lambda x:x, predict_proba=lambda x:x, fit=lambda x:x, target=list(), refresh=False):
        if refresh:
            answer = input('[Caution] Are you really want to refresh the memory of your model during training(y/n)?')
            if answer == 'y':
                logger['mlops'].info('Your model on trigger object lost all memory during training.')
                self.__model__ = self.__history__[0]
                self.__initial_memory__ = True

        assert isinstance(train, pandas.DataFrame)
        assert isinstance(validation, pandas.DataFrame)
        assert isinstance(inference, pandas.DataFrame)
        assert isinstance(target, (str, tuple, list))
        assert callable(predict), 'The predict object is Not Callable. It must be type of callable object.'
        assert callable(predict_proba), 'The predict_proba object is Not Callable. It must be type of callable object.'
        assert callable(fit), 'The fit object is Not Callable. It must be type of callable object.'

        model = deepcopy(self.__model__)
        setattr(model, 'fit', fit)
        setattr(model, 'predict', predict)
        setattr(model, 'predict_proba', predict_proba)

        X_train = train[train.columns[~train.columns.isin(target)]]
        y_train = train[train.columns[train.columns.isin(target)]]
        X_validation = validation[validation.columns[~validation.columns.isin(target)]]
        y_validation = validation[validation.columns[validation.columns.isin(target)]]
        X_test = inference[inference.columns[~inference.columns.isin(target)]]
        y_test = inference[inference.columns[inference.columns.isin(target)]]

        model.fit(X_train, y_train)

        y = dict()
        y['train'] = dict()
        y['validation'] = dict()
        y['test'] = dict()

        evaluation_metrics = list()
        for domain in y.keys():
            _X = locals()['X'+ '_' +domain] # X_train, X_validation, X_test
            _y = locals()['y'+ '_' +domain] # y_train, y_validation, y_test

            y[domain]['true'] = _y
            y[domain]['pred'] = model.predict(_X)
            y[domain]['prob'] = model.predict_proba(_X)

            evaluation_metric = cls_evaluate(y[domain]['true'], y[domain]['pred'], y[domain]['prob']).copy()
            evaluation_metric.insert(0, 'domain', domain)
            evaluation_metrics.append(evaluation_metric)
        evaluation_metrics = pandas.concat(evaluation_metrics, axis=0).reset_index(drop=True)
        evaluation_metrics.insert(0, 'session', deepcopy(self.__count__))
        evaluation_metrics['initial_memory'] = refresh if self.__count__ != 0 else self.__initial_memory__

        self.__count__ += 1
        self.__model__ = model
        self.__history__.append(deepcopy(model))
        self.__evaluation__ = pandas.concat([self.__evaluation__, evaluation_metrics], axis=0) if hasattr(self, '__evaluation__') else evaluation_metrics
        return self


    def reg_trigger(self, train, validation, inference, predict=lambda x:x, predict_proba=lambda x:x, fit=lambda x:x, target=list(), refresh=False):
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

    @property
    def evaluation(self):
        return self.__evaluation__

    @property
    def history(self):
        return self.__history__


@TrainScenario()
def equip(model):
    trigger = Trigger(model)
    return trigger

