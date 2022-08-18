#
#   Yolact models
#   Copyright EAVISE
#
import logging
import torch.nn as nn
import lightnet.network as lnn

__all__ = ['Yolact50', 'Yolact101']
log = logging.getLogger('lightnet.models')


class Yolact(lnn.module.Lightnet):
    """ Base Yolact network """
    stride = (128, 64, 32, 16, 8)
    inner_stride = 128
    remap_resnet = (
        (r'^backbone\.(.*)',   r'backbone.module.\1'),
    )

    def __init_module__(
        self,
        Backbone,
        num_classes,
        num_masks,
        aspect_ratios,
        scales,
        input_channels,
        inference_only=False,
    ):
        log.experimental('Yolact is still in development. Use at your own risk!')

        self.num_classes = num_classes
        self.num_masks = num_masks
        self.input_channels = input_channels
        self.aspect_ratios = aspect_ratios
        self.scales = scales
        self.inference_only = inference_only

        # Network
        self.backbone = lnn.layer.FeatureExtractor(
            Backbone(input_channels, 2048),
            ['6_residualgroup', '8_residualgroup'],
            True,
        )

        self.neck = lnn.layer.FPN(
            [512, 1024, 2048],
            256,
            5,
            make_prediction=lambda ci, co: lnn.layer.Conv2dReLU(ci, co, 3, 1, 1, bias=True),
            make_downsample=lambda ci, co: nn.Conv2d(ci, co, 3, 2, 1, bias=True),
            interpolation_mode='bilinear',
        )

        self.detection_head = lnn.head.DetectionYolact(256, len(self.aspect_ratios), num_classes, num_masks)
        self.mask_head = lnn.head.DetectionYolact.Protonet(256, num_masks)
        if not inference_only:
            self.semantic_head = nn.Conv2d(256, num_classes, 1, 1, 0, bias=True)

        # Set mode
        if self.inference_only:
            self.eval()

    def __init_weights__(self, name, mod):
        if isinstance(mod, nn.Conv2d):
            nn.init.xavier_uniform_(mod.weight)
            if mod.bias is not None:
                # Same init as original code, except we dont do the focal loss stuff.
                # It seems the author decided not to use focal loss, so not necessary here.
                nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        C5, C3, C4 = self.backbone(x)
        P3, P4, P5, P6, P7 = self.neck(C3, C4, C5)

        mask = self.mask_head(P3)
        O1 = self.detection_head(P3)
        O2 = self.detection_head(P4)
        O3 = self.detection_head(P5)
        O4 = self.detection_head(P6)
        O5 = self.detection_head(P7)

        if self.training:
            segment = self.semantic_head(P3)
            return ((O5, O4, O3, O2, O1), mask, segment)
        else:
            return ((O5, O4, O3, O2, O1), mask)

    def train(self, mode=True):
        if mode and self.inference_only:
            raise ValueError('Cannot set training mode for inference_only model')
        return super().train(mode)

    @staticmethod
    def remap_dbolya(k):
        if k.startswith('backbone.layers'):
            _, _, layer, num, mod, remainder = k.split('.', 5)
            layer = int(layer)
            num = int(num)

            start = (
                ('backbone.module.3_residual.', 'backbone.module.4_residualgroup.'),
                ('backbone.module.5_residual.', 'backbone.module.6_residualgroup.'),
                ('backbone.module.7_residual.', 'backbone.module.8_residualgroup.'),
                ('backbone.module.9_residual.', 'backbone.module.10_residualgroup.'),
            )[layer][int(num != 0)]
            if num != 0:
                start += f'{num-1}.'

            mid = {
                'conv1': '0.layers.0.',
                'bn1': '0.layers.1.',
                'conv2': '1.layers.0.',
                'bn2': '1.layers.1.',
                'conv3': '2.layers.0.',
                'bn3': '2.layers.1.',
                'downsample': 'skip.layers.',
            }[mod]

            return start + mid + remainder
        elif k.startswith('proto_net'):
            _, num, remainder = k.split('.', 3)
            num = int(num)
            return f'mask_head.{num//2}.layers.0.{remainder}'
        elif k.startswith('backbone.layer') or (k.startswith('fpn.downsample_layers') and int(k[22]) >= 2):
            # Original Yolact Code removes these extra layers as well
            # It seems earlier weights had one erroneous downsample layer
            return None
        else:
            return (
                (r'^backbone\.conv1\.(.*)', r'backbone.module.1_convbatch.layers.0.\1'),
                (r'^backbone\.bn1\.(.*)', r'backbone.module.1_convbatch.layers.1.\1'),
                (r'^fpn\.lat_layers\.0\.(.*)', r'neck.lateral.2.\1'),
                (r'^fpn\.lat_layers\.1\.(.*)', r'neck.lateral.1.\1'),
                (r'^fpn\.lat_layers\.2\.(.*)', r'neck.lateral.0.\1'),
                (r'^fpn\.pred_layers\.([0-2])\.(.*)', r'neck.prediction.\1.layers.0.\2'),
                (r'^fpn\.downsample_layers\.(.*)', r'neck.downsample.\1'),
                (r'^prediction_layers\.0\.upfeature\.(.*)', r'detection_head.0.layers.\1'),
                (r'^prediction_layers\.0\.bbox_layer\.(.*)', r'detection_head.1.0.\1'),
                (r'^prediction_layers\.0\.conf_layer\.(.*)', r'detection_head.1.1.\1'),
                (r'^prediction_layers\.0\.mask_layer\.(.*)', r'detection_head.1.2.0.\1'),
                (r'^semantic_seg_conv\.(.*)', r'semantic_head.\1'),
            )


class Yolact50(Yolact):
    """ Yolact Instance Segmentation Model with ResNet50 backbone :cit:`yolact`.

    .. admonition:: Experimental

       This network implementation is still in development
       and might not be yielding the same results as the official implementation.
       Use at your own risk!

    Args:
        num_classes (int): Number of classes (without background class)
        num_masks (int, optional): Number of prototype masks; Default **32**
        aspect_ratios (list<Number>, optional): Different aspect ratios for the anchors; Default **Yolact COCO**
            ``[1, 1/2, 2]``
        scales (list<int>, optional): Different scales for the anchors; Default **Yolact COCO**
            ``[384, 192, 96, 48, 24]``
        input_channels (int, optional): Number of input channels; Default **3**
        inference_only (boolean, optional): Whether to load the model purely for inference; Default **False**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_dbolya: Remapping rules for weights from the `official Yolact implementation <yolactImpl_>`_.

    .. _yolactImpl: https://github.com/dbolya/yolact
    """
    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        aspect_ratios=[1, 1/2, 2],
        scales=[384, 192, 96, 48, 24],
        input_channels=3,
        inference_only=False,
    ):
        super().__init_module__(lnn.backbone.Resnet.RN_50, num_classes, num_masks, aspect_ratios, scales, input_channels, inference_only)


class Yolact101(Yolact):
    """ Yolact Instance Segmentation Model with ResNet101 backbone :cit:`yolact`.

    .. admonition:: Experimental

       This network implementation is still in development
       and might not be yielding the same results as the official implementation.
       Use at your own risk!

    Args:
        num_classes (int): Number of classes (without background class)
        num_masks (int, optional): Number of prototype masks; Default **32**
        aspect_ratios (list<Number>, optional): Different aspect ratios for the anchors; Default **Yolact COCO**
            ``[1, 1/2, 2]``
        scales (list<int>, optional): Different scales for the anchors; Default **Yolact COCO**
            ``[384, 192, 96, 48, 24]``
        input_channels (int, optional): Number of input channels; Default **3**
        inference_only (boolean, optional): Whether to load the model purely for inference; Default **False**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_dbolya: Remapping rules for weights from the `official Yolact implementation <yolactImpl_>`_.

    .. _yolactImpl: https://github.com/dbolya/yolact
    """
    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        aspect_ratios=[1, 1/2, 2],
        scales=[384, 192, 96, 48, 24],
        input_channels=3,
        inference_only=False,
    ):
        super().__init_module__(lnn.backbone.Resnet.RN_101, num_classes, num_masks, aspect_ratios, scales, input_channels, inference_only)
