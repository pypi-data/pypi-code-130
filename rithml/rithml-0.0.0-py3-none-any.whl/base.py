'''
Contains base model class from which all other model classes inherit.
'''

from copy import deepcopy

class BaseModel():
    '''
    Class for the base model from which all other model classes inherit.
            
    Methods:
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''

    def __init__(self, **params):
        '''
        Creates a base model object.
        
        Parameters:
            **params : dict
                Model parameters.
        '''

        self._init_params = params
        
        # Set parameters as attributes
        for k in params.keys():
            setattr(self, k, params[k])
        
    def get_params(self, deep=True):
        '''
        Gets `__init__` parameter names and corresponding arguments.

        Parameters:
            deep : bool, default True
                If True, return parameter dictionary as a deep copy.
                Otherwise, return a shallow copy.
        
        Returns:
            params : dict
                Dictionary of `__init__` parameter names (keys) and
                corresponding arguments (values).
        '''

        # Obtain copy of `__init__` parameters (deep or shallow)
        params = (deepcopy(self._init_params) 
            if deep else self._init_params.copy())

        return params
    
    def set_params(self, **params):
        '''
        Sets the specified `__init__` parameters to the specified
        values.

        Parameters:
            params : dict
                Model parameters, i.e. dictionary of `__init__`
                parameter names (keys) and corresponding arguments
                (values).
        
        Returns:
            self : (depends)
                Model object.
        '''

        # Obtain valid parameter names
        keys = self._init_params.keys()

        for k in params.keys():
            # Check if parameter name is invalid
            if k not in keys:
                raise ValueError(f'{k} is not a valid parameter name. See \
valid parameter names with `model.get_params().keys()`, where `model` refers \
to the model object.')
            else:
                # Set parameter as attribute
                setattr(self, k, params[k])
                self._init_params[k] = params[k]

        return self