#
#   Darknet YOLOv2 model
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['YoloV2', 'O_YoloV2', 'M_YoloV2']


class YoloV2(lnn.module.Darknet):
    """ Yolo v2 implementation :cite:`yolo_v2`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV2 VOC**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet19: Remapping rules for weights from the :class:`~lightnet.models.Darknet19` model.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    stride = 32
    inner_stride = 32
    values_per_anchor = 2
    remap_darknet19 = (
        (r'^backbone\.(.*)',   r'backbone.module.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.3.28_convbatch.(.*)', r'head.0.\1'),
        (r'^layers.3.29_conv.(.*)', r'head.1.\1'),
        (r'^layers.1.24_convbatch.(.*)', r'neck.0.0.\1'),
        (r'^layers.1.25_convbatch.(.*)', r'neck.0.1.\1'),
        (r'^layers.2.26_convbatch.(.*)', r'neck.1.0.\1'),
        (r'^layers.0.(.*)', r'backbone.module.\1'),
        (r'^layers.1.(.*)', r'backbone.module.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV2_VOC,
    ):
        if not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != 1:
            raise ln.util.AnchorError(anchors, f'Expected 1 scale, but got {anchors.num_scales}')
        if anchors.values_per_anchor != self.values_per_anchor:
            raise ln.util.AnchorError(anchors, f'Expected {self.values_per_anchor} values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.Darknet.DN_19(input_channels, 1024, relu=relu, momentum=momentum),
            ['17_convbatch'],
            True,
        )

        self.neck = nn.ModuleList([
            nn.Sequential(
                lnn.layer.Conv2dBatchReLU(1024, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(1024, 1024, 3, 1, 1, relu=relu, momentum=momentum),
            ),
            nn.Sequential(
                lnn.layer.Conv2dBatchReLU(512, 64, 1, 1, 0, relu=relu, momentum=momentum),
                lnn.layer.Reorg(2),
            ),
        ])

        self.head = lnn.head.DetectionYoloAnchor(
            (4*64)+1024,
            self.anchors.num_anchors,
            self.num_classes,
            relu=relu,
            momentum=momentum,
        )

    def __init_weights__(self, name, mod):
        if isinstance(mod, nn.Conv2d):
            nn.init.kaiming_normal_(mod.weight, a=0.1, mode='fan_out')
            if mod.bias is not None:
                nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x, feat_17 = self.backbone(x)

        x = self.neck[0](x)
        feat_17 = self.neck[1](feat_17)

        x = self.head(torch.cat((feat_17, x), 1))

        return x


class O_YoloV2(YoloV2):
    """ Oriented YoloV2 variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.YoloV2`, which can predict bounding boxes with a rotation angle.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV2 VOC (zero angle)**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet19: Remapping rules for weights from the :class:`~lightnet.models.Darknet19` model.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    values_per_anchor = 3

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV2_VOC.append_values(0.0),
    ):
        super().__init_module__(num_classes, input_channels, anchors)

        self.head = lnn.head.DetectionOrientedAnchor(
            (4*64)+1024,
            self.anchors.num_anchors,
            self.num_classes,
        )


class M_YoloV2(YoloV2):
    """ Masked YoloV2 variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.YoloV2`, which can predict bounding boxes, as well as instance segmentation masks.

    Args:
        num_classes (int): Number of classes
        num_masks (int, optional): Number of prototype masks; Default **32**
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV2 VOC**

    Attributes:
        self.stride: Subsampling factor of the network bounding box output (input_dim / output_dim)
        self.mask_stride: Subsampling factor of the network mask output (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet19: Remapping rules for weights from the :class:`~lightnet.models.Darknet19` model.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    mask_stride = 16

    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV2_VOC,
    ):
        super().__init_module__(num_classes, input_channels, anchors)
        self.num_masks = num_masks

        self.detection_head = lnn.head.DetectionMaskedAnchor(
            (4*64)+1024,
            self.anchors.num_anchors,
            num_classes,
            num_masks,
        )

        self.mask_head = lnn.head.DetectionMaskedAnchor.Protonet(
            (4*64)+1024,
            num_masks,
        )

    def forward(self, x):
        x, feat_17 = self.backbone(x)

        x = self.neck[0](x)
        feat_17 = self.neck[1](feat_17)
        x = torch.cat((feat_17, x), 1)

        out = self.detection_head(x)
        mask = self.mask_head(x)

        return out, mask
