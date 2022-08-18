#
#   Fully Connected Classification head
#   Copyright EAVISE
#
import torch.nn as nn
from .._basemodule import BaseModule

__all__ = ['ClassificationFC']


class ClassificationFC(BaseModule):
    """ Fully Connected Classification head.

    Args:
        in_channels (int): Number of input channels
        num_classes (int): Number of classes
        pooling_size (int or tuple, optional): output_size of the :class:`~torch.nn.AdaptiveAvgPool2d` layer; Default **1**
        inter_channels (int, optional): How many channels to use for the intermediate layers (See Note); Default **0**
        dropout_first (bool, optional): Whether to add dropout layers before or after each of the intermediate Linear+ReLU layers; Default **False**

    .. rubric:: Models:

    - :class:`~lightnet.models.Alexnet`
    - :class:`~lightnet.models.VGG11`
    - :class:`~lightnet.models.VGG13`
    - :class:`~lightnet.models.VGG16`
    - :class:`~lightnet.models.VGG19`

    Examples:
        >>> head = ln.network.head.ClassificationFC(256, 1000)
        >>> print(head)
        Sequential(
          (0): AdaptiveAvgPool2d(output_size=1)
          (1): Flatten(start_dim=1, end_dim=-1)
          (2): Linear(in_features=256, out_features=1000, bias=True)
        )
        >>> in_tensor = torch.rand(1, 256, 13, 13)
        >>> out_tensor = head(in_tensor)
        >>> print(out_tensor.shape)
        torch.Size([1, 1000])

        >>> head = ln.network.head.ClassificationFC(256, 1000, inter_channels=4096)
        >>> print(head)
        Sequential(
          (0): AdaptiveAvgPool2d(output_size=1)
          (1): Flatten(start_dim=1, end_dim=-1)
          (2): Linear(in_features=256, out_features=4096, bias=True)
          (3): ReLU(inplace=True)
          (4): Dropout(p=0.5, inplace=False)
          (5): Linear(in_features=4096, out_features=4096, bias=True)
          (6): ReLU(inplace=True)
          (7): Dropout(p=0.5, inplace=False)
          (8): Linear(in_features=4096, out_features=1000, bias=True)
        )
        >>> in_tensor = torch.rand(1, 256, 13, 13)
        >>> out_tensor = head(in_tensor)
        >>> print(out_tensor.shape)
        torch.Size([1, 1000])
    """
    @BaseModule.layers
    def Default(
        in_channels,
        num_classes,
        pooling_size=1,
        inter_channels=0,
        dropout_first=False,
    ):
        if isinstance(pooling_size, int):
            in_channels *= pooling_size ** 2
        else:
            in_channels *= pooling_size[0] * pooling_size[1]

        if inter_channels:
            inter_layers = [
                nn.Linear(in_channels, inter_channels),
                nn.ReLU(inplace=True),
                nn.Linear(inter_channels, inter_channels),
                nn.ReLU(inplace=True),
            ]
            in_channels = inter_channels

            if dropout_first:
                inter_layers.insert(0, nn.Dropout())
                inter_layers.insert(3, nn.Dropout())
            else:
                inter_layers.insert(2, nn.Dropout())
                inter_layers.insert(5, nn.Dropout())
        else:
            inter_layers = []

        return (
            nn.AdaptiveAvgPool2d(pooling_size),
            nn.Flatten(),
            *inter_layers,
            nn.Linear(in_channels, num_classes),
        )
