#
#   YOLO model with a ResNet Backbone
#   Copyright EAVISE
#
import logging
import functools
from enum import Enum
import torch.nn as nn
import lightnet as ln
import lightnet.network as lnn

__all__ = ['ResnetYolo', 'M_ResnetYolo']
log = logging.getLogger('lightnet.models')


class NetworkTypes(Enum):
    NORMAL = 0          #: Regular ResNet backbone
    DEFORMABLE = 1      #: ResNet backbone with deformable convolutions
    MODULATED = 2       #: ResNet backbone with modulated deformable convolutions


class ResnetYolo(lnn.module.Lightnet):
    """ Multi-scale Yolo detection network with a ResNet50 backbone.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        outputs (list<bool, 4>, optional): Which output heads to use; Default **(True, True, True, True)**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV3 COCO**
        type (enum or int, optional): Which backbone type; Default **NORMAL**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_resnet50: Remapping rules for weights from the :class:`~lightnet.models.Resnet50` model.
        self.Types: The different backbone types (``NORMAL``, ``DEFORMABLE``, ``MODULATED``)

    Warning:
        As with most of the lightnet networks, the `stride` and `inner_stride` can be accessed from the class.
        However, as this network allows you to select which output heads you want,
        these values can change and are thus only set correctly on initialized models!

    Note:
        It is recommended to pass in custom anchors to this network,
        as we otherwise use the YoloV3 COCO anchors, which we arbitrarilly divide among the different output heads.

        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to input dimensions).
    """
    Types = NetworkTypes

    stride = (64, 32, 16, 8)
    inner_stride = 32
    values_per_anchor = 2
    remap_resnet50 = (
        (r'^backbone\.(.*)', r'backbone.module.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        outputs=(True, True, True, True),
        anchors=None,
        type=NetworkTypes.NORMAL,
    ):
        if len(outputs) != 4:
            raise ValueError('The `outputs` argument should be a list of 4 boolean values')
        if not any(outputs):
            raise ValueError('We need at least one output block')

        if anchors is None:
            log.error('No anchors set; Using YoloV3_COCO, which we arbitrarily split over the different scales.')
            anchors = ln.util.Anchors.YoloV3_COCO

            num_out = sum(outputs)
            anchors_scale = [anchors.num_anchors // num_out for _ in range(num_out)]
            remaining_anchors = anchors.num_anchors % num_out
            while remaining_anchors > 0:
                anchors_scale[num_out-1] += 1
                num_out -= 1
                remaining_anchors -= 1

            anchors = anchors.set_scales((idx for idx, num in enumerate(anchors_scale) for _ in range(num)))
        elif not isinstance(anchors, ln.util.Anchors):
            anchors = ln.util.Anchors.from_darknet(self, anchors)
        if anchors.num_scales != sum(outputs):
            raise ln.util.AnchorError(anchors, f'Expected {sum(outputs)} scales, but got {anchors.num_scales}')
        if anchors.values_per_anchor != self.values_per_anchor:
            raise ln.util.AnchorError(anchors, f'Expected {self.values_per_anchor} values per anchor, but got {anchors.values_per_anchor}')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.outputs = outputs
        self.anchors = anchors
        self.type = NetworkTypes(type)
        self.stride = tuple(s for s, o in zip(self.stride, self.outputs) if o)
        self.inner_stride = max(self.stride[0], self.inner_stride)
        if sum(self.outputs) == 1:
            self.stride = self.stride[0]

        # Backbone
        if self.type == NetworkTypes.MODULATED:
            Backbone = lnn.backbone.ModulatedResnet
        elif self.type == NetworkTypes.DEFORMABLE:
            Backbone = lnn.backbone.DeformableResnet
        else:
            Backbone = lnn.backbone.Resnet

        relu = functools.partial(nn.LeakyReLU, 0.1, inplace=True)
        self.backbone = lnn.layer.FeatureExtractor(
            Backbone.RN_50(input_channels, 2048, relu=relu),
            ['6_residualgroup', '8_residualgroup'],
            True,
        )

        # Neck
        self.neck = self._create_neck(self.outputs)

        # Heads
        self.head = nn.ModuleDict()
        scale_idx = 0
        head_idx_start = 0
        any_enabled = False
        for idx, enabled in enumerate(self.outputs):
            if enabled:
                self.head[str(idx - head_idx_start)] = lnn.head.DetectionYoloAnchor(
                    256,
                    self.anchors.get_scale(scale_idx).num_anchors,
                    self.num_classes,
                    512,
                    relu=relu,
                )

                scale_idx += 1
                any_enabled = True
            elif not any_enabled:
                head_idx_start += 1

    @property
    def __name__(self):
        if self.type == NetworkTypes.MODULATED:
            return f'{self.__class__.__name__}_Modulated'
        elif self.type == NetworkTypes.DEFORMABLE:
            return f'{self.__class__.__name__}_Deformable'
        else:
            return self.__class__.__name__

    def _create_neck(self, outputs):
        start_output = 0
        num_outputs = 4
        begin, end = 1, 0
        for o in outputs[::-1]:
            if not o:
                start_output += begin
                num_outputs -= begin
                end += 1
            else:
                begin, end = 0, 0
        num_outputs -= end

        return lnn.layer.FPN(
            [512, 1024, 2048],
            256,
            num_outputs=num_outputs,
            start_output=start_output,
            make_prediction=lambda ci, co: lnn.layer.Conv2dReLU(ci, co, 3, 1, 1, bias=True),
            make_downsample=lambda ci, co: nn.Conv2d(ci, co, 3, 2, 1, bias=True),
        )

    def forward(self, x):
        C5, C3, C4 = self.backbone(x)
        neck = self.neck(C3, C4, C5)[::-1]
        outputs = [head(neck[int(idx)]) for idx, head in self.head.items()]

        if len(outputs) == 1:
            return outputs[0]
        return outputs


class M_ResnetYolo(ResnetYolo):
    """ Multi-scale Masked Yolo detection network with a ResNet50 backbone.

    Args:
        num_classes (int): Number of classes
        num_masks (int, optional): Number of prototype masks; Default **32**
        input_channels (int, optional): Number of input channels; Default **3**
        outputs (list<bool, 4>, optional): Which output heads to use; Default **(True, True, True, True)**
        anchors (ln.util.Anchors, optional): single-scale list of anchor boxes; Default **Darknet YoloV3 COCO**
        deformable (bool, optional): Whether to use deformable convolutions for conv3-conv5; Default **False**
        modulated (bool, optional): (if deformable) Whether to use modulated deformable convolutions; Default **False**

    Attributes:
        self.stride: Subsampling factors of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_resnet50: Remapping rules for weights from the :class:`~lightnet.models.Resnet50` model.
        self.Types: The different backbone types (``NORMAL``, ``DEFORMABLE``, ``MODULATED``)

    Warning:
        As with most of the lightnet networks, the `stride`, `inner_stride` and `mask_stride` can be accessed from the class.
        However, as this network allows you to select which output heads you want,
        these values can change and are thus only set correctly on initialized models!

    Note:
        The mask protonet head is always ran on the last output from the FPN and thus has a stride of 4.
        This ensures the masks have the biggest spatial resolution possible.

    Note:
        It is recommended to pass in custom anchors to this network,
        as we otherwise use the YoloV3 COCO anchors, which we arbitrarilly divide among the different output heads.

        The preferred way to pass anchors is to use the :class:`~lightnet.util.Anchors`.
        However, for compatibility reasons, you can also pass in a list of tuples,
        which will be interpreted as darknet anchors (relative to input dimensions).
    """
    mask_stride = (32, 16, 8, 4)

    def __init_module__(
        self,
        num_classes,
        num_masks=32,
        input_channels=3,
        outputs=(True, True, True, True),
        mask_output=-1,
        anchors=None,
        type=NetworkTypes.NORMAL,
    ):
        self.num_masks = num_masks
        self.mask_output = mask_output
        self.mask_stride = self.mask_stride[mask_output]
        super().__init_module__(num_classes, input_channels, outputs, anchors, type)

        # Head
        self.head = nn.ModuleDict()
        scale_idx = 0
        head_idx_start = 0
        any_enabled = False
        for idx, enabled in enumerate(self.outputs):
            if enabled:
                self.head[str(idx - head_idx_start)] = lnn.head.DetectionMaskedAnchor(
                    256,
                    self.anchors.get_scale(scale_idx).num_anchors,
                    self.num_classes,
                    self.num_masks,
                    512,
                )

                scale_idx += 1
                any_enabled = True
            elif not any_enabled:
                head_idx_start += 1

        self.mask_head = lnn.head.DetectionMaskedAnchor.Protonet(
            256,
            self.num_masks,
        )

    def _create_neck(self, outputs):
        # Always enable mask output
        outputs = list(outputs)
        outputs[self.mask_output] = True
        return super()._create_neck(outputs)

    def forward(self, x):
        C5, C3, C4 = self.backbone(x)
        neck = self.neck(C3, C4, C5)[::-1]
        outputs = [head(neck[int(idx)]) for idx, head in self.head.items()]
        mask = self.mask_head(neck[self.mask_output])

        if len(outputs) == 1:
            return (outputs[0], mask)
        return (outputs, mask)
