#
#   Convolutional layers
#   Copyright EAVISE
#
from functools import partial
import torch.nn as nn

__all__ = ['Conv2dBatch', 'Conv2dBatchReLU', 'Conv2dReLU']


class Conv2dBatch(nn.Module):
    """ This convenience layer groups a 2D convolution and a batchnorm.
    They are executed in a sequential manner.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        kernel_size (int or tuple): Size of the kernel of the convolution
        stride (int or tuple): Stride of the convolution
        padding (int or tuple): padding of the convolution
        bias (bool, optional): Whether or not to enable the bias term for the convolution; Default **False**
        momentum (number, optional): momentum of the moving averages of the normalization; Default **0.1**
        conv (nn.Module class, optional): Kind of 2D convolution to use; Default :class`~torch.nn.Conv2d`

    .. figure:: /.static/api/conv2dbatch.*
       :width: 100%
       :alt: Conv2dBatch module design

    Note:
        Possible options for the `conv` argument are:

        - :class:`torch.nn.Conv2d`
        - :class:`lightnet.network.layer.DeformableConv2d`
        - :class:`lightnet.network.layer.ModulatedDeformableConv2d`

    Example:
        >>> module = ln.network.layer.Conv2dBatch(3, 32, 3, 1, 1)
        >>> print(module)
        Conv2dBatch(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        >>> in_tensor = torch.rand(1, 3, 10, 10)
        >>> out_tensor = module(in_tensor)
        >>> out_tensor.shape
        torch.Size([1, 32, 10, 10])
    """
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride,
        padding,
        bias=False,
        momentum=0.1,
        conv=nn.Conv2d,
    ):
        super().__init__()

        self.layers = nn.ModuleList([
            conv(in_channels, out_channels, kernel_size, stride, padding, bias=bias),
            nn.BatchNorm2d(out_channels, momentum=momentum),
        ])

    def forward(self, x):
        x = self.layers[0](x)
        x = self.layers[1](x)
        return x

    def __repr__(self):
        s = '{name}Batch({in_channels}, {out_channels}, kernel_size={kernel_size}, stride={stride}, padding={padding})'
        return s.format(
            name=self.layers[0].__class__.__name__,
            in_channels=self.layers[0].in_channels,
            out_channels=self.layers[0].out_channels,
            kernel_size=self.layers[0].kernel_size,
            stride=self.layers[0].stride,
            padding=self.layers[0].padding,
        )

    @property
    def in_channels(self):
        return self.layers[0].in_channels

    @property
    def out_channels(self):
        return self.layers[0].out_channels


class Conv2dBatchReLU(nn.Module):
    """ This convenience layer groups a 2D convolution, a batchnorm and a ReLU.
    They are executed in a sequential manner.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        kernel_size (int or tuple): Size of the kernel of the convolution
        stride (int or tuple): Stride of the convolution
        padding (int or tuple): padding of the convolution
        bias (bool, optional): Whether or not to enable the bias term for the convolution; Default **False**
        momentum (number, optional): momentum of the moving averages of the normalization; Default **0.1**
        relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`
        conv (nn.Module class, optional): Kind of 2D convolution to use; Default :class`~torch.nn.Conv2d`

    .. figure:: /.static/api/conv2dbatchrelu.*
       :width: 100%
       :alt: Conv2dBatchReLU module design

    Note:
        Possible options for the `conv` argument are:

        - :class:`torch.nn.Conv2d`
        - :class:`lightnet.network.layer.DeformableConv2d`
        - :class:`lightnet.network.layer.ModulatedDeformableConv2d`

    Example:
        >>> module = ln.network.layer.Conv2dBatchReLU(3, 32, 3, 1, 1)
        >>> print(module)
        Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
        >>> in_tensor = torch.rand(1, 3, 10, 10)
        >>> out_tensor = module(in_tensor)
        >>> out_tensor.shape
        torch.Size([1, 32, 10, 10])
    """
    default_relu = partial(nn.ReLU, inplace=True)

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride,
        padding,
        bias=False,
        momentum=0.1,
        relu=default_relu,
        conv=nn.Conv2d,
    ):
        super().__init__()

        self.layers = nn.ModuleList([
            conv(in_channels, out_channels, kernel_size, stride, padding, bias=bias),
            nn.BatchNorm2d(out_channels, momentum=momentum),
            relu(),
        ])

    def forward(self, x):
        x = self.layers[0](x)
        x = self.layers[1](x)
        x = self.layers[2](x)
        return x

    def __repr__(self):
        s = '{name}BatchReLU({in_channels}, {out_channels}, kernel_size={kernel_size}, stride={stride}, padding={padding}, {relu})'
        return s.format(
            name=self.layers[0].__class__.__name__,
            in_channels=self.layers[0].in_channels,
            out_channels=self.layers[0].out_channels,
            kernel_size=self.layers[0].kernel_size,
            stride=self.layers[0].stride,
            padding=self.layers[0].padding,
            relu=self.layers[2],
        )

    @property
    def in_channels(self):
        return self.layers[0].in_channels

    @property
    def out_channels(self):
        return self.layers[0].out_channels


class Conv2dReLU(nn.Module):
    """ This convenience layer groups a 2D convolution and a ReLU.
    They are executed in a sequential manner.

    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        kernel_size (int or tuple): Size of the kernel of the convolution
        stride (int or tuple): Stride of the convolution
        padding (int or tuple): padding of the convolution
        bias (bool, optional): Whether or not to enable the bias term for the convolution; Default **False**
        relu (class, optional): Which ReLU to use; Default :class:`torch.nn.ReLU`
        conv (nn.Module class, optional): Kind of 2D convolution to use; Default :class`~torch.nn.Conv2d`

    .. figure:: /.static/api/conv2drelu.*
       :width: 100%
       :alt: Conv2dBatchReLU module design

    Note:
        Possible options for the `conv` argument are:

        - :class:`torch.nn.Conv2d`
        - :class:`lightnet.network.layer.DeformableConv2d`
        - :class:`lightnet.network.layer.ModulatedDeformableConv2d`

    Example:
        >>> module = ln.network.layer.Conv2dReLU(3, 32, 3, 1, 1)
        >>> print(module)
        Conv2dReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
        >>> in_tensor = torch.rand(1, 3, 10, 10)
        >>> out_tensor = module(in_tensor)
        >>> out_tensor.shape
        torch.Size([1, 32, 10, 10])
    """
    default_relu = partial(nn.ReLU, inplace=True)

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride,
        padding,
        bias=False,
        relu=default_relu,
        conv=nn.Conv2d,
    ):
        super().__init__()

        self.layers = nn.ModuleList([
            conv(in_channels, out_channels, kernel_size, stride, padding, bias=bias),
            relu(),
        ])

    def forward(self, x):
        x = self.layers[0](x)
        x = self.layers[1](x)
        return x

    def __repr__(self):
        s = '{name}ReLU({in_channels}, {out_channels}, kernel_size={kernel_size}, stride={stride}, padding={padding}, {relu})'
        return s.format(
            name=self.layers[0].__class__.__name__,
            in_channels=self.layers[0].in_channels,
            out_channels=self.layers[0].out_channels,
            kernel_size=self.layers[0].kernel_size,
            stride=self.layers[0].stride,
            padding=self.layers[0].padding,
            relu=self.layers[1],
        )

    @property
    def in_channels(self):
        return self.layers[0].in_channels

    @property
    def out_channels(self):
        return self.layers[0].out_channels
