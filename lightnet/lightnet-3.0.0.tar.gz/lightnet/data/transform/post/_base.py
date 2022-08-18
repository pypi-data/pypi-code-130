#
#   Base multiscale getboxes class
#   Copyright EAVISE
#
import inspect
from collections import OrderedDict
from itertools import zip_longest
import torch


class MultiScale:
    """ Transform an existing post-processing GetBoxes class into a MultiScale variant.

    This function is probably unnecessarily complex, but allows me to create MultiScale getBoxes with less code.
    Basically, it allows me to call forward with multiple outputs (`output` is thus a list/tuple of tensors),
    and it will call forward on all of these tensors individually and merge the results.

    The complication lies in the fact that some arguments which are passed upon initialization,
    need to change for each of the forward calls.
    This class thus allows a user to pass in a list of values for each of these "multiscale" arguments,
    and this class will make sure the correct value is set each time before calling forward on one of the tensors. |br|
    Furthermore, this class has a few functions that allow to modify that behaviour according to the specific use case.

    Understanding the text above is probably more than enough to use these `GetMultiScaleBoxes` classes,
    but feel free to look at the code if you want to implement it yourself.
    """
    GETBOXES = None         #: Reference to the original GetBoxes class
    MULTISCALE_ARGS = ()    #: Name of the arguments that should be considered "multiscale"

    def __init__(self, *args, **kwargs):
        # Convert args to kwargs
        arguments = OrderedDict()
        if len(args) > 0:
            args = list(args)
            lenargs = len(args)
            sig = inspect.signature(self.GETBOXES.__init__)

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

        # Call transform init
        self.GETBOXES.__init__(self, *arguments.values(), *args, **kwargs)

        # Create dictionaries for each multiscale setup
        self.__multiscale_args = tuple(self._postprocess_multiscale_arg(ms, i) for i, ms in enumerate(ms_args))

    def forward(self, output):
        """ Runs the original forward method on each of the output tensors, whilst simply copying over the args and kwargs. |br|
        Any value that is dependent on the index of the output tensor should be implemented as a multiscale initialization argument instead of kwarg.
        """
        outputs = []
        for i, out in enumerate(output):
            for name, value in self.__multiscale_args[i].items():
                setattr(self, name, value)

            outputs.append(self.GETBOXES.forward(self, out))

        return self._combine_outputs(outputs)

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

    def _combine_outputs(self, outputs):
        """ Method that is run on the outputs from the different forward calls and should combine the different data.

        Args:
            outputs (list<any>): List containing the various outputs of the different forward calls.

        Returns:
            Combined outputs

        .. rubric:: Default:

        >>> return torch.cat(outputs, 0)
        """
        return torch.cat(outputs, 0)
