import paddle
from paddle import nn
import numpy as np
from paddle.nn import functional as F
from ._common import get_actf,conv3x3,conv1x1

class deeper(nn.Layer):
    def __init__(self, num_c, mode='bilinear', pos='m', ini_c=0, act='relu'):
        super(deeper, self).__init__()
        actf = get_actf(act)
        if pos == 'm':
            self.dper = nn.Sequential(conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.Upsample(scale_factor=1 / 2, mode=mode), nn.BatchNorm(num_c), actf,
                                      conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm2D(num_c), actf)
        else:
            self.dper = nn.Sequential(conv3x3(in_channels=ini_c, out_channels=num_c),
                                      nn.Upsample(scale_factor=1 / 2, mode=mode), nn.BatchNorm(num_c), actf,
                                      conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm2D(num_c), actf)

    def forward(self, x):
        return self.dper(x)


class skiper(nn.Layer):
    def __init__(self, num_c, out_c=0, act='relu'):
        super(skiper, self).__init__()
        actf = get_actf(act)
        self.sper = nn.Sequential(conv3x3(in_channels=num_c, out_channels=out_c), nn.BatchNorm(out_c), actf)

    def forward(self, x):
        return self.sper(x)


class upper(nn.Layer):
    def __init__(self, num_c, mode='bilinear', pos='m', out_c=0, act='relu'):
        super(upper, self).__init__()
        actf = get_actf(act)
        if pos == 'm':
            self.uper = nn.Sequential(nn.BatchNorm2D(num_c), conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm(num_c), actf, conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm2D(num_c), actf, nn.Upsample(scale_factor=2, mode=mode))
        else:
            self.uper = nn.Sequential(nn.BatchNorm2D(num_c), conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm(num_c), actf, conv3x3(in_channels=num_c, out_channels=num_c),
                                      nn.BatchNorm2D(num_c), actf, nn.Upsample(scale_factor=2, mode=mode),
                                      conv3x3(num_c, out_c))

    def forward(self, x):
        return self.uper(x)


class uedcode(nn.Layer):
    def __init__(self, num_c, out_c, mode, pos='m', ini_c=0, act='leakyrelu'):
        super(uedcode, self).__init__()
        self.deeper1 = deeper(num_c, mode, pos=pos, ini_c=ini_c, act=act)
        self.skiper1 = skiper(num_c, out_c, act=act)

    def forward(self, x):
        x1 = self.deeper1(x)
        x2 = self.skiper1(x1)

        return x1, x2


class Unet_skip(nn.Layer):
    def __init__(self, in_channels, out_channels, middle_channels, skip_channels, scale, act='leakyrelu',
                 mode='nearest'):
        super(Unet_skip, self).__init__()
        self.seq_d = nn.LayerList()
        self.seq_d.append(uedcode(middle_channels, skip_channels, mode=mode, pos='f', ini_c=in_channels, act=act))
        self.seq_u = nn.LayerList()
        self.seq_u.append(upper(middle_channels, mode=mode, act=act))
        for i in range(scale - 1):
            self.seq_d.append(uedcode(middle_channels, skip_channels, mode, act=act))
        for i in range(scale - 2):
            self.seq_u.append(upper(middle_channels + skip_channels * (i + 1), mode=mode, act=act))
        self.seq_u.append(
            upper(middle_channels + skip_channels * (scale - 1), mode=mode, pos='f', out_c=out_channels, act=act))

    def forward(self, x):
        skip_list = []
        for ix, layer_f in enumerate(self.seq_d):
            x, x1 = layer_f(x)
            if ix != len(self.seq_d) - 1:
                skip_list.append(x1)

        for ix, layer_f in enumerate(self.seq_u):
            if ix != 0:

                x = layer_f(paddle.concat([x, skip_list[-ix]], axis=1))
            else:
                x = layer_f(x)
        return x