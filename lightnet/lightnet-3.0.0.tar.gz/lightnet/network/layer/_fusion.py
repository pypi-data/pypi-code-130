#
#   Fusion module
#   Copyright EAVISE
#

import copy
import logging
from collections import OrderedDict
import torch
import torch.nn as nn
from torch.nn.modules.module import _addindent
from lightnet.util import get_module_shape


__all__ = ['Fusion', 'FusionSequential', 'FusionModule']
log = logging.getLogger(__name__)


class FusionSequential(nn.Module):
    """ Fusion module from :cite:`rgbd_fusion_v2`.
    This module is like a :class:`torch.nn.Sequential`, but it will perform the actions twice,
    once on the regular input and once on the fusion input. |br|
    The fusion will be performed by adding an extra 1x1 fuse convolution between the output of both streams and the input of the combined stream,
    to mix both streams and reduce the number of output feature maps by a factor of 2. |br|
    This module takes a single input feature map during its forward pass, and splits it evenly for both input streams.

    Args:
        layers (dict or list of pytorch modules): Layers that will be used. These layers are internally passed to a :class:`~torch.nn.Sequential` and must thus comply with the rules for this class
        fuse_layer (int, optional): Number between 0 and the number of layers + 1, that controls where to fuse both streams; Default **None**

    .. figure:: /.static/api/fusionsequential.*
       :width: 100%
       :alt: FusionSequential and fuse layer

    Warning:
        This module will create a :class:`~torch.nn.Sequential` for the regular convolutional stream and deepcopy that for the fusion stream.
        This will effectively create 2 different streams that have their own weights, but it does mean that both streams start with identical weights. |br|
        It is strongly advised to use pretrained weights or initialize your weights randomly after having created these modules.

    Warning:
        The way we compute the input and output feature maps for the 1x1 fuse convolution,
        is by looping through the regular stream or combined stream,
        looking for the last `out_channels` or first `in_channels` attribute of the layers respectively. |br|
        This means that this module only works if there are convolutional layers in the list,
        or any other layer that has these `in_channels` and `out_channels` attributes to be able to deduce the number of feature maps.

    Note:
        Depending on the value of the `fuse_layer` attribute, fusion is performed at different stages of the module. |br|

        - If no `fuse\\_layer` is given (or **None** is given as its value),\
        no fusion will be done and the input will be considered as an already fused combination.
        - If the `fuse\\_layer` attribute is an integer from 0 to :math:`num\\_layers`, the module will fuse both streams after the number of the layer that is given.\
        Giving a value of **0** thus means to fuse before the first layer and giving a value of **num_layers** to fuse after the last.
        - Finally, if :math:`fuse\\_layer == num\\_layers + 1`, then no fusion will occur, but rather both streams will be processed seperately\
        and the output feature maps will simply be concatenated at the end.

        These rules allow the chain multiple :class:`~lightnet.network.layer.Fusion` modules together, only fusing in one of them at a certain time.

    Note:
        In :cite:`rgbd_fusion_v2`, we demonstrated that mid to late fusion gives the best results. |br|
        As such, we developed a new :class:`~lightnet.network.layer.FusionModule`, which can run any module (and not only Sequentials) and simply fuses the outputs of that module.
        While this new module does not offer the choice of fusion layer, it is much simpler to use and allows to perform N fusions instead of being limited to only two.
        Transforming eg. a backbone to a :class:`~lightnet.network.layer.FusionModule` is more or less equal to mid/late fusion and should thus yield optimal results.

    Example:
        >>> layers = [
        ...   ln.network.layer.Conv2dBatchReLU(3,  32, 3, 1, 1),
        ...   ln.network.layer.Conv2dBatchReLU(32, 64, 3, 1, 1),
        ...   ln.network.layer.Conv2dBatchReLU(64, 32, 3, 1, 1),
        ... ]
        >>> # Streams are fused in the middle of the module
        >>> module = ln.network.layer.FusionSequential(layers, fuse_layer=1)
        >>> print(module)
        FusionSequential(
          (Regular & Fusion): Sequential(
            (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
          (Fuse): Conv2d(64, 32, kernel_size=(1, 1), stride=(1, 1), bias=False)
          (Combined): Sequential(
            (0): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (1): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
        )
        >>> # Streams are fused at the end of the module (after last convolution)
        >>> module = ln.network.layer.FusionSequential(layers, fuse_layer=3)
        >>> print(module)
        FusionSequential(
          (Regular & Fusion): Sequential(
            (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
          (Fuse): Conv2d(64, 32, kernel_size=(1, 1), stride=(1, 1), bias=False)
        )
        >>> # Streams are fused before the first layer
        >>> module = ln.network.layer.FusionSequential(layers, fuse_layer=0)
        >>> print(module)
        FusionSequential(
          (Fuse): Conv2d(6, 3, kernel_size=(1, 1), stride=(1, 1), bias=False)
          (Combined): Sequential(
            (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
        )
        >>> # Streams were fused before this module and thus there is no fusion involved (only combined sequential)
        >>> module = ln.network.layer.FusionSequential(layers, fuse_layer=None)
        >>> print(module)
        FusionSequential(
          (Combined): Sequential(
            (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
        )
        >>> # Streams are not fused in this module (duplicated regular and fusion sequentials)
        >>> module = ln.network.layer.FusionSequential(layers, fuse_layer=4)
        >>> print(module)
        FusionSequential(
          (Regular & Fusion): Sequential(
            (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          )
        )
    """
    def __init__(self, layers, fuse_layer=None):
        super().__init__()

        # Parameters
        self.fuse_layer = fuse_layer

        # layers
        if self.fuse_layer is None:             # Combined
            self.regular = None
            self.fusion = None
            if isinstance(layers, dict):
                self.combined = nn.Sequential(layers)
            else:
                self.combined = nn.Sequential(*layers)
            self.fuse = None
        elif self.fuse_layer == 0:              # Fuse + Combined
            self.regular = None
            self.fusion = None
            if isinstance(layers, dict):
                self.combined = nn.Sequential(layers)
            else:
                self.combined = nn.Sequential(*layers)
            self.fuse = self._get_fuse_conv()
        elif self.fuse_layer == len(layers):    # Reg/Fusion + Fuse
            if isinstance(layers, dict):
                self.regular = nn.Sequential(layers)
            else:
                self.regular = nn.Sequential(*layers)
            self.fusion = copy.deepcopy(self.regular)
            self.combined = None
            self.fuse = self._get_fuse_conv()
        elif self.fuse_layer > len(layers):     # Reg/Fusion
            if self.fuse_layer > len(layers) + 1:
                log.debug('fuse_layer variable is too high, setting it to {%d} which will not perform any fusion [%d]', len(layers)+1, self.fuse_layer)
                self.fuse_layer = len(layers) + 1

            if isinstance(layers, dict):
                self.regular = nn.Sequential(layers)
            else:
                self.regular = nn.Sequential(*layers)
            self.fusion = copy.deepcopy(self.regular)
            self.combined = None
            self.fuse = None
        elif self.fuse_layer < len(layers):     # Reg/Fusion + Fuse + Combined
            if isinstance(layers, dict):
                self.regular = nn.Sequential(OrderedDict(list(layers.items())[:self.fuse_layer]))
                self.fusion = copy.deepcopy(self.regular)
                self.combined = nn.Sequential(OrderedDict(list(layers.items())[self.fuse_layer:]))
            else:
                self.regular = nn.Sequential(*layers[:self.fuse_layer])
                self.fusion = copy.deepcopy(self.regular)
                self.combined = nn.Sequential(*layers[self.fuse_layer:])
            self.fuse = self._get_fuse_conv()

    def __repr__(self):
        main_str = self._get_name() + '('

        if self.regular is not None:
            mod_str = _addindent(repr(self.regular), 2)
            main_str += '\n  (Regular & Fusion): ' + mod_str
        if self.fuse is not None:
            mod_str = _addindent(repr(self.fuse), 2)
            main_str += '\n  (Fuse): ' + mod_str
        if self.combined is not None:
            mod_str = _addindent(repr(self.combined), 2)
            main_str += '\n  (Combined): ' + mod_str

        return main_str + '\n)'

    def _get_fuse_conv(self):
        channels = None
        if self.combined is not None:
            channels = find_attr(self.combined, 'in_channels')
        if channels is None and self.regular is not None:
            channels = find_attr(self.regular, 'out_channels', first=False)
        if channels is None:
            raise TypeError('Could not find "in_channels" or "out_channels" attribute in layers.')

        return nn.Conv2d(channels*2, channels, 1, 1, 0, bias=False).to(list(self.parameters())[0].device)

    def forward(self, x):
        if self.regular is not None:
            assert x.shape[1] % 2 == 0, 'Number of input channels should be divisible by 2'

            r = self.regular(x[:, :x.shape[1]//2])
            f = self.fusion(x[:, x.shape[1]//2:])
            x = torch.cat((r, f), 1)

        if self.fuse is not None:
            x = self.fuse(x)

        if self.combined is not None:
            x = self.combined(x)

        return x


def find_attr(module, name, first=True):
    if hasattr(module, name):
        return getattr(module, name)

    retval = None
    for mod in module.children():
        r = find_attr(mod, name, first)
        if r is not None:
            if first:
                return r
            else:
                retval = r

    return retval


class FusionModule(nn.Module):
    """
    This module will duplicate a module N times in order to perform data fusion on the channel dimension.

    The input to this module should be a single tensor, where the different inputs are concatenated in the channel dimension.
    We firstly run a 1x1 convolution on each (split) input, in order to have the correct shape for each input.
    After running each input through its own copy of the module,
    we finally concatenate each of the module outputs and run a final fusion convolution in order to reduce the number of output channels to the same of the original module.

    Args:
        module (nn.Module): Module to run
        in_channels (list<int>): Number of input channels per parallel module
        input_shape (list<int>): Input data shape to the base module you give
        fusion_kernel (int): Kernel size for the fusion convolutions (should be an odd number); Default **1**

    .. figure:: /.static/api/fusionmodule.*
       :width: 100%
       :alt: FusionModule and fuse layer

    Note:
        The ``input_shape`` argument is used during initialization in order to get the different outputs which come from the original module.
        This is then used to build correct fusion convolutions, which are used to combine the various outputs.

    Example:
        >>> # Perform data fusion on 3 different input types
        >>> layers = torch.nn.Sequential(
        ...   ln.network.layer.Conv2dBatchReLU(3,  32, 3, 1, 1),
        ...   ln.network.layer.Conv2dBatchReLU(32, 64, 3, 1, 1),
        ...   ln.network.layer.Conv2dBatchReLU(64, 32, 3, 1, 1),
        ... )
        >>> module = ln.network.layer.FusionModule(layers, (2, 2, 1), (1, 3, 416, 416))
        >>> print(module)
        FusionModule(
          in_channels=(2, 2, 1)
          (channel_conv): ModuleList(
            (0): Conv2d(2, 3, kernel_size=(1, 1), stride=(1, 1))
            (1): Conv2d(2, 3, kernel_size=(1, 1), stride=(1, 1))
            (2): Conv2d(1, 3, kernel_size=(1, 1), stride=(1, 1))
          )
          (fusion_module): ModuleList(
            (0): Sequential(
              (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            )
            (1): Sequential(
              (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            )
            (2): Sequential(
              (0): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (1): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
              (2): Conv2dBatchReLU(64, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            )
          )
          (fusion_conv): ModuleList(
            (0): Conv2d(96, 32, kernel_size=(1, 1), stride=(1, 1))
          )
        )
        >>> # Input should be a single tensor
        >>> input_tensor = torch.rand(1, 5, 416, 416)
        >>> output_tensor = module(input_tensor)
        >>> output_tensor.shape
        torch.Size([1, 32, 416, 416])

        >>> # The module can have multiple outputs as well
        >>> # Here we create a FeatureExtractor the returns an intermediate feature map as well as the output
        >>> layers = ln.network.layer.FeatureExtractor(ln.network.backbone.VGG.A(3, 512), ['8_conv'], True)
        >>> module = ln.network.layer.FusionModule(layers, (3, 1), (1, 3, 96, 96))
        >>> print(module)
        FusionModule(
          in_channels=(3, 1)
          (channel_conv): ModuleList(
            (0): Conv2d(3, 3, kernel_size=(1, 1), stride=(1, 1))
            (1): Conv2d(1, 3, kernel_size=(1, 1), stride=(1, 1))
          )
          (fusion_module): ModuleList(
            (0): FeatureExtractor(
              selection=[8_conv], return=True
              (module): Sequential(
                (1_conv): Conv2dReLU(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (3_conv): Conv2dReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (5_conv): Conv2dReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (6_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (7_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (8_conv): Conv2dReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (9_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (10_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (11_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (12_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (13_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              )
            )
            (1): FeatureExtractor(
              selection=[8_conv], return=True
              (module): Sequential(
                (1_conv): Conv2dReLU(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (3_conv): Conv2dReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (5_conv): Conv2dReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (6_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (7_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (8_conv): Conv2dReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (9_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (10_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                (11_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (12_conv): Conv2dReLU(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (13_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              )
            )
          )
          (fusion_conv): ModuleList(
            (0): Conv2d(1024, 512, kernel_size=(1, 1), stride=(1, 1))
            (1): Conv2d(1024, 512, kernel_size=(1, 1), stride=(1, 1))
          )
        )
        >>> input_tensor = torch.rand(1, 4, 96, 96)
        >>> output_tensors = module(input_tensor)
        >>> print([o.shape for o in output_tensors])
        [torch.Size([1, 512, 3, 3]), torch.Size([1, 512, 12, 12])]
    """
    def __init__(self, module, in_channels, input_shape, fusion_kernel=1):
        assert fusion_kernel % 2 == 1, 'Fusion kernel should be an odd number'
        super().__init__()

        self.in_channels = in_channels
        self.channel_conv = nn.ModuleList([
            nn.Conv2d(channel, input_shape[1], 1, 1, 0)
            for channel in in_channels
        ])

        self.fusion_module = nn.ModuleList([copy.deepcopy(module) for _ in self.in_channels])

        output_shape = get_module_shape(module, input_shape)
        output_channels = [o[1] for o in output_shape] if isinstance(output_shape, list) else [output_shape[1]]

        self.fusion_conv = nn.ModuleList([
            nn.Conv2d(len(self.in_channels) * channel, channel, fusion_kernel, 1, fusion_kernel // 2)
            for channel in output_channels
        ])

    def forward(self, x):
        assert x.shape[1] == sum(self.in_channels), 'Number of input channels not correct'

        # Run modules
        start, end = 0, 0
        outputs = []
        for idx, channel in enumerate(self.in_channels):
            end += channel
            input = self.channel_conv[idx](x[:, start:end])
            start += channel
            outputs.append(self.fusion_module[idx](input))

        # Fuse outputs
        if len(self.fusion_conv) == 1:
            return self.fusion_conv[0](torch.cat(outputs, dim=1))
        else:
            fused_outputs = []
            for idx, conv in enumerate(self.fusion_conv):
                input = torch.cat([o[idx] for o in outputs], dim=1)
                fused_outputs.append(conv(input))

            return fused_outputs

    def extra_repr(self):
        return f'in_channels={self.in_channels}'

    def _load_from_state_dict(
        self,
        state_dict,
        prefix,
        local_metadata,
        strict,
        missing_keys,
        unexpected_keys,
        error_msgs,
    ):
        if not any(k.startswith(f'{prefix}fusion_module') for k in state_dict.keys()):
            log.warning(
                'Loading regular weights in a fusion network. '
                'All branches will have the same weights and the first channel_conv and last fusion_conv will be left as is.',
            )

            keys = tuple(state_dict.keys())
            for key in keys:
                if key.startswith(prefix):
                    value = state_dict.pop(key)
                    for idx in range(len(self.fusion_module)):
                        state_dict[f'{prefix}fusion_module.{idx}.{key[len(prefix):]}'] = value.clone()

        return super()._load_from_state_dict(
            state_dict,
            prefix,
            local_metadata,
            strict,
            missing_keys,
            unexpected_keys,
            error_msgs,
        )


def Fusion(*args, **kwargs):
    log.deprecated_once('Fusion is renamed to FusionSequential.')
    return FusionSequential(*args, **kwargs)
