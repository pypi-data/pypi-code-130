#
#   Base Loss Modules
#   Copyright EAVISE
#
import logging
import inspect
from collections import OrderedDict
from itertools import groupby, zip_longest
import torch
import torch.nn as nn

__all__ = ['Loss', 'MultiScale']
log = logging.getLogger(__name__)


class Loss(nn.Module):
    """ Base Lightnet loss module """
    ENABLE_REDUCTION = False
    VALUES = ()

    def __init__(self):
        super().__init__()

        self._reduction = self.ENABLE_REDUCTION
        for name in self.VALUES:
            setattr(self, f'loss_{name}', torch.tensor(0.0))

    def __call__(self, *args, **kwargs):
        ret = super().__call__(*args, **kwargs)
        if self._reduction:
            ret = self.reduce(ret)
        return ret

    @property
    def values(self):
        """ Return detached sub-losses in a dictionary.

        Note:
            You can access the individual loss values directly as ``object.loss_<name>`` as well. |br|
            This will return the actual ModuleModuletensor with its attached computational graph and gives you full freedom for modifying this loss prior to the backward pass.
        """
        return {name: getattr(self, f'loss_{name}').detach() for name in self.VALUES}

    @property
    def reduction(self):
        if not self.ENABLE_REDUCTION:
            raise TypeError('This loss function does not support reduction')
        return self._reduction

    @reduction.setter
    def reduction(self, value):
        if not self.ENABLE_REDUCTION:
            raise TypeError('This loss function does not support reduction')

        if self._reduction != value:
            self._reduction = value
            self.reduction_updated()

    def reduction_updated(self):
        pass

    def reduce(self, return_value):
        for name in self.VALUES:
            value = getattr(self, f'loss_{name}')
            if isinstance(value, torch.Tensor) and value.ndim > 0:
                setattr(self, f'loss_{name}', value.mean())

        if isinstance(return_value, torch.Tensor) and return_value.ndim > 0:
            return_value = return_value.mean()
        return return_value


class MultiScale:
    """ Transform an existing :class:`lightnet.network.loss._base.Loss` into a MultiScale variant. """
    LOSS = None
    MULTISCALE_ARGS = ()
    MULTI_OUTPUT = False

    def __init__(self, *args, **kwargs):
        # Convert args to kwargs
        arguments = OrderedDict()
        if len(args) > 0:
            args = list(args)
            lenargs = len(args)
            sig = inspect.signature(self.LOSS.__init__)

            # Loop through parameters, but skip first "self" argument
            it = iter(sig.parameters.items())
            next(it)
            for name, param in it:
                if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
                    arguments[name] = args.pop(0)
                elif param.kind == param.VAR_POSITIONAL:
                    break
                else:
                    raise TypeError(f'{self.__class__.__name__}.__init__() takes {lenargs-len(args)} positional arguments but {lenargs} were given')

                if len(args) == 0:
                    break

        # Setup MultiScale Arguments
        ms_args = {}
        for name in self.MULTISCALE_ARGS:
            if name in arguments:
                ms_args[name] = arguments[name]
            elif name in kwargs:
                ms_args[name] = kwargs[name]
            else:
                raise TypeError(f'MultiScale variable [{name}] is a required value!')

        ms_args = self._setup_multiscale_args(ms_args)

        for name, value in ms_args[0].items():
            if name in arguments:
                arguments[name] = value
            elif name in kwargs:
                kwargs[name] = value

        # Call loss init
        self.LOSS.__init__(self, *arguments.values(), *args, **kwargs)

        # Create dictionaries for each multiscale setup
        self.__multiscale_args = tuple(self._postprocess_multiscale_arg(ms, i) for i, ms in enumerate(ms_args))

    def forward(self, output, target, **kwargs):
        losses = {name: 0 for name in self.VALUES}
        total = 0
        kwargs = self._setup_forward_kwargs(output, target, kwargs)

        # Run loss at different scales and sum resulting loss values
        for i, out in enumerate(self.__output_generator(output)):
            for name, value in self.__multiscale_args[i].items():
                setattr(self, name, value)

            total += self.LOSS.forward(self, out, target, **kwargs)

            for name in self.VALUES:
                losses[name] += getattr(self, f'loss_{name}')

        # Overwrite loss values with avg
        for name, value in losses.items():
            setattr(self, f'loss_{name}', value / i)

        return total / i

    def _get_device(self, output):
        """ Get the device from the output tensor or list. """
        try:
            while not isinstance(output, torch.Tensor):
                output = output[0]
            return output.device
        except BaseException:
            log.error('Could not get device from output tensor, defaulting to cpu')
            return torch.device('cpu')

    @staticmethod
    def _setup_multiscale_args(ms_args):
        """ Transforms a dictionary of Iterables into a tuple of dicts. |br|
        If one of the multiscale arguments does not contain enough values, we pad it with **None** values.
        """
        return tuple(dict(zip(ms_args, val)) for val in zip_longest(*ms_args.values()))

    def _postprocess_multiscale_arg(self, multiscale_arg, idx):
        """ Postprocess the multiscale argument dictionaries. |br|
        This function gets called multiple times for each of the multiscale entries.

        The reason for this function is that :func:`~MultiScale._setup_multiscale_args`
        is a staticmethod called before the init function and thus does not have access to any other init variables. |br|
        This function gets called after the original init function and can thus modify the multiscale arguments and look at other values.

        Args:
            multiscale_arg (dict): values that will be set to the object with :func:`setattr` before each of the multiscale forward passes
            idx (int): Index of the output on which these values will be used

        Returns:
            dict: Modified multiscale_arg dict for that particular pass

        .. rubric:: Default:

        >>> return multiscale_arg
        """
        return multiscale_arg

    def _setup_forward_kwargs(self, output, target, kwargs):
        """ Modify keyword arguments for the forward passes of the loss at each scale.

        Args:
            output: Output argument passed to the loss
            target: Target argument passed to the loss
            kwargs: Extra keyword arguments passed to the loss

        Returns:
            dict: New keyword arguments to pass to each scale subloss

        .. rubric:: Default:

        >>> return kwargs
        """
        return kwargs

    def __output_generator(self, output):
        if self.MULTI_OUTPUT:
            if all_equal(len(out) for out in output if isinstance(out, (list, tuple)) and len(out) > 1):
                log.error('This loss function works under the assumption that each output types either has one tensor or the same number of tensors.')
            return zip(*(get_output(out) for out in output))
        else:
            return output


def get_output(out):
    if isinstance(out, (list, tuple)):
        if len(out) == 1:
            return repeat(out[0])
        else:
            return out
    else:
        return repeat(out)


def repeat(value):
    while True:
        yield value


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)
