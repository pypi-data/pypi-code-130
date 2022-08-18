#
#   Transform any lightnet network for data fusion
#   Copyright EAVISE
#
import copy
import contextlib
import torch
from .. import layer as lnl
from ._lightnet import Lightnet

__all__ = ['Fusion']


class Fusion(torch.nn.Module):
    """
    This module takes a complete Lightnet network model and transforms it into a Fusion version. |br|
    More specifically, it will modify the backbone of the network to be a :class:`~lightnet.network.layer.FusionModule` of the original backbone.

    Args:
        network (lightnet.network.module.Lightnet): The network you want to transform
        fusion_channels (tuple<int>): The number of channels per fusion data type
        fusion_kernel (int): Kernel size for the fusion convolutions (should be an odd number); Default **1**
        input_shape (tuple<int>, optional): A possible input shape for the network; Default **automatically computed**

    Note:
        The ``network`` argument should be a :class:`~lightnet.network.module.Lightnet` module
        and contain a ``backbone`` and ``inner_stride`` variable.
        All provided :py:mod:`Lightnet Models <lightnet.models>` are valid targets.

    Note:
        If you do not pass an ``input_shape``,
        it will be automatically compute as: ``(1, fusion_channels[0], network.inner_stride, network.inner_stride)``.
        This means that you original network should be properly build so that its input channels match the input of the first fusion data type.

    Example:
        >>> # Create an RGB-D fusion model from YoloV2
        >>> net = ln.models.YoloV2(20)
        >>> fusion_net = ln.network.module.Fusion(net, (3, 1))
        >>> # Run network
        >>> input_tensor = torch.rand(1, 4, 416, 416)
        >>> output_tensor = fusion_net(input_tensor)
        >>> output_tensor.shape
        torch.Size([1, 125, 13, 13])
        >>> # Print network representation
        >>> fusion_net
        FusionYoloV2(
          (backbone): FusionModule(
            in_channels=(3, 1)
            (channel_conv): ModuleList(
              (0): Conv2d(3, 3, kernel_size=(1, 1), stride=(1, 1))
              (1): Conv2d(1, 3, kernel_size=(1, 1), stride=(1, 1))
            )
            (fusion_module): ModuleList(
              (0): FeatureExtractor(
                selection=[17_convbatch], return=True
                (module): Sequential(
                  (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (3_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (5_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (6_convbatch): Conv2dBatchReLU(128, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (10_convbatch): Conv2dBatchReLU(256, 128, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (11_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (12_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (13_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (14_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (15_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (16_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (17_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (18_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (19_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (20_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (21_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (22_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (23_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                )
              )
              (1): FeatureExtractor(
                selection=[17_convbatch], return=True
                (module): Sequential(
                  (1_convbatch): Conv2dBatchReLU(3, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (3_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (5_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (6_convbatch): Conv2dBatchReLU(128, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (10_convbatch): Conv2dBatchReLU(256, 128, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (11_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (12_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (13_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (14_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (15_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (16_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (17_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (18_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (19_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (20_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (21_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (22_convbatch): Conv2dBatchReLU(1024, 512, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (23_convbatch): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                )
              )
            )
            (fusion_conv): ModuleList(
              (0): Conv2d(2048, 1024, kernel_size=(1, 1), stride=(1, 1))
              (1): Conv2d(1024, 512, kernel_size=(1, 1), stride=(1, 1))
            )
          )
          (neck): ModuleList(
            (0): Sequential(
              (0): Conv2dBatchReLU(1024, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (1): Conv2dBatchReLU(1024, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            )
            (1): Sequential(
              (0): Conv2dBatchReLU(512, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
              (1): Reorg(stride=2)
            )
          )
          (head): Sequential(
            (0): Conv2dBatchReLU(1280, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            (1): Conv2d(1024, 125, kernel_size=(1, 1), stride=(1, 1))
          )
        )

        >>> # Create a Fusion model where the original input channels are different
        >>> net = ln.models.Yolt(20, input_channels=8)
        >>> fusion_net = ln.network.module.Fusion(net, (3, 2), input_shape=(1, 8, 416, 416))
        >>> input_tensor = torch.rand(1, 5, 416, 416)
        >>> output_tensor = fusion_net(input_tensor)
        >>> output_tensor.shape
        torch.Size([1, 125, 26, 26])
        >>> # Print network representation
        >>> fusion_net
        FusionYolt(
          (backbone): FusionModule(
            in_channels=(3, 2)
            (channel_conv): ModuleList(
              (0): Conv2d(3, 8, kernel_size=(1, 1), stride=(1, 1))
              (1): Conv2d(2, 8, kernel_size=(1, 1), stride=(1, 1))
            )
            (fusion_module): ModuleList(
              (0): FeatureExtractor(
                selection=[11_convbatch], return=True
                (module): Sequential(
                  (1_convbatch): Conv2dBatchReLU(8, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (3_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (5_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (6_convbatch): Conv2dBatchReLU(128, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (10_convbatch): Conv2dBatchReLU(256, 128, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (11_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (12_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (13_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (14_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (15_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (16_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (17_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                )
              )
              (1): FeatureExtractor(
                selection=[11_convbatch], return=True
                (module): Sequential(
                  (1_convbatch): Conv2dBatchReLU(8, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (2_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (3_convbatch): Conv2dBatchReLU(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (4_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (5_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (6_convbatch): Conv2dBatchReLU(128, 64, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (7_convbatch): Conv2dBatchReLU(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (8_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (9_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (10_convbatch): Conv2dBatchReLU(256, 128, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (11_convbatch): Conv2dBatchReLU(128, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (12_max): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
                  (13_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (14_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (15_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                  (16_convbatch): Conv2dBatchReLU(512, 256, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), LeakyReLU(negative_slope=0.1, inplace=True))
                  (17_convbatch): Conv2dBatchReLU(256, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
                )
              )
            )
            (fusion_conv): ModuleList(
              (0): Conv2d(1024, 512, kernel_size=(1, 1), stride=(1, 1))
              (1): Conv2d(512, 256, kernel_size=(1, 1), stride=(1, 1))
            )
          )
          (neck): ModuleList(
            (0): Sequential(
              (0): Conv2dBatchReLU(512, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
              (1): Conv2dBatchReLU(1024, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            )
            (1): Reorg(stride=2)
          )
          (head): Sequential(
            (0): Conv2dBatchReLU(2048, 1024, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), LeakyReLU(negative_slope=0.1, inplace=True))
            (1): Conv2d(1024, 125, kernel_size=(1, 1), stride=(1, 1))
          )
        )
    """
    __init_done = False

    def __init__(self, network, fusion_channels, fusion_kernel=1, input_shape=None):
        super().__init__()
        assert isinstance(network, Lightnet), 'The network should be a lightnet.network.module.Lightnet subclass'
        assert hasattr(network, 'backbone'), 'The network requires a "backbone" attribute'
        if input_shape is None:
            assert hasattr(network, 'inner_stride'), 'The network requires an "inner_stride" attribute'
            input_shape = (1, fusion_channels[0], network.inner_stride, network.inner_stride)

        self.fusion_channels = fusion_channels
        self.network = copy.deepcopy(network)
        self.network.backbone = lnl.FusionModule(
            self.network.backbone,
            fusion_channels,
            input_shape,
            fusion_kernel,
        )

        self.__init_done = True

    def forward(self, *args, **kwargs):
        return self.network.forward(*args, **kwargs)

    def __repr__(self):
        return f'Fusion{repr(self.network)}'

    def __str__(self):
        return f'Fusion(fusion_channels={self.fusion_channels}, network={str(self.network)})'

    def __getattr__(self, name):
        # Try to get attribute from super class
        with contextlib.suppress(AttributeError):
            return super().__getattr__(name)

        # Try to get attribute from self.network
        try:
            return getattr(self.network, name)
        except AttributeError as err:
            raise AttributeError(f'{name} attribute does not exist') from err

    def __setattr__(self, name, value):
        if self.__init_done and name not in dir(self) and hasattr(self.network, name):
            setattr(self.network, name, value)
        else:
            super().__setattr__(name, value)
