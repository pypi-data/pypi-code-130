import collections
import unittest
import torch
from irisml.tasks.train.build_optimizer import OptimizerFactory


class TestBuildOptimizer(unittest.TestCase):
    def test_create(self):
        self._check_build_optimizer('sgd', 0.001)
        self._check_build_optimizer('adam', 0.001)
        self._check_build_optimizer('amsgrad', 0.001)
        self._check_build_optimizer('adamw', 0.001)
        self._check_build_optimizer('adamw_amsgrad', 0.001)
        self._check_build_optimizer('rmsprop', 0.001)

    def test_no_weight_decay_param_names(self):
        model = torch.nn.Conv2d(3, 3, 3)

        factory = OptimizerFactory('sgd', 0.001, weight_decay=0.1, no_weight_decay_param_names=['.*bias'])
        optimizer = factory(model)
        w = collections.defaultdict(list)
        for group in optimizer.param_groups:
            w[group['weight_decay']].extend(group['params'])

        self.assertEqual(w, {0.1: [model.weight], 0.0: [model.bias]})

    def test_no_weight_decay_module_class_names(self):
        model = torch.nn.Sequential(torch.nn.Conv2d(3, 3, 3), torch.nn.BatchNorm2d(3))

        factory = OptimizerFactory('sgd', 0.001, weight_decay=0.1, no_weight_decay_module_class_names=['BatchNorm2d'])
        optimizer = factory(model)
        w = collections.defaultdict(list)
        for group in optimizer.param_groups:
            w[group['weight_decay']].extend(group['params'])

        self.assertEqual(w, {0.1: [model[0].weight, model[0].bias], 0.0: [model[1].weight, model[1].bias]})

    def _check_build_optimizer(self, *args):
        module = torch.nn.Conv2d(3, 3, 3)
        factory = OptimizerFactory(*args)
        optimizer = factory(module)
        self.assertIsInstance(optimizer, torch.optim.Optimizer)
