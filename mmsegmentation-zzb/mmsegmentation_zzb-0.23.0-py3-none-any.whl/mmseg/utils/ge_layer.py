# Copyright (c) Ethan. All rights reserved.
import torch
from mmcv.cnn import build_conv_layer, build_norm_layer
from mmcv.runner import Sequential
from torch import nn as nn
from mmcv.cnn import ConvModule
from mmseg.ops import resize
class Identity(nn.Module):
    def __init__(self):
        super(Identity, self).__init__()

    def forward(self, x):
        return x
class GELayer(nn.Module):
    """Gather-Excitation Module.

        Args:
            channels (int): The input (and output) channels of the GE layer.
            ratio (int): Squeeze ratio in GELayer, the intermediate channel will be
                ``int(channels/ratio)``. Default: 16.
            conv_cfg (None or dict): Config dict for convolution layer.
                Default: None, which means using conv2d.
            act_cfg (dict or Sequence[dict]): Config dict for activation layer.
                If act_cfg is a dict, two activation layers will be configured
                by this dict. If act_cfg is a sequence of dicts, the first
                activation layer will be configured by the first dict and the
                second activation layer will be configured by the second dict.
                Default: (dict(type='ReLU'), dict(type='HSigmoid', bias=3.0,
                divisor=6.0)).
        """
    def __init__(self,
                 # in_channels,
                 out_channels, extent, extra_params, use_mlp, stride, spatial,
                 ration,
                 norm_cfg=nn.BatchNorm2d,
                 ):
        super(GELayer, self).__init__()
        self.norm_cfg = norm_cfg,
        # self.bn1 = nn.BatchNorm2d(in_channels)
        # self.relu1 = nn.ReLU(inplace=True)
        # self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride,
        #                        padding=1, bias=False)
        # self.bn2 = nn.BatchNorm2d(out_channels)
        # self.relu2 = nn.ReLU(inplace=True)
        # self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1,
        #                        padding=1, bias=False)
        # self.equalInOut = (in_channels == out_channels)
        # self.convShortcut = (not self.equalInOut) and nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride,
        #                                                         padding=0, bias=False) or None

        self.extent = extent

        if extra_params is True:
            if extent == 0:
                # Global DW Conv + BN
                self.downop = ConvModule(in_channels=out_channels, out_channels=out_channels, kernel_size=spatial, stride=2, padding=1,
                                         groups=out_channels, norm_cfg=dict(type='BN'))
            elif extent == 2:
                self.downop = ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                         groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1),

            elif extent == 4:
                self.downop = nn.Sequential(ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                                       groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1),
                                            ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                                       groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1),)
            elif extent == 8:
                self.downop = nn.Sequential(ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                                       groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1),
                                            ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                                       groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1),
                                            ConvModule(in_channels=out_channels, out_channels=out_channels,kernel_size=3,
                                                       groups=out_channels, norm_cfg=dict(type='BN'), stride=2, padding=1))

            else:

                raise NotImplementedError('Extent must be 0,2,4 or 8 for now')
        else:
            if extent == 0:
                self.downop = nn.AdaptiveAvgPool2d(1)
            else:
                self.downop = nn.AdaptiveAvgPool2d(spatial // extent)
        if use_mlp:
            self.mlp = nn.Sequential(nn.Conv2d(out_channels, out_channels // 16, kernel_size=1, padding=0, bias=False),
                                     nn.ReLU(),
                                     nn.Conv2d(out_channels // 16, out_channels, kernel_size=1, padding=0, bias=False),
                                     )
        else:
            self.mlp = Identity()

    def forward(self, input):

        # x = self.relu2(self.bn2(self.conv1(input)))
        # out = self.conv2(x)
        out = self.downop(input)
        out = self.mlp(out)
        out = resize(out, size=input.size()[2:], mode='bilinear',)
        out = torch.sigmoid(out)
        return out * input

ge = GELayer(out_channels=3, extent=8,extra_params=True,
             use_mlp=False,stride=3,spatial=16,ration=16,)
# import numpy as np
# from PIL import Image
# from torchvision import transforms
# im = Image.open('E:/AI/project/mmsegmentation/bochum_000000_000313_leftImg8bit.png')
# to_tensor = transforms.ToTensor()
# im = to_tensor(im)
# resize = transforms.Resize([1024,1024])
# im = resize(im)
# # im = np.transpose(im)
# im = torch.tensor(im)
# im = torch.unsqueeze(im,0)
# print(im.shape,im)
x = torch.rand(1,3,224,224)
y = ge(x)
print(y.shape)