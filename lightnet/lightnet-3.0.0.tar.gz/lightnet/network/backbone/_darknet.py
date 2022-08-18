#
#   Darknet Backbone
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['Darknet']


class Darknet(BaseModule):
    """ Darknet backbones. """
    default_relu = partial(nn.LeakyReLU, 0.1, inplace=True)

    @BaseModule.layers(named=True, primary=True)
    def DN(in_channels, out_channels, momentum=0.01, relu=default_relu):
        """
        Base Darknet backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            momentum (float, optional): Momentum of the moving averages of the normalization; Default **0.01**
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.LeakyReLU(0.1)`

        .. rubric:: Models:

        - :class:`~lightnet.models.Darknet`
        - :class:`~lightnet.models.TinyYoloV2`
        - :class:`~lightnet.models.TinyYoloV3`

        Examples:
            >>> backbone = ln.network.backbone.Darknet(3, 512)
            >>> print(backbone)
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 16, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (3_convbatch): Conv2dBatchReLU(16, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (5_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (6_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (10_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (11_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 512, 20, 20])
        """
        return (
            ('1_convbatch',     lnl.Conv2dBatchReLU(in_channels, 16, 3, 1, 1, relu=relu, momentum=momentum)),
            ('2_max',           nn.MaxPool2d(2, 2)),
            ('3_convbatch',     lnl.Conv2dBatchReLU(16, 32, 3, 1, 1, relu=relu, momentum=momentum)),
            ('4_max',           nn.MaxPool2d(2, 2)),
            ('5_convbatch',     lnl.Conv2dBatchReLU(32, 64, 3, 1, 1, relu=relu, momentum=momentum)),
            ('6_max',           nn.MaxPool2d(2, 2)),
            ('7_convbatch',     lnl.Conv2dBatchReLU(64, 128, 3, 1, 1, relu=relu, momentum=momentum)),
            ('8_max',           nn.MaxPool2d(2, 2)),
            ('9_convbatch',     lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum)),
            ('10_max',          nn.MaxPool2d(2, 2)),
            ('11_convbatch',    lnl.Conv2dBatchReLU(256, out_channels, 3, 1, 1, relu=relu, momentum=momentum)),
        )

    @BaseModule.layers(named=True)
    def DN_19(in_channels, out_channels, momentum=0.01, relu=default_relu):
        """
        Darknet19 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            momentum (float, optional): Momentum of the moving averages of the normalization; Default **0.01**
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.LeakyReLU(0.1)`

        .. rubric:: Models:

        - :class:`~lightnet.models.Darknet19`
        - :class:`~lightnet.models.DYolo`
        - :class:`~lightnet.models.YoloV2`
        - :class:`~lightnet.models.YoloV2Upsample`
        - :class:`~lightnet.models.Yolt`

        Examples:
            >>> backbone = ln.network.backbone.Darknet.DN_19(3, 1024)
            >>> print(backbone)
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (3_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (5_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (6_convbatch): Conv2dBatchReLU(128, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (10_convbatch): Conv2dBatchReLU(256, 128, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (11_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (12_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (13_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (14_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (15_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (16_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (17_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (18_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
              (19_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (20_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (21_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (22_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (23_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 1024, 20, 20])
        """
        return (
            ('1_convbatch',     lnl.Conv2dBatchReLU(in_channels, 32, 3, 1, 1, relu=relu, momentum=momentum)),
            ('2_max',           nn.MaxPool2d(2, 2)),
            ('3_convbatch',     lnl.Conv2dBatchReLU(32, 64, 3, 1, 1, relu=relu, momentum=momentum)),
            ('4_max',           nn.MaxPool2d(2, 2)),
            ('5_convbatch',     lnl.Conv2dBatchReLU(64, 128, 3, 1, 1, relu=relu, momentum=momentum)),
            ('6_convbatch',     lnl.Conv2dBatchReLU(128, 64, 1, 1, 0, relu=relu, momentum=momentum)),
            ('7_convbatch',     lnl.Conv2dBatchReLU(64, 128, 3, 1, 1, relu=relu, momentum=momentum)),
            ('8_max',           nn.MaxPool2d(2, 2)),
            ('9_convbatch',     lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum)),
            ('10_convbatch',    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum)),
            ('11_convbatch',    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum)),
            ('12_max',          nn.MaxPool2d(2, 2)),
            ('13_convbatch',    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum)),
            ('14_convbatch',    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum)),
            ('15_convbatch',    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum)),
            ('16_convbatch',    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum)),
            ('17_convbatch',    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum)),
            ('18_max',          nn.MaxPool2d(2, 2)),
            ('19_convbatch',    lnl.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum)),
            ('20_convbatch',    lnl.Conv2dBatchReLU(1024, 512, 1, 1, 0, relu=relu, momentum=momentum)),
            ('21_convbatch',    lnl.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum)),
            ('22_convbatch',    lnl.Conv2dBatchReLU(1024, 512, 1, 1, 0, relu=relu, momentum=momentum)),
            ('23_convbatch',    lnl.Conv2dBatchReLU(512, out_channels, 3, 1, 1, relu=relu, momentum=momentum)),
        )

    @BaseModule.layers(named=True)
    def DN_53(in_channels, out_channels, momentum=0.01, relu=default_relu):
        """
        Darknet53 backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels
            momentum (float, optional): Momentum of the moving averages of the normalization; Default **0.01**
            relu (class, optional): Which ReLU to use; Default :class:`torch.nn.LeakyReLU(0.1)`

        .. rubric:: Models:

        - :class:`~lightnet.models.Darknet53`
        - :class:`~lightnet.models.YoloV3`

        Examples:
            >>> backbone = ln.network.backbone.Darknet.DN_53(3, 1024)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (2_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (3_residual): Residual(...)
              (4_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (5_residual): Residual(...)
              (6_residual): Residual(...)
              (7_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (8_residual): Residual(...)
              (9_residual): Residual(...)
              (10_residual): Residual(...)
              (11_residual): Residual(...)
              (12_residual): Residual(...)
              (13_residual): Residual(...)
              (14_residual): Residual(...)
              (15_residual): Residual(...)
              (16_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (17_residual): Residual(...)
              (18_residual): Residual(...)
              (19_residual): Residual(...)
              (20_residual): Residual(...)
              (21_residual): Residual(...)
              (22_residual): Residual(...)
              (23_residual): Residual(...)
              (24_residual): Residual(...)
              (25_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (26_residual): Residual(...)
              (27_residual): Residual(...)
              (28_residual): Residual(...)
              (29_residual): Residual(...)
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 1024, 20, 20])
        """
        return (
            ('1_convbatch',         lnl.Conv2dBatchReLU(in_channels, 32, 3, 1, 1, relu=relu, momentum=momentum)),
            ('2_convbatch',         lnl.Conv2dBatchReLU(32, 64, 3, 2, 1, relu=relu, momentum=momentum)),
            ('3_residual',          lnl.Residual(
                                    lnl.Conv2dBatchReLU(64, 32, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(32, 64, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('4_convbatch',         lnl.Conv2dBatchReLU(64, 128, 3, 2, 1, relu=relu, momentum=momentum)),
            ('5_residual',          lnl.Residual(
                                    lnl.Conv2dBatchReLU(128, 64, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(64, 128, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('6_residual',          lnl.Residual(
                                    lnl.Conv2dBatchReLU(128, 64, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(64, 128, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('7_convbatch',         lnl.Conv2dBatchReLU(128, 256, 3, 2, 1, relu=relu, momentum=momentum)),
            ('8_residual',          lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('9_residual',          lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('10_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('11_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('12_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('13_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('14_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('15_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('16_convbatch',        lnl.Conv2dBatchReLU(256, 512, 3, 2, 1, relu=relu, momentum=momentum)),
            ('17_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('18_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('19_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('20_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('21_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('22_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('23_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('24_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('25_convbatch',        lnl.Conv2dBatchReLU(512, out_channels, 3, 2, 1, relu=relu, momentum=momentum)),
            ('26_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(out_channels, 512, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(512, out_channels, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('27_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(out_channels, 512, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(512, out_channels, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('28_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(out_channels, 512, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(512, out_channels, 3, 1, 1, relu=relu, momentum=momentum),
            )),
            ('29_residual',         lnl.Residual(
                                    lnl.Conv2dBatchReLU(out_channels, 512, 1, 1, 0, relu=relu, momentum=momentum),
                                    lnl.Conv2dBatchReLU(512, out_channels, 3, 1, 1, relu=relu, momentum=momentum),
            )),
        )
