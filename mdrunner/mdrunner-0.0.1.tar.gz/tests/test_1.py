import importlib
from src.mdrunner import Runner
from tests.models import ModelType


class Test_1:

    def test_models(self):
        ''' Register and run models '''

        # configure models to run
        all_models = importlib.import_module('tests.models')
        selected_models = ['In1']
        runner = Runner(all_models, selected_models)

        # feed models with external inputs
        values = {'p1': 2.0, 'p2': 3.0}
        runner.add(values, ModelType.In)

        # run models
        runner.run_models()

        # check result
        assert runner.params == {'In.p1': 2.0, 'In.x': 6.0, 'In.p2': 3.0}

        # get individual values
        assert runner.In.p1 == 2.0
