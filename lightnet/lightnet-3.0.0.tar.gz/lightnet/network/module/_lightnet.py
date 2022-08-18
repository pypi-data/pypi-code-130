#
#   Base lightnet network module structure
#   Copyright EAVISE
#
import inspect
import logging
import re
from abc import abstractmethod
from collections import OrderedDict, Iterable
from operator import attrgetter
import torch
import torch.nn as nn

from lightnet.network.layer import DeformableConv2d, ModulatedDeformableConv2d

__all__ = ['Lightnet']
log = logging.getLogger(__name__)


class Lightnet(nn.Module):
    """ This class provides an abstraction layer on top of :class:`pytorch:torch.nn.Module`
    and is used as a base for every network implemented in this framework.

    The default initialization will first call :func:`~lightnet.network.module.Lightnet.__init_module`,
    which is meant to initialize all the layers of the network.
    Afterwards, it will loop through :func:`torch.nn.Module.named_modules`
    and call :func:`~lightnet.network.module.Lightnet.__init_weights` on each module, in order to initialize the weights.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.__init_module__(*args, **kwargs)
        with torch.no_grad():
            self.apply(self.__init_weights__)

    @abstractmethod
    def __init_module__(self, *args, **kwargs):
        """ This function should be implemented by subclasses
        and should be used to create all the layers of the network.
        """

    def __init_weights__(self, name, mod):
        """ This method initializes the weights of the network. |br|
        You should return **True** if you successfully initialized the weights of a module, so that we do not recurse into its children.

        The default implementation intializes the following layers:

        - :class:`~torch.nn.Conv2d` |br|
          Weights get initialized with a kaiming_normal distribution in 'fan_out' mode and with 'relu' as the nonlinearity.
          If there is a bias, it gets initialized with a constant value of 0.
        - :class:`~torch.nn.BatchNorm2d`, :class:`~torch.nn.GroupNorm` |br|
          Weights get initialized with a constant value of 1, bias with a constant value of 0.
        - :class:`~torch.nn.Linear` |br|
          Weights get initialized from a normal distribution with mean=0 and std=0.01.
          Biases get initialized with a constant value of 0.
        - :class:`~lightnet.network.layer.DeformableConv2d`, :class:`~lightnet.network.layer.ModulatedDeformableConv2d` |br|
          The regular convolution gets initialized with a kaiming_normal distribution, similarly to a regular 2D convolution.
          The offset/modulation convolution weights get initialized with a constant value of 0.

        Args:
            name (str): name of the layer
            mod (nn.Module): layer module

        Note:
            As a user, you can overwrite this method and set values for some layers.
            Call `return super().__init_weights(name, mod)` add the end of your custom method,
            so that other layers get this default behaviour.
        """
        if isinstance(mod, (DeformableConv2d, ModulatedDeformableConv2d)):
            nn.init.kaiming_normal_(mod.conv.weight, mode='fan_out', nonlinearity='relu')
            if mod.conv.bias is not None:
                nn.init.constant_(mod.conv.bias, 0)

            nn.init.constant_(mod.deformable_module.weight, 0)
            if mod.deformable_module.bias is not None:
                nn.init.constant_(mod.deformable_module.bias, 0)

            return True
        elif isinstance(mod, nn.Conv2d):
            nn.init.kaiming_normal_(mod.weight, mode='fan_out', nonlinearity='relu')
            if mod.bias is not None:
                nn.init.constant_(mod.bias, 0)
            return True
        elif isinstance(mod, (nn.BatchNorm2d, nn.GroupNorm)):
            nn.init.constant_(mod.weight, 1)
            nn.init.constant_(mod.bias, 0)
            return True
        elif isinstance(mod, nn.Linear):
            nn.init.normal_(mod.weight, 0, 0.01)
            nn.init.constant_(mod.bias, 0)
            return True

    def modules(self, types=None, recurse_into_matched=True):
        """ Overload for :func:`torch.nn.Modules.modules` that provides extra features. |br|
        This version of the method allows you to pass in a list of module types for which you are interested.
        Only those modules will be returned from the generator.
        Additionally, you can set `recurse_into_matched` to **False**,
        so that the generator will not yield submodules from previously matched modules.

        Args:
            types (list<class>, optional): List of layers you want to return; Default **return all modules**
            recurse_into_matched (bool, optional): (with types only) Whether to recurse into previously matched layers ; Default **True**

        Yields:
            Module: a module in the network

        Note:
            We use the ``isinstance`` function in order to check whether a module is of a certain type.
            This does mean that if you are looking for :class:`torch.nn.Sequential`, any subclass will also be returned.
        """
        for _, m in self.named_modules(types=types, recurse_into_matched=recurse_into_matched):
            yield m

    def named_modules(self, memo=None, *args, types=None, recurse_into_matched=True, **kwargs):
        """ Overload for :func:`torch.nn.Modules.named_modules` that provides extra features. |br|
        This version of the method allows you to pass in a list of module types for which you are interested.
        Only those modules will be returned from the generator.
        Additionally, you can set `recurse_into_matched` to **False**,
        so that the generator will not yield submodules from previously matched modules.

        Args:
            memo (set, optional): a memo to store the set of modules already added to the result
            args: Extra arguments passed to the underlying named_modules
            types (list<class>, optional): List of layers you want to return; Default **return all modules**
            recurse_into_matched (bool, optional): (with types only) Whether to recurse into previously matched layers ; Default **True**
            kwargs: Extra keyword arguments passed to the underlying named_modules

        Yields:
            tuple<string, Module>: Tuple of name and module

        Note:
            We use the ``isinstance`` function in order to check whether a layer is of a certain type.
            This does mean that if you are looking for :class:`torch.nn.Sequential`, any subclass will also be returned.
        """
        if types is None:
            yield from super().named_modules(memo, *args, **kwargs)
            return

        if memo is None:
            memo = set()
        yield from self.__named_typed_modules(self, tuple(types), recurse_into_matched, memo, *args, **kwargs)

    def __named_typed_modules(self, root, types, recurse_into_matched, memo, prefix='', remove_duplicate=True):
        if root not in memo:
            if remove_duplicate:
                memo.add(root)

            if isinstance(root, types):
                yield prefix, root
                if not recurse_into_matched:
                    return

            for name, module in root._modules.items():
                if module is None:
                    continue
                submodule_prefix = prefix + ('.' if prefix else '') + name
                yield from self.__named_typed_modules(module, types, recurse_into_matched, memo, submodule_prefix, remove_duplicate)

    def apply(self, fn):
        """ Overload for :func:`torch.nn.Module.apply` that provides extra features. |br|
        This method works similarly to :func:`torch.nn.Module.apply`,
        but allows to pass in a function that takes two arguments `fn(name, module)`.
        Additionally, if your function returns **True**, we will not recurse into its children.
        """
        try:
            add_name = len(inspect.signature(fn).parameters) == 2
        except BaseException:
            add_name = False

        if add_name:
            self.__apply_name(self, fn, '')
        else:
            self.__apply(self, fn)

        return self

    def __apply(self, root, fn):
        if fn(root):
            return

        for module in root.children():
            self.__apply(module, fn)

    def __apply_name(self, root, fn, prefix):
        if fn(prefix, root):
            return

        for name, module in root.named_children():
            submodule_prefix = prefix + ('.' if prefix else '') + name
            self.__apply_name(module, fn, submodule_prefix)

    def layer_loop(self, layers, mod=None):
        """ This function will recursively loop over all its child modules,
        and return only the layers, which type you specified through the ``layers`` argument.

        .. deprecated:: 3.0.0
            |br| This method is being deprecated in favor of our overloaded :class:`~lightnet.network.modules.Lightnet.modules` method.
        """
        log.deprecated_once('The `layer_loop` method is being deprecated. Use the overloaded `modules` method instead.')
        if mod is not None:
            raise ValueError('Setting a base module is not supported anymore')

        return self.modules(layers)

    def named_layer_loop(self, layers, mod=None, prefix=''):
        """ Named version of :func:`~lightnet.network.modules.Lightnet.layer_loop`.

        .. deprecated:: 3.0.0
            |br| This method is being deprecated in favor of our overloaded :class:`~lightnet.network.modules.Lightnet.named_modules` method.
        """
        log.deprecated_once('The `named_layer_loop` method is being deprecated. Use the overloaded `named_modules` method instead.')
        if mod is not None:
            raise ValueError('Setting a base module is not supported anymore')

        return self.named_modules(layers, prefix=prefix)

    def load(self, weights_file, remap=None, strict=True):
        """ This function will load the weights from a file.
        It also allows to load in a weights file with only a part of the weights in.

        Args:
            weights_file (str): path to file
            remap (callable or list, optional): Remapping of the weights, see :func:`~lightnet.network.module.Lightnet.weight_remapping`; Default **None**
            strict (Boolean, optional): Whether the weight file should contain all layers of the model; Default **True**

        Note:
            This function will load the weights to CPU,
            so you should use ``network.to(device)`` afterwards to send it to the device of your choice.
        """
        state = torch.load(weights_file, 'cpu')
        model_version = state.pop('_LN_MODEL_VERSION', 0)

        if remap is not None:
            if model_version != getattr(self, 'MODEL_VERSION', 0):
                log.error('Your weight file does not match the model version. We are not attempting automatic version remapping, as a remapping method has been specified.')

            state = self.weight_remapping(state, remap)
            remap = ' remapped'
        else:
            remap = ''
            state = self._remap_model_version(state, model_version)

        log.info('Loading%s weights from file [%s]', remap, weights_file)
        if not strict and state.keys() != self.state_dict().keys():
            log.warning('Modules not matching, performing partial update')

        self.load_state_dict(state, strict=strict)

    def load_pruned(self, weights_file, strict=True):
        """ This function will load pruned weights from a file.
        It also allows to load a weights file,
        which contains less channels in a convolution than orginally defined in the network.

        Args:
            weights_file (str): path to file
            strict (Boolean, optional): Whether the weight file should contain all layers of the model; Default **True**

        Note:
            This function will load the weights to CPU,
            so you should use ``network.to(device)`` afterwards to send it to the device of your choice.
        """
        state = torch.load(weights_file, 'cpu')
        model_version = state.pop('_LN_MODEL_VERSION', 0)
        state = self._remap_model_version(state, model_version)

        keys = set(self.state_dict().keys())
        log.info('Loading pruned weights from file [%s]', weights_file)

        # Prune tensors
        for key, val in state.items():
            if key in keys:
                mod_path, tensor_path = key.rsplit('.', 1)
                module = attrgetter(mod_path)(self)
                tensor = getattr(module, tensor_path)

                if tensor.shape != val.shape:
                    slices = [slice(0, s) for s in val.shape]
                    if isinstance(tensor, torch.nn.Parameter):
                        setattr(module, tensor_path, torch.nn.Parameter(tensor[slices]))
                    else:
                        setattr(module, tensor_path, tensor[slices])

        # Modify module metadata
        for module in self.modules():
            if isinstance(module, torch.nn.Conv2d):
                if module.groups == 1:
                    module.in_channels = module.weight.shape[1]
                    module.out_channels = module.weight.shape[0]
                elif module.groups == module.in_channels == module.out_channels:
                    module.out_channels = module.weight.shape[0]
                    module.in_channels = module.out_channels
                    module.groups = module.out_channels
            elif isinstance(module, torch.nn.BatchNorm2d):
                if module.weight is not None:
                    module.num_features = module.weight.shape[0]
                elif module.running_mean is not None:
                    module.num_features = module.running_mean.shape[0]

        # Load weights
        if not strict and state.keys() != keys:
            log.warning('Modules not matching, performing partial update')
        self.load_state_dict(state, strict=strict)

    def _remap_model_version(self, state, version):
        model_version = getattr(self, 'MODEL_VERSION', 0)
        if version > model_version:
            raise RuntimeError(
                'Trying to load weights from newer model than the one provided. '
                'Please update your package.',
            )

        while version < model_version:
            version += 1
            remap = getattr(self, f'remap_v{version}', None)
            if remap is None:
                raise NotImplementedError(
                    'You are trying to load old weights, '
                    f'but the automatic version remapping is not detected for this model ({version-1} -> {model_version}).',
                )
            else:
                log.deprecated(
                    'Your weight file is using an old format. '
                    'We are automatically adapting them for now, but make sure to resave your weights.',
                )

            state = self.weight_remapping(state, remap)

        return state

    def save(self, weights_file, remap=None):
        """ This function will save the weights to a file.

        Args:
            weights_file (str): path to file
            remap (callable or list, optional): Remapping of the weights, see :func:`~lightnet.network.module.Lightnet.weight_remapping`; Default **None**
        """
        if remap is not None:
            state = self.weight_remapping(self.state_dict(), remap)
            remap = ' remapped'
        else:
            state = self.state_dict()
            remap = ''

        model_version = getattr(self, 'MODEL_VERSION', 0)
        state['_LN_MODEL_VERSION'] = model_version

        torch.save(state, weights_file)
        log.info('Saved%s weights as %s', remap, weights_file)

    def __str__(self):
        """ Shorter version than default PyTorch one. """
        args = list(inspect.signature(self.__class__.__init_module__).parameters.keys())
        args.remove('self')

        string = self.__class__.__module__ + '.' + self.__class__.__name__ + '('
        for i, arg in enumerate(args):
            if i > 0:
                string += ', '
            val = getattr(self, arg, '?')
            string += f'{arg}={val}'
        string += ')'

        return string

    @property
    def __name__(self):
        return self.__class__.__name__

    @staticmethod
    def weight_remapping(weights, remap):
        r""" This function is used to remap the keys of a ``state_dict``.
        This can be useful to load in weights from a different framework or to modify weights from a backbone network,
        for usage in another (detection) network. |br|
        This method does not usually get called directly, but is used by :func:`~lightnet.network.module.Lightnet.load`
        and :func:`~lightnet.network.module.Lightnet.save` to modify the weights prior to loading/saving them.

        Args:
            weights (dict): The weights state dictionary
            remap (callable or list): Remapping of the weights, see Note

        Note:
            The optional ``remap`` parameter expects a callable object or a list of tuples.

            if the ``remap`` argument is a list of tuples, they should contain **('old', 'new')** remapping sequences.
            The remapping sequence can contain strings or regex objects. |br|
            What happens when you supply a remapping list,
            is that this function will loop over the ``state_dict`` of the model
            and for each item of the ``state_dict`` it will loop through the remapping list.
            If the first string or regex of the remapping sequence is found in the ``state_dict`` key,
            it will be replaced by the second string or regex of that remapping sequence. |br|
            There are two important things to note here:

            - If a key does not match any remapping sequence, it gets discarded.
              To save all the weights, even if you need no remapping, add a last remapping sequence of **(r'(.*)', r'\\1')** which will match with all keys, but not modify them.
            - The remapping sequences or processed in order.
              This means that if a key matches with a certain remapping sequence, the following sequences will not be considered anymore.

            If the argument is callable, it will be called with each key in the ``state_dict`` and it should return one of the following:

            - String : This string is used as the new remapped key
            - List<Tuple<str, str>> : We perform the same routine as explained above, but only for that specific key.
            - None : The weight will be removed from the new state_dict.
        """
        new_weights = OrderedDict()

        if callable(remap):
            for k, v in weights.items():
                nk = remap(k)
                if isinstance(nk, str):
                    log.debug('Remapping [%s] -> [%s]', k, nk)
                    new_weights[nk] = v
                elif isinstance(nk, Iterable):
                    done = False
                    for r in nk:
                        match = re.search(r[0], k)
                        if match:
                            nk = match.expand(r[1])
                            log.debug('Remapping [%s] -> [%s]', k, nk)
                            new_weights[nk] = v
                            done = True
                            break
                    if not done:
                        log.debug('Not remapping [%s]', k)
                else:
                    log.debug('Not remapping [%s]', k)
        else:
            for k, v in weights.items():
                done = False
                for r in remap:
                    match = re.search(r[0], k)
                    if match:
                        nk = match.expand(r[1])
                        log.debug('Remapping [%s] -> [%s]', k, nk)
                        new_weights[nk] = v
                        done = True
                        break
                if not done:
                    log.debug('Not remapping [%s]', k)

        return new_weights
