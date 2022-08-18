#
#   Darknet Darknet model
#   Copyright EAVISE
#
import functools
import torch.nn as nn
import lightnet.network as lnn

__all__ = ['Darknet']


class Darknet(lnn.module.Darknet):
    """ Darknet reference implementation :cite:`yolo_v1`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0
    """
    inner_stride = 64

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.0.13\w+.(.*)', r'head.1.\1'),
        (r'^layers.0.(.*)', r'backbone.\1'),
        (r'^layers.1.15_conv.(.*)', r'head.3.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
    ):
        self.num_classes = num_classes
        self.input_channels = input_channels

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.backbone.Darknet(input_channels, 512, relu=relu, momentum=momentum)
        self.head = nn.Sequential(
            nn.MaxPool2d(2, 2),
            lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
            *lnn.head.ClassificationConv(1024, num_classes),
        )

    def __init_weights__(self, name, mod):
        if isinstance(mod, nn.Conv2d):
            nn.init.kaiming_normal_(mod.weight, a=0.1, mode='fan_out')
            if mod.bias is not None:
                nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)

        return x
