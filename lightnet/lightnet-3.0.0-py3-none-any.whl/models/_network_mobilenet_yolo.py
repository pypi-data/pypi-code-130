#
#   Darknet YOLOv2 model with Mobilenet backend
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['MobilenetYolo']


class MobilenetYolo(lnn.module.Lightnet):
    """ Yolo v2 implementation with a mobilenet v1 backend.

    Args:
        num_classes (int): Number of classes
        alpha (float, optional): Number between [0-1] that controls the number of filters of the mobilenet convolutions; Default **1**
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV2 VOC**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_mobilenet_v1: Remapping rules for weights from the :class:`~lightnet.models.MobileNetV1` model.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    Warning:
        When changing the ``alpha`` value, you are changing the network architecture.
        This means you cannot use weights from this network with a different alpha value.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    stride = 32
    inner_stride = 32
    remap_mobilenet_v1 = (
        (r'^backbone\.(.*)',   r'backbone.module.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.0.(.*)', r'backbone.module.\1'),
        (r'^layers.1.(.*)', r'backbone.module.\1'),
        (r'^layers.2.15_convbatch.(.*)', r'neck.0.\1'),
        (r'^layers.3.17_convbatch.(.*)', r'head.0.\1'),
        (r'^layers.3.18_conv.(.*)', r'head.1.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        alpha=1.0,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV2_VOC,
    ):
        if not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != 1:
            raise ln.util.AnchorError(anchors, f'Expected 1 scale, but got {anchors.num_scales}')
        if anchors.values_per_anchor != 2:
            raise ln.util.AnchorError(anchors, f'Expected 2 values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.ReLU6, inplace=True)
        momentum = 0.1

        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.Mobilenet(input_channels, int(alpha*1024), alpha, relu=relu, momentum=momentum),
            ['9_convdw'],
            True,
        )

        self.neck = nn.Sequential(
            lnn.layer.Conv2dBatchReLU(int(alpha*512), 64, 1, 1, 0, relu=relu, momentum=momentum),
            lnn.layer.Reorg(2),
        )

        self.head = lnn.head.DetectionYoloAnchor(
            (4*64)+int(alpha*1024),
            self.anchors.num_anchors,
            self.num_classes,
            relu=relu,
            momentum=momentum,
        )

    def forward(self, x):
        x, feat_9 = self.backbone(x)

        feat_9 = self.neck(feat_9)

        x = self.head(torch.cat((feat_9, x), 1))

        return x
