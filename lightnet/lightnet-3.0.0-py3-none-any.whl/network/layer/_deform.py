#
#   Deformable Convolutional layer
#   Copyright EAVISE
#
from packaging import version
import torch.nn as nn
import torchvision
from torchvision import ops

__all__ = ['DeformableConv2d', 'ModulatedDeformableConv2d']


class DeformableConv2d(nn.Module):
    """ This layer implements a Deformable 2D Convolution :cite:`deformable_conv`. |br|
    We run a simple :class:`~torch.nn.Conv2d` on the input to get the offsets,
    which we then use with the :class:`torchvision.ops.DeformConv2d` operator.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        kernel_size (int or tuple): Size of the kernel of the convolutions
        stride (int or tuple, optional): Stride of the convolutions; Default **1**
        padding (int or tuple, optional): padding of the convolutions; Default **0**
        bias (bool, optional): Whether or not to enable the bias term for the deformable convolution; Default **True**
        lr_scale (number, optional): Learning Rate scaling for the offset convolution; Default **0.1**

    .. figure:: /.static/api/deformableconv.*
       :width: 100%
       :alt: Deformable Convolution module design

    Example:
        >>> module = ln.network.layer.DeformableConv2d(3, 32, 3, 1, 1)
        >>> print(module)
        DeformableConv2d(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), lr_scale=0.1)
        >>> in_tensor = torch.rand(1, 3, 10, 10)
        >>> out_tensor = module(in_tensor)
        >>> out_tensor.shape
        torch.Size([1, 32, 10, 10])

    Note:
        The offset convolution never uses a bias term.
    """
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        padding=0,
        bias=True,
        lr_scale=0.1,
    ):
        super().__init__()

        self.conv = ops.DeformConv2d(in_channels, out_channels, kernel_size, stride, padding, bias=bias)
        self.deformable_module = nn.Conv2d(
            in_channels,
            2 * self.conv.kernel_size[1] * self.conv.kernel_size[0],
            kernel_size,
            stride,
            padding,
            bias=False,
        )

        self._lr_scale_hook = None
        self.lr_scale = lr_scale

    def forward(self, x):
        offset = self.deformable_module(x)
        return self.conv(x, offset)

    def _reduce_lr(self, grad):
        return self.lr_scale * grad

    @property
    def lr_scale(self):
        return self._lr_scale

    @lr_scale.setter
    def lr_scale(self, value):
        self._lr_scale = value

        if value != 1 and self._lr_scale_hook is None:
            self._lr_scale_hook = self.deformable_module.weight.register_hook(self._reduce_lr)
        elif value == 1 and self._lr_scale_hook is not None:
            self._lr_scale_hook.remove()
            self._lr_scale_hook = None

    def __repr__(self):
        s = '{name}({in_channels}, {out_channels}, kernel_size={kernel_size}, stride={stride}, padding={padding}, lr_scale={lr_scale})'
        return s.format(
            name=self.__class__.__name__,
            in_channels=self.conv.in_channels,
            out_channels=self.conv.out_channels,
            kernel_size=self.conv.kernel_size,
            stride=self.conv.stride,
            padding=self.conv.padding,
            lr_scale=self.lr_scale,
        )

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.conv, name)


class ModulatedDeformableConv2d(DeformableConv2d):
    """ This layer implements a Modulated Deformable 2D Convolution :cite:`deformable_conv2`. |br|
    We run a simple :class:`~torch.nn.Conv2d` on the input to get the masks and offsets,
    which we then use with the :class:`torchvision.ops.DeformConv2d` operator.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        kernel_size (int or tuple): Size of the kernel of the convolutions
        stride (int or tuple, optional): Stride of the convolutions; Default **1**
        padding (int or tuple, optional): padding of the convolutions; Default **0**
        bias (bool, optional): Whether or not to enable the bias term for the deformable convolution; Default **True**
        lr_scale (number, optional): Learning Rate scaling for the modulator convolution; Default **0.1**

    .. figure:: /.static/api/modulateddeformableconv.*
       :width: 100%
       :alt: Deformable Convolution module design

    Example:
        >>> module = ln.network.layer.ModulatedDeformableConv2d(3, 32, 3, 1, 1)
        >>> print(module)
        ModulatedDeformableConv2d(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), lr_scale=0.1)
        >>> in_tensor = torch.rand(1, 3, 10, 10)
        >>> out_tensor = module(in_tensor)
        >>> out_tensor.shape
        torch.Size([1, 32, 10, 10])

    Note:
        The modulation convolution never uses a bias term.
    """
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        padding=0,
        bias=True,
        lr_scale=0.1,
    ):
        super(DeformableConv2d, self).__init__()

        if version.parse(torchvision.__version__) < version.parse('0.9.0'):
            raise NotImplementedError('ModulatedDeformableConvolutions require torchvision 0.9.0')

        self.conv = ops.DeformConv2d(in_channels, out_channels, kernel_size, stride, padding, bias=bias)
        self.deformable_module = nn.Conv2d(
            in_channels,
            3 * self.conv.kernel_size[1] * self.conv.kernel_size[0],
            kernel_size,
            stride,
            padding,
            bias=False,
        )

        self._offset_shape = 2 * self.conv.kernel_size[1] * self.conv.kernel_size[0]
        self._lr_scale_hook = None
        self.lr_scale = lr_scale

    def forward(self, x):
        module = self.deformable_module(x)
        offset = module[:, :self._offset_shape, ...]
        mask = module[:, self._offset_shape:, ...].sigmoid()

        return self.conv(x, offset, mask)
