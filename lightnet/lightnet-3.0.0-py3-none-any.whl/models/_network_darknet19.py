#
#   Darknet Darknet19 model
#   Copyright EAVISE
#
import torch.nn as nn
import lightnet.network as lnn

__all__ = ['Darknet19']


class Darknet19(lnn.module.Darknet):
    """ Darknet19 implementation :cite:`yolo_v2`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0
    """
    inner_stride = 32

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.0.(.*)', r'backbone.\1'),
        (r'^layers.1.24_conv.(.*)', r'head.0.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
    ):
        self.num_classes = num_classes
        self.input_channels = input_channels

        # Network
        self.backbone = lnn.backbone.Darknet.DN_19(input_channels, 1024)
        self.head = lnn.head.ClassificationConv(1024, num_classes, conv_first=True)

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
