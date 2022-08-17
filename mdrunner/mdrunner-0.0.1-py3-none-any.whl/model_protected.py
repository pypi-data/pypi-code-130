
class ModelProtected:
    """Model base class, internal part
    The instantiation and execution of the models are governed by a Runner class.
    Models are defined by a model_type and a model_class_name that contains the calculations
    """

    def __init__(self, model_runner: 'Runner'):

        '''The parent class that instantiated this model'''
        self._model_runner = model_runner

        '''models being pushed to us from other models by a call to
            <other_model>.push(<this_model>)
        '''
        self._models_pushed_to_us = {}

        '''All input models connected to this model
        including our requested models and models pushed to us
        '''
        self._input_models = {}

        '''Registered param
        example: { 'name' : param(name='name'), ... }
        '''
        self._params = {}

    def _init(self):
        ''' Register the dependencies between models '''
        # Let the user model register the models they need params from
        # and the models they want to push data to
        self.init()

    def _register_input_from(self, source_model_type: 'ModelType'):
        """Request input from a <source_model> that <this_model> needs data from
           <source_model> --> <this_model>
        """
        # <source_model>
        source_model = self._model_runner._get_model(source_model_type)

        # add to dict
        self._input_models[source_model_type] = source_model
        # add as class attribute for easy access
        setattr(self, source_model_type.name, source_model)

    def _run(self):
        """This function is called prior to the run model to make sure
        preprocessing is handled before run can exectute
        This function is called by the Runner
        """
        # now we can call this models run method
        self.run()

    def _register_model_pushed_to_us(self, model_type: 'ModelType', model_instance: 'Model'):
        '''
        A model will be pushing param to us by a call to
            <other_model>.push( <this_model> )

        Register this request
        '''
        self._models_pushed_to_us[model_type] = model_instance
        self._register_input_from(model_type)

    def _get_model_dependency_depth(self, loops: int = 0) -> int:
        """
        Find the level of input models this model is depending on
        Example: Find the max level for the following models
            modelA --> modelB --> modelC
                   --> modelD
        gives
            modelA = 0
            modelB = 1
            modelC = 2
            modelD = 1

        This is used for knowing the execution order of each model
        so each model has the needed input before execution

        The max number of loops without circular dependency if every models is referring to all previous models
        The first model does not refer to any model
        n = models
        i = models that can depends on other models = n - 1
        max dependencies = i(i+1)/2 = (n-1)(n-1+1)/2 = (n-1)n/2
        example A -> B,  A,B -> C, A,B,C -> D
        total num of dependencies = 1+2+3+ ... + (n-1) = (n-1)n/2
        """
        depth = [0]
        n = self._model_runner._numof_created_models
        i = n - 1
        max_loop = (n - 1) * n / 2
        for model_name, model_instance in self._input_models.items():
            loops += 1
            if loops > max_loop:
                raise KeyError(
                    f'(ModelType.{self.model_type.name}, {self.name}):'
                    f'found circular dependency between models, '
                    f'max {max_loop} '
                    f'dependencies allowed for {n} models')
            child_depth = model_instance._get_model_dependency_depth(loops) + 1
            depth.append(child_depth)
        return max(depth)
