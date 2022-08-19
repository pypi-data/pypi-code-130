# -*- coding: utf-8 -*-
import math
from typing import Any, List, Optional

import hao
from hao.namespaces import attr, from_args
from tailors.exceptions import TailorsError
from torch.optim.lr_scheduler import CosineAnnealingLR, CosineAnnealingWarmRestarts, OneCycleLR, ReduceLROnPlateau, _LRScheduler

LOGGER = hao.logs.get_logger(__name__)


@from_args(prefix='sched')
class SchedulerConf:
    interval: str = attr(str, default='epoch', choices=('epoch', 'step'))
    monitor: str = attr(str, default='val_loss')


@from_args(prefix='sched')
class ReduceLROnPlateauConf(SchedulerConf):
    mode: str = attr(str, default='min', choices=('min', 'max'))
    factor: float = attr(float, default=0.1)
    patience: int = attr(int, default=1)
    threshold: float = attr(float, default=0.0001)
    threshold_mode: str = attr(str, default='abs', choices=('abs', 'rel'))
    cooldown: int = attr(int, default=1)
    min_lr: float = attr(float, default=0)
    eps: float = attr(float, default=1e-8)
    verbose: bool = attr(bool, default=False, action='store_true')


@from_args(prefix='sched')
class WarmupLRConf(SchedulerConf):
    init_lr: float = attr(float, default=1e-3)
    num_warmup: int = attr(int, default=1)
    warmup_strategy: str = attr(str, default='linear', choices=('cos', 'linear', 'constant'))


class WarmupLR(_LRScheduler):
    """
    https://github.com/lehduong/torch-warmup-lr
    """
    def __init__(self, scheduler, init_lr=1e-3, num_warmup=1, warmup_strategy='linear'):
        self._scheduler = scheduler
        self._init_lr = init_lr
        self._num_warmup = num_warmup
        self._step_count = 0

        self._warmup_strategies = {
            'cos': self._warmup_cos,
            'linear': self._warmup_linear,
            'constant': self._warmup_const,
        }

        self._warmup_strategy = warmup_strategy
        self._warmup_func = self._warmup_strategies.get(warmup_strategy)
        if self._warmup_func is None:
            raise TailorsError(f"Expect warmup_strategy to be one of ['linear', 'cos', 'constant'] but got {warmup_strategy}")

        # save initial learning rate of each param group
        # only useful when each param groups having different learning rate
        self._format_param()

    def __getattr__(self, name):
        return getattr(self._scheduler, name)

    def state_dict(self):
        """Returns the state of the scheduler as a :class:`dict`.
        It contains an entry for every variable in self.__dict__ which
        is not the optimizer.
        """
        wrapper_state_dict = {key: value for key, value in self.__dict__.items() if (key != 'optimizer' and key != '_scheduler')}
        wrapped_state_dict = {key: value for key, value in self._scheduler.__dict__.items() if key != 'optimizer'}
        return {'wrapped': wrapped_state_dict, 'wrapper': wrapper_state_dict}

    def load_state_dict(self, state_dict):
        """Loads the schedulers state.
        Arguments:
            state_dict (dict): scheduler state. Should be an object returned
                from a call to :meth:`state_dict`.
        """
        self.__dict__.update(state_dict['wrapper'])
        self._scheduler.__dict__.update(state_dict['wrapped'])

    def _format_param(self):
        # learning rate of each param group will increase
        # from the min_lr to initial_lr
        for group in self._scheduler.optimizer.param_groups:
            group['warmup_max_lr'] = group['lr']
            group['warmup_initial_lr'] = min(self._init_lr, group['lr'])

    @staticmethod
    def _warmup_cos(start, end, pct):
        cos_out = math.cos(math.pi * pct) + 1
        return end + (start - end) / 2.0 * cos_out

    @staticmethod
    def _warmup_const(start, end, pct):
        return start if pct < 0.9999 else end

    @staticmethod
    def _warmup_linear(start, end, pct):
        return (end - start) * pct + start

    def get_lr(self):
        lrs = []
        step_num = self._step_count
        # warm up learning rate
        if step_num <= self._num_warmup:
            for group in self._scheduler.optimizer.param_groups:
                computed_lr = self._warmup_func(group['warmup_initial_lr'],
                                                group['warmup_max_lr'],
                                                step_num / self._num_warmup)
                lrs.append(computed_lr)
        else:
            lrs = self._scheduler.get_lr()
        return lrs

    def step(self, *args):
        if self._step_count <= self._num_warmup:
            values = self.get_lr()
            for param_group, lr in zip(self._scheduler.optimizer.param_groups, values):
                param_group['lr'] = lr
            self._step_count += 1
        else:
            self._scheduler.step(*args)


@from_args(prefix='sched')
class WarmupReduceLROnPlateauConf(SchedulerConf):
    warmup_steps: int = attr(int, default=1000)
    warmup_delta: float = attr(float, default=0.01)
    mode: str = attr(str, default='min', choices=('min', 'max'))
    factor: float = attr(float, default=0.1)
    patience: int = attr(int, default=1)
    threshold: float = attr(float, default=0.0001)
    threshold_mode: str = attr(str, default='abs', choices=('abs', 'rel'))
    cooldown: int = attr(int, default=1)
    min_lr: float = attr(float, default=0)
    eps: float = attr(float, default=1e-8)
    verbose: bool = attr(bool, default=False, action='store_true')


class WarmupReduceLROnPlateau(ReduceLROnPlateau):
    """
    https://github.com/mlbench/mlbench-core/blob/develop/mlbench_core/lr_scheduler/pytorch/lr.py#L104
    """

    def __init__(self,
                 optimizer,
                 warmup_steps: int,
                 warmup_delta: float,
                 mode='min',
                 factor=0.1,
                 patience=10,
                 threshold=1e-4,
                 threshold_mode='rel',
                 cooldown=0,
                 min_lr=0,
                 eps=1e-8,
                 verbose=False):
        self.warmup_steps = warmup_steps
        self.warmup_delta = warmup_delta
        self._step_count = 0
        super().__init__(
            optimizer,
            mode=mode,
            factor=factor,
            patience=patience,
            threshold=threshold,
            threshold_mode=threshold_mode,
            cooldown=cooldown,
            min_lr=min_lr,
            eps=eps,
            verbose=verbose
        )

    def step(self, metrics: Any, epoch: Optional[int] = ...) -> None:
        self._step_count += 1
        if self._step_count < self.warmup_steps:
            for i, group in enumerate(self.optimizer.param_groups):
                group['lr'] = float(group['lr']) + self.warmup_delta
            self._last_lr = [group['lr'] for group in self.optimizer.param_groups]
        else:
            super().step(metrics, epoch)

    def get_last_lr(self):
        return self._last_lr


@from_args(prefix='sched')
class CosineAnnealingLRConf(SchedulerConf):
    T_max: int = attr(int, required=True, help='Maximum number of iterations')
    eta_min: float = attr(float, default=0, help='Minimum learning rate')
    last_epoch: int = attr(int, default=-1, help='The index of last epoch')
    verbose: bool = attr(bool, default=False, action='store_true')


@from_args(prefix='sched')
class CosineAnnealingWarmRestartsConf(SchedulerConf):
    T_0: int = attr(int, required=True, help='Number of iterations for the first restart')
    T_mult: int = attr(int, default=1, help='A factor increases :math:`T_{i}` after a restart')
    last_epoch: int = attr(int, default=-1, help='The index of last epoch')
    verbose: bool = attr(bool, default=False, action='store_true')


@from_args(prefix='sched')
class OneCycleLRConf(SchedulerConf):
    max_lr: List[float] = attr(list, required=True, help='Upper learning rate boundaries in the cycle for each parameter group')
    total_steps: int = attr(int, default=1, help='The total number of steps in the cycle')
    epochs: int = attr(int, default=1, help='The number of epochs to train for')
    pct_start: float = attr(float, default=0.3, help='The percentage of the cycle (in number of steps) spent increasing the learning rate')
    anneal_strategy: str = attr(str, default='cos', choices=('cos', 'linear'), help='The index of last epoch')
    cycle_momentum: bool = attr(bool, default=True, help='momentum is cycled inversely to learning rate between `base_momentum` and `max_momentum`')
    base_momentum: List[float] = attr(list, default=[0.85], help='Lower momentum boundaries in the cycle for each parameter group')
    max_momentum: List[float] = attr(list, default=[0.85], help='Upper momentum boundaries in the cycle for each parameter group')
    div_factor: float = attr(float, default=25, help='initial_lr = max_lr/div_factor')
    final_div_factor: float = attr(float, default=1e4, help='min_lr = initial_lr/final_div_factor')
    three_phase: bool = attr(bool, default=False, help='use a third phase of the schedule to annihilate the learning rate according to `final_div_factor` instead of modifying the second phase')
    last_epoch: int = attr(int, default=-1, help='The index of last epoch')
    verbose: bool = attr(bool, default=False, action='store_true')


SCHEDULERS = {
    'reduce-on-plateau': (ReduceLROnPlateau, ReduceLROnPlateauConf),
    'warm-reduce-on-plateau': (WarmupReduceLROnPlateau, WarmupReduceLROnPlateauConf),
    'cosine': (CosineAnnealingLR, CosineAnnealingLRConf),
    'cosine-warm': (CosineAnnealingWarmRestarts, CosineAnnealingWarmRestartsConf),
    'one-cycle': (OneCycleLR, OneCycleLRConf),
}


def get(scheduler: str, optimizer, steps_per_epoch: int):
    scheduler, conf_class = SCHEDULERS.get(scheduler)
    scheduler_conf = conf_class()
    params = {
        'optimizer': optimizer,
        'steps_per_epoch': steps_per_epoch,
        'verbose': False,
        **scheduler_conf.to_dict()
    }
    LOGGER.info(f'[scheduler] {scheduler.__name__}')
    LOGGER.info(scheduler_conf)
    return hao.invoker.invoke(scheduler, **params)
