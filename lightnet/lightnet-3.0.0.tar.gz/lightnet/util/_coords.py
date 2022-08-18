#
#   Coordinate Utilities
#   Copyright EAVISE
#
import torch

__all__ = ['cwh_xyxy', 'tlwh_xyxy', 'xyxy_cwh']


def cwh_xyxy(coords, cat=True):
    """ Transform coordinates from the (xc, yc, w, h) to the (x1, y1, x2, y2) format.

    Args:
        coords (torch.Tensor): List of bounding boxes in the CWH format.
        cat (boolean, optional): Whether to concatenate the result in one tensor or return 4 separate tensors.

    Returns:
        torch.Tensor or tuple<torch.Tensor>
    """
    xy1 = (coords[:, :2] - (coords[:, 2:4] / 2))
    xy2 = (coords[:, :2] + (coords[:, 2:4] / 2))

    if cat:
        return torch.cat((xy1, xy2), dim=1)
    else:
        return (*xy1.split(1, 1), *xy2.split(1, 1))


def tlwh_xyxy(coords, cat=True):
    """ Transform coordinates from the (xtl, ytl, w, h) to the (x1, y1, x2, y2) format.

    Args:
        coords (torch.Tensor): List of bounding boxes in the TLWH format.
        cat (boolean, optional): Whether to concatenate the result in one tensor or return 4 separate tensors.

    Returns:
        torch.Tensor or tuple<torch.Tensor>
    """
    x1, y1 = coords[:, 0:1], coords[:, 1:2]
    xy2 = coords[:, :2] + coords[:, 2:4]

    if cat:
        return torch.cat((x1, y1, xy2), dim=1)
    return (x1, y1, *xy2.split(1, 1))


def xyxy_cwh(coords, cat=True):
    """ Transform coordinates from the (x1, y1, x2, y2) to the (xc, yc, w, h) format.

    Args:
        coords (torch.Tensor): List of bounding boxes in the XYXY format.
        cat (boolean, optional): Whether to concatenate the result in one tensor or return 4 separate tensors.

    Returns:
        torch.Tensor or tuple<torch.Tensor>
    """
    xy = (coords[:, :2] + coords[:, 2:4]) / 2
    wh = coords[:, 2:4] - coords[:, :2]

    if cat:
        return torch.cat((xy, wh), dim=1)
    else:
        return (*xy.split(1, 1), *wh.split(1, 1))
