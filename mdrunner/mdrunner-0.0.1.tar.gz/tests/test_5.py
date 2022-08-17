import importlib
from src.mdrunner import Runner
from tests.models import ModelType
import numpy as np


class Test_5:

    def test_models(self):
        ''' Register and run models '''

        # configure models to run
        all_models = importlib.import_module('tests.models')
        selected_models = ['In2', 'A1', 'B1']
        runner = Runner(all_models, selected_models)

        # feed models with external inputs
        p1 = np.array([1.0, 2.0, 3.0])
        p2 = np.array([4.0, 5.0, 6.0])
        p3 = np.array([7.0, 8.0, 9.0])
        values = {'p1': p1, 'p2': p2, 'p3': p3}

        runner.add(values, ModelType.In)

        # run models
        runner.run_models()

        # check results
        # x = p1 * p2
        assert np.array_equal(runner.A.x, np.array([4, 10, 18]))
        # y = p1 * p3
        assert np.array_equal(runner.B.x, np.array([28.0, 80, 162.0]))
