#
#   Resnet Backbone
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['Resnet']


class Resnet(BaseModule):
    """ Resnet Backbones. """
    default_relu = partial(nn.ReLU, inplace=True)
    groups = {
        50: (2, 3, 5, 2),
        101: (2, 3, 22, 2),
        152: (2, 7, 35, 2),
    }

    @BaseModule.layers(named=True, classmethod=True, primary=True)
    def Default(
        cls,
        in_channels,
        out_channels,
        groups,
        relu=default_relu,
    ):
        """
        Primary backbone builder, which allows you to specify the number of residual blocks per group.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            groups (list<int>): Number of residual blocks per group (4 numbers required, see Note)
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`

        Note:
            The authors of the original Resnet paper split their models in 4 subgroups,
            each containing a different number of residual blocks :cite:`resnet`.
            The ``groups`` arguments requires a list of 4 numbers,
            that define how many residual blocks are created for each of the groups. |br|
            The ``Resnet.groups`` dictionary attribute contains common group definitions

            Note that our implementation already adds the first residual block of each group separately
            and thus the number of blocks per group should be one less than what is written in the official paper!

        Example:
            >>> backbone = ln.network.backbone.Resnet(3, 2048, [2, 3, 5, 2])
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_max): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
              (3_residual): Residual(
                (0): Conv2dBatchReLU(64, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
                (1): Conv2dBatchReLU(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (skip): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (post): ReLU(inplace=True)
              )
              (4_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
              (5_residual): Residual(...)
              (6_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
              )
              (7_residual): Residual(...)
              (8_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
                (3): Residual(...)
                (4): Residual(...)
              )
              (9_residual): Residual(...)
              (10_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 2048, 20, 20])
        """
        return cls.get_layers(in_channels, out_channels, groups, relu)

    @BaseModule.layers(named=True, classmethod=True)
    def RN_50(
        cls,
        in_channels,
        out_channels,
        relu=default_relu,
    ):
        """
        ResNet50 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`

        .. rubric:: Models:

        - :class:`~lightnet.models.Resnet50`
        - :class:`~lightnet.models.ResnetYolo`
        - :class:`~lightnet.models.M_ResnetYolo`

        Example:
            >>> backbone = ln.network.backbone.Resnet.RN_50(3, 2048)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_max): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
              (3_residual): Residual(
                (0): Conv2dBatchReLU(64, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
                (1): Conv2dBatchReLU(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (skip): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (post): ReLU(inplace=True)
              )
              (4_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
              (5_residual): Residual(...)
              (6_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
              )
              (7_residual): Residual(...)
              (8_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
                (3): Residual(...)
                (4): Residual(...)
              )
              (9_residual): Residual(...)
              (10_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 2048, 20, 20])
        """
        return cls.get_layers(in_channels, out_channels, cls.groups[50], relu)

    @BaseModule.layers(named=True, classmethod=True)
    def RN_101(
        cls,
        in_channels,
        out_channels,
        relu=default_relu,
    ):
        """
        ResNet101 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`

        .. rubric:: Models:

        - :class:`~lightnet.models.Resnet101`

        Example:
            >>> backbone = ln.network.backbone.Resnet.RN_101(3, 2048)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_max): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
              (3_residual): Residual(
                (0): Conv2dBatchReLU(64, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
                (1): Conv2dBatchReLU(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (skip): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (post): ReLU(inplace=True)
              )
              (4_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
              (5_residual): Residual(...)
              (6_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
              )
              (7_residual): Residual(...)
              (8_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
                (3): Residual(...)
                (4): Residual(...)
                (5): Residual(...)
                (6): Residual(...)
                (7): Residual(...)
                (8): Residual(...)
                (9): Residual(...)
                (10): Residual(...)
                (11): Residual(...)
                (12): Residual(...)
                (13): Residual(...)
                (14): Residual(...)
                (15): Residual(...)
                (16): Residual(...)
                (17): Residual(...)
                (18): Residual(...)
                (19): Residual(...)
                (20): Residual(...)
                (21): Residual(...)
              )
              (9_residual): Residual(...)
              (10_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 2048, 20, 20])
        """
        return cls.get_layers(in_channels, out_channels, cls.groups[101], relu)

    @BaseModule.layers(named=True, classmethod=True)
    def RN_152(
        cls,
        in_channels,
        out_channels,
        relu=default_relu,
    ):
        """
        ResNet152 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`

        .. rubric:: Models:

        - :class:`~lightnet.models.Resnet152`

        Example:
            >>> backbone = ln.network.backbone.Resnet.RN_50(3, 2048)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_max): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
              (3_residual): Residual(
                (0): Conv2dBatchReLU(64, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
                (1): Conv2dBatchReLU(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (2): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (skip): Conv2dBatch(64, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (post): ReLU(inplace=True)
              )
              (4_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
              (5_residual): Residual(...)
              (6_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
                (3): Residual(...)
                (4): Residual(...)
                (5): Residual(...)
                (6): Residual(...)
              )
              (7_residual): Residual(...)
              (8_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
                (2): Residual(...)
                (3): Residual(...)
                (4): Residual(...)
                (5): Residual(...)
                (6): Residual(...)
                (7): Residual(...)
                (8): Residual(...)
                (9): Residual(...)
                (10): Residual(...)
                (11): Residual(...)
                (12): Residual(...)
                (13): Residual(...)
                (14): Residual(...)
                (15): Residual(...)
                (16): Residual(...)
                (17): Residual(...)
                (18): Residual(...)
                (19): Residual(...)
                (20): Residual(...)
                (21): Residual(...)
                (22): Residual(...)
                (23): Residual(...)
                (24): Residual(...)
                (25): Residual(...)
                (26): Residual(...)
                (27): Residual(...)
                (28): Residual(...)
                (29): Residual(...)
                (30): Residual(...)
                (31): Residual(...)
                (32): Residual(...)
                (33): Residual(...)
                (34): Residual(...)
              )
              (9_residual): Residual(...)
              (10_residualgroup): Sequential(
                (0): Residual(...)
                (1): Residual(...)
              )
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 2048, 20, 20])
        """
        return cls.get_layers(in_channels, out_channels, cls.groups[152], relu)

    @classmethod
    def get_layers(cls, in_channels, out_channels, groups, relu):
        get_block = cls.get_bottleneck
        return (
            # Conv 1
            ('1_convbatch',         lnl.Conv2dBatchReLU(in_channels, 64, 7, 2, 3, relu=relu)),
            ('2_max',               nn.MaxPool2d(3, 2, 1)),

            # Conv 2_x
            ('3_residual',          get_block(64, 64, 256, 1, relu)),
            ('4_residualgroup',     nn.Sequential(*(groups[0]*[get_block(256, 64, 256, 1, relu)]))),

            # Conv 3_x
            ('5_residual',          get_block(256, 128, 512, 2, relu)),
            ('6_residualgroup',     nn.Sequential(*(groups[1]*[get_block(512, 128, 512, 1, relu)]))),

            # Conv 4_x
            ('7_residual',          get_block(512, 256, 1024, 2, relu)),
            ('8_residualgroup',     nn.Sequential(*(groups[2]*[get_block(1024, 256, 1024, 1, relu)]))),

            # Conv 5_x
            ('9_residual',          get_block(1024, 512, out_channels, 2, relu)),
            ('10_residualgroup',    nn.Sequential(*(groups[3]*[get_block(out_channels, 512, out_channels, 1, relu)]))),
        )

    @staticmethod
    def get_bottleneck(in_channels, inter_channels, out_channels, stride, relu):
        return lnl.Residual(
            lnl.Conv2dBatchReLU(in_channels, inter_channels, 1, 1, 0, relu=relu),
            lnl.Conv2dBatchReLU(inter_channels, inter_channels, 3, stride, 1, relu=relu),
            lnl.Conv2dBatch(inter_channels, out_channels, 1, 1, 0),

            skip=None if (in_channels == out_channels) and (stride == 1) else lnl.Conv2dBatch(in_channels, out_channels, 1, stride, 0),
            post=relu(),
        )
