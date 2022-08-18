#
#   Yolact instance segmentation head
#   Copyright EAVISE
#
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['DetectionYolact']


class DetectionYolact(BaseModule):
    """ Yolact Instance Segmentation head.

    Args:
        in_channels (int): Number of input channels
        num_anchors (int): Number of anchors
        num_classes (int): Number of classes
        num_masks (int): Number of prototype masks

    .. rubric:: Models:

    - :class:`~lightnet.models.Yolact50`
    - :class:`~lightnet.models.Yolact101`

    Examples:
        >>> detection_head = ln.network.head.DetectionYolact.Prediction(256, 3, 20, 32)
        >>> mask_head = ln.network.head.DetectionYolact.Protonet(256, 32)
        >>> print(detection_head)
        Sequential(
          (0): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (1): ParallelCat(
            (0): Conv2d(256, 12, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (1): Conv2d(256, 63, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
            (2): Sequential(
              (0): Conv2d(256, 96, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
              (1): Tanh()
            )
          )
        )
        >>> print(mask_head)
        Sequential(
          (0): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (1): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (2): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (3): Upsample(scale_factor=2.0, mode=bilinear)
          (4): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (5): Conv2dReLU(256, 32, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
        )
        >>> in_tensor = torch.rand(1, 256, 8, 8)
        >>> out_tensor = prediction_head(in_tensor)
        >>> print(out_tensor.shape)
        torch.Size([1, 171, 8, 8])
        >>> mask_tensor = mask_head(in_tensor)
        >>> print(mask_tensor.shape)
        torch.Size([1, 32, 16, 16])
    """
    wrapper = nn.ModuleDict

    @BaseModule.layers(primary=True)
    def Prediction(
        in_channels,
        num_anchors,
        num_classes,
        num_masks,
        inter_channels=256,
    ):
        """
        Create the object detection head.

        Args:
            in_channels (int): Number of input channels
            num_anchors (int): Number of anchors
            num_classes (int): Number of classes
            num_masks (int): Number of prototype masks
            inter_channels (int, optional): How many channels to use for the intermediate convolutions; Default **256**
        """
        return (
            lnl.Conv2dReLU(in_channels, inter_channels, 3, 1, 1, bias=True),
            lnl.ParallelCat(
                nn.Conv2d(inter_channels, 4*num_anchors, 3, 1, 1, bias=True),
                nn.Conv2d(inter_channels, (num_classes+1)*num_anchors, 3, 1, 1, bias=True),
                nn.Sequential(
                    nn.Conv2d(inter_channels, num_masks*num_anchors, 3, 1, 1, bias=True),
                    nn.Tanh(),
                ),
            ),
        )

    @BaseModule.layers
    def Protonet(
        in_channels,
        num_masks,
        inter_channels=256,
    ):
        """
        Create the mask prototype head.

        Args:
            in_channels (int): Number of input channels
            num_masks (int): Number of prototype masks
            inter_channels (int, optional): How many channels to use for the intermediate convolutions; Default **256**
        """
        return (
            lnl.Conv2dReLU(in_channels, inter_channels, 3, 1, 1, bias=True),
            lnl.Conv2dReLU(inter_channels, inter_channels, 3, 1, 1, bias=True),
            lnl.Conv2dReLU(inter_channels, inter_channels, 3, 1, 1, bias=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
            lnl.Conv2dReLU(inter_channels, inter_channels, 3, 1, 1, bias=True),
            lnl.Conv2dReLU(inter_channels, num_masks, 1, 1, 0, bias=True),
        )
