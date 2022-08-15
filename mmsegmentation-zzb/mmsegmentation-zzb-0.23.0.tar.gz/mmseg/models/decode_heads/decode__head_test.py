import torch
from mmseg.models import decode_heads
from mmseg.models import backbones
# mobilenetv3 = backbones.MyMobileNetV3(arch='large',out_indices=(1,3,16))
# input = torch.rand(1,3,224,224)
# # # out = mobilenetv3(input)
# sppm_head = decode_heads.SPPMHead(pool_scales=(2,3,6),in_channels=960,channels=128,num_classes=21,align_corners=False)
# # print(sppm)
# x = [torch.rand(1,960,28,28)]
# y = sppm_head(x)
# print(y.shape)
#
# lite_aspp = decode_heads.LiteASPPHead(dilations=(4, 6),in_channels=960,channels=128,num_classes=21)
# x = [torch.rand(1,960,28,28)]
# y = lite_aspp(x)
# print(y.shape)
# lraspp = decode_heads.LRASPPHead(in_channels=(64,112,960),channels=128,num_classes=2,input_transform='multiple_select',in_index=(0,1,2))
# x = [torch.rand(1,64,128,128),torch.rand(1,112,64,64),torch.rand(1,960,64,64)]
# y = lraspp(x)
# print(y.shape)
# mobilenet_aspp = decode_heads.MobilenetASPP(in_channels=(24,40,112,960),channels=40,input_transform='multiple_select',num_classes=21,in_index=(0,1,2,3))

# y = mobilenet_aspp(x)
# print(y.shape)

# from mmseg.models.decode_heads.cross_se import SELayer,CrossSEHead,CrossSe
# selayer = SELayer(channels=40, squeeze_channels=None, ratio=16, divisor=8, return_weight=True)
# cross_se = CrossSe(in_channels=(24,40,112,960),channels=24,input_transform='multiple_select',num_classes=21,in_index=(0,1,2,3))
# x = [torch.rand(1,24,128,128),torch.rand(1,40,64,64), torch.rand(1,112,32,32), torch.rand(1,960,16,16)]
# y = cross_se(x)
# print(y.shape)
# ge = decode_heads.GELayer(in_channels=3, out_channels=3, extent=0,extra_params=True,
#              use_mlp=False,stride=3,spatial=16,ration=16,conv_cfg=dict(type='conv2d'))
# x = torch.rand(1,3,224,224)
# y = ge(x)
# print(y.shape)

# bisenetse = decode_heads.FldUAFMHead(in_channels=(256,512,1024),channels=128,
#                                                 num_classes=21,in_index=(0,1,2),input_transform='multiple_select')
# # from torchstat import stat
# # stat(bisenetse, (1,3, 224, 224))
# x = [torch.rand(1,256,128,128),torch.rand(1,512,64,64),torch.rand(1,1024,64,64)]
# y = bisenetse(x)
# from mmseg.models.decode_heads.cross_cbam_bisenet import ChannelAttention,SpatialAttention,CrosseCbamHead
# channe = CrosseCbamHead(in_channels=(256,512,2014),channels=128,in_index=(0,1,2),num_classes=19,
#                         input_transform='multiple_select')
# x = [torch.rand(1,256,64,64),torch.rand(1,512,32,32),torch.rand(1,1024,16,16)]
# print(channe(x).shape)
from mmseg.models.decode_heads import SeASPPHead
seaspp = SeASPPHead(dilations=(1, 3),in_channels=1024, channels=512, num_classes=19)
x = torch.rand(1, 1024, 64, 64)
y = seaspp([x])
print(y.shape)


