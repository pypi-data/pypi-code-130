#
#   Resnet Backbone
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn
from .. import layer as lnl
from ._resnet import Resnet

__all__ = ['DeformableResnet', 'ModulatedResnet']


class DeformableResnet(Resnet):
    """
    Resnet Backbone with deformable convolutions. |br|
    The convolutions in the blocks C3-C5 (original resnet naming) are replaced by deformable convolutions,
    as explained in :cite:`deformable_conv2`.
    """
    default_relu = partial(nn.ReLU, inplace=True)
    conv_type1 = nn.Conv2d
    conv_type2 = lnl.DeformableConv2d

    @classmethod
    def get_layers(cls, in_channels, out_channels, groups, relu=default_relu):
        get_block1 = cls.get_bottleneck(cls.conv_type1)
        get_block2 = cls.get_bottleneck(cls.conv_type2)

        return (
            # Conv1
            ('1_convbatch',         lnl.Conv2dBatchReLU(in_channels, 64, 7, 2, 3, relu=relu)),
            ('2_max',               nn.MaxPool2d(3, 2, 1)),

            # Conv 2_x
            ('3_residual',          get_block1(64, 64, 256, 1, relu)),
            ('4_residualgroup',     nn.Sequential(*(groups[0]*[get_block1(256, 64, 256, 1, relu)]))),

            # Conv 3_x
            ('5_residual',          get_block2(256, 128, 512, 2, relu)),
            ('6_residualgroup',     nn.Sequential(*(groups[1]*[get_block2(512, 128, 512, 1, relu)]))),

            # Conv 4_x
            ('7_residual',          get_block2(512, 256, 1024, 2, relu)),
            ('8_residualgroup',     nn.Sequential(*(groups[2]*[get_block2(1024, 256, 1024, 1, relu)]))),

            # Conv 5_x
            ('9_residual',          get_block2(1024, 512, out_channels, 2, relu)),
            ('10_residualgroup',    nn.Sequential(*(groups[3]*[get_block2(out_channels, 512, out_channels, 1, relu)]))),
        )

    @staticmethod
    def get_bottleneck(convtype):
        def bottleneck(in_channels, inter_channels, out_channels, stride, relu):
            return lnl.Residual(
                lnl.Conv2dBatchReLU(in_channels, inter_channels, 1, 1, 0, relu=relu, conv=convtype),
                lnl.Conv2dBatchReLU(inter_channels, inter_channels, 3, stride, 1, relu=relu, conv=convtype),
                lnl.Conv2dBatch(inter_channels, out_channels, 1, 1, 0, conv=convtype),

                skip=None if (in_channels == out_channels) and (stride == 1) else lnl.Conv2dBatch(in_channels, out_channels, 1, stride, 0, conv=convtype),
                post=relu(),
            )

        return bottleneck


class ModulatedResnet(DeformableResnet):
    """
    Resnet Backbone with modulated deformable convolutions. |br|
    The convolutions in the blocks C3-C5 (original resnet naming) are replaced by modulated deformable convolutions,
    as explained in :cite:`deformable_conv2`.
    """
    conv_type2 = lnl.ModulatedDeformableConv2d
