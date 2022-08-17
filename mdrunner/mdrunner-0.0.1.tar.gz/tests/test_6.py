import importlib
from src.mdrunner import Runner, Model
from tests.models import ModelType
from typing import List


class Test_6:

    def test_models(self):
        ''' Register and run models '''

        # configure models to run
        all_models = importlib.import_module('tests.models')
        selected_models = ['Out1', 'B3', 'C3', 'A2', 'In3']
        runner = Runner(all_models, selected_models)

        # feed models with external inputs
        values = {'p1': 2.0, 'p2': 3.0, 'x': 4.0}

        runner.add(values, ModelType.In)

        # run models
        runner.run_models()

        # check run order
        assert [model.type.name for model in runner.model_run_order] == ['In', 'A', 'B', 'C', 'Out']
        assert [model.name for model in runner.model_run_order] == ['In3', 'A2', 'B3', 'C3', 'Out1']

        # check all params
        assert runner.params == {'A.x': 6.0, 'B.x': 10.0, 'C.x': 20.0, 'In.p1': 2.0, 'In.p2': 3.0, 'In.x': 4.0,
                                 'Out.x': 40.0}

        # check input
        assert runner.In.x == 4.0
        self.check_model(
            model=runner.In,
            expected_param_names=['In.p1', 'In.p2', 'In.x'],
            expected_pushed_model_types=[],
            expected_pushed_param_names=[])

        # check A
        assert runner.A.x == 6.0
        self.check_model(
            model=runner.A,
            expected_param_names=['A.x'],
            expected_pushed_model_types=[],
            expected_pushed_param_names=[])

        # check B
        assert runner.B.x == 10.0
        self.check_model(
            model=runner.B,
            expected_param_names=['B.x'],
            expected_pushed_model_types=[],
            expected_pushed_param_names=[])

        # check C
        assert runner.C.x == 20.0
        self.check_model(
            model=runner.C,
            expected_param_names=['C.x'],
            expected_pushed_model_types=[],
            expected_pushed_param_names=[])

        # check output
        assert runner.Out.x == 40.0
        self.check_model(
            model=runner.Out,
            expected_param_names=['Out.x'],
            expected_pushed_model_types=[ModelType.B, ModelType.C, ModelType.A, ModelType.In],
            expected_pushed_param_names=['B.x', 'C.x', 'A.x', 'In.p1', 'In.p2', 'In.x'])

    def check_model(
            self, model: Model,
            expected_param_names: List[str],
            expected_pushed_model_types: List[ModelType],
            expected_pushed_param_names: List[str]
    ):
        param_names = [param_name for param_name, param in model.params.items()]
        assert param_names == expected_param_names

        model_types = [model.type for model in model.pushed_models]
        assert model_types == expected_pushed_model_types

        pushed_param_names = [param_name for param_name, param in model.pushed_params.items()]
        assert pushed_param_names == expected_pushed_param_names
