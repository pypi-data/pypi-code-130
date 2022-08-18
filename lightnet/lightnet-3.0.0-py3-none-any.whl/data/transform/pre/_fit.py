#
#   Lightnet preprocessing for fitting data to certain dimensions
#   Copyright EAVISE
#
import random
import collections
import numpy as np
import torch
import torch.nn.functional as F
from lightnet._imports import cv2, Image, ImageOps, pygeos
from ._base import ImageAnnoTransform, AnnoTransform

__all__ = ['Crop', 'Letterbox', 'Pad', 'FitAnno']


class Crop(ImageAnnoTransform):
    """ Rescale and crop images/annotations to the right network dimensions.
    This transform will first rescale to the closest (bigger) dimension possible and then take a crop to the exact dimensions.

    Args:
        dimension (tuple, optional): Default size for the letterboxing, expressed as a (width, height) tuple; Default **None**
        dataset (lightnet.data.Dataset, optional): Dataset that uses this transform; Default **None**
        center (Boolean, optional): Whether to take the crop from the center or randomly.
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Warning:
        This transformation only modifies the annotations to fit the new scale and origin point of the image.
        It does not crop the annotations to fit inside the new boundaries, nor does it filter annotations that fall outside of these new boundaries.
        Check out :class:`~lightnet.data.transform.FitAnno` for a transformation that does this.
    """
    def __init__(self, dimension=None, dataset=None, center=True, **kwargs):
        super().__init__(**kwargs)
        self.dimension = dimension
        self.dataset = dataset
        self.center = center
        if self.dimension is None and self.dataset is None:
            raise ValueError('This transform either requires a dimension or a dataset to infer the dimension')

        # Parameters
        self._img_width = None
        self._img_height = None
        self._scale = None
        self._crop = None

    def get_parameters(self, img_width, img_height):
        self._img_width = img_width
        self._img_height = img_height

        if self.dataset is not None:
            net_w, net_h = self.dataset.input_dim
        elif isinstance(self.dimension, int):
            net_w, net_h = self.dimension, self.dimension
        else:
            net_w, net_h = self.dimension

        if net_w / img_width >= net_h / img_height:
            self._scale = net_w / img_width
            xcrop = 0
            ycrop = int(img_height * self._scale - net_h + 0.5)
        else:
            self._scale = net_h / img_height
            xcrop = int(img_width * self._scale - net_w + 0.5)
            ycrop = 0

        if xcrop == 0 and ycrop == 0:
            self._crop = None
        else:
            dx = xcrop // 2 if self.center else random.randint(0, xcrop)
            dy = ycrop // 2 if self.center else random.randint(0, ycrop)
            self._crop = (dx, dy, dx + net_w, dy + net_h)

    @torch.jit.unused
    def _tf_pil(self, img):
        if self._scale != 1:
            bands = img.split()
            bands = [
                b.resize((int(self._scale*self._img_width+0.5), int(self._scale*self._img_height+0.5)), resample=Image.BILINEAR)
                for b in bands
            ]
            img = Image.merge(img.mode, bands)

        if self._crop is not None:
            img = img.crop(self._crop)

        return img

    @torch.jit.unused
    def _tf_cv(self, img):
        if self._scale != 1:
            img = cv2.resize(img, (int(self._scale*self._img_width+0.5), int(self._scale*self._img_height+0.5)), interpolation=cv2.INTER_LINEAR)

        if self._crop is not None:
            img = img[self._crop[1]:self._crop[3], self._crop[0]:self._crop[2]]

        return img

    def _tf_torch(self, img):
        if self._scale != 1:
            if img.ndim == 3:
                img = img[None, ...]
            elif img.ndim == 2:
                img = img[None, None, ...]
            img = F.interpolate(
                img,
                size=(int(self._scale*self._img_height+0.5), int(self._scale*self._img_width+0.5)),
                mode='bilinear',
                align_corners=False,
            ).squeeze().clamp(min=0, max=255)

        # Crop
        if self._crop is not None:
            img = img[..., self._crop[1]:self._crop[3], self._crop[0]:self._crop[2]]

        return img

    @torch.jit.unused
    def _tf_anno(self, anno):
        if 'segmentation' in anno.columns:
            if self._scale != 1 or self._crop is not None:
                crop = self._crop if self._crop is not None else (0, 0)
                anno['segmentation'] = anno['segmentation'].geos.affine((
                    self._scale, 0,
                    0, self._scale,
                    -crop[0],
                    -crop[1],
                ))

                bounds = anno['segmentation'].geos.bounds()
                anno['x_top_left'] = bounds['xmin']
                anno['y_top_left'] = bounds['ymin']
                anno['width'] = bounds['xmax'] - bounds['xmin']
                anno['height'] = bounds['ymax'] - bounds['ymin']
        else:
            if self._scale != 1:
                anno['x_top_left'] *= self._scale
                anno['y_top_left'] *= self._scale
                anno['width'] *= self._scale
                anno['height'] *= self._scale

            if self._crop is not None:
                anno['x_top_left'] -= self._crop[0]
                anno['y_top_left'] -= self._crop[1]

        return anno


class Letterbox(ImageAnnoTransform):
    """ Rescale images/annotations and add top/bottom borders to get to the right network dimensions.

    Args:
        dimension (tuple, optional): Default size for the letterboxing, expressed as a (width, height) tuple; Default **None**
        dataset (lightnet.data.Dataset, optional): Dataset that uses this transform; Default **None**
        fill_color (int or float, optional): Fill color to be used for padding (if int, will be divided by 255); Default **0.5**
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Note:
        Create 1 Letterbox object and use it for both image and annotation transforms.
        This object will save data from the image transform and use that on the annotation transform.
    """
    def __init__(self, dimension=None, dataset=None, fill_color=0.5, **kwargs):
        super().__init__(**kwargs)
        self.dimension = dimension
        self.dataset = dataset
        self.fill_color = fill_color if isinstance(fill_color, float) else fill_color / 255
        if self.dimension is None and self.dataset is None:
            raise ValueError('This transform either requires a dimension or a dataset to infer the dimension')

        # Parameters
        self._img_width = None
        self._img_height = None
        self._scale = None
        self._pad = None

    def get_parameters(self, img_width, img_height):
        self._img_width = img_width
        self._img_height = img_height

        if self.dataset is not None:
            net_w, net_h = self.dataset.input_dim
        elif isinstance(self.dimension, int):
            net_w, net_h = self.dimension, self.dimension
        else:
            net_w, net_h = self.dimension

        if img_width / net_w >= img_height / net_h:
            self._scale = net_w / img_width
        else:
            self._scale = net_h / img_height

        pad_w = (net_w - int(self._scale*img_width+0.5)) / 2
        pad_h = (net_h - int(self._scale*img_height+0.5)) / 2
        self._pad = (int(pad_w), int(pad_h), int(pad_w+.5), int(pad_h+.5))

    @torch.jit.unused
    def _tf_pil(self, img):
        if self._scale != 1:
            bands = img.split()
            bands = [
                b.resize((int(self._scale*self._img_width+0.5), int(self._scale*self._img_height+0.5)), resample=Image.BILINEAR)
                for b in bands
            ]
            img = Image.merge(img.mode, bands)

        if self._pad != (0, 0, 0, 0):
            channels = len(img.getbands())
            img = ImageOps.expand(img, border=self._pad, fill=(int(self.fill_color*255),)*channels)

        return img

    @torch.jit.unused
    def _tf_cv(self, img):
        if self._scale != 1:
            img = cv2.resize(img, (int(self._scale*self._img_width+0.5), int(self._scale*self._img_height+0.5)), interpolation=cv2.INTER_LINEAR)

        if self._pad != (0, 0, 0, 0):
            channels = img.shape[2] if len(img.shape) > 2 else 1
            img = cv2.copyMakeBorder(img, self._pad[1], self._pad[3], self._pad[0], self._pad[2], cv2.BORDER_CONSTANT, value=(int(self.fill_color*255),)*channels)

        return img

    def _tf_torch(self, img):
        if self._scale != 1:
            if img.ndim == 3:
                img = img[None, ...]
            elif img.ndim == 2:
                img = img[None, None, ...]
            img = F.interpolate(
                img,
                size=(int(self._scale*self._img_height+0.5), int(self._scale*self._img_width+0.5)),
                mode='bilinear',
                align_corners=False,
            ).squeeze().clamp(min=0, max=255)

        if self._pad != (0, 0, 0, 0):
            img = F.pad(img, (self._pad[0], self._pad[2], self._pad[1], self._pad[3]), value=self.fill_color)

        return img

    @torch.jit.unused
    def _tf_anno(self, anno):
        if self._scale != 1:
            anno['x_top_left'] *= self._scale
            anno['y_top_left'] *= self._scale
            anno['width'] *= self._scale
            anno['height'] *= self._scale

        if self._pad != (0, 0, 0, 0):
            anno['x_top_left'] += self._pad[0]
            anno['y_top_left'] += self._pad[1]

        if 'segmentation' in anno.columns and (self._scale != 1 or self._pad != (0, 0, 0, 0)):
            anno['segmentation'] = anno['segmentation'].geos.affine((
                self._scale, 0,
                0, self._scale,
                self._pad[0],
                self._pad[1],
            ))

        return anno


class Pad(ImageAnnoTransform):
    """ Pad images/annotations to a certain dimension.

    Args:
        dimension (int or tuple, optional): Default size for the padding, expressed as a single integer or as a (width, height) tuple; Default **None**
        dataset (lightnet.data.Dataset, optional): Dataset that uses this transform; Default **None**
        multiple_dim (boolean, optional): Consider given dimensions to be multiples instead of exact values; Default **True**
        fill_color (int or float, optional): Fill color to be used for padding (if int, will be divided by 255); Default **0.5**
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Warning:
        Do note that the ``dimension`` or ``dataset`` argument here uses the given width and height as a multiple instead of a real dimension by default.
        Given a certain value X, the image (and annotations) will be padded, so that the image dimensions are a multiple of X. |br|
        This is different compared to :class:`~lightnet.data.transform.Crop` or :class:`~lightnet.data.transform.Letterbox`.

        You can toggle this behaviour by setting ``multiple_dim=False``, but keep in mind that the given dimensions should always be bigger than the original input image dimensions.
    """
    def __init__(self, dimension=None, dataset=None, multiple_dim=True, fill_color=127, **kwargs):
        super().__init__(**kwargs)
        self.dimension = dimension
        self.dataset = dataset
        self.multiple_dim = multiple_dim
        self.fill_color = fill_color if isinstance(fill_color, float) else fill_color / 255
        if self.dimension is None and self.dataset is None:
            raise ValueError('This transform either requires a dimension or a dataset to infer the dimension')

        # Parameters
        self._pad = None

    def get_parameters(self, img_width, img_height):
        if self.dataset is not None:
            net_w, net_h = self.dataset.input_dim
        elif isinstance(self.dimension, int):
            net_w, net_h = self.dimension, self.dimension
        else:
            net_w, net_h = self.dimension

        if self.multiple_dim:
            if img_width % net_w == 0 and img_height % net_h == 0:
                self._pad = (0, 0, 0, 0)
            else:
                pad_w = ((net_w - (img_width % net_w)) % net_w) / 2
                pad_h = ((net_h - (img_height % net_h)) % net_h) / 2
                self._pad = (int(pad_w), int(pad_h), int(pad_w+.5), int(pad_h+.5))
        else:
            if img_width == net_w and img_height == net_h:
                self._pad = (0, 0, 0, 0)
            elif img_width <= net_w and img_height <= net_h:
                pad_w = (net_w - img_width) / 2
                pad_h = (net_h - img_height) / 2
                self._pad = (int(pad_w), int(pad_h), int(pad_w+.5), int(pad_h+.5))
            else:
                raise ValueError(f'Can only pad to bigger dimensions. Image is bigger than network dimensions [({img_height}, {img_width}) -> ({net_h}, {net_w})]')

    @torch.jit.unused
    def _tf_pil(self, img):
        if self._pad != (0, 0, 0, 0):
            shape = np.array(img).shape
            channels = shape[2] if len(shape) > 2 else 1
            img = ImageOps.expand(img, border=self._pad, fill=(int(self.fill_color*255),)*channels)

        return img

    @torch.jit.unused
    def _tf_cv(self, img):
        if self._pad != (0, 0, 0, 0):
            channels = img.shape[2] if len(img.shape) > 2 else 1
            img = cv2.copyMakeBorder(img, self._pad[1], self._pad[3], self._pad[0], self._pad[2], cv2.BORDER_CONSTANT, value=(int(self.fill_color*255),)*channels)

        return img

    def _tf_torch(self, img):
        if self._pad != (0, 0, 0, 0):
            img = F.pad(img, (self._pad[0], self._pad[2], self._pad[1], self._pad[3]), value=self.fill_color)

        return img

    @torch.jit.unused
    def _tf_anno(self, anno):
        if self._pad != (0, 0, 0, 0):
            anno['x_top_left'] += self._pad[0]
            anno['y_top_left'] += self._pad[1]
            if 'segmentation' in anno.columns:
                anno['segmentation'] = anno['segmentation'].geos.translate(*self._pad)

        return anno


class FitAnno(AnnoTransform):
    """ Crop and filter annotations to fit inside of the image boundaries. |br|
    This transformation also modifies the `truncated` columns of the annotations, by computing how much of the annotation was cut off.

    Args:
        crop (boolean, optional): Whether to actually crop annotations to fit inside the image boundaries; Default **True**
        filter (boolean, optional): Whether to filter the annotations if they are not completely inside of the image boundaries; Default **True**
        filter_type (string, optional): How to filter ('remove' or 'ignore'); Default **remove**
        filter_threshold (number, optional): Minimal percentage of the bounding box area that still needs to be inside the image; Default **0.001**
        remove_empty (boolean, optional): Whether to remove annotations whose bounding box area is zero (independent of filter args); Default **True**
        allow_segmentation (boolean, optional): Whether to allow to compute the filtering and cropping from the segmentation data; Default **True**
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Note:
        This transformation does not modify the image data, but is still a multi-transform as it needs to read the image to get the dimensions.
        Create 1 FitAnno object and use it for both image and annotation transforms.

    Note:
        If the `filter_threshold` is a tuple of 2 numbers, then they are to be considered as **(width, height)** threshold values.
        Otherwise the threshold is to be considered as an area threshold.
        This does mean that we cannot use the segmentation data for computing the filter mask when using a tuple.
    """
    def __init__(self, crop=True, filter=True, filter_type='remove', filter_threshold=0.001, remove_empty=True, allow_segmentation=True, **kwargs):
        super(AnnoTransform, self).__init__(**kwargs)
        self.crop = crop
        self.filter = filter
        self.filter_type = filter_type.lower()
        self.filter_threshold = filter_threshold
        self.remove_empty = True
        self.allow_segmentation = allow_segmentation

        # Parameters
        self._img_width = None
        self._img_height = None

    def get_parameters(self, img_width, img_height):
        self._img_width = img_width
        self._img_height = img_height

    @torch.jit.unused
    def _tf_anno(self, anno):
        crop_coords = np.empty((4, len(anno.index)), dtype=np.float64)
        crop_coords[0] = anno['x_top_left'].values
        crop_coords[1] = crop_coords[0] + anno['width'].values
        crop_coords[2] = anno['y_top_left'].values
        crop_coords[3] = crop_coords[2] + anno['height'].values
        crop_coords[:2] = crop_coords[:2].clip(0, self._img_width)
        crop_coords[2:] = crop_coords[2:].clip(0, self._img_height)
        crop_width = crop_coords[1] - crop_coords[0]
        crop_height = crop_coords[3] - crop_coords[2]
        seg_col = 'segmentation' in anno.columns
        if seg_col:
            try:
                intersection = anno['segmentation'].geos.clip_by_rect(0, 0, self._img_width, self._img_height).geos.make_valid()
            except BaseException:
                intersection = anno['segmentation'].geos.intersection(pygeos.box(0, 0, self._img_width, self._img_height))

            intersect = intersection.geos.area()
            area = anno['segmentation'].geos.area()

        # UserWarnings occur when box width or height is zero (divide by zero)
        # Disable theses annoying warnings as we manually handle the nan cases:
        #   - Masks: `nan >= X = False`
        #   - Computes: `np.nan_to_num(nan) = 0`
        with np.errstate(divide='ignore', invalid='ignore'):
            if self.filter:
                if isinstance(self.filter_threshold, collections.Sequence):
                    mask = (
                        ((crop_width / anno['width'].values) >= self.filter_threshold[0])
                        & ((crop_height / anno['height'].values) >= self.filter_threshold[1])
                    )
                elif seg_col and self.allow_segmentation:
                    mask = (intersect.values / area.values) >= self.filter_threshold
                else:
                    mask = ((crop_width * crop_height) / (anno['width'].values * anno['height'].values)) >= self.filter_threshold

                if self.filter_type == 'ignore':
                    anno.loc[~mask, 'ignore'] = True
                else:
                    anno = anno[mask].copy()
                    if len(anno.index) == 0:
                        return anno

                    crop_coords = crop_coords[:, mask]
                    crop_width = crop_width[mask]
                    crop_height = crop_height[mask]
                    if seg_col:
                        intersection = intersection[mask]
                        intersect = intersect[mask]
                        area = area[mask]

            if self.crop:
                if seg_col and self.allow_segmentation:
                    anno['truncated'] = np.nan_to_num((1 - ((intersect.values * (1 - anno['truncated'].values)) / area.values)).clip(0, 1))
                    anno['segmentation'] = intersection
                    bounds = intersection.geos.bounds()
                    anno['x_top_left'] = bounds['xmin']
                    anno['y_top_left'] = bounds['ymin']
                    anno['width'] = bounds['xmax'] - bounds['xmin']
                    anno['height'] = bounds['ymax'] - bounds['ymin']
                else:
                    anno['truncated'] = np.nan_to_num((1 - ((crop_width * crop_height * (1 - anno['truncated'].values)) / (anno['width'].values * anno['height'].values))).clip(0, 1))
                    anno['x_top_left'] = crop_coords[0]
                    anno['y_top_left'] = crop_coords[2]
                    anno['width'] = crop_width
                    anno['height'] = crop_height
                    if seg_col:
                        anno['segmentation'] = intersection

        if self.remove_empty:
            anno = anno[(anno['width'] > 0) & (anno['height'] > 0)].copy()

        return anno
