#
#   Mobilenet Backbone
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['Mobilenet']


class Mobilenet(BaseModule):
    """ Mobilenet backbones. """
    default_relu = partial(nn.ReLU6, inplace=True)

    @BaseModule.layers(named=True, primary=True)
    def V1(
        in_channels,
        out_channels,
        alpha=1,
        momentum=0.1,
        relu=default_relu,
    ):
        """
        Mobilenet V1 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            alpha (float, optional): Number between [0-1] that controls the number of filters of the mobilenet convolutions; Default **1**
            momentum (float, optional): Momentum of the moving averages of the normalization; Default **0.1**
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU6`

        .. rubric:: Models:

        - :class:`~lightnet.models.MobilenetV1`
        - :class:`~lightnet.models.MobilenetYolo`

        Examples:
            >>> backbone = ln.network.backbone.Mobilenet.V1(3, 1024)
            >>> print(backbone)
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (2_convdw): Conv2dDepthWise(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (3_convdw): Conv2dDepthWise(64, 128, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (4_convdw): Conv2dDepthWise(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (5_convdw): Conv2dDepthWise(128, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (6_convdw): Conv2dDepthWise(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (7_convdw): Conv2dDepthWise(256, 512, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (8_convdw): Conv2dDepthWise(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (9_convdw): Conv2dDepthWise(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (10_convdw): Conv2dDepthWise(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (11_convdw): Conv2dDepthWise(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (12_convdw): Conv2dDepthWise(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
              (13_convdw): Conv2dDepthWise(512, 1024, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (14_convdw): Conv2dDepthWise(1024, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU6(inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 1024, 20, 20])
        """
        return (
            ('1_convbatch', lnl.Conv2dBatchReLU(in_channels, int(alpha*32), 3, 2, 1, relu=relu, momentum=momentum)),
            ('2_convdw',    lnl.Conv2dDepthWise(int(alpha*32), int(alpha*64), 3, 1, 1, relu=relu, momentum=momentum)),
            ('3_convdw',    lnl.Conv2dDepthWise(int(alpha*64), int(alpha*128), 3, 2, 1, relu=relu, momentum=momentum)),
            ('4_convdw',    lnl.Conv2dDepthWise(int(alpha*128), int(alpha*128), 3, 1, 1, relu=relu, momentum=momentum)),
            ('5_convdw',    lnl.Conv2dDepthWise(int(alpha*128), int(alpha*256), 3, 2, 1, relu=relu, momentum=momentum)),
            ('6_convdw',    lnl.Conv2dDepthWise(int(alpha*256), int(alpha*256), 3, 1, 1, relu=relu, momentum=momentum)),
            ('7_convdw',    lnl.Conv2dDepthWise(int(alpha*256), int(alpha*512), 3, 2, 1, relu=relu, momentum=momentum)),
            ('8_convdw',    lnl.Conv2dDepthWise(int(alpha*512), int(alpha*512), 3, 1, 1, relu=relu, momentum=momentum)),
            ('9_convdw',    lnl.Conv2dDepthWise(int(alpha*512), int(alpha*512), 3, 1, 1, relu=relu, momentum=momentum)),
            ('10_convdw',   lnl.Conv2dDepthWise(int(alpha*512), int(alpha*512), 3, 1, 1, relu=relu, momentum=momentum)),
            ('11_convdw',   lnl.Conv2dDepthWise(int(alpha*512), int(alpha*512), 3, 1, 1, relu=relu, momentum=momentum)),
            ('12_convdw',   lnl.Conv2dDepthWise(int(alpha*512), int(alpha*512), 3, 1, 1, relu=relu, momentum=momentum)),
            ('13_convdw',   lnl.Conv2dDepthWise(int(alpha*512), int(alpha*1024), 3, 2, 1, relu=relu, momentum=momentum)),
            ('14_convdw',   lnl.Conv2dDepthWise(int(alpha*1024), out_channels, 3, 1, 1, relu=relu, momentum=momentum)),
        )

    @BaseModule.layers(named=True)
    def V2(
        in_channels,
        out_channels,
        alpha=1,
        momentum=0.1,
        relu=default_relu,
    ):
        """
        Mobilenet V2 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            alpha (float, optional): Number between [0-1] that controls the number of filters of the mobilenet convolutions; Default **1**
            momentum (float, optional): Momentum of the moving averages of the normalization; Default **0.1**
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU6`

        .. rubric:: Models:

        - :class:`~lightnet.models.MobilenetV2`

        Examples:
            >>> backbone = ln.network.backbone.Mobilenet.V2(3, 1024)
            >>> print(backbone)
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), ReLU6(inplace=True))
              (2_bottleneck): InvertedBottleneck(32, 16, kernel_size=(3, 3), stride=(1, 1), expansion=1, ReLU6(inplace=True))
              (3_bottleneck): InvertedBottleneck(16, 24, kernel_size=(3, 3), stride=(2, 2), expansion=6, ReLU6(inplace=True))
              (4_bottleneck): InvertedBottleneck(24, 24, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (5_bottleneck): InvertedBottleneck(24, 32, kernel_size=(3, 3), stride=(2, 2), expansion=6, ReLU6(inplace=True))
              (6_bottleneck): InvertedBottleneck(32, 32, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (7_bottleneck): InvertedBottleneck(32, 32, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (8_bottleneck): InvertedBottleneck(32, 64, kernel_size=(3, 3), stride=(2, 2), expansion=6, ReLU6(inplace=True))
              (9_bottleneck): InvertedBottleneck(64, 64, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (10_bottleneck): InvertedBottleneck(64, 64, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (11_bottleneck): InvertedBottleneck(64, 64, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (12_bottleneck): InvertedBottleneck(64, 96, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True))
              (13_bottleneck): InvertedBottleneck(96, 96, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (14_bottleneck): InvertedBottleneck(96, 96, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (15_bottleneck): InvertedBottleneck(96, 160, kernel_size=(3, 3), stride=(2, 2), expansion=6, ReLU6(inplace=True))
              (16_bottleneck): InvertedBottleneck(160, 160, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (17_bottleneck): InvertedBottleneck(160, 160, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True), residual_connection)
              (18_bottleneck): InvertedBottleneck(160, 320, kernel_size=(3, 3), stride=(1, 1), expansion=6, ReLU6(inplace=True))
              (19_convbatch): Conv2dBatchReLU(320, 1024, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU6(inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 1024, 20, 20])
        """
        return (
            ('1_convbatch',     lnl.Conv2dBatchReLU(in_channels, int(alpha*32), 3, 2, 1, relu=relu, momentum=momentum)),
            ('2_bottleneck',    lnl.InvertedBottleneck(int(alpha*32), int(alpha*16), 3, 1, 1, relu=relu, momentum=momentum)),
            ('3_bottleneck',    lnl.InvertedBottleneck(int(alpha*16), int(alpha*24), 3, 2, 6, relu=relu, momentum=momentum)),
            ('4_bottleneck',    lnl.InvertedBottleneck(int(alpha*24), int(alpha*24), 3, 1, 6, relu=relu, momentum=momentum)),
            ('5_bottleneck',    lnl.InvertedBottleneck(int(alpha*24), int(alpha*32), 3, 2, 6, relu=relu, momentum=momentum)),
            ('6_bottleneck',    lnl.InvertedBottleneck(int(alpha*32), int(alpha*32), 3, 1, 6, relu=relu, momentum=momentum)),
            ('7_bottleneck',    lnl.InvertedBottleneck(int(alpha*32), int(alpha*32), 3, 1, 6, relu=relu, momentum=momentum)),
            ('8_bottleneck',    lnl.InvertedBottleneck(int(alpha*32), int(alpha*64), 3, 2, 6, relu=relu, momentum=momentum)),
            ('9_bottleneck',    lnl.InvertedBottleneck(int(alpha*64), int(alpha*64), 3, 1, 6, relu=relu, momentum=momentum)),
            ('10_bottleneck',   lnl.InvertedBottleneck(int(alpha*64), int(alpha*64), 3, 1, 6, relu=relu, momentum=momentum)),
            ('11_bottleneck',   lnl.InvertedBottleneck(int(alpha*64), int(alpha*64), 3, 1, 6, relu=relu, momentum=momentum)),
            ('12_bottleneck',   lnl.InvertedBottleneck(int(alpha*64), int(alpha*96), 3, 1, 6, relu=relu, momentum=momentum)),
            ('13_bottleneck',   lnl.InvertedBottleneck(int(alpha*96), int(alpha*96), 3, 1, 6, relu=relu, momentum=momentum)),
            ('14_bottleneck',   lnl.InvertedBottleneck(int(alpha*96), int(alpha*96), 3, 1, 6, relu=relu, momentum=momentum)),
            ('15_bottleneck',   lnl.InvertedBottleneck(int(alpha*96), int(alpha*160), 3, 2, 6, relu=relu, momentum=momentum)),
            ('16_bottleneck',   lnl.InvertedBottleneck(int(alpha*160), int(alpha*160), 3, 1, 6, relu=relu, momentum=momentum)),
            ('17_bottleneck',   lnl.InvertedBottleneck(int(alpha*160), int(alpha*160), 3, 1, 6, relu=relu, momentum=momentum)),
            ('18_bottleneck',   lnl.InvertedBottleneck(int(alpha*160), int(alpha*320), 3, 1, 6, relu=relu, momentum=momentum)),
            ('19_convbatch',    lnl.Conv2dBatchReLU(int(alpha*320), out_channels,  1, 1, 0, relu=relu, momentum=momentum)),
        )
