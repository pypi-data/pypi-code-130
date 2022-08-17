from .model_protected import ModelProtected
from typing import List, Dict


class Model(ModelProtected):
    """Model base class, end user part
    The instantiation and execution of the models are governed by a Runner class.
    Models are defined by a model_type and a model_class_name that contains the calculations
    """

    # A user defined ModelType needs to be defined for each instantiated model
    model_type = None

    def init(self):
        """Override this function to register needed input models
        for the calculations. This function is called by the Runner
        """
        raise NotImplementedError(
            f"Please implemented method 'def init(self):' in '{self.name}'")

    def run(self):
        """In each model override this function to do the actual model calculations
        This function is called by the Runner
        """
        raise NotImplementedError(
            f"Please implemented method 'def run(self):' in '{self.name}'")

    def __init__(self, model_runner: 'Runner'):
        super().__init__(model_runner)

    def get(self, source_model_type: 'ModelType'):
        """Request input from a <source_model> that <this_model> needs data from
           <source_model> --> <this_model>"""
        self._register_input_from(source_model_type)

    def push(self, target_model_type: 'ModelType'):
        """<this_model> wants to push itself to a <target_model>
           <this_model> --> <target_model>
        Tell the <target_model> our intentions"""
        # <target model>
        target_model = self._model_runner._get_model(target_model_type)

        # <this model>
        this_model_type = self.model_type
        this_model_instance = self

        # let the <target_model> know that we will push our model to them
        target_model._register_model_pushed_to_us(this_model_type, this_model_instance)

    def add(self, name: str, val: any):
        """add a (name, value) pair to this model"""

        if not isinstance(name, str):
            raise ValueError(f"parameter name '{name}' must be a str in model '{self.__class__.__name__}'")

        if '.' in name:
            raise ValueError(f"'.' character not allowed in parameter '{name}' in model '{self.__class__.__name__}'")

        # add in a dict
        if name in self._params:
            raise ValueError(f"parameter '{name}' already exist as param in model '{self.name}'")
        else:
            self._params[name] = val

        # add as class attribute for easy access
        if name in dir(self):
            raise ValueError(f"parameter '{name}' already exist as model attribute in model '{self.name}'")
        else:
            setattr(self, name, val)

    @property
    def type(self) -> 'ModelType':
        return self.model_type

    @property
    def name(self) -> str:
        """return the class name of this instance"""
        return type(self).__name__

    @property
    def models(self) -> List['Model']:
        """Return a list of models that is connected to this model"""
        models = []
        for model_name, model in self._input_models.items():
            models.append(model)
        return models

    @property
    def pushed_models(self) -> List['Model']:
        """Return a list of models that is pushed to this model"""
        models = []
        for model_name, model in self._models_pushed_to_us.items():
            models.append(model)
        return models

    @property
    def params(self) -> Dict[str, any]:
        """Returns a dict with this model parameters.
        { 'model_type.param_name' : value }  of type (str:any)"""
        params = {}
        for param_name, param_val in self._params.items():
            params[f"{self.type.name}.{param_name}"] = param_val
        return params

    @property
    def pushed_params(self) -> Dict[str, any]:
        """Returns a dict with the parameters that was pushed as input to this model.
        { 'model_type.param_name' : value }  of type (str:any)"""
        pushed_params = {}
        for model in self.pushed_models:
            pushed_params.update(model.params)
        return pushed_params

    def __repr__(self):
        return f"Model(name='{self.name}', type='{self.type}', params={self._params})"
