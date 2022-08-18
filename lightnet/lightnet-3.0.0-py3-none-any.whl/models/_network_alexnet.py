#
#   Alexnet model
#   Copyright EAVISE
#
import lightnet.network as lnn

__all__ = ['Alexnet']


class Alexnet(lnn.module.Lightnet):
    """ Alexnet implementation :cite:`alexnet`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_alexnet
    """
    inner_stride = 32
    remap_torchvision = (
        (r'^features.0.(.*)', r'backbone.1_conv.layers.0.\1'),
        (r'^features.3.(.*)', r'backbone.3_conv.layers.0.\1'),
        (r'^features.6.(.*)', r'backbone.5_conv.layers.0.\1'),
        (r'^features.8.(.*)', r'backbone.6_conv.layers.0.\1'),
        (r'^features.10.(.*)', r'backbone.7_conv.layers.0.\1'),
        (r'^classifier.1.(.*)', r'head.3.\1'),
        (r'^classifier.4.(.*)', r'head.6.\1'),
        (r'^classifier.6.(.*)', r'head.8.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
    ):
        self.num_classes = num_classes
        self.input_channels = input_channels

        # Network
        self.backbone = lnn.backbone.Alexnet(input_channels, 256)
        self.head = lnn.head.ClassificationFC(256, num_classes, pooling_size=6, inter_channels=4096, dropout_first=True)

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)

        return x
