#
#   Learning Rate Scheduling
#   Copyright EAVISE
#
from collections import Iterable
import itertools
import torch
import logging

__all__ = ['SchedulerCompositor', 'MultiLRScheduler']
log = logging.getLogger(__name__)


def SchedulerCompositor(*args, last_epoch=-1):
    log.deprecated('SchedulerCompositor is deprecated for the new MultiLRScheduler')
    epoch, sched = zip(*args)
    return MultiLRScheduler(sched, epoch[1:], True, last_epoch)


class MultiLRScheduler:
    """ This class can be used to schedule schedulers to run at different moments on the same parameters of a network. |br|
    This compositor has a notion of count values. These can be batch number, epoch number, etc. and dictate when each scheduler is being used.

    Args:
        schedulers (list): List of the schedulers to use during training
        epochs (list): List of values at which to switch to another scheduler
        cumulative (bool, optional): Whether to cumulatively keep the `epoch` for each individual scheduler (see Note); Default **False**
        last_epoch (int): The index of last epoch; Default **-1**

    Example:
        >>> class DummyScheduler:
        ...     " Dummy scheduler that does nothing but print it's id value. "
        ...     def __init__(self, id_value):
        ...         self.id = id_value;
        ...     def step(self):
        ...         print(f'{self.last_epoch} - Dummy Scheduler: {self.id}')
        >>> s = ln.engine.MultiLRScheduler(
        ...     [DummyScheduler('start'), DummyScheduler('middle'), DummyScheduler('end')],
        ...     [3, 6]
        ... )
        >>> for _ in range(7):
        ...     s.step()
        1 - Dummy Scheduler: start
        2 - Dummy Scheduler: start
        3 - Dummy Scheduler: middle
        4 - Dummy Scheduler: middle
        5 - Dummy Scheduler: middle
        6 - Dummy Scheduler: end
        7 - Dummy Scheduler: end
    """
    def __init__(self, schedulers, epochs, cumulative=False, last_epoch=-1):
        self.last_epoch = last_epoch
        self.schedulers = schedulers
        self.epochs = epochs if isinstance(epochs, Iterable) else [epochs]

        if isinstance(cumulative, bool):
            self.cumulative = [cumulative] * len(self.schedulers)
        else:
            self.cumulative = cumulative

        if len(self.schedulers) < len(self.epochs) - 1:
            raise ValueError("Need at least {} schedulers according to 'epochs', but only {} are given".format(
                len(self.epochs) + 1,
                len(self.schedulers),
            ))
        if len(self.schedulers) > len(self.cumulative):
            raise ValueError("Need at least {} 'cumulative' values, but only {} are given".format(
                len(self.schedulers),
                len(self.cumulative),
            ))
        if not all(e1 < e2 for e1, e2 in zip(self.epochs, self.epochs[1:])):
            raise ValueError("'epoch' values need to be strictly increasing")

        # First scheduler should be used for LR of first epoch
        if self.last_epoch == -1:
            self.schedulers[0].last_epoch = -1
            self.schedulers[0]._step_count = 0
            self.schedulers[0].step()
            self.last_epoch = 0

    def step(self, epoch=None, **kwargs):
        if epoch is not None:
            raise ValueError('The MultiLRScheduler does not work with the deprecated epoch parameter')

        # Get Scheduler
        idx = self._get_idx()
        sched = self.schedulers[idx]

        # Set last_epoch
        # NOTE: Schedulers automatically increase last_epoch in step, so pass in previous value
        if self.cumulative[idx] or idx == 0:
            sched.last_epoch = self.last_epoch
        else:
            sched.last_epoch = self.last_epoch - self.epochs[idx-1]

        # Step
        sched.step(**kwargs)
        self.last_epoch += 1

    def _get_idx(self):
        for i, e in enumerate(self.epochs):
            if self.last_epoch < e:
                break
            else:
                i += 1

        return i

    def __repr__(self):
        format_string = self.__class__.__name__ + ' ['

        clen = max(len(str(c)) for c in self.epochs)
        for i, e in enumerate(itertools.chain([0], self.epochs)):
            if i >= len(self.schedulers):
                break

            name = getattr(self.schedulers[i], '__name__', self.schedulers[i].__class__.__name__)
            format_string += f'\n  {e:>{clen}}:  {name}'

        format_string += '\n]'
        return format_string

    def get_last_lr(self):
        return self.schedulers[self._get_idx()].get_last_lr()

    @property
    def optimizer(self):
        return self.schedulers[self._get_idx()].optimizer

    def state_dict(self):
        state_dict = {key: value for key, value in self.__dict__.items() if key != 'schedulers'}
        state_dict['schedulers'] = [s.state_dict() for s in self.schedulers]
        return state_dict

    def load_state_dict(self, state_dict):
        schedulers = state_dict.pop('schedulers')
        [self.schedulers[i].load_state_dict(s) for i, s in enumerate(schedulers)]
        self.__dict__.update(state_dict)

    def to(self, device):
        """ Cast schedulers to a certain device.

        Args:
            device (torch.device): Device to cast the scheduler to.
        """
        for sched in self.schedulers:
            for param in sched.__dict__.values():
                if isinstance(param, torch.Tensor):
                    param.data = param.data.to(device)
                    if param._grad is not None:
                        param._grad.data = param._grad.data.to(device)
