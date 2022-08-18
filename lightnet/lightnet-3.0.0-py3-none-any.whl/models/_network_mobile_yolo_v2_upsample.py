#
#   Mobile YOLOv2 model
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['MobileYoloV2Upsample']


class MobileYoloV2Upsample(lnn.module.Darknet):
    """ MobileYolo v2 implementation with an upsampling layer instead of a reorg layer :cite:`optim_detection`.

    This is a variant of :class:`~lightnet.models.MobileYoloV2` where we removed the reorg layer
    and instead upsample the other branch before concatenation.
    This results in a two times bigger output feature map, but only has a limited number of extra computations,
    as there are only two convolutions after the concat operation.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV2 VOC**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_mobile_darknet19: Remapping rules for weights from the :class:`~lightnet.models.MobileDarknet19` model.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to output dimensions).
    """
    stride = 16
    inner_stride = 32
    remap_mobile_darknet19 = (
        (r'^backbone\.(.*)',   r'backbone.module.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.3.24_convbatch.(.*)', r'head.0.\1'),
        (r'^layers.3.25_conv.(.*)', r'head.1.\1'),
        (r'^layers.1.20_convdw.(.*)', r'neck.0.0.\1'),
        (r'^layers.1.21_convdw.(.*)', r'neck.0.1.\1'),
        (r'^layers.2.23_convbatch.(.*)', r'neck.1.\1'),
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
        if anchors.values_per_anchor != 2:
            raise ln.util.AnchorError(anchors, f'Expected 2 values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.MobileDarknet.DN_19(input_channels, 1024, relu=relu, momentum=momentum),
            ['13_convdw'],
            True,
        )

        self.neck = nn.ModuleList([
            nn.Sequential(
                lnn.layer.Conv2dDepthWise(1024, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dDepthWise(1024, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                torch.nn.Upsample(scale_factor=2, mode='nearest'),
            ),
            lnn.layer.Conv2dBatchReLU(512, 4*64, 1, 1, 0, relu=relu, momentum=momentum),
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
        x, feat_13 = self.backbone(x)

        x = self.neck[0](x)
        feat_13 = self.neck[1](feat_13)

        x = self.head(torch.cat((feat_13, x), 1))

        return x
