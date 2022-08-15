from mmseg.models import backbones
from torchstat import stat
import torch
import torch.nn as nn
# mymobilenetv3_small = backbones.MyMobileNetV3(arch='small',out_indices=(3,6,9,13),)
# mymobilenetv3_large = backbones.MyMobileNetV3(arch='large',out_indices=(3,6,9,13),)
# mobilenetv3 = backbones.MobileNetV3(arch='large',out_indices=(1,3,16))
# # stat(mymobilenetv3,(3,224,224))
# # stat(mobilenetv3,(3,224,224))
# # print(mymobilenetv3)
# x = torch.rand(4,3,512,512)
# y_small = mymobilenetv3_small(x)
# # print(y_small)
# y_large = mymobilenetv3_large(x)
# # print(y[0],y[1],y[2])
#
# print(y_small[0].shape,y_small[1].shape,y_small[2].shape,y_small[3].shape)
# print(y_large[0].shape,y_large[1].shape,y_large[2].shape,y_large[3].shape)
from mmseg.models.backbones.ddrnet import BasicBlock
# ddrnet = backbones.DualResNet(depth=18, num_stages=2, out_indices=(0, 1,), strides=(1,2),style='pytorch',dilations=(1,1))
# print(ddrnet)
# x = torch.rand(2, 3, 512, 512)
# y = ddrnet(x)
# print(y[0].shape, y[1].shape)

# resnet18 = backbones.ResNetV1c(depth=18, num_stages=4, out_indices=(0, 1, 2, 3,), strides=(1,2,2,2),style='pytorch')
# # print(resnet18)
# x = torch.rand(1, 3, 224, 224)
# y = resnet18(x)
# print(y[0].shape, y[1].shape, y[2]act_cfg=dict(type='ReLU'),.shape, y[3].shape,)
norm_cfg = dict(type='BN', requires_grad=True)
stdc = backbones.STDCNet(stdc_type='STDCNet1',in_channels=3,channels=(32, 64, 256, 512, 1024),
                         bottleneck_type='cat',norm_cfg=norm_cfg,act_cfg=dict(type='ReLU'),)

x = torch.rand(1, 3, 512, 512)
y = stdc(x)
print(y[0].shape,y[1].shape,y[2].shape,)