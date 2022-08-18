#
#   Darknet Tiny YOLOv3 model
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['TinyYoloV3']


class TinyYoloV3(lnn.module.Darknet):
    """ Tiny Yolo v3 implementation :cite:`yolo_v3`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet Tiny YoloV3 COCO**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet: Remapping rules for weights from the `~lightnet.models.Darknet` model.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    Warning:
        The :class:`~lightnet.network.loss.MultiScaleRegionLoss` and :class:`~lightnet.data.transform.GetMultiScaleBoundingBoxes`
        do not implement the overlapping class labels of the original implementation.
        Your weight files from darknet will thus not have the same accuracies as in darknet itself.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to input dimensions).
    """
    stride = (32, 16)
    inner_stride = 32
    remap_darknet = (
        (r'^backbone\.(.*)', r'backbone.module.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^extractor.13_convbatch.(.*)', r'neck.module.1.\1'),
        (r'^extractor.14_convbatch.(.*)', r'neck.module.2.\1'),
        (r'^detector.1.17_convbatch.(.*)', r'neck.module.3.\1'),
        (r'^detector.0.15_convbatch.(.*)', r'head.0.0.\1'),
        (r'^detector.0.16_conv.(.*)', r'head.0.1.\1'),
        (r'^detector.2.19_convbatch.(.*)', r'head.1.0.\1'),
        (r'^detector.2.20_conv.(.*)', r'head.1.1.\1'),
        (r'^extractor.(.*)', r'backbone.module.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.TinyYoloV3_COCO,
    ):
        if not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != 2:
            raise ln.util.AnchorError(anchors, f'Expected 2 scales, but got {anchors.num_scales}')
        if anchors.values_per_anchor != 2:
            raise ln.util.AnchorError(anchors, f'Expected 2 values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.Darknet(input_channels, 512, relu=relu, momentum=momentum),
            ['9_convbatch'],
            True,
        )

        self.neck = lnn.layer.FeatureExtractor(
            nn.Sequential(
                lnn.layer.PaddedMaxPool2d(2, 1, (0, 1, 0, 1)),
                lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(1024, 256, 1, 1, 0, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                nn.Upsample(scale_factor=2, mode='nearest'),
            ),
            [2],
            True,
        )

        self.head = nn.ModuleList([
            lnn.head.DetectionYoloAnchor(
                256,
                self.anchors.get_scale(0).num_anchors,
                self.num_classes,
                512,
                relu=relu,
                momentum=momentum,
            ),
            lnn.head.DetectionYoloAnchor(
                128+256,
                self.anchors.get_scale(1).num_anchors,
                self.num_classes,
                256,
                relu=relu,
                momentum=momentum,
            ),
        ])

    def __init_weights__(self, name, mod):
        if isinstance(mod, nn.Conv2d):
            nn.init.kaiming_normal_(mod.weight, a=0.1, mode='fan_out')
            if mod.bias is not None:
                nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x, feat_9 = self.backbone(x)

        x, out_0 = self.neck(x)

        out_0 = self.head[0](out_0)
        out_1 = self.head[1](torch.cat((x, feat_9), 1))

        return [out_0, out_1]
