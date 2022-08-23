from typing import Any, List, Optional, OrderedDict

import torch
from torch import nn
from torch.nn import functional as F
from torchvision.models._utils import IntermediateLayerGetter
from torchvision.models.resnet import resnet101, ResNet101_Weights
from .resnet import ResNet, resnet101_nch
from torchvision.models.segmentation._utils import _SimpleSegmentationModel
from torchvision.models.segmentation.fcn import FCNHead
from torchvision.models.segmentation.deeplabv3 import ASPP, DeepLabV3

__all__ = [
    "DeepLabV3",
    "deeplabv3plus_resnet101",
    "multitask_model_multi_encoder",
    "multitask_model"
]

class DeepLabV3Plus(_SimpleSegmentationModel):
    def forward(self, x):
        input_shape = x.shape[-2:]
        # contract: features is a dict of tensors
        features = self.backbone(x)

        result = OrderedDict()
        x = self.classifier(features)
        x = F.interpolate(x, size=input_shape, mode="bilinear", align_corners=False)
        result["out"] = x

        if self.aux_classifier is not None:
            x = features["aux"]
            x = self.aux_classifier(x)
            x = F.interpolate(x, size=input_shape, mode="bilinear", align_corners=False)
            result["aux"] = x

        return result

class MultiTaskModel(nn.Module):
    def __init__(
        self, backbones: nn.ModuleList, encoder_chs: List[int],
        hl_project: nn.Module, ll_project: nn.Module,
        height_decoder: nn.Module, seg_decoder: nn.Module, aux_classifier: Optional[nn.Module] = None
        ) -> None:
        super().__init__()
        self.backbones = backbones
        self.encoder_chs = encoder_chs
        self.hl_project = hl_project
        self.ll_project = ll_project
        self.height_decoder = height_decoder
        self.seg_decoder = seg_decoder
        self.aux_classifier = aux_classifier

    def forward(self, x):
        input_shape = x.shape[-2:]
        assert x.shape[1] == sum(self.encoder_chs), 'channels in input not equal to sum of encoders input channels!'
        # contract: features is a dict of tensors
        features_list = [
            backbone(
                x[:, sum(self.encoder_chs[:i]) : sum(self.encoder_chs[:i+1])]
            ) for i, backbone in enumerate(self.backbones) 
        ]
        features = {
            'low_level': self.ll_project(
                torch.cat([f['low_level'] for f in features_list], dim=1)
            ),
            'out': self.hl_project(
                torch.cat([f['out'] for f in features_list], dim=1)
            )
        }
        result = OrderedDict()
        height_x = self.height_decoder(features)
        seg_x = self.seg_decoder(features)
        height_x = F.interpolate(height_x, size=input_shape, mode="bilinear", align_corners=False)
        seg_x = F.interpolate(seg_x, size=input_shape, mode="bilinear", align_corners=False)
        result["height"] = height_x
        result["segmentation"] = seg_x

        if self.aux_classifier is not None:
            x = features["aux"]
            x = self.aux_classifier(x)
            x = F.interpolate(x, size=input_shape, mode="bilinear", align_corners=False)
            result["aux"] = x

        return result

class DeepLabHead(nn.Sequential):
    def __init__(self, in_channels: int, num_classes: int) -> None:
        super().__init__(
            ASPP(in_channels, [12, 24, 36]),
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, num_classes, 1),
        )

class DeepLabPlusHead(nn.Module):
    def __init__(self, in_channels: int, low_level_channels: int,  num_classes: int) -> None:
        super().__init__()
        self.project = nn.Sequential(
            nn.Conv2d(low_level_channels, 48, 1, bias=False),
            nn.BatchNorm2d(48),
            nn.ReLU(),
        )
        self.aspp = ASPP(in_channels, [12, 24, 36])
        self.classifier = nn.Sequential(
            nn.Conv2d(304, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, num_classes, 1),
        )
        self._init_weights()

    def forward(self, feature):
        low_level_feature = self.project(feature['low_level'])
        high_level_feature = self.aspp(feature['out'])
        upscale_hl_feature = F.interpolate(high_level_feature, size=low_level_feature.shape[-2:], mode='bilinear', align_corners=False)
        combined_feature = torch.cat([low_level_feature, upscale_hl_feature], dim=1)
        return self.classifier(combined_feature)

    def _init_weights(self): # need to do this because we have no pretraining for DeepLabV3+
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

class FeatureProjection(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.project = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            # nn.BatchNorm2d(out_channels),
            nn.ReLU(),
        )

        self._init_weights()
    
    def forward(self, x):
        return self.project(x)

    def _init_weights(self): # need to do this because we have no pretraining for DeepLabV3+
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)


def _deeplabv3_resnet(
    backbone: ResNet,
    num_classes: int,
    aux: Optional[bool],
    plus: Optional[bool]=False
) -> DeepLabV3:
    return_layers = {"layer4": "out"}
    if plus:
        return_layers["layer1"] = "low_level"
    if aux:
        return_layers["layer3"] = "aux"
    backbone = IntermediateLayerGetter(backbone, return_layers=return_layers)

    aux_classifier = FCNHead(1024, num_classes) if aux else None
    classifier = DeepLabPlusHead(2048, 256, num_classes) if plus else DeepLabHead(2048, num_classes)

    if plus:
        return DeepLabV3Plus(backbone, classifier, aux_classifier)
    else:
        return DeepLabV3(backbone, classifier, aux_classifier)

def _multitask_model(
    backbones: nn.ModuleList,
    encoder_chs: List[int],
    num_seg_classes: int,
    aux: Optional[bool]
) -> MultiTaskModel:
    return_layers = {"layer4": "out", "layer1": "low_level"}
    if aux:
        return_layers["layer3"] = "aux"
    backbones = nn.ModuleList([
        IntermediateLayerGetter(backbone, return_layers=return_layers) for backbone in backbones
    ])

    high_lvl_chs = 2048
    low_lvl_chs = 256
    high_lvl_project = FeatureProjection(high_lvl_chs*len(encoder_chs), high_lvl_chs)
    low_lvl_project = FeatureProjection(low_lvl_chs*len(encoder_chs), low_lvl_chs)

    aux_classifier = FCNHead(1024, num_seg_classes) if aux else None # kind of useless tbh
    height_decoder = DeepLabPlusHead(high_lvl_chs, low_lvl_chs, 1) # always one channel for height
    seg_decoder = DeepLabPlusHead(high_lvl_chs, low_lvl_chs, num_seg_classes)

    return MultiTaskModel(backbones, encoder_chs, high_lvl_project, low_lvl_project, height_decoder, seg_decoder, aux_classifier)

def multitask_model(
    *,
    num_seg_classes: Optional[int] = None,
    aux_loss: Optional[bool] = None,
    weights_backbone: Optional[ResNet101_Weights] = ResNet101_Weights.IMAGENET1K_V2,
    **kwargs: Any,
) -> DeepLabV3:
    """Constructs a multitask model with a ResNet-101 backbone and decoder heads for DSM height and surface segmentation.
    Based on DeepLabV3+

    Reference: `Rethinking Atrous Convolution for Semantic Image Segmentation <https://arxiv.org/abs/1706.05587>`__.
    Reference: `Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation <https://arxiv.org/pdf/1802.02611>`__.
    """
    weights_backbone = ResNet101_Weights.verify(weights_backbone)

    if num_seg_classes is None:
        num_seg_classes = 21

    backbone = resnet101(weights=weights_backbone, replace_stride_with_dilation=[False, True, True])
    model = _multitask_model(nn.ModuleList([backbone]), [3], num_seg_classes, aux_loss)

    return model

def multitask_model_multi_encoder(
    *,
    encoder_chs = [1],
    num_seg_classes: Optional[int] = None,
    aux_loss: Optional[bool] = None,
    weights_backbone: Optional[ResNet101_Weights] = ResNet101_Weights.IMAGENET1K_V2,
    **kwargs: Any,
) -> DeepLabV3:
    """Constructs a multitask model with a ResNet-101 backbone and decoder heads for DSM height and surface segmentation.
    Based on DeepLabV3+

    Reference: `Rethinking Atrous Convolution for Semantic Image Segmentation <https://arxiv.org/abs/1706.05587>`__.
    Reference: `Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation <https://arxiv.org/pdf/1802.02611>`__.
    """
    # weights_backbone = ResNet101_Weights.verify(weights_backbone)
    weights_backbone = None # no pre-trained model available for single channel

    if num_seg_classes is None:
        num_seg_classes = 21

    backbones = nn.ModuleList([
        resnet101_nch(in_img_chs=chs, replace_stride_with_dilation=[False, True, True]) for chs in encoder_chs
    ])
    model = _multitask_model(backbones, encoder_chs, num_seg_classes, aux_loss)

    return model

def deeplabv3plus_resnet101(
    *,
    num_classes: Optional[int] = None,
    aux_loss: Optional[bool] = None,
    weights_backbone: Optional[ResNet101_Weights] = ResNet101_Weights.IMAGENET1K_V2,
    **kwargs: Any,
) -> DeepLabV3:
    """Constructs a DeepLabV3+ model with a ResNet-101 backbone.

    Reference: `Rethinking Atrous Convolution for Semantic Image Segmentation <https://arxiv.org/abs/1706.05587>`__.
    """
    weights_backbone = ResNet101_Weights.verify(weights_backbone)

    if num_classes is None:
        num_classes = 21

    backbone = resnet101(weights=weights_backbone, replace_stride_with_dilation=[False, True, True])
    model = _deeplabv3_resnet(backbone, num_classes, aux_loss, plus=True)

    return model
