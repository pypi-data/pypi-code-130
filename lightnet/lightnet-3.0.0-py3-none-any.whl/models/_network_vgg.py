#
#   VGG models
#   Copyright EAVISE
#
import lightnet.network as lnn

__all__ = ['VGG11', 'VGG13', 'VGG16', 'VGG19']


class VGG(lnn.module.Lightnet):
    """ Base VGG network """
    inner_stride = 32

    def __init_module__(
        self,
        Backbone,
        num_classes,
        input_channels=3,
        batch_norm=False,
    ):
        self.num_classes = num_classes
        self.input_channels = input_channels
        self.batch_norm = batch_norm

        # Network
        self.backbone = Backbone(input_channels, 512, batch_norm=batch_norm)
        self.head = lnn.head.ClassificationFC(512, num_classes, pooling_size=7, inter_channels=4096)

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)

        return x

    def remap_torchvision(self, k):
        if k.startswith('features'):
            _, num, remainder = k.split('.', 2)
            num = int(num)

            delta = 1
            step = -2 if self.batch_norm else -1
            for n, _ in self.backbone.named_children():
                if n.endswith('conv'):
                    target_num = int(n.split('_', 1)[0])
                    if num + delta == target_num:
                        return f'backbone.{n}.layers.0.{remainder}'
                    elif self.batch_norm and num + delta - 1 == target_num:
                        return f'backbone.{n}.layers.1.{remainder}'

                    delta += step

            return None
        else:
            return (
                (r'^classifier.0.(.*)', r'head.2.\1'),
                (r'^classifier.3.(.*)', r'head.5.\1'),
                (r'^classifier.6.(.*)', r'head.8.\1'),
            )


class VGG11(VGG):
    """ VGG11 implementation :cite:`vgg`. |br|
    This is configuration A from the paper.

    Args:
        num_classes (Number, optional): Number of classes; Default **1000**
        input_channels (Number, optional): Number of input channels; Default **3**
        batch_norm (bool, optional): Whether are not to have batchnorm after each convolution; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_vgg
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        batch_norm=False,
    ):
        super().__init_module__(lnn.backbone.VGG.A, num_classes, input_channels, batch_norm)


class VGG13(VGG):
    """ VGG13 implementation :cite:`vgg`. |br|
    This is configuration B from the paper.

    Args:
        num_classes (Number, optional): Number of classes; Default **1000**
        input_channels (Number, optional): Number of input channels; Default **3**
        batch_norm (bool, optional): Whether are not to have batchnorm after each convolution; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_vgg
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        batch_norm=False,
    ):
        super().__init_module__(lnn.backbone.VGG.B, num_classes, input_channels, batch_norm)


class VGG16(VGG):
    """ VGG16 implementation :cite:`vgg`. |br|
    This is configuration D from the paper.

    Args:
        num_classes (Number, optional): Number of classes; Default **1000**
        input_channels (Number, optional): Number of input channels; Default **3**
        batch_norm (bool, optional): Whether are not to have batchnorm after each convolution; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_vgg
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        batch_norm=False,
    ):
        super().__init_module__(lnn.backbone.VGG.D, num_classes, input_channels, batch_norm)


class VGG19(VGG):
    """ VGG19 implementation :cite:`vgg`. |br|
    This is configuration E from the paper.

    Args:
        num_classes (Number, optional): Number of classes; Default **1000**
        input_channels (Number, optional): Number of input channels; Default **3**
        batch_norm (bool, optional): Whether are not to have batchnorm after each convolution; Default **False**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_torchvision: Remapping rules for weights from the `torchvision implementation <torchvision_>`_.

    .. _torchvision: https://pytorch.org/hub/pytorch_vision_vgg
    """
    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        batch_norm=False,
    ):
        super().__init_module__(lnn.backbone.VGG.E, num_classes, input_channels, batch_norm)
