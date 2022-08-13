# ***************************************************************
# Copyright (c) 2022 Jittor. All Rights Reserved. 
# Maintainers: 
#     Guowei Yang <471184555@qq.com>
#     Dun Liang <randonlang@gmail.com>. 
# 
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
# ***************************************************************
# This model is generated by pytorch converter.
import jittor as jt
from jittor import nn
from jittor import init
from collections import OrderedDict


def densenet121(pretrained=False, **kwargs):
    '''Densenet-121 model from
    `"Densely Connected Convolutional Networks" <https://arxiv.org/pdf/1608.06993.pdf>`_
    
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    '''
    model = DenseNet(num_init_features=64, growth_rate=32, block_config=(6, 12, 24, 16), **kwargs)
    if pretrained: model.load("jittorhub://densenet121.pkl")
    return model

def densenet161(pretrained=False, **kwargs):
    '''Densenet-161 model from
    `"Densely Connected Convolutional Networks" <https://arxiv.org/pdf/1608.06993.pdf>`_
    
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    '''
    model = DenseNet(num_init_features=96, growth_rate=48, block_config=(6, 12, 36, 24), **kwargs)
    if pretrained: model.load("jittorhub://densenet161.pkl")
    return model

def densenet169(pretrained=False, **kwargs):
    '''Densenet-169 model from
    `"Densely Connected Convolutional Networks" <https://arxiv.org/pdf/1608.06993.pdf>`_
    
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    '''
    model = DenseNet(num_init_features=64, growth_rate=32, block_config=(6, 12, 32, 32), **kwargs)
    if pretrained: model.load("jittorhub://densenet169.pkl")
    return model

def densenet201(pretrained=False, **kwargs):
    '''Densenet-201 model from
    `"Densely Connected Convolutional Networks" <https://arxiv.org/pdf/1608.06993.pdf>`_
    
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    '''
    model = DenseNet(num_init_features=64, growth_rate=32, block_config=(6, 12, 48, 32), **kwargs)
    if pretrained: model.load("jittorhub://densenet201.pkl")
    return model


class _DenseLayer(nn.Sequential):

    def __init__(self, num_input_features, growth_rate, bn_size, drop_rate):
        super(_DenseLayer, self).__init__()
        self.add_module('norm1', nn.BatchNorm(num_input_features))
        self.add_module('relu1', nn.ReLU())
        self.add_module('conv1', nn.Conv(num_input_features, (bn_size * growth_rate), 1, stride=1, bias=False))
        self.add_module('norm2', nn.BatchNorm((bn_size * growth_rate)))
        self.add_module('relu2', nn.ReLU())
        self.add_module('conv2', nn.Conv((bn_size * growth_rate), growth_rate, 3, stride=1, padding=1, bias=False))
        self.drop_rate = drop_rate
        self.drop = nn.Dropout(self.drop_rate)

    def execute(self, x):
        new_features = super(_DenseLayer, self).execute(x)
        if (self.drop_rate > 0):
            new_features = self.drop(new_features)
        return jt.concat([x, new_features], dim=1)

class _DenseBlock(nn.Sequential):

    def __init__(self, num_layers, num_input_features, bn_size, growth_rate, drop_rate):
        super(_DenseBlock, self).__init__()
        for i in range(num_layers):
            layer = _DenseLayer((num_input_features + (i * growth_rate)), growth_rate, bn_size, drop_rate)
            self.add_module('denselayer%d' % (i + 1), layer)

class _Transition(nn.Sequential):

    def __init__(self, num_input_features, num_output_features):
        super(_Transition, self).__init__()
        self.add_module('norm', nn.BatchNorm(num_input_features))
        self.add_module('relu', nn.ReLU())
        self.add_module('conv', nn.Conv(num_input_features, num_output_features, 1, stride=1, bias=False))
        self.add_module('pool', nn.Pool(2, stride=2, op='mean'))

class DenseNet(nn.Module):
    '''Densenet-BC model class, based on
        `"Densely Connected Convolutional Networks" <https://arxiv.org/pdf/1608.06993.pdf>`_
    
        Args:
            growth_rate (int) - how many filters to add each layer (`k` in paper)
            block_config (list of 4 ints) - how many layers in each pooling block
            num_init_features (int) - the number of filters to learn in the first convolution layer
            bn_size (int) - multiplicative factor for number of bottle neck layers
              (i.e. bn_size * k features in the bottleneck layer)
            drop_rate (float) - dropout rate after each dense layer
            num_classes (int) - number of classification classes
    '''

    def __init__(self, growth_rate=32, block_config=(6, 12, 24, 16), num_init_features=64, bn_size=4, drop_rate=0, num_classes=1000):
        super(DenseNet, self).__init__()
        self.features = nn.Sequential(OrderedDict([
            ('conv0', nn.Conv(3, num_init_features, 7, stride=2, padding=3, bias=False)),
            ('norm0', nn.BatchNorm(num_init_features)),
            ('relu0', nn.ReLU()),
            ('pool0', nn.Pool(3, stride=2, padding=1, op='maximum')),
        ]))
        num_features = num_init_features
        for (i, num_layers) in enumerate(block_config):
            block = _DenseBlock(num_layers=num_layers, num_input_features=num_features, bn_size=bn_size, growth_rate=growth_rate, drop_rate=drop_rate)
            self.features.add_module('denseblock%d' % (i + 1), block)
            num_features = (num_features + (num_layers * growth_rate))
            if (i != (len(block_config) - 1)):
                trans = _Transition(num_input_features=num_features, num_output_features=(num_features // 2))
                self.features.add_module('transition%d' % (i + 1), trans)
                num_features = (num_features // 2)
        self.features.add_module('norm5', nn.BatchNorm(num_features))
        self.classifier = nn.Linear(num_features, num_classes)
        for m in self.modules():
            if isinstance(m, nn.Conv):
                nn.init.invariant_uniform_(m.weight)
            elif isinstance(m, nn.BatchNorm):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.constant_(m.bias, 0)

    def execute(self, x):
        features = self.features(x)
        out = nn.relu(features)
        out = out.mean([2,3])
        out = self.classifier(out)
        return out
