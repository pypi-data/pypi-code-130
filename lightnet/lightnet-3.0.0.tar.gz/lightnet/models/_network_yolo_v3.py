#
#   Darknet YOLOv3 model
#   Copyright EAVISE
#
import functools
import torch
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['YoloV3', 'O_YoloV3', 'M_YoloV3']


class YoloV3(lnn.module.Darknet):
    """ Yolo v3 implementation :cite:`yolo_v3`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV3 COCO**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet53: Remapping rules for weights from the :class:`~lightnet.models.Darknet53` model.
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
    stride = (32, 16, 8)
    inner_stride = 32
    values_per_anchor = 2
    remap_darknet53 = (
        (r'^backbone\.(.*)', r'backbone.module.\1'),
    )

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^extractor.a_residual.3_\w+.(.*)', r'backbone.module.3_residual.0.\1'),
        (r'^extractor.a_residual.4_\w+.(.*)', r'backbone.module.3_residual.1.\1'),
        (r'^extractor.5_(.*)', r'backbone.module.4_\1'),
        (r'^extractor.b_residual.6_\w+.(.*)', r'backbone.module.5_residual.0.\1'),
        (r'^extractor.b_residual.7_\w+.(.*)', r'backbone.module.5_residual.1.\1'),
        (r'^extractor.c_residual.8_\w+.(.*)', r'backbone.module.6_residual.0.\1'),
        (r'^extractor.c_residual.9_\w+.(.*)', r'backbone.module.6_residual.1.\1'),
        (r'^extractor.10_(.*)', r'backbone.module.7_\1'),
        (r'^extractor.d_residual.11_\w+.(.*)', r'backbone.module.8_residual.0.\1'),
        (r'^extractor.d_residual.12_\w+.(.*)', r'backbone.module.8_residual.1.\1'),
        (r'^extractor.e_residual.13_\w+.(.*)', r'backbone.module.9_residual.0.\1'),
        (r'^extractor.e_residual.14_\w+.(.*)', r'backbone.module.9_residual.1.\1'),
        (r'^extractor.f_residual.15_\w+.(.*)', r'backbone.module.10_residual.0.\1'),
        (r'^extractor.f_residual.16_\w+.(.*)', r'backbone.module.10_residual.1.\1'),
        (r'^extractor.g_residual.17_\w+.(.*)', r'backbone.module.11_residual.0.\1'),
        (r'^extractor.g_residual.18_\w+.(.*)', r'backbone.module.11_residual.1.\1'),
        (r'^extractor.h_residual.19_\w+.(.*)', r'backbone.module.12_residual.0.\1'),
        (r'^extractor.h_residual.20_\w+.(.*)', r'backbone.module.12_residual.1.\1'),
        (r'^extractor.i_residual.21_\w+.(.*)', r'backbone.module.13_residual.0.\1'),
        (r'^extractor.i_residual.22_\w+.(.*)', r'backbone.module.13_residual.1.\1'),
        (r'^extractor.j_residual.23_\w+.(.*)', r'backbone.module.14_residual.0.\1'),
        (r'^extractor.j_residual.24_\w+.(.*)', r'backbone.module.14_residual.1.\1'),
        (r'^extractor.k_residual.25_\w+.(.*)', r'backbone.module.15_residual.0.\1'),
        (r'^extractor.k_residual.26_\w+.(.*)', r'backbone.module.15_residual.1.\1'),
        (r'^extractor.27_(.*)', r'backbone.module.16_\1'),
        (r'^extractor.l_residual.28_\w+.(.*)', r'backbone.module.17_residual.0.\1'),
        (r'^extractor.l_residual.29_\w+.(.*)', r'backbone.module.17_residual.1.\1'),
        (r'^extractor.m_residual.30_\w+.(.*)', r'backbone.module.18_residual.0.\1'),
        (r'^extractor.m_residual.31_\w+.(.*)', r'backbone.module.18_residual.1.\1'),
        (r'^extractor.n_residual.32_\w+.(.*)', r'backbone.module.19_residual.0.\1'),
        (r'^extractor.n_residual.33_\w+.(.*)', r'backbone.module.19_residual.1.\1'),
        (r'^extractor.o_residual.34_\w+.(.*)', r'backbone.module.20_residual.0.\1'),
        (r'^extractor.o_residual.35_\w+.(.*)', r'backbone.module.20_residual.1.\1'),
        (r'^extractor.p_residual.36_\w+.(.*)', r'backbone.module.21_residual.0.\1'),
        (r'^extractor.p_residual.37_\w+.(.*)', r'backbone.module.21_residual.1.\1'),
        (r'^extractor.q_residual.38_\w+.(.*)', r'backbone.module.22_residual.0.\1'),
        (r'^extractor.q_residual.39_\w+.(.*)', r'backbone.module.22_residual.1.\1'),
        (r'^extractor.r_residual.40_\w+.(.*)', r'backbone.module.23_residual.0.\1'),
        (r'^extractor.r_residual.41_\w+.(.*)', r'backbone.module.23_residual.1.\1'),
        (r'^extractor.s_residual.42_\w+.(.*)', r'backbone.module.24_residual.0.\1'),
        (r'^extractor.s_residual.43_\w+.(.*)', r'backbone.module.24_residual.1.\1'),
        (r'^extractor.44_(.*)', r'backbone.module.25_\1'),
        (r'^extractor.t_residual.45_\w+.(.*)', r'backbone.module.26_residual.0.\1'),
        (r'^extractor.t_residual.46_\w+.(.*)', r'backbone.module.26_residual.1.\1'),
        (r'^extractor.u_residual.47_\w+.(.*)', r'backbone.module.27_residual.0.\1'),
        (r'^extractor.u_residual.48_\w+.(.*)', r'backbone.module.27_residual.1.\1'),
        (r'^extractor.v_residual.49_\w+.(.*)', r'backbone.module.28_residual.0.\1'),
        (r'^extractor.v_residual.50_\w+.(.*)', r'backbone.module.28_residual.1.\1'),
        (r'^extractor.w_residual.51_\w+.(.*)', r'backbone.module.29_residual.0.\1'),
        (r'^extractor.w_residual.52_\w+.(.*)', r'backbone.module.29_residual.1.\1'),
        (r'^extractor.(.*)', r'backbone.module.\1'),
        (r'^detector.0.53_convbatch.(.*)', r'neck.0.module.0.\1'),
        (r'^detector.0.54_convbatch.(.*)', r'neck.0.module.1.\1'),
        (r'^detector.0.55_convbatch.(.*)', r'neck.0.module.2.\1'),
        (r'^detector.0.56_convbatch.(.*)', r'neck.0.module.3.\1'),
        (r'^detector.0.57_convbatch.(.*)', r'neck.0.module.4.\1'),
        (r'^detector.1.60_convbatch.(.*)', r'neck.0.module.5.\1'),
        (r'^detector.2.62_convbatch.(.*)', r'neck.1.module.0.\1'),
        (r'^detector.2.63_convbatch.(.*)', r'neck.1.module.1.\1'),
        (r'^detector.2.64_convbatch.(.*)', r'neck.1.module.2.\1'),
        (r'^detector.2.65_convbatch.(.*)', r'neck.1.module.3.\1'),
        (r'^detector.2.66_convbatch.(.*)', r'neck.1.module.4.\1'),
        (r'^detector.3.69_convbatch.(.*)', r'neck.1.module.5.\1'),
        (r'^detector.4.71_convbatch.(.*)', r'neck.2.0.\1'),
        (r'^detector.4.72_convbatch.(.*)', r'neck.2.1.\1'),
        (r'^detector.4.73_convbatch.(.*)', r'neck.2.2.\1'),
        (r'^detector.4.74_convbatch.(.*)', r'neck.2.3.\1'),
        (r'^detector.4.75_convbatch.(.*)', r'neck.2.4.\1'),
        (r'^detector.0.58_convbatch.(.*)', r'head.0.0.\1'),
        (r'^detector.0.59_conv.(.*)', r'head.0.1.\1'),
        (r'^detector.2.67_convbatch.(.*)', r'head.1.0.\1'),
        (r'^detector.2.68_conv.(.*)', r'head.1.1.\1'),
        (r'^detector.4.76_convbatch.(.*)', r'head.2.0.\1'),
        (r'^detector.4.77_conv.(.*)', r'head.2.1.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV3_COCO,
    ):
        if not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != 3:
            raise ln.util.AnchorError(anchors, f'Expected 3 scales, but got {anchors.num_scales}')
        if anchors.values_per_anchor != self.values_per_anchor:
            raise ln.util.AnchorError(anchors, f'Expected {self.values_per_anchor} values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.anchors = anchors

        # Network
        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        momentum = 0.01

        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.Darknet.DN_53(input_channels, 1024, relu=relu, momentum=momentum),
            ['15_residual', '24_residual'],
            True,
        )

        self.neck = nn.ModuleList([
            lnn.layer.FeatureExtractor(
                nn.Sequential(
                    lnn.layer.Conv2dBatchReLU(1024, 512, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(1024, 512, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(512, 1024, 3, 1, 1, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(1024, 512, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                    nn.Upsample(scale_factor=2, mode='nearest'),
                ),
                [4],
                True,
            ),
            lnn.layer.FeatureExtractor(
                nn.Sequential(
                    lnn.layer.Conv2dBatchReLU(256+512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(256, 512, 3, 1, 1, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(512, 256, 1, 1, 0, relu=relu, momentum=momentum),
                    lnn.layer.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                    nn.Upsample(scale_factor=2, mode='nearest'),
                ),
                [4],
                True,
            ),
            nn.Sequential(
                lnn.layer.Conv2dBatchReLU(128+256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(128, 256, 3, 1, 1, relu=relu, momentum=momentum),
                lnn.layer.Conv2dBatchReLU(256, 128, 1, 1, 0, relu=relu, momentum=momentum),
            ),
        ])

        self.head = nn.ModuleList([
            lnn.head.DetectionYoloAnchor(
                512,
                self.anchors.get_scale(0).num_anchors,
                self.num_classes,
                1024,
                relu=relu,
                momentum=momentum,
            ),
            lnn.head.DetectionYoloAnchor(
                256,
                self.anchors.get_scale(1).num_anchors,
                self.num_classes,
                512,
                relu=relu,
                momentum=momentum,
            ),
            lnn.head.DetectionYoloAnchor(
                128,
                self.anchors.get_scale(2).num_anchors,
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
        x, feat_15, feat_24 = self.backbone(x)

        x, out_0 = self.neck[0](x)
        x, out_1 = self.neck[1](torch.cat((x, feat_24), 1))
        out_2 = self.neck[2](torch.cat((x, feat_15), 1))

        out_0 = self.head[0](out_0)
        out_1 = self.head[1](out_1)
        out_2 = self.head[2](out_2)

        return [out_0, out_1, out_2]


class O_YoloV3(YoloV3):
    """ Oriented YoloV3 variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.YoloV3`, which can predict bounding boxes with a rotation angle.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV3 COCO (zero angle)**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet19: Remapping rules for weights from the :class:`~lightnet.models.Darknet19` model.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to input dimensions).
    """
    values_per_anchor = 3

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV3_COCO.append_values(0.0),
    ):
        super().__init_module__(num_classes, input_channels, anchors)

        self.head = nn.ModuleList([
            lnn.head.DetectionOrientedAnchor(
                512,
                self.anchors.get_scale(0).num_anchors,
                self.num_classes,
                1024,
            ),
            lnn.head.DetectionOrientedAnchor(
                256,
                self.anchors.get_scale(1).num_anchors,
                self.num_classes,
                512,
            ),
            lnn.head.DetectionOrientedAnchor(
                128,
                self.anchors.get_scale(2).num_anchors,
                self.num_classes,
                256,
            ),
        ])


class M_YoloV3(YoloV3):
    """ Masked YoloV3 variant. |br|
    This detector is the oriented variant of :class:`~lightnet.models.YoloV3`, which can predict bounding boxes, as well as instance segmentation masks.

    Args:
        num_classes (int): Number of classes
        num_masks (int, optional): Number of prototype masks; Default **32**
        input_channels (int, optional): Number of input channels; Default **3**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV3 COCO**

    Attributes:
        self.stride: Subsampling factors of the network bounding box output (input_dim / output_dim)
        self.mask_stride: Subsampling factors of the network mask output (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_darknet19: Remapping rules for weights from the :class:`~lightnet.models.Darknet19` model.

    Note:
        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to input dimensions).
    """
    mask_stride = 4

    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        input_channels=3,
        anchors=ln.util.Anchors.YoloV3_COCO,
    ):
        super().__init_module__(num_classes, input_channels, anchors)
        self.num_masks = num_masks

        self.detection_head = nn.ModuleList([
            lnn.head.DetectionMaskedAnchor(
                512,
                self.anchors.get_scale(0).num_anchors,
                self.num_classes,
                self.num_masks,
                1024,
            ),
            lnn.head.DetectionMaskedAnchor(
                256,
                self.anchors.get_scale(1).num_anchors,
                self.num_classes,
                self.num_masks,
                512,
            ),
            lnn.head.DetectionMaskedAnchor(
                128,
                self.anchors.get_scale(2).num_anchors,
                self.num_classes,
                self.num_masks,
                256,
            ),
        ])

        self.mask_head = lnn.head.DetectionMaskedAnchor.Protonet(
            128,
            self.num_masks,
            256,
        )

    def forward(self, x):
        x, feat_15, feat_24 = self.backbone(x)

        x, neck_0 = self.neck[0](x)
        x, neck_1 = self.neck[1](torch.cat((x, feat_24), 1))
        neck_2 = self.neck[2](torch.cat((x, feat_15), 1))

        out_0 = self.detection_head[0](neck_0)
        out_1 = self.detection_head[1](neck_1)
        out_2 = self.detection_head[2](neck_2)
        mask = self.mask_head(neck_2)

        return ([out_0, out_1, out_2], mask)
