import numpy as np

from inference.config import SEGMENTATION_MASK
from inference.utils import crop_bbox_from_image


def crop_segmentation_mask(segmentation_mask: dict,
                           bbox: np.ndarray | list[int|float, int|float, int|float, int|float] |
                                 tuple[int|float, int|float, int|float, int|float],
                           copy: bool = True) -> dict:
    """
    Crops the segmentation mask to the given bounding box.

    :param segmentation_mask: dict. The segmentation mask of the scene. Contains the following keys:
            ('segmentation_mask', 'background_class_idx', 'class_names_list').
    :param bbox: np.ndarray or iterable with 4 ints or floats. The bounding box of the subimage to be cropped.
    :param copy: bool. If True, the returned segmentation mask will be copied.

    :return dict. The input dictionary but with the segmentation mask cropped to the given bounding box.
    """
    assert type(segmentation_mask) is dict, f"The segmentation mask must be a dictionary. Got {type(segmentation_mask)}."
    seg_mask = segmentation_mask[SEGMENTATION_MASK]
    assert type(seg_mask) is np.ndarray, f"The segmentation mask must be a numpy array. Got {type(seg_mask)}."
    assert len(bbox) == 4, f"The bounding box must be a list or tuple of length 4. Got {len(bbox)}."

    mask = crop_bbox_from_image(image=seg_mask, bbox_xyxy=bbox, is_normalized=True, copy=copy)

    return {**segmentation_mask, SEGMENTATION_MASK: mask}
