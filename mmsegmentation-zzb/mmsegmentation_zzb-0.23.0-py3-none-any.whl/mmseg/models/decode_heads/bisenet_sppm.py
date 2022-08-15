# Copyright (c) OpenMMLab. All rights reserved.
import torch
import torch.nn as nn
from mmcv import is_tuple_of
from mmcv.cnn import ConvModule
from mmseg.models.decode_heads import LiteASPPHead
from mmseg.ops import resize
from ..builder import HEADS
from .decode_head import BaseDecodeHead

@HEADS.register_module()
class BiseNetASPPHead(BaseDecodeHead):
    def __init__(self, dilations=(2, 4), **kwargs):
        super(BiseNetASPPHead, self).__init__(**kwargs)
        self.dilations = dilations
        # self.last_conv = nn.Conv2d(in_channels=512, out_channels=112, kernel_size=1, stride=1)
        self.penultimate = nn.Conv2d(in_channels=1024, out_channels=256, kernel_size=1, stride=1)
        self.bottom_third = nn.Conv2d(in_channels=512, out_channels=256, kernel_size=1, stride=1)

        self.last_liteaspp = LiteASPPHead(dilations, in_channels=1024, channels=512, num_classes=21)
        self.penultimate_liteaspp = LiteASPPHead(dilations, in_channels=512, channels=512, num_classes=21)
        self.bottom_third_liteaspp = LiteASPPHead(dilations, in_channels=256, channels=256, num_classes=21)
        # self.bottom_fourth_liteaspp = LiteASPPHead(dilations, in_channels=24, channels=24, num_classes=21)
    # def init_weights(self):
    #     pass
    def forward(self, inputs):
        inputs = self._transform_inputs(inputs)
        x = inputs[-1]
        # print(f"x[-1]={x.shape}")
        # last_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x.size()[1],channels=512,num_classes=21)
        x = self.last_liteaspp([x])
        # print(f"x_last_liteaspp={x.shape}")
        # x = self.last_conv(x)
        x = resize(x, size=inputs[-2].size()[2:], mode='bilinear', align_corners=self.align_corners)

        x_penultimate = inputs[-2]
        # penultimate_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_penultimate.size()[1],channels=112,num_classes=21)
        x_penultimate = self.penultimate_liteaspp([x_penultimate])
        # print(f"x_penultimate.shape={x_penultimate.shape}")
        x = torch.cat([x, x_penultimate], 1)

        x = self.penultimate(x)

        # print(f"x.shape={x.shape}")
        x = resize(x, size=inputs[-3].size()[2:], mode='bilinear', align_corners=self.align_corners)
        # print(f"x.resize={x.shape}")

        x_bottom_third = inputs[-3]
        # bottom_third_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_bottom_third.size()[1],channels=40,num_classes=21)
        x_bottom_third = self.bottom_third_liteaspp([x_bottom_third])
        # print(f"x_bottom_third={x_bottom_third.shape}")
        x = torch.cat([x,x_bottom_third],1)
        # print(f"x_bottom_third.cat={x.shape}")
        x = self.bottom_third(x)#512->256

        # print(f"x.={x.shape}")
        # x =resize(x,size=inputs[-4].size()[2:],mode='bilinear',align_corners=self.align_corners)
        #
        # x_bottom_fourth = inputs[-4]
        # bottom_fourth_liteaspp = LiteASPPHead(dilations=(2,4),in_channels=x_bottom_fourth.size()[1],channels=24,num_classes=21)
        # x_bottom_fourth = self.bottom_fourth_liteaspp([x_bottom_fourth])

        # x = torch.cat([x,x_bottom_fourth],1)
        # print(f"x.fourth.cat={x.shape}")
        return self.cls_seg(x)



