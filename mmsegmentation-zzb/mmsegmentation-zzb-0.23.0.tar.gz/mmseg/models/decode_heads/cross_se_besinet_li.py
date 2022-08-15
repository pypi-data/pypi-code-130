# import mmcv
# import torch
# import torch.nn as nn
# from mmcv import is_tuple_of
# from mmcv.cnn import ConvModule
# from mmcv.runner import BaseModule
# from mmseg.models.decode_heads import LiteASPPHead
# from mmseg.ops import resize
# from ..builder import HEADS
# from .decode_head import BaseDecodeHead
#
# def make_divisible(value, divisor, min_value=None, min_ratio=0.9):
#     """Make divisible function.
#
#     This function rounds the channel number down to the nearest value that can
#     be divisible by the divisor.
#
#     Args:
#         value (int): The original channel number.
#         divisor (int): The divisor to fully divide the channel number.
#         min_value (int, optional): The minimum value of the output channel.
#             Default: None, means that the minimum value equal to the divisor.
#         min_ratio (float): The minimum ratio of the rounded channel
#             number to the original channel number. Default: 0.9.
#     Returns:
#         int: The modified output channel number
#     """
#
#     if min_value is None:
#         min_value = divisor
#     new_value = max(min_value, int(value + divisor / 2) // divisor * divisor)
#     # Make sure that round down does not go down by more than (1-min_ratio).
#     if new_value < min_ratio * value:
#         new_value += divisor
#     return new_value
# class SELayer(BaseModule):
#     """Squeeze-and-Excitation Module.
#
#     Args:
#         channels (int): The input (and output) channels of the SE layer.
#         squeeze_channels (None or int): The intermediate channel number of
#             SElayer. Default: None, means the value of ``squeeze_channels``
#             is ``make_divisible(channels // ratio, divisor)``.
#         ratio (int): Squeeze ratio in SELayer, the intermediate channel will
#             be ``make_divisible(channels // ratio, divisor)``. Only used when
#             ``squeeze_channels`` is None. Default: 16.
#         divisor(int): The divisor to true divide the channel number. Only
#             used when ``squeeze_channels`` is None. Default: 8.
#         conv_cfg (None or dict): Config dict for convolution layer. Default:
#             None, which means using conv2d.
#         return_weight(bool): Whether to return the weight. Default: False.
#         act_cfg (dict or Sequence[dict]): Config dict for activation layer.
#             If act_cfg is a dict, two activation layers will be configurated
#             by this dict. If act_cfg is a sequence of dicts, the first
#             activation layer will be configurated by the first dict and the
#             second activation layer will be configurated by the second dict.
#             Default: (dict(type='ReLU'), dict(type='Sigmoid'))
#     """
#
#     def __init__(self,
#                  channels,
#                  squeeze_channels=None,
#                  ratio=16,
#                  divisor=8,
#                  bias='auto',
#                  conv_cfg=None,
#                  act_cfg=(dict(type='ReLU'), dict(type='Sigmoid')),
#                  return_weight=True,
#                  init_cfg=None):
#         super(SELayer, self).__init__(init_cfg)
#         if isinstance(act_cfg, dict):
#             act_cfg = (act_cfg, act_cfg)
#         assert len(act_cfg) == 2
#         assert mmcv.is_tuple_of(act_cfg, dict)
#         self.global_avgpool = nn.AdaptiveAvgPool2d(1)
#         if squeeze_channels is None:
#             squeeze_channels = make_divisible(channels // ratio, divisor)
#         assert isinstance(squeeze_channels, int) and squeeze_channels > 0, \
#             '"squeeze_channels" should be a positive integer, but get ' + \
#             f'{squeeze_channels} instead.'
#         self.return_weight = return_weight
#         self.conv1 = ConvModule(
#             in_channels=channels,
#             out_channels=squeeze_channels,
#             kernel_size=1,
#             stride=1,
#             bias=bias,
#             conv_cfg=conv_cfg,
#             act_cfg=act_cfg[0])
#         self.conv2 = ConvModule(
#             in_channels=squeeze_channels,
#             out_channels=channels,
#             kernel_size=1,
#             stride=1,
#             bias=bias,
#             conv_cfg=conv_cfg,
#             act_cfg=act_cfg[1])
#
#     def forward(self, x):
#         out = self.global_avgpool(x)
#         out = self.conv1(out)
#         out = self.conv2(out)
#         if self.return_weight:
#             return out
#         else:
#             return x * out
# class CrossSEHead(nn.Module):
#     def __init__(self,
#                  in_channels,
#                  ):
#         super(CrossSEHead, self).__init__()
#         self.in_channels = in_channels
#
#         self.se_liteaspp = SELayer(in_channels)
#         self.se_up = SELayer(in_channels)
#     def forward(self,x_liteaspp,x_up):
#         x1 = self.se_liteaspp(x_liteaspp)#liteaspp输出经过se层
#         x2 = self.se_up(x_up)#上采样输出经过se层
#         x1 = x1 * x_up
#         x2 = x2 * x_liteaspp
#         out = x1 + x2
#         return out
#
#
# @HEADS.register_module()
# class LiteAsppCrossSeBisenet(BaseDecodeHead):
#     def __init__(self, dilations=(2, 4), **kwargs):
#         super(LiteAsppCrossSeBisenet, self).__init__(**kwargs)
#         self.dilations = dilations
#         self.last_conv = nn.Conv2d(in_channels=512, out_channels=256, kernel_size=1, stride=1)
#         # self.penultimate_conv = nn.Conv2d(in_channels=256, out_channels=128, kernel_size=1, stride=1)
#         # self.bottom_third_conv = nn.Conv2d(in_channels=40, out_channels=24, kernel_size=1, stride=1)
#
#         self.last_liteaspp = LiteASPPHead(dilations, in_channels=1024, channels=512, num_classes=21)
#         self.penultimate_liteaspp = LiteASPPHead(dilations, in_channels=512, channels=512, num_classes=21)
#         self.bottom_third_liteaspp = LiteASPPHead(dilations, in_channels=256, channels=256, num_classes=21)
#         # self.bottom_fourth_liteaspp = LiteASPPHead(dilations, in_channels=24, channels=24, num_classes=21)
#
#         self.last_cross_se = CrossSEHead(in_channels=512)
#         self.penultimate_cross_se = CrossSEHead(in_channels=256)
#         # self.bottom_third_cross_Se = CrossSEHead(in_channels=24)
#
#     def forward(self, inputs):
#         inputs = self._transform_inputs(inputs)
#         x = inputs[-1]
#         # print(f"x[-1]={x.shape}")
#         # last_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x.size()[1],channels=512,num_classes=21)
#         x = self.last_liteaspp([x])#1024->512, 16
#         # print(f"x_last_liteaspp={x.shape}")
#         # x = self.last_conv(x)
#         x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=self.align_corners)#upsample to 32
#
#         x_penultimate = inputs[-2]
#         # penultimate_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_penultimate.size()[1],channels=112,num_classes=21)
#         x_penultimate = self.penultimate_liteaspp([x_penultimate])
#         # print(f"x_penultimate.shape={x_penultimate.shape}")
#         x = self.last_cross_se(x, x_penultimate)
#
#         x = self.last_conv(x)#512->256
#
#         # print(f"x.shape={x.shape}")
#         x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=self.align_corners)#up to 64
#         # print(f"x.resize={x.shape}")
#
#         x_bottom_third = inputs[-3]
#         # bottom_third_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_bottom_third.size()[1],channels=40,num_classes=21)
#         x_bottom_third = self.bottom_third_liteaspp([x_bottom_third])
#         # print(f"x_bottom_third={x_bottom_third.shape}")
#         x = self.penultimate_cross_se(x, x_bottom_third)
#         # print(f"x_bottom_third.cat={x.shape}")
#         # x = self.bottom_third_conv(x)  # 80->16
#
#         # print(f"x.={x.shape}")
#         # x = resize(x, size=inputs[-4].size()[2:], mode='bilinear', align_corners=self.align_corners)
#         #
#         # x_bottom_fourth = inputs[-4]
#         # bottom_fourth_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_bottom_fourth.size()[1],channels=24,num_classes=21)
#         # x_bottom_fourth = self.bottom_fourth_liteaspp([x_bottom_fourth])
#
#         # x = self.bottom_third_cross_Se(x, x_bottom_fourth)
#         # print(f"x.fourth.cat={x.shape}")
#         return self.cls_seg(x)

import mmcv
import torch
import torch.nn as nn
from mmcv import is_tuple_of
from mmcv.cnn import ConvModule
from mmcv.runner import BaseModule
from mmseg.models.decode_heads import LiteASPPHead
from mmseg.ops import resize
from ..builder import HEADS
from .decode_head import BaseDecodeHead

def make_divisible(value, divisor, min_value=None, min_ratio=0.9):
    """Make divisible function.

    This function rounds the channel number down to the nearest value that can
    be divisible by the divisor.

    Args:
        value (int): The original channel number.
        divisor (int): The divisor to fully divide the channel number.
        min_value (int, optional): The minimum value of the output channel.
            Default: None, means that the minimum value equal to the divisor.
        min_ratio (float): The minimum ratio of the rounded channel
            number to the original channel number. Default: 0.9.
    Returns:
        int: The modified output channel number
    """

    if min_value is None:
        min_value = divisor
    new_value = max(min_value, int(value + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than (1-min_ratio).
    if new_value < min_ratio * value:
        new_value += divisor
    return new_value
class SELayer(BaseModule):
    """Squeeze-and-Excitation Module.

    Args:
        channels (int): The input (and output) channels of the SE layer.
        squeeze_channels (None or int): The intermediate channel number of
            SElayer. Default: None, means the value of ``squeeze_channels``
            is ``make_divisible(channels // ratio, divisor)``.
        ratio (int): Squeeze ratio in SELayer, the intermediate channel will
            be ``make_divisible(channels // ratio, divisor)``. Only used when
            ``squeeze_channels`` is None. Default: 16.
        divisor(int): The divisor to true divide the channel number. Only
            used when ``squeeze_channels`` is None. Default: 8.
        conv_cfg (None or dict): Config dict for convolution layer. Default:
            None, which means using conv2d.
        return_weight(bool): Whether to return the weight. Default: False.
        act_cfg (dict or Sequence[dict]): Config dict for activation layer.
            If act_cfg is a dict, two activation layers will be configurated
            by this dict. If act_cfg is a sequence of dicts, the first
            activation layer will be configurated by the first dict and the
            second activation layer will be configurated by the second dict.
            Default: (dict(type='ReLU'), dict(type='Sigmoid'))
    """

    def __init__(self,
                 channels,
                 squeeze_channels=None,
                 ratio=16,
                 divisor=8,
                 bias='auto',
                 conv_cfg=None,
                 act_cfg=(dict(type='ReLU'), dict(type='Sigmoid')),
                 return_weight=True,
                 init_cfg=None):
        super(SELayer, self).__init__(init_cfg)
        if isinstance(act_cfg, dict):
            act_cfg = (act_cfg, act_cfg)
        assert len(act_cfg) == 2
        assert mmcv.is_tuple_of(act_cfg, dict)
        self.global_avgpool = nn.AdaptiveAvgPool2d(1)
        if squeeze_channels is None:
            squeeze_channels = make_divisible(channels // ratio, divisor)
        assert isinstance(squeeze_channels, int) and squeeze_channels > 0, \
            '"squeeze_channels" should be a positive integer, but get ' + \
            f'{squeeze_channels} instead.'
        self.return_weight = return_weight
        self.conv1 = ConvModule(
            in_channels=channels,
            out_channels=squeeze_channels,
            kernel_size=1,
            stride=1,
            bias=bias,
            conv_cfg=conv_cfg,
            act_cfg=act_cfg[0])
        self.conv2 = ConvModule(
            in_channels=squeeze_channels,
            out_channels=channels,
            kernel_size=1,
            stride=1,
            bias=bias,
            conv_cfg=conv_cfg,
            act_cfg=act_cfg[1])

    def forward(self, x):
        out = self.global_avgpool(x)
        out = self.conv1(out)
        out = self.conv2(out)
        if self.return_weight:
            return out
        else:
            return x * out
class CrossSEHead(nn.Module):
    def __init__(self,
                 in_channels,
                 ):
        super(CrossSEHead, self).__init__()
        self.in_channels = in_channels

        self.se_liteaspp = SELayer(in_channels)
        self.se_up = SELayer(in_channels)
    def forward(self,x_liteaspp,x_up):
        x1 = self.se_liteaspp(x_liteaspp)#liteaspp输出经过se层
        x2 = self.se_up(x_up)#上采样输出经过se层
        x1 = x1 * x_up
        x2 = x2 * x_liteaspp
        out = x1 + x2
        return out


@HEADS.register_module()
class LiteAsppCrossSeBisenetLi(BaseDecodeHead):
    def __init__(self, dilations=(1,3), **kwargs):
        super(LiteAsppCrossSeBisenetLi, self).__init__(**kwargs)
        self.dilations = dilations
        self.last_conv = nn.Conv2d(in_channels=512, out_channels=256, kernel_size=1, stride=1)
        # self.penultimate_conv = nn.Conv2d(in_channels=256, out_channels=128, kernel_size=1, stride=1)
        # self.bottom_third_conv = nn.Conv2d(in_channels=40, out_channels=24, kernel_size=1, stride=1)

        self.last_liteaspp = LiteASPPHead(dilations, in_channels=1024, channels=512, num_classes=21)


        self.last_cross_se = CrossSEHead(in_channels=512)
        self.penultimate_cross_se = CrossSEHead(in_channels=256)
        # self.bottom_third_cross_Se = CrossSEHead(in_channels=24)

    def forward(self, inputs):
        inputs = self._transform_inputs(inputs)
        x = inputs[-1]
        x = self.last_liteaspp([x])#1024->512, 16

        x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=self.align_corners)#upsample to 32

        x_penultimate = inputs[-2]

        # x_penultimate = self.penultimate_liteaspp([x_penultimate])

        x = self.last_cross_se(x, x_penultimate)
        x = self.last_conv(x)#512->256

        x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=self.align_corners)#up to 64


        x_bottom_third = inputs[-3]

        # x_bottom_third = self.bottom_third_liteaspp([x_bottom_third])

        x = self.penultimate_cross_se(x, x_bottom_third)

        return self.cls_seg(x)