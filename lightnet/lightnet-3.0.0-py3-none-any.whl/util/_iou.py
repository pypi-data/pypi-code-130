#
#   IoU Utilities
#   Copyright EAVISE
#
import math
import torch
from ._coords import cwh_xyxy, tlwh_xyxy

__all__ = ['iou_cwh', 'iou_tlwh', 'iou_xyxy', 'iou_wh', 'iou_bb_cwha', 'iou_bb_quad', 'iou_circle_cwha']


def iou_cwh(boxes1, boxes2):
    """ Compute IoU between 2 tensors of boxes, when the centerpoint, width and height are given.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Note:
        Tensor format: [[xc, yc, w, h],...]
    """
    b1 = cwh_xyxy(boxes1, False)
    b2 = cwh_xyxy(boxes2, False)
    return _iou(*b1, *b2)


def iou_tlwh(boxes1, boxes2):
    """ Compute IoU between 2 tensors of boxes, when the top-left corner, width and height are given.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Note:
        Tensor format: [[xtl, ytl, w, h],...]
    """
    b1 = tlwh_xyxy(boxes1, False)
    b2 = tlwh_xyxy(boxes2, False)
    return _iou(*b1, *b2)


def iou_xyxy(boxes1, boxes2):
    """ Compute IoU between 2 tensors of boxes, when the top-left and bottom-right corner are given.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Note:
        Tensor format: [[xtl, ytl, xbr, ybr],...]
    """
    b1 = boxes1[:, 0:1], boxes1[:, 1:2], boxes1[:, 2:3], boxes1[:, 3:4]
    b2 = boxes2[:, 0:1], boxes2[:, 1:2], boxes2[:, 2:3], boxes2[:, 3:4]
    return _iou(*b1, *b2)


def iou_wh(boxes1, boxes2):
    """ Compute IoU between 2 tensors of boxes, when only the width and height are given. |br|
    This function assumes the boxes have the same center.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values when discarding X/Y offsets

    Note:
        Tensor format: [[w, h],...]
    """
    b1w, b1h = boxes1.clamp(min=0).split(1, 1)
    b2w, b2h = boxes2.clamp(min=0).split(1, 1)
    b2w, b2h = b2w.squeeze(1), b2h.squeeze(1)

    intersections = b1w.min(b2w) * b1h.min(b2h)
    unions = (b1w * b1h) + (b2w * b2h) - intersections

    return intersections / unions


def iou_bb_cwha(boxes1, boxes2):
    """ Compute the IoU between the enclosed horiontal bounding boxes of rotated rectangles.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Warning:
        This function does not compute the actual IoU between the rotated rectangles,
        but approximates it as the IoU of the enclosed horizontal bounding boxes of the rectangles.

    Note:
        Tensor format: [[xc, yc, w, h, a],...]
    """
    b1abs = boxes1[:, 4].abs()
    b1sin = b1abs.sin()
    b1cos = b1abs.cos()
    b1w2 = boxes1[:, 2] / 2
    b1h2 = boxes1[:, 3] / 2
    b1x1 = (boxes1[:, 0] - b1h2 * b1sin - b1w2 * b1cos).unsqueeze(1)
    b1x2 = (boxes1[:, 0] + b1h2 * b1sin + b1w2 * b1cos).unsqueeze(1)
    b1y1 = (boxes1[:, 1] - b1h2 * b1cos - b1w2 * b1sin).unsqueeze(1)
    b1y2 = (boxes1[:, 1] + b1h2 * b1cos + b1w2 * b1sin).unsqueeze(1)

    b2abs = boxes2[:, 4].abs()
    b2sin = b2abs.sin()
    b2cos = b2abs.cos()
    b2w2 = boxes2[:, 2] / 2
    b2h2 = boxes2[:, 3] / 2
    b2x1 = (boxes2[:, 0] - b2h2 * b2sin - b2w2 * b2cos).unsqueeze(1)
    b2x2 = (boxes2[:, 0] + b2h2 * b2sin + b2w2 * b2cos).unsqueeze(1)
    b2y1 = (boxes2[:, 1] - b2h2 * b2cos - b2w2 * b2sin).unsqueeze(1)
    b2y2 = (boxes2[:, 1] + b2h2 * b2cos + b2w2 * b2sin).unsqueeze(1)

    return _iou(b1x1, b1y1, b1x2, b1y2, b2x1, b2y1, b2x2, b2y2)


def iou_bb_quad(boxes1, boxes2):
    """ Compute the IoU between the enclosed horiontal bounding boxes of quads.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Warning:
        This function does not compute the actual IoU between quads,
        but approximates it as the IoU of the enclosed horizontal bounding boxes of the quads.

    Note:
        Tensor format: [[x1, y1, x2, y2, x3, y3, x4, y4],...]

        Technically, this function can be used to compute the "iou_bb" from any polygon,
        but the polygons of each boxes tensor need the same number of points.
        In order to achieve this, you could pad the tensor by duplicating points, as we simply take the min/max values.
    """
    b1x = boxes1[:, ::2]
    b1x1, b1x2 = b1x.min(axis=1)[0], b1x.max(axis=1)[0]
    b1y = boxes1[:, 1::2]
    b1y1, b1y2 = b1y.min(axis=1)[0], b1y.max(axis=1)[0]
    b2x = boxes2[:, ::2]
    b2x1, b2x2 = b2x.min(axis=1)[0], b2x.max(axis=1)[0]
    b2y = boxes2[:, 1::2]
    b2y1, b2y2 = b2y.min(axis=1)[0], b2y.max(axis=1)[0]

    return _iou(b1x1, b1y1, b1x2, b1y2, b2x1, b2y1, b2x2, b2y2)


def iou_circle_cwha(boxes1, boxes2):
    """ Compute the IoU of the minimum bounding circle of the rotated rectangles :cite:`ciou`.

    Args:
        boxes1 (torch.Tensor): List of bounding boxes
        boxes2 (torch.Tensor): List of bounding boxes

    Returns:
        torch.Tensor[len(boxes1) X len(boxes2)]: IoU values

    Warning:
        This function does not compute the actual IoU between the rotated rectangles,
        but approximates it as the IoU of the minimum enclosed bounding circles of the rectangles.

    Note:
        Tensor format: [[xc, yc, w, h, a],...]
    """
    # Compute radii and squared radii (radius = half of the box diagonal)
    b1r2 = ((boxes1[:, 2] ** 2 + boxes1[:, 3] ** 2) / 4).unsqueeze(1)
    b1r1 = b1r2 ** 0.5
    b2r2 = ((boxes2[:, 2] ** 2 + boxes2[:, 3] ** 2) / 4).unsqueeze(0)
    b2r1 = b2r2 ** 0.5

    d2 = (
        (boxes1[:, 0].unsqueeze(1) - boxes2[:, 0].unsqueeze(0)) ** 2
        + (boxes1[:, 1].unsqueeze(1) - boxes2[:, 1].unsqueeze(0)) ** 2
    )
    d1 = d2 ** 0.5

    lx = (b1r2 - b2r2 + d2) / (2 * d1)
    ly = (b1r2 - lx ** 2) ** 0.5

    intersections = b1r2 * torch.asin(ly / b1r1) + b2r2 * torch.asin(ly / b2r1) - ly * (lx + (b1r2 - b2r2 + lx**2) ** 0.5)
    unions = math.pi * (b1r2 + b2r2) - intersections

    return intersections / unions


def _iou(b1x1, b1y1, b1x2, b1y2, b2x1, b2y1, b2x2, b2y2):
    """ Internal IoU function to reduce code duplication. """
    dx = (b1x2.min(b2x2.t()) - b1x1.max(b2x1.t())).clamp(min=0)
    dy = (b1y2.min(b2y2.t()) - b1y1.max(b2y1.t())).clamp(min=0)
    intersections = dx * dy

    areas1 = (b1x2 - b1x1) * (b1y2 - b1y1)
    areas2 = (b2x2 - b2x1) * (b2y2 - b2y1)
    unions = (areas1 + areas2.t()) - intersections

    return intersections / unions
