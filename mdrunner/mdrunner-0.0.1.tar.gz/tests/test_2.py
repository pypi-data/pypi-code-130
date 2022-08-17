import importlib
from src.mdrunner import Runner
from tests.models import ModelType


class Test_2:

    def test_models(self):
        ''' Register and run models '''

        # configure models to run
        all_models = importlib.import_module('tests.models')
        selected_models = ['In2', 'A1', 'B1']
        runner = Runner(all_models, selected_models)

        # feed models with external inputs
        values = {'p1': 2.0, 'p2': 3.0, 'p3': 4.0}
        runner.add(values, ModelType.In)

        # run models
        runner.run_models()

        # check results
        all_params = runner.params
        assert all_params == {'A.x': 6.0,
                              'B.x': 24.0,
                              'In.p1': 2.0,
                              'In.p2': 3.0,
                              'In.p3': 4.0}

        # get individual values
        assert runner.B.x == 24.0
