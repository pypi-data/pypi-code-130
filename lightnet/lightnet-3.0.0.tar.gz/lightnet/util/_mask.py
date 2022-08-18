#
#   Mask Utilities
#   Copyright EAVISE
#
import torch

__all__ = ['crop_mask']


def crop_mask(masks, coords, relative_coords=False):
    """ Crop predicted masks by zeroing out everything not in the predicted bbox.

    Args:
        masks (torch.Tensor): Different masks to be cropped
        coords (torch.Tensor): Cropping coordinates in XYXY format
        relative_coords (boolean, optional): Whether the coordinates are relative (0-1) or absolute values; Default **False**

    Returns:
        torch.Tensor: Cropped masks
    """
    n, h, w = masks.shape

    # Transform coordinates
    if relative_coords:
        coords *= torch.tensor((w, h, w, h), device=coords.device)
    coords = torch.clamp(coords, 0)

    # Floor XY1 and ceil XY2
    coords[:, :2].floor_()
    coords[:, 2:].ceil_()

    # Create cropping mask
    rows = torch.arange(w, device=masks.device, dtype=coords.dtype).view(1, 1, -1).expand(n, h, w)
    cols = torch.arange(h, device=masks.device, dtype=coords.dtype).view(1, -1, 1).expand(n, h, w)

    masks_l = rows >= coords[:, 0].view(-1, 1, 1)
    masks_r = rows < coords[:, 2].view(-1, 1, 1)
    masks_u = cols >= coords[:, 1].view(-1, 1, 1)
    masks_d = cols < coords[:, 3].view(-1, 1, 1)
    crop_mask = masks_l * masks_r * masks_u * masks_d

    return masks * crop_mask.float()
