#
#   ResNet models
#   Copyright EAVISE
#
import logging
import lightnet.network as lnn
import torch.nn as nn

__all__ = ['Resnet50', 'Resnet101', 'Resnet152']
log = logging.getLogger('lightnet.models')


class Resnet(lnn.module.Lightnet):
    """ Base Resnet network """
    inner_stride = 32

    def __init_module__(
        self,
        groups,
        num_classes,
        input_channels=3,
        deformable=False,
        modulated=False,
    ):
        self.num_classes = num_classes
        self.input_channels = input_channels
        self.deformable = deformable
        self.modulated = modulated

        if not self.deformable and self.modulated:
            log.error('Modulated is set to true, but we are not using deformable convolutions.')

        # Network
        if deformable and modulated:
            Backbone = lnn.backbone.ModulatedResnet
        elif deformable:
            Backbone = lnn.backbone.DeformableResnet
        else:
            Backbone = lnn.backbone.Resnet

        self.backbone = Backbone(input_channels, 2048, groups)
        self.head = lnn.head.ClassificationFC(2048, num_classes)

    def __init_weights__(self, name, mod):
        if name.endswith('residual.2.layers.1') or ('residualgroup' in name and name.endswith('2.layers.1')):
            nn.init.constant_(mod.weight, 0)
            nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)

        return x

    def remap_torchvision(self, k):
        if k.startswith('layer'):
            layer, num, mod, remainder = k.split('.', 3)
            layernum = int(layer[-1])
            num = int(num)

            start = (
                ('backbone.3_residual.', 'backbone.4_residualgroup.'),
                ('backbone.5_residual.', 'backbone.6_residualgroup.'),
                ('backbone.7_residual.', 'backbone.8_residualgroup.'),
                ('backbone.9_residual.', 'backbone.10_residualgroup.'),
            )[layernum - 1][int(num != 0)]
            if num != 0:
                start += f'{num-1}.'

            if self.deformable and layernum >= 2:
                mid = {
                    'conv1': '0.layers.0.conv.',
                    'bn1': '0.layers.1.',
                    'conv2': '1.layers.0.conv.',
                    'bn2': '1.layers.1.',
                    'conv3': '2.layers.0.conv.',
                    'bn3': '2.layers.1.',
                    'downsample': 'skip.layers.',
                }[mod]

                if mod == 'downsample' and remainder.startswith('0'):
                    mid += '0.conv.'
                    remainder = remainder[2:]

            else:
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
        else:
            return (
                (r'^conv1.(.*)', r'backbone.1_convbatch.layers.0.\1'),
                (r'^bn1.(.*)', r'backbone.1_convbatch.layers.1.\1'),
                (r'^fc.(.*)', r'head.2.\1'),
            )


class Resnet50(Resnet):
    """ ResNet50 implementation :cite:`resnet`.

    Args:
        num_classes (Number): Number of classes
        input_channels (Number, optional): Number of input channels; Default **3**
        deformable (bool, optional): Whether to use deformable convolutions for conv3-conv5; Default **False**
        modulated (bool, optional): (if deformable) Whether to use modulated deformable convolutions; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    Note:
        We zero-initialize the last BN in each residual branch,
        so that the residual branch starts with zeros and each residual block behaves like an identity.
        This improves the model by 0.2~0.3% according to :cite:`imagenet_1h`.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_resnet
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        deformable=False,
        modulated=False,
    ):
        super().__init_module__(lnn.backbone.Resnet.groups[50], num_classes, input_channels, deformable, modulated)


class Resnet101(Resnet):
    """ ResNet101 implementation :cite:`resnet`.

    Args:
        num_classes (Number): Number of classes
        input_channels (Number, optional): Number of input channels; Default **3**
        deformable (bool, optional): Whether to use deformable convolutions for conv3-conv5; Default **False**
        modulated (bool, optional): (if deformable) Whether to use modulated deformable convolutions; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    Note:
        We zero-initialize the last BN in each residual branch,
        so that the residual branch starts with zeros and each residual block behaves like an identity.
        This improves the model by 0.2~0.3% according to :cite:`imagenet_1h`.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_resnet
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        deformable=False,
        modulated=False,
    ):
        super().__init_module__(lnn.backbone.Resnet.groups[101], num_classes, input_channels, deformable, modulated)


class Resnet152(Resnet):
    """ ResNet152 implementation :cite:`resnet`.

    Args:
        num_classes (Number): Number of classes
        input_channels (Number, optional): Number of input channels; Default **3**
        deformable (bool, optional): Whether to use deformable convolutions for conv3-conv5; Default **False**
        modulated (bool, optional): (if deformable) Whether to use modulated deformable convolutions; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    Note:
        We zero-initialize the last BN in each residual branch,
        so that the residual branch starts with zeros and each residual block behaves like an identity.
        This improves the model by 0.2~0.3% according to :cite:`imagenet_1h`.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_resnet
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        deformable=False,
        modulated=False,
    ):
        super().__init_module__(lnn.backbone.Resnet.groups[152], num_classes, input_channels, deformable, modulated)
