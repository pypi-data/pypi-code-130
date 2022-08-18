#
#   Yolt model
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['Yolt', 'O_Yolt', 'M_Yolt']


class Yolt(lnn.module.Lightnet):
    """ Yolt object detector :cite:`yolt`. |br|
    This detector is optimized for detecting small objects and is more lightweight than YoloV2.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet Tiny YoloV2 VOC**

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
    stride = 16
    inner_stride = 16
    values_per_anchor = 2
    remap_darknet19 = (
        (r'^backbone.([1-9]_.*)', r'backbone.module.\1'),    # layers 1-9
        (r'^backbone.(1[0-7]_.*)', r'backbone.module.\1'),   # layers 10-17
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.3.21_convbatch.(.*)', r'head.0.\1'),
        (r'^layers.3.22_conv.(.*)', r'head.1.\1'),
        (r'^layers.1.18_convbatch.(.*)', r'neck.0.0.\1'),
        (r'^layers.1.19_convbatch.(.*)', r'neck.0.1.\1'),
        (r'^layers.0.(.*)', r'backbone.module.\1'),
        (r'^layers.1.(.*)', r'backbone.module.\1'),
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
        if anchors.values_per_anchor != self.values_per_anchor:
            raise ln.util.AnchorError(anchors, f'Expected {self.values_per_anchor} values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.layer.FeatureExtractor(
            # Yolt only has the 17 first layers from the orignal Darknet19 network
            lnn.backbone.Darknet.DN_19(input_channels, 1024, relu=relu, momentum=momentum)[:17],
            ['11_convbatch'],
            True,
        )

        self.neck = nn.ModuleList([
            nn.Sequential(
                lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(1024, 1024, 3, 1, 1, relu=relu, momentum=momentum),
            ),
            lnn.layer.Reorg(2),
        ])

        self.head = lnn.head.DetectionYoloAnchor(
            (4*256)+1024,
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
        x, feat_11 = self.backbone(x)

        x = self.neck[0](x)
        feat_11 = self.neck[1](feat_11)

        x = self.head(torch.cat((feat_11, x), 1))

        return x


class O_Yolt(Yolt):
    """ Oriented Yolt variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.Yolt`, which can predict bounding boxes with a rotation angle.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet Tiny YoloV2 VOC (zero angle)**

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
        anchors=ln.util.Anchors.TinyYoloV2_VOC.append_values(0.0),
    ):
        super().__init_module__(num_classes, input_channels, anchors)

        self.head = lnn.head.DetectionOrientedAnchor(
            (4*256)+1024,
            self.anchors.num_anchors,
            self.num_classes,
        )


class M_Yolt(Yolt):
    """ Masked Yolt variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.Yolt`, which can predict bounding boxes, as well as instance segmentation masks.

    Args:
        num_classes (int): Number of classes
        num_masks (int, optional): Number of prototype masks; Default **32**
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet Tiny YoloV2 VOC**

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
    mask_stride = 8

    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        input_channels=3,
        anchors=ln.util.Anchors.TinyYoloV2_VOC,
    ):
        super().__init_module__(num_classes, input_channels, anchors)
        self.num_masks = num_masks

        self.detection_head = lnn.head.DetectionMaskedAnchor(
            (4*256)+1024,
            self.anchors.num_anchors,
            num_classes,
            num_masks,
        )

        self.mask_head = lnn.head.DetectionMaskedAnchor.Protonet(
            (4*256)+1024,
            num_masks,
        )

    def forward(self, x):
        x, feat_11 = self.backbone(x)

        x = self.neck[0](x)
        feat_11 = self.neck[1](feat_11)
        x = torch.cat((feat_11, x), 1)

        out = self.detection_head(x)
        mask = self.mask_head(x)

        return out, mask
