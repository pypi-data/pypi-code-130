#
#   Cornernet Backbones
#   Copyright EAVISE
#
from collections import OrderedDict
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['Cornernet']


class Cornernet(BaseModule):
    """ Cornernet backbones.

    .. rubric:: Models:

    - :class:`~lightnet.models.Cornernet`
    - :class:`~lightnet.models.CornernetSqueeze`

    """
    @BaseModule.layers(named=True, classmethod=True, primary=True)
    def Default(cls, in_channels, out_channels):
        """
        Default Cornernet backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels

        Examples:
            >>> backbone = ln.network.backbone.Cornernet(3, 256)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 128, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_residual): Residual(...)
              (para): ParallelSum(
                (0): Sequential(
                  (3_hourglass): HourGlass(order=5, ...)
                  (4_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                  (5_conv): Conv2d(256, 256, kernel_size=(1, 1), stride=(1, 1), bias=False)
                  (6_batchnorm): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
                )
                (1): Sequential(
                  (7_conv): Conv2d(256, 256, kernel_size=(1, 1), stride=(1, 1), bias=False)
                  (8_batchnorm): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
                )
                (post): ReLU(inplace=True)
              )
              (9_residual): Residual(...)
              (10_hourglass): HourGlass(order=5, ...)
              (11_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 256, 160, 160])
        """
        return (
            ('1_convbatch',         lnl.Conv2dBatchReLU(in_channels, 128, 7, 2, 3)),
            ('2_residual',          cls.get_residual(128, 256, stride=2)),
            ('residual',            lnl.Residual(OrderedDict([
                ('3_hourglass',     cls.get_hourglass(cls.get_residual)),
                ('4_convbatch',     lnl.Conv2dBatchReLU(256, 256, 3, 1, 1)),
                ('5_convbatch',     lnl.Conv2dBatch(256, 256, 1, 1, 0)),
                ('skip',            lnl.Conv2dBatch(256, 256, 1, 1, 0)),
                ('post',            nn.ReLU(inplace=True)),
            ]))),
            ('6_residual',          cls.get_residual(256, 256)),
            ('7_hourglass',         cls.get_hourglass(cls.get_residual)),
            ('8_convbatch',         lnl.Conv2dBatchReLU(256, out_channels, 3, 1, 1)),
        )

    @BaseModule.layers(named=True, classmethod=True)
    def Squeeze(cls, in_channels, out_channels):
        """
        Cornernet Squeeze backbone.

        Args:
            in_channels (int): Number of input channels
            out_channels (int): Number of output channels

        Examples:
            >>> backbone = ln.network.backbone.Cornernet.Squeeze(3, 256)
            >>> print(backbone)     # doctest: +SKIP
            Sequential(
              (1_convbatch): Conv2dBatchReLU(3, 128, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), ReLU(inplace=True))
              (2_residual): Residual(...)
              (3_residual): Residual(...)
              (residual): Residual(
                (4_hourglass): HourGlass(order=4, ...)
                (5_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
                (6_convbatch): Conv2dBatch(256, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (skip): Conv2dBatch(256, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
                (post): ReLU(inplace=True)
              )
              (7_residual): Residual(...)
              (8_hourglass): HourGlass(order=4, ...)
              (9_convbatch): Conv2dBatchReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
            )
            >>> in_tensor = torch.rand(1, 3, 640, 640)
            >>> out_tensor = backbone(in_tensor)
            >>> print(out_tensor.shape)
            torch.Size([1, 256, 80, 80])
        """
        return (
            ('1_convbatch',         lnl.Conv2dBatchReLU(in_channels, 128, 7, 2, 3)),
            ('2_residual',          cls.get_residual(128, 256, stride=2)),
            ('3_residual',          cls.get_residual(256, 256, stride=2)),
            ('residual',            lnl.Residual(OrderedDict([
                ('4_hourglass',     cls.get_hourglass_squeeze(cls.get_fire)),
                ('5_convbatch',     lnl.Conv2dBatchReLU(256, 256, 3, 1, 1)),
                ('6_convbatch',     lnl.Conv2dBatch(256, 256, 1, 1, 0)),
                ('skip',            lnl.Conv2dBatch(256, 256, 1, 1, 0)),
                ('post',            nn.ReLU(inplace=True)),
            ]))),
            ('7_residual',          cls.get_residual(256, 256)),
            ('8_hourglass',         cls.get_hourglass_squeeze(cls.get_fire)),
            ('9_convbatch',         lnl.Conv2dBatchReLU(256, out_channels, 3, 1, 1)),
        )

    @staticmethod
    def get_residual(in_channels, out_channels, kernel=3, stride=1, padding=1):
        return lnl.Residual(
            nn.Conv2d(in_channels, out_channels, kernel, stride, padding, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel, 1, padding, bias=False),
            nn.BatchNorm2d(out_channels),

            skip=None if (in_channels == out_channels) and (stride == 1) else lnl.Conv2dBatch(in_channels, out_channels, 1, stride, 0),
            post=nn.ReLU(inplace=True),
        )

    @staticmethod
    def get_fire(in_channels, out_channels, kernel=3, stride=1, padding=1):
        layers = [
            nn.Conv2d(in_channels, out_channels // 2, 1, 1, 0, bias=False),
            nn.BatchNorm2d(out_channels // 2),
            lnl.ParallelCat(
                nn.Conv2d(out_channels // 2, out_channels // 2, 1, stride, 0, bias=False),
                nn.Conv2d(out_channels // 2, out_channels // 2, kernel, stride, padding, bias=False, groups=out_channels // 2),
            ),
            nn.BatchNorm2d(out_channels),
        ]

        if stride == 1 and in_channels == out_channels:
            return lnl.Residual(*layers, post=nn.ReLU(inplace=True))
        else:
            return nn.Sequential(*layers, nn.ReLU(inplace=True))

    @staticmethod
    def get_hourglass(residual):
        return lnl.HourGlass(
            5, [256, 256, 384, 384, 384, 512],
            make_upper=lambda ci, co: nn.Sequential(*[residual(ci, co) for _ in range(2)]),
            make_down1=lambda ci, co: nn.Sequential(residual(ci, co, stride=2), residual(co, co)),
            make_inner=lambda ci, co: nn.Sequential(*[residual(ci, co) for _ in range(4)]),
            make_down2=lambda ci, co: nn.Sequential(residual(ci, ci), residual(ci, co), nn.Upsample(scale_factor=2, mode='nearest')),
        )

    @staticmethod
    def get_hourglass_squeeze(residual):
        return lnl.HourGlass(
            4, [256, 256, 384, 384, 512],
            make_upper=lambda ci, co: nn.Sequential(*[residual(ci, co) for _ in range(2)]),
            make_down1=lambda ci, co: nn.Sequential(residual(ci, co, stride=2), residual(co, co)),
            make_inner=lambda ci, co: nn.Sequential(*[residual(ci, co) for _ in range(4)]),
            make_down2=lambda ci, co: nn.Sequential(residual(ci, ci), residual(ci, co), nn.ConvTranspose2d(co, co, 4, 2, 1)),
        )
