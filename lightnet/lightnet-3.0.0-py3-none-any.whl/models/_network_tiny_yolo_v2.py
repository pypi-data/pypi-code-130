#
#   Darknet Tiny YOLOv2 model
#   Copyright EAVISE
#
import functools
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['TinyYoloV2']


class TinyYoloV2(lnn.module.Darknet):
    """ Tiny Yolo v2 implementation :cite:`yolo_v2`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet Tiny YoloV2 VOC**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet: Remapping rules for weights from the :class:`~lightnet.models.Darknet` model.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    stride = 32
    inner_stride = 32
    remap_darknet = (
        (r'^backbone\.(.*)',   r'backbone.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.13_convbatch.(.*)', r'head.1.\1'),
        (r'^layers.14_convbatch.(.*)', r'head.2.\1'),
        (r'^layers.15_conv.(.*)', r'head.3.\1'),
        (r'^layers.(.*)', r'backbone.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.TinyYoloV2_VOC,
    ):
        if not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != 1:
            raise ln.util.AnchorError(anchors, f'Expected 1 scale, but got {anchors.num_scales}')
        if anchors.values_per_anchor != 2:
            raise ln.util.AnchorError(anchors, f'Expected 2 values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.backbone.Darknet(input_channels, 512, relu=relu, momentum=momentum)
        self.head = nn.Sequential(
            lnn.layer.PaddedMaxPool2d(2, 1, (0, 1, 0, 1)),
            lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
            *lnn.head.DetectionYoloAnchor(
                1024,
                self.anchors.num_anchors,
                self.num_classes,
                relu=relu,
                momentum=momentum,
            ),
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
