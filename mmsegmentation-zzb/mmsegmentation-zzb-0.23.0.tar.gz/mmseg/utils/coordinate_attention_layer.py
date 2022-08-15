import torch
import torch.nn as nn
from mmcv.cnn import ConvModule, build_conv_layer
class CoodinateAttLayer(nn.Module):#in_channels and out_channels must be same
    def __init__(self, in_channels, out_channels, reduction=4, ):
        super(CoodinateAttLayer, self).__init__()
        self.h_pool = nn.AdaptiveAvgPool2d((None, 1))
        self.w_pool = nn.AdaptiveAvgPool2d((1, None))
        self.out_channels = max(8, in_channels // reduction)
        self.conv_bn_relu = ConvModule(in_channels=in_channels,
                                       out_channels=self.out_channels,
                                       kernel_size=1,
                                       norm_cfg=dict(type='BN')
                                       )
        self.conv1 = build_conv_layer(in_channels=self.out_channels,
                                      out_channels=out_channels,
                                      kernel_size=1,
                                      cfg=None,
                                      )
        self.conv2 = build_conv_layer(in_channels=self.out_channels,
                                      out_channels=in_channels,
                                      kernel_size=1,
                                      cfg=None,
                                      )

    def forward(self, x1, x2):
        x = torch.cat([x1, x2], dim=1)
        orignal = x
        b, c, h, w = x.size()
        x_h = self.h_pool(x).permute(0, 1, 3, 2) # 将h,w换一下
        x_w = self.w_pool(x)
        x = torch.cat([x_h, x_w], dim=3)

        x = self.conv_bn_relu(x)
        x_h, x_w = torch.split(x, [h, w], dim=3)
        x_h = x_h.permute(0, 1, 3, 2)
        x_h = self.conv1(x_h).sigmoid()
        x_w = self.conv2(x_w).sigmoid()
        out = orignal * x_h * x_w
        return out


coordinate_layer = CoodinateAttLayer(in_channels=38, out_channels=38)
x = torch.rand(1, 24, 224, 224)
x1 = torch.rand(1,14, 224, 224)
y = coordinate_layer(x, x1)
print(y[0].shape)

