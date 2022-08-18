#
#   Cornernet detection head
#   Copyright EAVISE
#
from collections import OrderedDict
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['DetectionCorner']


class DetectionCorner(BaseModule):
    """ Corner Detection head.

    Args:
        in_channels (int): Number of input channels
        num_classes (int): Number of classes
        squeeze (bool, optional): Whether to use the "squeeze" version of the detection head, where some convolutions become pointwise; Default **False**

    .. rubric:: Models:

    - :class:`~lightnet.models.Cornernet`
    - :class:`~lightnet.models.CornernetSqueeze`

    Examples:
        >>> head = ln.network.head.DetectionCorner(256, 20)
        >>> print(head)
        ParallelCat(
          (topleft): Sequential(
            (1_corner): CornerPool(256, TopPool, LeftPool, inter_channels=128, ReLU(inplace=True))
            (2_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (output): ParallelCat(
              (heatmap): Sequential(
                (3_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (4_conv): Conv2d(256, 20, kernel_size=(1, 1), stride=(1, 1))
              )
              (embedding): Sequential(
                (5_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (6_conv): Conv2d(256, 1, kernel_size=(1, 1), stride=(1, 1))
              )
              (offset): Sequential(
                (7_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (8_conv): Conv2d(256, 2, kernel_size=(1, 1), stride=(1, 1))
              )
            )
          )
          (bottomright): Sequential(
            (1_corner): CornerPool(256, BottomPool, RightPool, inter_channels=128, ReLU(inplace=True))
            (2_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            (output): ParallelCat(
              (heatmap): Sequential(
                (3_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (4_conv): Conv2d(256, 20, kernel_size=(1, 1), stride=(1, 1))
              )
              (embedding): Sequential(
                (5_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (6_conv): Conv2d(256, 1, kernel_size=(1, 1), stride=(1, 1))
              )
              (offset): Sequential(
                (7_conv): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (8_conv): Conv2d(256, 2, kernel_size=(1, 1), stride=(1, 1))
              )
            )
          )
        )
        >>> in_tensor = torch.rand(1, 256, 104, 104)
        >>> out_tensor = head(in_tensor)
        >>> print(out_tensor.shape)
        torch.Size([1, 46, 104, 104])
    """
    @BaseModule.layers(named=True, wrapper=lnl.ParallelCat)
    def Default(
        in_channels,
        num_classes,
        squeeze=False,
    ):
        kernel = (1, 1, 0) if squeeze else (3, 1, 1)
        return (
            ('topleft',                 nn.Sequential(OrderedDict([
                ('1_corner',            lnl.CornerPool(in_channels, lnl.TopPool, lnl.LeftPool)),
                ('2_convbatch',         lnl.Conv2dBatchReLU(in_channels, 256, 3, 1, 1)),
                ('output',              lnl.ParallelCat(OrderedDict([
                    ('heatmap',         nn.Sequential(OrderedDict([
                        ('3_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('4_conv',      nn.Conv2d(256, num_classes, 1, 1, 0)),
                    ]))),
                    ('embedding',       nn.Sequential(OrderedDict([
                        ('5_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('6_conv',      nn.Conv2d(256, 1, 1, 1, 0)),
                    ]))),
                    ('offset',          nn.Sequential(OrderedDict([
                        ('7_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('8_conv',      nn.Conv2d(256, 2, 1, 1, 0)),
                    ]))),
                ]))),
            ]))),
            ('bottomright',             nn.Sequential(OrderedDict([
                ('1_corner',            lnl.CornerPool(in_channels, lnl.BottomPool, lnl.RightPool)),
                ('2_convbatch',         lnl.Conv2dBatchReLU(in_channels, 256, 3, 1, 1)),
                ('output',              lnl.ParallelCat(OrderedDict([
                    ('heatmap',         nn.Sequential(OrderedDict([
                        ('3_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('4_conv',      nn.Conv2d(256, num_classes, 1, 1, 0)),
                    ]))),
                    ('embedding',       nn.Sequential(OrderedDict([
                        ('5_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('6_conv',      nn.Conv2d(256, 1, 1, 1, 0)),
                    ]))),
                    ('offset',          nn.Sequential(OrderedDict([
                        ('7_conv',      lnl.Conv2dReLU(256, 256, *kernel, bias=True)),
                        ('8_conv',      nn.Conv2d(256, 2, 1, 1, 0)),
                    ]))),
                ]))),
            ]))),
        )
