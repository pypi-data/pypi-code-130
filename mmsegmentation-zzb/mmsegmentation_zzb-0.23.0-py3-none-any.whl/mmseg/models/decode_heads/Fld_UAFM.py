import torch
import torch.nn as nn
from mmcv.cnn import ConvModule
from mmseg.ops import resize
from mmseg.models.decode_heads import SPPMHead,PSPHead
from mmseg.models.decode_heads.decode_head import BaseDecodeHead
from mmseg.models.builder import HEADS
class ChannelAttention(nn.Module):
    def __init__(self, in_channels):
        super(ChannelAttention, self).__init__()
        self.max = nn.AdaptiveMaxPool2d(1)
        self.avg = nn.AdaptiveAvgPool2d(1)
        self.mlp = ConvModule(in_channels=in_channels*4, out_channels=in_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x1, x2):
        x1 = resize(x1, size=x2.size()[2:], mode='bilinear')
        result1_max = self.max(x1)
        result1_avg = self.avg(x1)
        result2_max = self.max(x2)
        result2_avg = self.avg(x2)
        x = torch.cat([result1_max, result1_avg, result2_max, result2_avg], dim=1)
        x = self.mlp(x)
        x = self.sigmoid(x)
        out = (x * x1) + ((1-x) * x2)
        return out

class SpatialAttention(nn.Module):
    def __init__(self, in_channels):
        super(SpatialAttention, self).__init__()
        self.mlp = ConvModule(in_channels=4, out_channels=1, kernel_size=1,
                              norm_cfg=dict(type='BN', eps=0.001, requires_grad=True))
        self.sigmoid = nn.Sigmoid()

    def forward(self, x1, x2):
        # print(x1)
        x1 = resize(x1, size=x2.size()[2:], mode='bilinear')
        result1_max, _ = torch.max(x1, dim=1, keepdim=True)
        result1_avg = torch.mean(x1, dim=1,  keepdim=True)
        result2_max, _ = torch.max(x2, dim=1, keepdim=True)
        result2_avg = torch.mean(x2, dim=1, keepdim=True)
        x = torch.cat([result1_max, result1_avg, result2_max, result2_avg], dim=1)
        x = self.mlp(x)
        x = self.sigmoid(x)
        out = (x * x1) + ((1-x) * x2)
        return out

@HEADS.register_module()
class FldUAFMHead(BaseDecodeHead):
    def __init__(self, **kwargs):
        super(FldUAFMHead, self).__init__(**kwargs)
        self.conv1 = ConvModule(in_channels=self.in_channels[-1], out_channels=self.in_channels[-1] // 8, kernel_size=1,
                                norm_cfg=dict(type='BN', eps=0.001, requires_grad=True))
        self.conv2 = ConvModule(in_channels=self.in_channels[-2], out_channels=self.in_channels[-2] // 8, kernel_size=1,
                                norm_cfg=dict(type='BN', eps=0.001, requires_grad=True))
        self.conv3 = ConvModule(in_channels=self.in_channels[-3], out_channels=self.in_channels[-3] // 8, kernel_size=1,
                                norm_cfg=dict(type='BN', eps=0.001, requires_grad=True))
        # self.conv1 = nn.Conv2d(in_channels=1024, out_channels=128, kernel_size=1)
        # self.conv2 = nn.Conv2d(in_channels=512, out_channels=64, kernel_size=1)
        # self.conv3 = nn.Conv2d(in_channels=256, out_channels=32, kernel_size=1)
        self.conv4 = nn.Conv2d(in_channels=self.in_channels[-2] // 8, out_channels=self.in_channels[-3] // 8,kernel_size=1)
        self.sppm = SPPMHead(in_channels=self.in_channels[-1] // 8, channels=self.in_channels[-2] // 8, num_classes=19,in_index=0,pool_scales=(1, 2, 4))#num_classes没有用

        self.UAFM_last = SpatialAttention(in_channels=self.in_channels[-2] // 8)
        self.UAFM_penultimate = SpatialAttention(in_channels=self.in_channels[-3] // 8)

    def forward(self, inputs):
        inputs = self._transform_inputs(inputs)
        x = self.conv1(inputs[-1])#1024->128
        x = self.sppm([x])#128->64
        x_penultimate = self.conv2(inputs[-2])
        x = self.UAFM_last(x, x_penultimate)#3,64,64,64
        x = self.conv4(x)#64->32
        x_last_three = self.conv3(inputs[-3])
        x = self.UAFM_penultimate(x, x_last_three)
        return self.cls_seg(x)

# bisenetse = FldUAFMHead(in_channels=(256,512,1024),channels=32,
#                         num_classes=21,in_index=(0,1,2),input_transform='multiple_select')
# # from torchstat import stat
# # stat(bisenetse, (1,3, 224, 224))
# x = [torch.rand(3,256,128,128),torch.rand(3,512,64,64),torch.rand(3,1024,64,64)]
# y = bisenetse(x)



