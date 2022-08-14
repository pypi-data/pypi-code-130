import paddle
from paddle import nn
import numpy as np
from paddle.nn import functional as F

def get_actf(name):
    name = name.lower()
    if name == 'relu':
        act = nn.ReLU()
    elif name == 'elu':
        act = nn.ELU()
    elif name == 'leakyrelu':
        act = nn.LeakyReLU()
    elif name == 'sigmoid':
        act - nn.Sigmoid()
    else:
        raise NameError('Activation Function support ReLU,RELU,Leaky ReLU,Sigmoid, no ' + name + '.')
    return act


class conv3x3(nn.Layer):
    def __init__(self, in_channels, out_channels):
        super(conv3x3, self).__init__()
        self.conv = nn.Conv2D(in_channels=in_channels, out_channels=out_channels, stride=1, kernel_size=3, padding=1)

    def forward(self, x):
        return self.conv(x)


class conv1x1(nn.Layer):
    def __init__(self, in_channels, out_channels):
        super(conv1x1, self).__init__()
        self.conv = nn.Conv2D(in_channels=in_channels, out_channels=out_channels, stride=1, kernel_size=1, padding=0)

    def forward(self, x):
        return self.conv(x)