#
#   Alexnet Backbone
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['Alexnet']


class Alexnet(BaseModule):
    """ Alexnet backbone.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`

    .. rubric:: Models:

    - :class:`~lightnet.models.Alexnet`

    Examples:
        >>> backbone = ln.network.backbone.Alexnet(3, 256)
        >>> print(backbone)
        Sequential(
          (1_conv): Conv2dReLU(3, 64, kernel_size=(11, 11), stride=(4, 4), padding=(2, 2), ReLU(inplace=True))
          (2_max): MaxPool2d(kernel_size=3, stride=2, padding=0, dilation=1, ceil_mode=False)
          (3_conv): Conv2dReLU(64, 192, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2), ReLU(inplace=True))
          (4_max): MaxPool2d(kernel_size=3, stride=2, padding=0, dilation=1, ceil_mode=False)
          (5_conv): Conv2dReLU(192, 384, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (6_conv): Conv2dReLU(384, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (7_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (8_max): MaxPool2d(kernel_size=3, stride=2, padding=0, dilation=1, ceil_mode=False)
        )
        >>> in_tensor = torch.rand(1, 3, 640, 640)
        >>> out_tensor = backbone(in_tensor)
        >>> print(out_tensor.shape)
        torch.Size([1, 256, 19, 19])
    """
    default_relu = partial(nn.ReLU, inplace=True)

    @BaseModule.layers(named=True)
    def Default(in_channels, out_channels, relu=default_relu):
        return (
            ('1_conv',  lnl.Conv2dReLU(in_channels, 64, 11, 4, 2, bias=True, relu=relu)),
            ('2_max',   nn.MaxPool2d(3, 2)),
            ('3_conv',  lnl.Conv2dReLU(64, 192, 5, 1, 2, bias=True, relu=relu)),
            ('4_max',   nn.MaxPool2d(3, 2)),
            ('5_conv',  lnl.Conv2dReLU(192, 384, 3, 1, 1, bias=True, relu=relu)),
            ('6_conv',  lnl.Conv2dReLU(384, 256, 3, 1, 1, bias=True, relu=relu)),
            ('7_conv',  lnl.Conv2dReLU(256, out_channels, 3, 1, 1, bias=True, relu=relu)),
            ('8_max',   nn.MaxPool2d(3, 2)),
        )
