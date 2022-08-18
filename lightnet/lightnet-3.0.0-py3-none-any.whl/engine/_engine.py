#
#   Base engine class
#   Copyright EAVISE
#
import logging
import signal
from abc import ABCMeta, abstractmethod
from collections import Sequence
from enum import Flag, auto
from functools import wraps, update_wrapper
from itertools import chain
from types import MethodType
import torch
from ._parameter import HyperParameters


__all__ = ['Engine', 'Hook']
log = logging.getLogger(__name__)


class HookType(Flag):
    BATCH_START = auto()
    BATCH_END = auto()
    EPOCH_START = auto()
    EPOCH_END = auto()

    BATCH = BATCH_START | BATCH_END
    EPOCH = EPOCH_START | EPOCH_END

    def __str__(self):
        return self.name.lower()


class Hook:
    NEXT_ID = 0
    TYPES = HookType

    def __init__(self, hook_type, periodicity, fn, *, id=None, engine=None):
        self.type = hook_type
        self.periodicity = periodicity

        if id is None:
            self.id = Hook.NEXT_ID
            Hook.NEXT_ID += 1
        else:
            self.id = id

        if engine is None:
            self.fn = fn
        else:
            self.fn = MethodType(fn, engine)

        update_wrapper(self, self.fn)

    def to_object(self, engine):
        return self.__class__(
            self.type,
            self.periodicity,
            self.fn,
            id=self.id,
            engine=engine,
        )

    def is_active(self, value, type=None):
        if type is not None and self.type not in type:
            return False

        return any(
            (slice.start is None or value >= slice.start)
            and (slice.stop is None or value < slice.stop)
            and (slice.step is None or (value - (slice.start or 0)) % slice.step == 0)
            for slice in self.periodicity
        )

    def __repr__(self):
        return f'<Hook {self.id}: fn={repr(self.fn)}>'

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class HookSetter:
    TYPES = HookType

    def __init__(self, hook_type, engine=None):
        self.type = hook_type
        self.__engine = engine
        self.hooks = {}

    def to_object(self, engine):
        new = self.__class__(self.type, engine)
        new.hooks = {k: v.to_object(engine) for k, v in self.hooks.items()}
        return new

    def copy(self):
        new = self.__class__(self.type, self.__engine)
        new.hooks = {k: v for k, v in self.hooks.items()}
        return new

    def register(self, hook):
        self.hooks[hook.id] = hook

    def remove(self, hook):
        if hook.id not in self.hooks:
            log.warning('Hook not in this HookSetter')
            return
        del self.hooks[hook.id]

    def run_hooks(self, value):
        for hook in self.hooks.values():
            if hook.is_active(value):
                hook()

    def __getitem__(self, *idx):
        # Process indices
        def process_idx(i):
            if isinstance(i, slice):
                return i
            elif isinstance(i, int):
                return slice(i, i+1)
            else:
                raise TypeError(f'Hook indices should be integers or slices, but got {type(i)}')

        if len(idx) == 1 and isinstance(idx[0], Sequence):
            idx = idx[0]
        idx = tuple(process_idx(i) for i in idx)
        del process_idx

        # Return decorator function
        def wrapper(fn):
            hook = Hook(self.type, idx, fn)
            self.register(hook)
            return hook

        return wrapper

    def __call__(self, fn):
        if isinstance(fn, int):
            log.deprecated(f'Calling Engine.{self.type}(number) is deprecated, use Engine.{self.type}[::number]')
            return self[::fn]
        elif callable(fn):
            return self[::1](fn)
        else:
            raise TypeError('HookSetter should be called with a callable object')


class engine_meta(ABCMeta):
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # Keep copy of hooksetters on base class
        if len(bases) > 0:
            bases[-1]._batch_start_copy = bases[-1].batch_start.copy()
            bases[-1]._batch_end_copy = bases[-1].batch_end.copy()
            bases[-1]._epoch_start_copy = bases[-1].epoch_start.copy()
            bases[-1]._epoch_end_copy = bases[-1].epoch_end.copy()

        return super().__prepare__(cls, name, bases, **kwargs)

    def __new__(cls, name, bases, classdict):
        cls = super().__new__(cls, name, bases, classdict)

        # Reset hooksetters of the base class
        if len(bases) > 0:
            cls.batch_start = bases[-1].batch_start
            bases[-1].batch_start = bases[-1]._batch_start_copy
            del bases[-1]._batch_start_copy

            cls.batch_end = bases[-1].batch_end
            bases[-1].batch_end = bases[-1]._batch_end_copy
            del bases[-1]._batch_end_copy

            cls.epoch_start = bases[-1].epoch_start
            bases[-1].epoch_start = bases[-1]._epoch_start_copy
            del bases[-1]._epoch_start_copy

            cls.epoch_end = bases[-1].epoch_end
            bases[-1].epoch_end = bases[-1]._epoch_end_copy
            del bases[-1]._epoch_end_copy

        return cls

    def __call__(self, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)

        # Create bound copies of HookSetter and Hook instances
        obj._hook_setters = {}
        for key in dir(obj):
            value = getattr(obj, key, None)
            if isinstance(value, HookSetter):
                new_value = value.to_object(obj)
                setattr(obj, key, new_value)
                obj._hook_setters[new_value.type] = new_value

        # Update Hook attributes to the bound variants
        for key in dir(obj):
            value = getattr(obj, key, None)
            if isinstance(value, Hook):
                setattr(obj, key, obj._hook_setters[value.type].hooks[value.id])

        return obj


class Engine(metaclass=engine_meta):
    """ This class removes the boilerplate code needed for writing your training cycle. |br|

    .. warning::
       There are already a lot of PyTorch libraries that are created to ease the creation of a training pipeline.

       In order to limit the burden on the Lightnet dev-team, we will stop working on our own engine
       and instead be slowly transitioning towards `PyTorch Lightning <lightning_>`_. |br|
       This transition will be slow and this engine will thus remain in the codebase for quite some time,
       but no further development will be made to this.

       Besides, PyTorch Lightnig offers a ton of extra functionality
       and is being maintained by a much bigger group of people,
       which allows it to stay up-to-date with recent Deep Learning trends much faster!

    Here is the code that runs when the engine is called:

    .. literalinclude:: /../lightnet/engine/_engine.py
       :language: python
       :pyobject: Engine.__call__
       :dedent: 4

    Args:
        params (lightnet.engine.HyperParameters): Serializable hyperparameters for the engine to work with
        dataloader (torch.utils.data.DataLoader, optional): Dataloader for the training data; Default **None**
        **kwargs (dict, optional): Keywords arguments that will be set as attributes of the engine

    Attributes:
        self.params: HyperParameter object
        self.dataloader: Dataloader object
        self.sigint: Boolean value indicating whether a SIGINT (CTRL+C) was send; Default **False**
        self.*: All values that were passed with the init function and all values from the :class:`~lightnet.engine.HyperParameters` can be accessed in this class

    Note:
        This class expects a `self.dataloader` object to be present. |br|
        You can either pass a dataloader when initializing this class, or you can define it yourself.
        This allows to define `self.dataloader` as a computed property (@property) of your class, opening up a number of different possibilities,
        like eg. computing different dataloaders depending on which epoch you are.

    Note:
        This engine allows to define hook functions to run at certain points in the training *(epoch_start, epoch_end, batch_start, batch_end)*.
        These functions should take a single :class:`~lightnet.engine.Engine` argument and return nothing.
        They can be used to store backups, perform validation runs, update (hyper)parameters, log data, etc.

        There are 4 different decorator functions to register a hook.
        An optional square bracket index/slice notation allows you to specify different iteration ranges for the hooks.

        >>> class TrainingEngine(ln.engine.Engine):
        ...     def start(self):
        ...         pass
        ...
        ...     @ln.engine.Engine.epoch_start
        ...     def custom_function_1(self):
        ...         pass    # This method will be executed at the start of every epoch
        ...
        ...     @ln.engine.Engine.epoch_end[::100]
        ...     def custom_function_2(self):
        ...         pass    # This method will be executed at the end of every 100th epoch
        ...
        ...     @ln.engine.Engine.batch_start[100:500:50]
        ...     def custom_function_3(self):
        ...         pass    # This method will be executed at the start of batch 100, 150, 200, ..., 450
        ...
        ...     @ln.engine.Engine.batch_end[500, 1500, 2500]
        ...     def custom_function_4(self):
        ...         pass    # This method will be executed at the end of batch 500, 1500 and 2500
        ...
        ...     @ln.engine.Engine.epoch_end[100, 700::100]
        ...     def custom_function_5(self):
        ...         pass    # This method will be executed at the en of epoch 100 and 700, 800, 900, ...
        ...
        >>> # Create TrainingEngine object and run it
        >>> engine = TrainingEngine(...)    # doctest: +SKIP
        >>> engine()                        # doctest: +SKIP

        You can also call the decorators in code, allowing you to compute the periodicity values. |br|
        Any function can also be hooked, as long as it has the correct signature (1 argument).

        >>> def custom_function_1(engine):
        ...     pass
        ...
        >>> class TrainingEngine(ln.engine.Engine):
        ...     def start(self):
        ...         backup_rate = getattr(self, 'backup_rate', None)
        ...         if backup_rate is not None:
        ...             hook = self.batch_start[::backup_rate](backup)
        ...             # The returned hook can be used to disable it: `self.batch_start.remove(hook)`
        ...             # All hooks can also be found as: `self.batch_start.hooks`
        ...
        >>> @TrainingEngine.epoch_start
        ... def custom_function_2(engine):
        ...     pass    # This function will be executed at the start of every epoch
        ...
        >>> # Create TrainingEngine object and run it
        >>> engine = TrainingEngine(...)    # doctest: +SKIP
        >>> engine()                        # doctest: +SKIP

        Note that the decorator syntax with square brackets only works in python 3.9 or above.
        If you are using an older python version,
        you can use the regular calling syntax or wrap the decorator in an identity function.

        >>> def _(i):
        ...     return i
        ...
        >>> class TrainingEngine(ln.engine.Engine):
        ...     def start(self):
        ...         # Option 1 : Call the decorators manually
        ...         self.custom_function_1 = self.batch_start[::15](self.custom_function_1)
        ...
        ...     def custom_function_1(self):
        ...         pass
        ...
        ...     # Option 2 : Wrap the decorator in an id function
        ...     @_(ln.engine.Engine.epoch_end[:1500:100])
        ...     def custom_function_2(self):
        ...         pass
    """
    __init_done = False
    _required_attr = ['network', 'batch_size', 'dataloader']
    _handled_signals = [signal.SIGINT, signal.SIGTERM]

    epoch_start = HookSetter(HookType.EPOCH_START)
    """ Register a hook to run at the start of an epoch. |br|
    You can specify epoch ranges using square bracket notation.

    Note:
        The `self.epoch` attribute contains the number of processed epochs,
        and will thus be one lower than the epoch you are currently starting.
        For example, when starting training with the very first epoch,
        the `self.epoch` attribute will be set to **0** during any `epoch_start` hook. |br|
        However, the epoch ranges will be computed with the correct number (ic. `self.epoch` + 1).
    """

    epoch_end = HookSetter(HookType.EPOCH_END)
    """ Register a hook to run at the end of an epoch. |br|
    You can specify epoch ranges using square bracket notation.

    Note:
        The `self.epoch` attribute contains the number of processed epochs.
    """

    batch_start = HookSetter(HookType.BATCH_START)
    """ Register a hook to run at the start of a batch. |br|
    You can specify batch ranges using square bracket notation.

    Note:
        The `self.batch` attribute contains the number of processed batches,
        and will thus be one lower than the batch you are currently starting.
        For example, when starting training with the very first batch,
        the `self.batch` attribute will be set to **0** during any `batch_start` hook. |br|
        However, the batch ranges will be computed with the correct number (ic. `self.batch` + 1).
    """

    batch_end = HookSetter(HookType.BATCH_END)
    """ Register a hook to run at the end of a batch. |br|
    You can specify batch ranges using square bracket notation.

    Note:
        The `self.batch` attribute contains the number of processed batches.
    """

    def __init__(self, params, dataloader=None, **kwargs):
        self.params = params
        if dataloader is not None:
            self.dataloader = dataloader

        # Sigint handling
        self.sigint = False
        for sig in self._handled_signals:
            signal.signal(sig, self.__sigint_handler)

        # Set attributes
        for key in kwargs:
            if not hasattr(self, key):
                setattr(self, key, kwargs[key])
            else:
                log.warning('%s attribute already exists on engine.', key)

        self.__init_done = True

    def __call__(self):
        """ Start the training cycle. """
        self.__check_attr()
        self.start()

        log.info('Start training')
        self.network.train()

        idx = 0
        while True:
            # Check if we need to stop training
            if self.quit() or self.sigint:
                log.info('Reached quitting criteria')
                return

            # Epoch Start
            self.epoch_start.run_hooks(self.epoch + 1)

            idx %= self.batch_subdivisions
            loader = self.dataloader
            for idx, data in enumerate(loader, idx+1):      # noqa: B020
                # Batch Start
                if (idx - 1) % self.batch_subdivisions == 0:
                    self.batch_start.run_hooks(self.batch + 1)

                # Forward and backward on (mini-)batches
                self.process_batch(data)
                if idx % self.batch_subdivisions != 0:
                    continue

                # Optimizer step
                self.batch += 1     # Should only be called after train, but this is easier to use self.batch in function
                self.train_batch()

                # Batch End
                self.batch_end.run_hooks(self.batch)

                # Check if we need to stop training
                if self.quit() or self.sigint:
                    log.info('Reached quitting criteria')
                    return

            # Epoch End
            self.epoch += 1
            self.epoch_end.run_hooks(self.epoch)

    def __getattr__(self, name):
        try:
            return getattr(self.params, name)
        except AttributeError as err:
            raise AttributeError(f'{name} attribute does not exist') from err

    def __setattr__(self, name, value):
        if self.__init_done and name not in dir(self) and hasattr(self.params, name):
            setattr(self.params, name, value)
        else:
            super().__setattr__(name, value)

    def __sigint_handler(self, signal, frame):
        if not self.sigint:
            log.debug('SIGINT/SIGTERM caught. Waiting for gracefull exit')
            self.sigint = True

    def __check_attr(self):
        for attr in self._required_attr:
            if not hasattr(self, attr):
                raise AttributeError(f'Engine requires attribute [{attr}] (as an engine or hyperparameter attribute)')

        if not hasattr(self, 'mini_batch_size'):
            log.warning('No [mini_batch_size] attribute found, setting it to [batch_size]')
            self.mini_batch_size = self.batch_size
        elif self.batch_size % self.mini_batch_size != 0 or self.mini_batch_size > self.batch_size:
            raise ValueError('batch_size should be a multiple of mini_batch_size')

    def log(self, msg, *args, **kwargs):
        """ Log messages about training and testing.
        This function will automatically prepend the messages with **TRAIN** or **EVAL**.
        """
        if self.network.training:
            msg = '[TRAIN] ' + msg
        else:
            msg = '[EVAL]  ' + msg
        log.info(msg, *args, **kwargs)

    @staticmethod
    def eval(fn):
        """" Run a function in evaluation mode """
        @wraps(fn)
        def wrapper(self):
            for v in chain(self.__dict__.values(), self.params.values()):
                if not isinstance(v, HyperParameters):
                    train = getattr(v, 'train', None)
                    if callable(train):
                        train(False)

            nograd = getattr(torch, 'inference_mode', torch.no_grad)
            with nograd():
                retval = fn(self)

            for v in chain(self.__dict__.values(), self.params.values()):
                if not isinstance(v, HyperParameters):
                    train = getattr(v, 'train', None)
                    if callable(train):
                        train(True)

            return retval

        return wrapper

    @property
    def batch_subdivisions(self):
        """ Get number of mini-batches per batch.

        Return:
            int: Computed as self.batch_size // self.mini_batch_size
        """
        return self.batch_size // self.mini_batch_size

    def start(self):
        """ First function that gets called when starting the engine. |br|
        Any required setup code can come in here.
        """

    @abstractmethod
    def process_batch(self, data):
        """ This function should contain the code to process the forward and backward pass of one (mini-)batch.

        Args:
            data: The data that comes from your dataloader

        Note:
            If you are working with mini-batches, you should pay attention to how you process your loss and backwards function. |br|
            PyTorch accumulates gradients when performing multiple backward() calls before using your optimizer.
            However, usually your loss function performs some kind of average over your batch-size (eg. reduction='mean' in a lot of default pytorch functions).
            When that is the case, you should also average your losses over the mini-batches, by dividing your resulting loss:

            .. code:: bash

                loss = loss_function(output, target) / self.batch_subdivisions
                loss.backward()
        """

    @abstractmethod
    def train_batch(self):
        """ This function should contain the code to update the weights of the network. |br|
        Things such as computing batch statistics also happen in this method.
        """

    def quit(self):
        """ This function gets called after every training epoch and decides if the training cycle continues.

        Return:
            Boolean: Whether are not to stop the training cycle

        Note:
            This function gets called before checking the ``self.sigint`` attribute.
            This means you can also check this attribute in this function. |br|
            If it evaluates to **True**, you know the program will exit after this function and you can thus
            perform the necessary actions (eg. save last weights).
        """
        return False
