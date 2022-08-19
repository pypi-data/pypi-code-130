#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#   Visualization functionality
#
import logging
from collections.abc import Sequence
from pathlib import Path
from enum import Enum
import numpy as np
import pandas as pd
from . import BoundingBoxTransformer

log = logging.getLogger(__name__)   # noqa
default = None                      # noqa

try:
    import cv2
    default = 0
except ModuleNotFoundError:
    log.debug('OpenCV not installed')
    cv2 = None

try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    default = 1

    try:
        font = ImageFont.truetype('DejaVuSansMono', 10)
    except IOError:
        font = ImageFont.load_default()
except ModuleNotFoundError:
    log.debug('Pillow not installed')
    Image = None

if Image is None and cv2 is None:
    log.error('Neither Pillow nor OpenCV installed, visualization functions will not work')


__all__ = ['BoxDrawer', 'draw_boxes', 'DrawMethod']


class DrawMethod(Enum):
    """ Which library to use for drawing """
    CV = 0 if cv2 is not None else None     #: Use OpenCV
    PIL = 1 if Image is not None else None  #: Use Pillow


def draw_boxes(img, boxes, label=False, color=None, size=3, alpha=1, fill=False, method=default):
    """ Draws bounding boxes on an image. |br|
    If the boxes dataframe contains a segmentation column, a polygon is drawn.
    Otherwise we draw a horizontal bounding box.

    Args:
        img (OpenCV image or PIL image or filename):
            Image to draw on
        boxes (pandas.DataFrame):
            Bounding boxes to draw
        label (pandas.Series, optional):
            Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series, optional):
            Alpha value for the border or fill if enabled; Default **1**
        fill (pandas.Series, optional):
            Whether to fill the boxes or not; Default **False**
        method (DrawMethod, optional):
            Whether to use OpenCV or Pillow for opening the image (only useful when filename given); Default: **DrawMethod.PIL**

    Returns:
        OpenCV or PIL image: Image with bounding boxes drawn

    Note:
        The `label`, `color`, `size`, `alpha` and `fill` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

    Note:
        The default drawing method depends on whichever library is installed (cv2 or PIL) and is only used if the image passed is a string or Path object.
        If both are installed, Pillow is the default choice.
    """
    if DrawMethod(method).value is None:
        raise ImportError(f'Could not find the correct library for the chosen drawing method [{DrawMethod(method)}]')

    # Open image
    if isinstance(img, (str, Path)):
        if method == DrawMethod.CV:
            img = cv2.imread(img)
        else:
            method = DrawMethod.PIL
            original = Image.open(img)
            if original.mode == 'L':
                original = original.convert('RGB')
            img = ImageDraw.Draw(original, 'RGBA')
    elif Image is not None and isinstance(img, Image.Image):
        img = img.copy()
        if img.mode == 'L':
            original = img.convert('RGB')
        else:
            original = img
        img = ImageDraw.Draw(original, 'RGBA')
        method = DrawMethod.PIL
    elif cv2 is not None and isinstance(img, np.ndarray):
        img = img.copy()
        method = DrawMethod.CV
    else:
        raise TypeError(f'Unkown image type [{type(img)}]')

    # Draw
    if method == DrawMethod.CV:
        draw = draw_cv
    else:
        draw = draw_pil

    if not boxes.empty:
        boxes = setup_boxes(boxes, label, color, size, alpha, fill)
        for box in boxes.itertuples():
            draw(img, box)

    if method == DrawMethod.PIL:
        return original
    else:
        return img


class BoxDrawer:
    """ This class allows to iterate over all images in a dataset and draw their respective bounding boxes.

    Args:
        images (callable or dict-like object):
            A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame):
            Bounding boxes to draw
        label (pandas.Series, optional):
            Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series, optional):
            Alpha value for the border or fill if enabled; Default **1**
        fill (pandas.Series, optional):
            Whether to fill the boxes or not; Default **False**
        show_empty (boolean, optional):
            Whether to also show images without bounding boxes; Default **True**
        method (DrawMethod, optional):
            Whether to use OpenCV or Pillow for opening the image (only useful when filename given); Default: **DrawMethod.PIL**

    Note:
        If the `images` argument is callable, the image or path to the image will be retrieved in the following way:

        >>> image = self.images(image_label)

        Otherwise the image or path is retrieved as:

        >>> image = self.images[image_label]

    Note:
        The `label`, `color`, `size`, `alpha` and `fill` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

    Note:
        The default drawing method depends on whichever library is installed (cv2 or PIL) and is only used if the images passed are string or Path objects.
        If both are installed, Pillow is the default choice.
    """
    def __init__(self, images, boxes, label=False, color=None, size=3, alpha=1, fill=None, show_empty=True, method=default):
        self.images = images
        self.boxes = setup_boxes(boxes, label, color, size, alpha, fill)

        self.method = method
        if DrawMethod(self.method).value is None:
            raise ImportError(f'Could not find the correct library for the chosen drawing method [{DrawMethod(method)}]')

        if show_empty:
            self.image_labels = list(self.boxes.image.cat.categories)
        else:
            self.image_labels = list(self.boxes.image.cat.remove_unused_categories().cat.categories)

    def __len__(self):
        return len(self.image_labels)

    def __getitem__(self, idx):
        """ Get image with boxes drawn onto it.

        Args:
            idx (str or int): Numerical index or image string

        Returns:
            OpenCV or PIL image: Image with bounding boxes drawn
        """
        if isinstance(idx, int):
            lbl = self.image_labels[idx]
        else:
            lbl = idx

        if callable(self.images):
            img = self.images(lbl)
        else:
            img = self.images[lbl]

        return self.draw(lbl, img, self.boxes[self.boxes.image == lbl])

    def draw(self, lbl, img, boxes):
        if isinstance(img, (str, Path)):
            if self.method == DrawMethod.CV:
                img = cv2.imread(img)
                method = DrawMethod.CV
            else:
                original = Image.open(img)
                if original.mode == 'L':
                    original = original.convert('RGB')
                img = ImageDraw.Draw(original, 'RGBA')
                method = DrawMethod.PIL
        elif Image is not None and isinstance(img, Image.Image):
            if img.mode == 'L':
                original = img.convert('RGB')
            else:
                original = img
            img = ImageDraw.Draw(original, 'RGBA')
            method = DrawMethod.PIL
        elif cv2 is not None and isinstance(img, np.ndarray):
            method = DrawMethod.CV
        else:
            raise TypeError(f'Unkown image type [{type(img)}]')

        # Draw
        if method == DrawMethod.CV:
            draw = draw_cv
        else:
            draw = draw_pil

        if not boxes.empty:
            for box in boxes.itertuples():
                draw(img, box)

        if method == DrawMethod.PIL:
            return original
        else:
            return img


def setup_boxes(boxes, label=False, color=None, size=3, alpha=1, fill=False):
    """ Setup the boxes dataframe with the correct metadata columns to draw them.
    This function basically adds on 3 columns ['label', 'color', 'size'] if they are not yet on the dataframe.

    Args:
        boxes (pandas.DataFrame):
            Bounding boxes to draw
        label (pandas.Series, optional):
            Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional):
            Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional):
            Thickness of the border of the bounding boxes; Default **3**
        alpha (pandas.Series, optional):
            Alpha value for the border or fill if enabled; Default **1**
        fill (pandas.Series, optional):
            Whether to fill the boxes or not; Default **False**

    Returns:
        pandas.DataFrame:
            brambox dataframe with 6 extra columns ['points', 'label', 'color', 'size', 'alpha', 'fill']
    """
    default_colors = [
        (31, 119, 180),
        (255, 127, 14),
        (44, 160, 44),
        (214, 39, 40),
        (148, 103, 189),
        (140, 86, 75),
        (227, 119, 194),
        (127, 127, 127),
        (188, 189, 34),
        (23, 190, 207),
    ]
    boxes = boxes.copy()

    # Filter NaN and Inf coordinates
    coords = ['x_top_left', 'y_top_left', 'width', 'height']
    isinf = np.any(np.isinf(boxes[coords]))
    isna = pd.isna(boxes[coords]).any(axis=None)

    if isinf:
        log.error('Some bounding boxes contain Inf coordinates')
        boxes[coords] = boxes[coords].replace((np.inf, -np.inf), np.nan)
    if isna:
        log.error('Some bounding boxes contain NaN coordinates')
    if isinf or isna:
        boxes = boxes.dropna(subset=coords)

    # Setup color
    if 'color' not in boxes.columns:
        if color is not None:
            # Check if color is a single RGB sequence
            if isinstance(color, Sequence) and len(color) == 3 and isinstance(color[0], int):
                boxes['color'] = [color] * len(boxes)
            else:
                boxes['color'] = color
        else:
            labels = sorted(boxes.class_label.unique())
            boxes['color'] = boxes.class_label.map({v: i for i, v in enumerate(labels)})

    # If color column is integer, we assume user wants to map it to default color list
    if pd.api.types.is_integer_dtype(boxes['color']):
        boxes['color'] %= len(default_colors)
        boxes['color'] = boxes['color'].map({i: v for i, v in enumerate(default_colors)})

    # Setup border width
    if 'size' not in boxes.columns:
        boxes['size'] = size
        boxes['size'] = boxes['size'].astype(int)

    # Setup label
    if 'label' not in boxes.columns:
        if label is True:
            boxes['label'] = boxes.apply(lambda b: f'{b.class_label}{" "+str(b.id) if not np.isnan(b.id) else ""}', axis=1)
            if 'confidence' in boxes.columns:
                boxes.label += ' [' + (boxes.confidence * 100).round(2).astype(str) + '%]'
        else:
            boxes['label'] = label

    # Setup alpha
    if 'alpha' not in boxes.columns:
        boxes['alpha'] = alpha
        boxes['alpha'] = boxes['alpha'].astype(float)

    # Setup fill
    if 'fill' not in boxes.columns:
        boxes['fill'] = fill
        boxes['fill'] = boxes['fill'].astype(bool)

    # Setup polygon points
    if 'segmentation' in boxes.columns or 'angle' in boxes.columns:
        polys = BoundingBoxTransformer(boxes).get_poly(force_poly=True)['segmentation']
        empty = polys.geos.is_empty()
        if empty.any():
            log.error('Some bounding boxes contain empty segmentation geometries')
            boxes = boxes[~empty].copy()

        points = polys.geos.get_coordinates_2d().astype(int)
        boxes['points'] = points.apply(tuple, axis=1).groupby(points.index).apply(tuple)
    else:
        x0 = boxes['x_top_left'].astype(int)
        y0 = boxes['y_top_left'].astype(int)
        x1 = (boxes['x_top_left'] + boxes['width']).astype(int)
        y1 = (boxes['y_top_left'] + boxes['height']).astype(int)

        points = pd.DataFrame({
            'pt1': x0.combine(y0, lambda x, y: (x, y)),
            'pt2': x1.combine(y0, lambda x, y: (x, y)),
            'pt3': x1.combine(y1, lambda x, y: (x, y)),
            'pt4': x0.combine(y1, lambda x, y: (x, y)),
        })
        points['pt5'] = points['pt1']

        boxes['points'] = points.apply(tuple, axis=1)

    return boxes


def draw_pil(img, box):
    """ Draw a bounding box on a Pillow image """
    alpha = int(box.alpha * 255)
    if isinstance(box.color, str):
        color = ImageColor.getrgb(box.color)
        if len(color) == 3:
            color = (*color, alpha)
        else:
            color[4] = alpha
    else:
        color = (*box.color[:3], alpha)

    if box.fill:
        img.polygon(box.points, color)
    else:
        img.line(box.points, color, box.size)

    if box.label:
        offset = 12 + box.size
        pt0 = box.points[0]
        img.text((pt0[0], pt0[1]-offset), box.label, (*box.color, 255), font)


def draw_cv(img, box):
    """ Draw a bounding box on an OpenCV image """
    if not isinstance(box.color, Sequence):
        raise ValueError('Color should be an RGB tuple')

    color = box.color[::-1]
    pts = np.array(box.points, dtype=np.int32).reshape(-1, 1, 2)

    if box.alpha != 1:
        color = (*color, int(box.alpha * 255))
        original = np.zeros_like(img, shape=(*img.shape[:-1], 4))
        img, original = original, img

    if box.fill:
        cv2.fillPoly(img, [pts], color)
    else:
        cv2.polylines(img, [pts], False, color, box.size)

    if box.alpha != 1:
        alpha = img[..., -1:] / 255
        img = alpha * img[..., :3] + (1 - alpha) * original
        original[...] = img
        img = original

    if box.label:
        pt0 = box.points[0]
        cv2.putText(img, box.label, (pt0[0], pt0[1]-5), cv2.FONT_HERSHEY_PLAIN, .75, color, 1, cv2.LINE_AA)
