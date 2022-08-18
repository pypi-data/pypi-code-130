#
#   Yolact instance segmentation head
#   Copyright EAVISE
#
import torch.nn as nn
from .. import layer as lnl
from .._basemodule import BaseModule

__all__ = ['DetectionMaskedAnchor']


class DetectionMaskedAnchor(BaseModule):
    """ Masked Anchor Detection head. |br|
    This heads predicts instance segmentation masks as well as bounding boxes.

    It works in a similar way as :cite:`yolact`, where it outputs prototype masks as well as the bounding boxes.
    Each bounding box then outputs a number for each mask, which are then used to generate the final mask foreach bounding box by taking a linear combination.

    .. rubric:: Models:

    - :class:`~lightnet.models.M_DYolo`
    - :class:`~lightnet.models.M_YoloV2`
    - :class:`~lightnet.models.M_YoloV3`
    - :class:`~lightnet.models.M_Yolt`

    Note:
        Every model needs at least one detection head and one mask protonet head.

    Examples:
        >>> detection_head = ln.network.head.DetectionMaskedAnchor.Prediction(1280, 5, 20, 32)
        >>> mask_head = ln.network.head.DetectionMaskedAnchor.Protonet(1280, 32)
        >>> print(detection_head)
        Sequential(
          (0): Conv2dReLU(1280, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (1): ParallelCat(
            (0): Conv2d(256, 125, kernel_size=(1, 1), stride=(1, 1))
            (1): Sequential(
              (0): Conv2d(256, 160, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
              (1): Tanh()
            )
          )
        )
        >>> print(mask_head)
        Sequential(
          (0): Conv2dReLU(1280, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (1): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (2): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (3): Upsample(scale_factor=2.0, mode=bilinear)
          (4): Conv2dReLU(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), ReLU(inplace=True))
          (5): Conv2dReLU(256, 32, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), ReLU(inplace=True))
        )
        >>> in_tensor = torch.rand(1, 1280, 13, 13)
        >>> out = detection_head(in_tensor)
        >>> mask = mask_head(in_tensor)
        >>> print(out.shape)
        torch.Size([1, 285, 13, 13])
        >>> print(mask.shape)
        torch.Size([1, 32, 26, 26])
    """
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
                nn.Conv2d(inter_channels, num_anchors*(5+num_classes), 1, 1, 0),
                nn.Sequential(
                    nn.Conv2d(inter_channels, num_anchors*num_masks, 3, 1, 1, bias=True),
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
