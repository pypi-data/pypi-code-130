import torch
import torch.nn as nn
from mmcv.cnn import ConvModule
from mmseg.ops import resize
from mmseg.models.decode_heads import SPPMHead, PSPHead
from mmseg.models.decode_heads import LiteASPPHead
from mmseg.models.decode_heads import SeASPPHead
from mmseg.models.decode_heads.decode_head import BaseDecodeHead
from mmseg.models.builder import HEADS
class ChannelAttention(nn.Module):
    def __init__(self, in_channels):
        super(ChannelAttention, self).__init__()
        self.max = nn.AdaptiveMaxPool2d(1)
        self.avg = nn.AdaptiveAvgPool2d(1)
        self.mlp1 = ConvModule(in_channels=in_channels, out_channels=in_channels // 16, kernel_size=1)
        # self.relu = nn.ReLU()
        self.mlp2 = ConvModule(in_channels=in_channels // 16, out_channels=in_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x1):
        result_max = self.max(x1)
        result_avg = self.avg(x1)
        # x = torch.cat([result_max, result_avg], dim=1)
        result_max = self.mlp2(self.mlp1(result_max))
        result_avg = self.mlp2(self.mlp1(result_avg))
        out = self.sigmoid(result_max+result_avg)
        return out

class SpatialAttention(nn.Module):
    def __init__(self):
        super(SpatialAttention, self).__init__()
        self.mlp = ConvModule(in_channels=2, out_channels=1, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x1):
        result_max, _ = torch.max(x1, dim=1, keepdim=True)
        result_avg = torch.mean(x1, dim=1,  keepdim=True)
        x = torch.cat([result_max, result_avg], dim=1)
        x = self.mlp(x)
        out = self.sigmoid(x)
        return out

class CrosseCbam(nn.Module):
    def __init__(self, in_channles):
        super(CrosseCbam, self).__init__()
        self.low_channel_attention = ChannelAttention(in_channels=in_channles)
        self.low_spatial_attention = SpatialAttention()
        self.high_channel_attention = ChannelAttention(in_channels=in_channles)
        self.high_spatial_attention = SpatialAttention()

    def forward(self, x1, x2):
        low_channel_output = self.low_channel_attention(x1)
        high_channel_output = self.high_channel_attention(x2)
        after_low_channel_out = x2 * low_channel_output
        after_high_channel_out = x1 * high_channel_output

        low_spatial_output = self.low_spatial_attention(after_low_channel_out)
        high_spatial_output = self.high_spatial_attention(after_high_channel_out)
        low_out = after_high_channel_out * low_spatial_output
        high_out = after_low_channel_out * high_spatial_output
        return low_out+high_out

# @HEADS.register_module()
# class CrosseCbamHead(BaseDecodeHead):
#     def __init__(self, dilations=(1, 3), **kwargs):
#         super(CrosseCbamHead, self).__init__(**kwargs)
#         # self.lite_aspp = LiteASPPHead(dilations=dilations, in_channels=1024, channels=512, num_classes=19)
#         self.lite_aspp = SeASPPHead(dilations=dilations, in_channels=1024, channels=512, num_classes=19)
#         self.last_crosse_cabm = CrosseCbam(in_channles=512)
#         self.penultimate_crosse_cbam = CrosseCbam(in_channles=256)
#
#         # self.last_conv = ConvModule(in_channels=1024, out_channels=512, kernel_size=1)
#         self.penultimate_conv = ConvModule(in_channels=512, out_channels=256, kernel_size=1, norm_cfg=self.norm_cfg)
#         self.bottom_three_conv = ConvModule(in_channels=256, out_channels=128, kernel_size=1, norm_cfg=self.norm_cfg)
#     def forward(self, inputs):
#         inputs = self._transform_inputs(inputs)
#         x = self.lite_aspp([inputs[-1]])
#         x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=False)
#         x = self.last_crosse_cabm(inputs[-2], x)
#         x = self.penultimate_conv(x)
#         x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=False)
#         x = self.penultimate_crosse_cbam(inputs[-3], x)
#         x = self.bottom_three_conv(x)
#         return self.cls_seg(x)
#         # return x

#channels-256
# @HEADS.register_module()
# class CrosseCbamHead(BaseDecodeHead):
#     def __init__(self, dilations=(1, 3), **kwargs):
#         super(CrosseCbamHead, self).__init__(**kwargs)
#         # self.lite_aspp = LiteASPPHead(dilations=dilations, in_channels=1024, channels=512, num_classes=19)
#         self.lite_aspp = SeASPPHead(dilations=dilations, in_channels=1024, channels=256, num_classes=19)
#         self.last_crosse_cabm = CrosseCbam(in_channles=256)
#         self.penultimate_crosse_cbam = CrosseCbam(in_channles=256)
#
#         # self.last_conv = ConvModule(in_channels=1024, out_channels=512, kernel_size=1)
#         self.penultimate_conv = ConvModule(in_channels=512, out_channels=256, kernel_size=1, norm_cfg=self.norm_cfg)
#         self.bottom_three_conv = ConvModule(in_channels=256, out_channels=128, kernel_size=1, norm_cfg=self.norm_cfg)
#     def forward(self, inputs):
#         inputs = self._transform_inputs(inputs)
#         x = self.lite_aspp([inputs[-1]])
#         x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=False)
#         x1 = self.penultimate_conv(inputs[-2])
#         x = self.last_crosse_cabm(x1, x)
#
#         x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=False)
#         x = self.penultimate_crosse_cbam(inputs[-3], x)
#         x = self.bottom_three_conv(x)
#         return self.cls_seg(x)
#         # return x

@HEADS.register_module()
class CrosseCbamHead(BaseDecodeHead):
    def __init__(self, dilations=(1, 3), **kwargs):
        super(CrosseCbamHead, self).__init__(**kwargs)
        # self.lite_aspp = LiteASPPHead(dilations=dilations, in_channels=1024, channels=512, num_classes=19)
        self.lite_aspp = SeASPPHead(dilations=dilations, in_channels=1024, channels=256, num_classes=19)
        self.last_crosse_cabm = CrosseCbam(in_channles=256)
        self.penultimate_crosse_cbam = CrosseCbam(in_channles=256)

        self.last_conv = ConvModule(in_channels=1024, out_channels=256, kernel_size=1, norm_cfg=self.norm_cfg)
        self.penultimate_conv = ConvModule(in_channels=512, out_channels=256, kernel_size=1, norm_cfg=self.norm_cfg)
        self.bottom_three_conv = ConvModule(in_channels=256, out_channels=128, kernel_size=1, norm_cfg=self.norm_cfg)
    def forward(self, inputs):
        inputs = self._transform_inputs(inputs)
        x = self.lite_aspp([inputs[-1]])
        # x = self.last_conv(inputs[-1])
        # x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=False)
        # x1 = self.penultimate_conv(inputs[-2])
        # x = self.last_crosse_cabm(x1, x)
        #
        # x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=False)
        # x = self.penultimate_crosse_cbam(inputs[-3], x)
        # x = self.bottom_three_conv(x)

        return self.cls_seg(x)
        # return x