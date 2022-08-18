#
#   Anchors Functionality
#   Copyright EAVISE
#
import logging
import operator
from collections.abc import Iterable
import numpy as np
import pandas as pd
import brambox as bb
import torch
from lightnet.data.transform import ImageAnnoTransform
from lightnet._imports import Image, tqdm

__all__ = ['AnchorError', 'Anchors', 'check_anchors', 'compute_anchors']
log = logging.getLogger(__name__)


class AnchorError(Exception):
    """ Raised whenever an error occurs with anchors. """
    def __init__(self, *args, **kwargs):
        self.anchor = None
        if len(args) >= 1 and isinstance(args[0], Anchors):
            self.anchor = args[0]
            args = args[1:]
        super().__init__(*args, **kwargs)

    def __str__(self):
        value = super().__str__()
        if self.anchor is not None:
            return f'{value}\n{self.anchor}'
        else:
            return value


class anchor_meta(type):
    """ Anchor MetaClass so that we can add 'classproperties' that return commonly used anchors. """
    @property
    def TinyYoloV2_VOC(cls):
        """ Tiny YoloV2 Anchors for the VOC dataset. """
        return Anchors.from_darknet(
            32,
            ((1.08, 1.19), (3.42, 4.41), (6.63, 11.38), (9.42, 5.11), (16.62, 10.52)),
        )

    @property
    def YoloV2_VOC(cls):
        """ YoloV2 Anchors for the VOC dataset. """
        return Anchors.from_darknet(
            32,
            ((1.3221, 1.73145), (3.19275, 4.00944), (5.05587, 8.09892), (9.47112, 4.84053), (11.2364, 10.0071)),
        )

    @property
    def TinyYoloV3_COCO(cls):
        """ Tiny YoloV3 Anchors for the MS COCO dataset. """
        return Anchors.from_darknet(
            (32, 16),
            ((81, 82), (135, 169), (344, 319), (10, 14), (23, 27), (37, 58)),
            (0, 0, 0, 1, 1, 1),
        )

    @property
    def YoloV3_COCO(cls):
        """ YoloV3 Anchors for the MS COCO dataset. """
        return Anchors.from_darknet(
            (32, 16, 8),
            ((116, 90), (156, 198), (373, 326), (30, 61), (62, 45), (59, 119), (10, 13), (16, 30), (33, 23)),
            (0, 0, 0, 1, 1, 1, 2, 2, 2),
        )


class Anchors(metaclass=anchor_meta):
    """ This class allows to define anchors in a predictable way. |br|
    Darknet anchors are inconsistent, because they get specified differently depending on whether the model is multiscale or not:

    Single Scale
        The anchors are defined relative to the output feature map size. |br|
        For the case of YoloV2 on Pascal VOC, the anchors are relative to a size of 32x32, which are the output feature map dimensions.
        This means you cannot easily reuse these anchors for a model with a different stride.

    Multi Scale
        The anchors are defined relative to the input image size.
        This is because there are multiple output feature maps with different dimensions, which would make referencing those confusing. |br|
        For the case of YoloV3 on MS COCO, the anchors are relative to a size of 608x608, as this is the input image size of the model for that dataset.

    This class provides a predictable interface, and always store anchors compared to their **input image size**.
    However, we still allow to create anchors with values relative to :meth:`input image <lightnet.util.Anchors.__init__>`
    or relative to the :class:`output feature maps <lightnet.util.Anchors.from_output>`.

    .. rubric:: Anchors:

    This class also has some properties that provide common anchors.

    - `Anchors.TinyYoloV2_VOC`: Darknet Tiny YoloV2 anchors for the VOC dataset
    - `Anchors.YoloV2_VOC`: Darknet YoloV2 anchors for the VOC dataset
    - `Anchors.TinyYoloV3_COCO`: Darknet Tiny YoloV3 anchors for the MS COCO dataset
    - `Anchors.YoloV3_COCO`: Darknet YoloV3 anchors for the MS COCO dataset

    Note:
        See :func:`~lightnet.util.compute_anchors` for a way of computing good anchors for your data
        and :func:`~lightnet.util.check_anchors` for a way to check how well a set of anchors matches with your data.

    Examples:
        >>> # Construct anchors from values relative to the input image size (ic. YoloV3)
        >>> anchors_yoloV3 = ln.util.Anchors([[(116, 90), (156, 198), (373, 326)], [(30, 61), (62, 45), (59, 119)], [(10, 13), (16, 30), (33, 23)]])
        >>> anchors_yoloV3
        Anchors(
          [
            (116, 90)
            (156, 198)
            (373, 326)
          ]
          [
            (30, 61)
            (62, 45)
            (59, 119)
          ]
          [
            (10, 13)
            (16, 30)
            (33, 23)
          ]
        )

        >>> # Alternatively, we can construct it with a 2D list and a scales list
        >>> anchors_yoloV3 = ln.util.Anchors(
        ...     [(116, 90), (156, 198), (373, 326), (30, 61), (62, 45), (59, 119), (10, 13), (16, 30), (33, 23)],
        ...     [0, 0, 0, 1, 1, 1, 2, 2, 2],
        ... )
        >>> print(anchors_yoloV3)
        Anchors(
          ((116, 90), (156, 198), (373, 326))
          ((30, 61), (62, 45), (59, 119))
          ((10, 13), (16, 30), (33, 23))
        )

        >>> # Construct anchors from values relative to the output feature maps (ic. YoloV2)
        >>> # Note that they get transformed to be relative to the input image size
        >>> anchors_yoloV2 = ln.util.Anchors.from_output(
        ...     ln.models.YoloV2,
        ...     [(1.3221, 1.73145), (3.19275, 4.00944), (5.05587, 8.09892), (9.47112, 4.84053), (11.2364, 10.0071)],
        ... )
        >>> print(anchors_yoloV2)
        Anchors(((42.3072, 55.4064), (102.168, 128.30208), (161.78784, 259.16544), (303.07584, 154.89696), (359.5648, 320.2272)))
        >>> # It is now trivial to convert these anchors to another model
        >>> # ic. DYolo has a stride of 8, so the anchor values should be divided by 8
        >>> anchors_yoloV2.as_output(ln.models.DYolo)
        tensor([[ 5.2884,  6.9258],
                [12.7710, 16.0378],
                [20.2235, 32.3957],
                [37.8845, 19.3621],
                [44.9456, 40.0284]])
        >>> # We can even adapt it for multiscale detectors by dividing the anchors among the different scales
        >>> anchor_tensors = anchors_yoloV2.set_scales((0,0,1,2,2)).as_output(ln.models.YoloV3, merged=False)
        >>> anchor_tensors[0]
        tensor([[1.3221, 1.7314],
                [3.1927, 4.0094]])
        >>> anchor_tensors[1]
        tensor([[10.1117, 16.1978]])
        >>> anchor_tensors[2]
        tensor([[37.8845, 19.3621],
                [44.9456, 40.0284]])

        >>> # Finally, the from_darknet method allows us to build anchors from either input/output depending on the model
        >>> # YoloV3 is a multiscale model and thus the darknet anchors are relative to the input
        >>> anchors_yoloV3 = ln.util.Anchors.from_darknet(
        ...     ln.models.YoloV3,
        ...     [[(116, 90), (156, 198), (373, 326)], [(30, 61), (62, 45), (59, 119)], [(10, 13), (16, 30), (33, 23)]],
        ... )
        >>> print(anchors_yoloV3)
        Anchors(
          ((116, 90), (156, 198), (373, 326))
          ((30, 61), (62, 45), (59, 119))
          ((10, 13), (16, 30), (33, 23))
        )

        >>> # YoloV2 is a singlescale model and thus the darknet anchors are relative to the output
        >>> anchors_yoloV2 = ln.util.Anchors.from_darknet(
        ...     ln.models.YoloV2,
        ...     [(1.3221, 1.73145), (3.19275, 4.00944), (5.05587, 8.09892), (9.47112, 4.84053), (11.2364, 10.0071)],
        ... )
        >>> print(anchors_yoloV2)
        Anchors(((42.3072, 55.4064), (102.168, 128.30208), (161.78784, 259.16544), (303.07584, 154.89696), (359.5648, 320.2272)))
    """
    def __init__(self, anchors, scales=None):
        """ Construct anchors from values relative to the input.

        Args:
            anchors (Iterable): 2D list of anchors or 3D list of anchors
            scales (Iterable, optional): list linking each anchor to a specific scale (Only used for 2D lists of anchors); Default **None**
        """
        if scales is not None:
            # 2D list with mulitscale list
            self.anchors = tuple(tuple(a) for a in anchors)
            self.scales = tuple(scales)
            if len(self.anchors) != len(self.scales):
                raise AnchorError(f'Anchors and scales should have same length. [{len(self.anchors)} - {len(self.scales)}]')
        elif not isinstance(anchors[0][0], (int, float)):
            # 3D list as input
            self.anchors = tuple(tuple(a) for aa in anchors for a in aa)
            self.scales = tuple(i for i, aa in enumerate(anchors) for a in aa)
        else:
            # 2D anchors
            self.anchors = tuple(tuple(a) for a in anchors)
            self.scales = tuple(0 for _ in self.anchors)

    @classmethod
    def from_output(cls, stride_or_model, anchors, scales=None):
        """ Construct anchors from values which are relative to the output feature maps.

        Args:
            stride_or_model (Number or Iterable or model): list of stride values for the different scales or model from which to fetch the stride
            anchors (Iterable): 2D list of anchors or 3D list of anchors
            scales (Iterable, optioan): list linking each anchor to a specific scale (Only used for 2D lists of anchors); Default **None**
        """
        stride = getattr(stride_or_model, 'stride', stride_or_model)
        if not isinstance(stride, Iterable):
            stride = (stride,)

        anchors = cls(anchors, scales)

        try:
            return anchors * stride
        except AnchorError as err:
            raise AnchorError(f'Expected {anchors.num_scales} stride(s), but got {len(stride)}') from err

    @classmethod
    def from_darknet(cls, stride_or_model, anchors, scales=None):
        """ Construct anchors from values which come from the darknet framework. |br|
        More specifically, this means you have values relative to the output for single scale models,
        and values relative to the input for multiscale models.

        Args:
            stride_or_model (Number or Iterable or model): list of stride values for the different scales or model from which to fetch the stride
            anchors (Iterable): 2D list of anchors or 3D list of anchors
            scales (Iterable, optioan): list linking each anchor to a specific scale (Only used for 2D lists of anchors); Default **None**
        """
        stride = getattr(stride_or_model, 'stride', stride_or_model)
        if not isinstance(stride, Iterable):
            stride = (stride,)

        if len(stride) > 1:
            return cls(anchors, scales)
        else:
            return cls.from_output(stride, anchors, scales)

    def as_input(self, merged=True):
        """ Return the anchors as a tensor.

        Args:
            merged (bool, optional):
                Whether to merge all anchors in one tensor or have a tuple of separate tensors per anchor; Default **True**
        """
        tensors = tuple(torch.tensor(self.__get_scale(i), dtype=torch.float) for i in range(self.num_scales))

        if merged:
            return torch.cat(tensors)
        else:
            return tensors

    def as_output(self, stride_or_model, merged=True):
        """ Return the anchors as one tensor per scale, compared to the output feature map dimensions. |br|
        The difference with :meth:`~lightnet.util.Anchors.as_input` is that we divide the anchor widths and heights by their matching stride,
        so that the anchors are relative to the output feature map dimensions.

        Args:
            stride_or_model (number or Iterable<number> or lightnet model):
                stride or model for which you want the output anchors.
            merged (bool, optional):
                Whether to merge all anchors in one tensor or have a tuple of separate tensors per anchor; Default **True**

        Note:
            If there is only one scale, we return a tensor as opposed to a tuple of tensors.
        """
        stride = getattr(stride_or_model, 'stride', stride_or_model)
        if not isinstance(stride, Iterable):
            stride = (stride,)

        try:
            anchors = self / stride
        except AnchorError as err:
            raise AnchorError(f'Expected {self.num_scales} stride(s), but got {len(stride)}') from err

        return anchors.as_input(merged)

    def resize(self, scales, all=False, inplace=False, op=operator.mul):
        """ Resize anchors.

        Args:
            scales (number or Iterable):
                Value used to to resize the anchors. Can also be an iterable to resize by different values for each scale
            all (boolean, optional):
                Whether to multiply all anchor values or only the first two (width, height); Default **False**
            inplace (boolean, optional):
                Whether to perform inplace modification or return new anchors; Default **False**
            op (callable, optional):
                Which rescaling operation to use; Default **operator.mul**

        Returns:
            Anchors or None: Resized anchors or **None** if inplace.
        """
        if isinstance(scales, Iterable):
            if len(scales) != self.num_scales:
                raise AnchorError(f'Expected {self.num_scales} scale(s), but got {len(scales)}')

            if all:
                anchors = (tuple(op(aa, scales[s]) for aa in a) for a, s in zip(self.anchors, self.scales))
            else:
                anchors = ((op(w, scales[s]), op(h, scales[s]), *a) for (w, h, *a), s in zip(self.anchors, self.scales))

            if inplace:
                self.anchors = tuple(anchors)
            else:
                return self.__class__(anchors, self.scales)
        else:
            return self.resize(
                tuple(scales for _ in range(self.num_scales)),
                all,
                inplace,
                op,
            )

    def append_values(self, values, inplace=False):
        """ Append extra values (eg. angles) to your anchors. |br|
        For each value, this method will duplicate all of your existing anchors and append that value.

        This is the exact opposite of :meth:`~lightnet.util.Anchors.remove_values`.

        Args:
            values (number or Iterable): Different values to add to each anchor
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if not isinstance(values, Iterable):
            values = (values,)

        anchors = ((*a, v) for a in self.anchors for v in values)
        scales = (s for s in self.scales for _ in values)

        if inplace:
            self.anchors = tuple(anchors)
            self.scales = tuple(scales)
        else:
            return self.__class__(anchors, scales)

    def remove_values(self, index, inplace=False):
        """ Remove values (eg. angles) from your anchors. |br|
        This method will remove the given indices from each anchor and then filter to only keep unique anchors

        This is the exact opposite of :meth:`~lightnet.util.Anchors.append_values`.

        Args:
            index (int): The index of the value you want to remove from each anchor
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if index < 0:
            index = self.values_per_anchor + index
        if index < 0 or index >= self.values_per_anchor:
            raise IndexError('Index is out of bounds')

        # Remove values
        new_anchors = tuple(tuple(a for i, a in enumerate(anchor) if i != index) for anchor in self.anchors)

        # Filter duplicates
        anchors, scales = [], []
        for a, s in zip(new_anchors, self.scales):
            duplicate = False
            for na, ns in zip(anchors, scales):
                if (a == na) and (s == ns):
                    duplicate = True
                    break

            if not duplicate:
                anchors.append(a)
                scales.append(s)

        if inplace:
            self.anchors = tuple(anchors)
            self.scales = tuple(scales)
        else:
            return self.__class__(anchors, scales)

    def append_anchor(self, anchor, scale=0, inplace=False):
        """ Append an extra anchor.

        Args:
            anchor (tuple): new anchor value (eg. (w, h))
            scale (int, optional): The scale to which the anchor belongs; Default **0**
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if not isinstance(anchor, tuple):
            anchor = tuple(anchor)
        if len(anchor) != self.values_per_anchor:
            log.warning(
                'New anchor does not have the same number of items as existing anchors. [%d - %d]',
                len(anchor),
                self.values_per_anchor,
            )

        anchors = self.anchors + (tuple(anchor),)
        scales = self.scales + (scale,)

        if inplace:
            self.anchors = anchors
            self.scales = scales
        else:
            return self.__class__(anchors, scales)

    def remove_anchor(self, index, scale=0, inplace=False):
        """ Remove an anchor. |br|
        This function remove the n'th anchor from a certain scale.

        Args:
            index (int): The index of the anchor
            scale (int, optional): The scale to which the anchor belongs; Default **0**
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if index < 0:
            index = self.num_anchors + index
        if index < 0 or index >= self.num_anchors:
            raise IndexError('Index is out of bounds')

        anchors = (a for s in range(self.num_scales) for i, a in enumerate(self.__get_scale(s)) if (s != scale or i != index))
        scales = (s for s in range(self.num_scales) for i, _ in enumerate(self.__get_scale(s)) if (s != scale or i != index))

        if inplace:
            self.anchors = tuple(anchors)
            self.scales = tuple(scales)
        else:
            return self.__class__(anchors, scales)

    def get_scale(self, scale, as_anchor=True):
        """ Return the anchors of a given scale.

        Args:
            scale (number): The scale for which you want the anchors
            as_anchor (boolean, optional): Whether to return the anchors as a tuple or an Anchors instance; Default **True**
        """
        if scale >= self.num_scales:
            raise IndexError(f'Expected scale to be less than {self.num_scales}, but got {scale}')
        anchors = self.__get_scale(scale)

        if as_anchor:
            return self.__class__(anchors)
        else:
            return anchors

    def remove_scale(self, scale, inplace=False):
        """ Remove the anchors of a given scale.

        Args:
            scale (number): The scale for which you want the anchors
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if scale < 0:
            scale = self.num_scales + scale
        if scale < 0 or scale >= self.num_scales:
            raise IndexError('Scale is out of bounds')

        anchors = (a for s in range(self.num_scales) for a in self.__get_scale(s) if s != scale)
        scales = (s if s < scale else s-1 for s in range(self.num_scales) for _ in self.__get_scale(s) if s != scale)

        if inplace:
            self.anchors = tuple(anchors)
            self.scales = tuple(scales)
        else:
            return self.__class__(anchors, scales)

    def set_scales(self, scales=None, inplace=False):
        """ Set which anchor belongs to which scale. |br|
        If no scales are passed, we set each anchor to belong to scale zero.

        Args:
            scales (Iterable): A list with indices for each of the anchors; Default **None**
            inplace (boolean, optional): Whether to perform inplace modification or return new anchors; Default **False**

        Returns:
            Anchors or None: New anchors or **None** if inplace.
        """
        if scales is None:
            scales = tuple(0 for _ in range(self.num_anchors))
        else:
            scales = tuple(scales)
            if len(scales) != self.num_anchors:
                raise AnchorError(f'Expected {self.num_anchors} scale values, but got {len(scales)}')
            elif any(scale < 0 for scale in scales):
                raise AnchorError('Scale value should not be smaller than zero')

        if inplace:
            self.scales = scales
        else:
            return Anchors(self.anchors, scales)

    def split_scales(self):
        """ Return an anchor object per scale. """
        return tuple(self.__class__(self.__get_scale(s)) for s in range(self.num_scales))

    @property
    def multiscale(self):
        """ Returns whether these anchors are multiscale. """
        return any(scale > 1 for scale in self.scales)

    @property
    def num_scales(self):
        """ Return the number of scales. """
        return max(self.scales) + 1

    @property
    def num_anchors(self):
        """ Returns the number of anchors. """
        return len(self.anchors)

    @property
    def values_per_anchor(self):
        """ Returns the number of values per anchor. |br|
        This is usually two (w, h) or three (w, h, a).

        Note:
            All your anchors should have the same number of values.
            If this is not the case, we log an error and return the maximal number of items.
        """
        values = tuple(len(a) for a in self.anchors)
        if len(set(values)) != 1:
            log.error('We expect the same number of values per anchor, but this is not the case!')
            return max(values)
        else:
            return values[0]

    def __str__(self):
        if self.multiscale:
            anchors = '\n  '.join(str(self.__get_scale(i)) for i in range(self.num_scales))
            return f'Anchors(\n  {anchors}\n)'
        else:
            return f'Anchors({self.anchors})'

    def __repr__(self):
        string = 'Anchors(\n'
        for i in range(self.num_scales):
            anchors = self.__get_scale(i)
            string += '  [\n    ' + '\n    '.join(str(a) for a in anchors) + '\n  ]\n'
        return string + ')'

    def __mul__(self, other):
        """ Resize anchors by multiplying them with a value.

        Args:
            other (number or Iterable): Value to multiply. Can also be an iterable to multiply by different values for each scale

        Warning:
            This method only multiplies the 2 first values, as these are assumed to be `width, height`. |br|
            See :meth:`~lightnet.util.Anchors.resize` if you want to modify all values of each anchor.
        """
        return self.resize(other, False, False, operator.mul)

    def __truediv__(self, other):
        """ Resize anchors by performing a true division with a value.

        Args:
            other (number or Iterable): Value to divide. Can also be an iterable to divide by different values for each scale

        Warning:
            This method only divides the 2 first values, as these are assumed to be `width, height`. |br|
            See :meth:`~lightnet.util.Anchors.resize` if you want to modify all values of each anchor.
        """
        return self.resize(other, False, False, operator.truediv)

    def __floordiv__(self, other):
        """ Resize anchors by performing a floor division with a value.

        Args:
            other (number or Iterable): Value to divide. Can also be an iterable to divide by different values for each scale

        Warning:
            This method only divides the 2 first values, as these are assumed to be `width, height`. |br|
            See :meth:`~lightnet.util.Anchors.resize` if you want to modify all values of each anchor.
        """
        return self.resize(other, False, False, operator.floordiv)

    def __get_scale(self, scale):
        return tuple(a for a, s in zip(self.anchors, self.scales) if s == scale)


def check_anchors(
    anno,
    anchors,
    fit=None,
    identify=None,
):
    """ Check how well your anchors match your data. |br|
    This function compares the IoU of your anchors with your data
    and returns the index of the best matching anchor, as well as its IoU.

    Args:
        anno (pandas.DataFrame): brambox annotation dataframe
        anchors (lightnet.util.Anchors): anchors you want to check
        fit (lightnet.data.transform.ImageAnnoTransform, optional):
            Fit transformation that will be used on the data prior to running the network; Default **None**
        identify (function, optional):
            Lambda/function to get image based of annotation filename or image id (only necessary when using ``fit``); Default **use image column**

    Returns:
        pandas.DataFrame:
            annotation dataframe with extra `iou` and `anchor` columns.

    Examples:
        In this example, we check the darknet anchors for YoloV2 on the Pascal VOC data.
        We assume the VOCDevkit folder is located in the `data` folder.

        .. doctest::
            :options: +SKIP

            >>> import brambox as bb
            >>> # Load training annotations
            >>> annos = bb.io.load('pandas', './data/traintest/train.h5')
            >>> # This function can take a while, so debug level logs will give us slightly more information on progress
            >>> ln.logger.setConsoleLevel(0)
            >>> # Run clustering
            >>> anno_check = ln.util.check_anchors(
            ...     # Annotations
            ...     annos,
            ...     # YoloV2 VOC Anchors
            ...     ln.util.Anchors.YoloV2_VOC,
            ...     # The default YoloV2 VOC pipeline uses a Letterbox transform to 416x416 input dimensions
            ...     ln.data.transform.Letterbox((416, 416)),
            ...     # Function to get the image path from the image column names in the anno dataframe
            ...     lambda name: f'data/VOCdevkit/{name}.jpg',
            ... )
            DEBUG      Preparing Data...
            DEBUG      Computing IoU...
            INFO       Mean IoU: 59.2727
            >>> # Show details about anchors and annotations
            >>> anno_check.groupby('anchor')['iou'].describe()
                      count       mean        std        min        25%        50%        75%        max
            anchor
            0       13148.0  46.754048  18.891594   1.299347  34.266265  46.888465  59.243871  99.102039
            1       11329.0  59.624666  14.235351  13.456843  48.868130  58.669011  69.162150  99.700601
            2        6314.0  69.302292  10.923282  26.622607  61.696656  67.821839  76.732285  99.604734
            3        4979.0  66.865035  12.436371  15.426576  60.468238  66.713623  74.787686  99.831313
            4        4288.0  73.143479   9.584754  49.041309  65.662809  72.233269  79.995130  98.806671

        We now compare with our own computed values (see :func:`~lightnet.utils.compute_anchors`).

        .. doctest::
            :options: +SKIP

            >>> import brambox as bb
            >>> annos = bb.io.load('pandas', './data/traintest/train.h5')
            >>> anchors = ln.util.Anchors([
            ...     (1.4468439759089717, 1.6985520980941464),
            ...     (3.5225374094743707, 4.2042482723184245),
            ...     (4.920028618844079, 7.9136117509865915),
            ...     (9.676090986871095, 4.912409782262316),
            ...     (10.215033909012737, 9.345741034451954),
            ... ])
            >>> ln.logger.setConsoleLevel(0)
            >>> anno_check = ln.util.check_anchors(
            ...     annos,
            ...     anchors,
            ...     ln.data.transform.Letterbox((416, 416)),
            ...     lambda name: f'data/VOCdevkit/{name}.jpg',
            ... )
            DEBUG      Preparing Data...
            DEBUG      Computing IoU...
            INFO       Mean IoU: 59.1404
            >>> # Show details about anchors and annotations
            >>> anno_check.groupby('anchor')['iou'].describe()
                      count       mean        std        min        25%        50%        75%        max
            anchor
            0       13971.0  45.964699  18.965163   1.198617  33.779201  45.765369  58.160156  99.237757
            1       10960.0  59.729672  14.539442  16.562483  48.392678  59.312899  69.980972  99.059593
            2        5684.0  70.421430  11.087780  26.861254  63.312217  69.573508  77.756115  99.807359
            3        4503.0  67.641370  12.562783  15.397835  60.738373  67.860458  75.864460  99.058363
            4        4940.0  74.367050   9.117949  49.847761  67.788584  74.254623  80.091776  99.380822

        As you can see, our own computed anchors get really close to the original results.
    """
    # Parse arguments
    if not isinstance(anchors, Anchors):
        log.warning('Anchors are not of the anchor type. We assume the values are relative to the input image size.')
        anchors = Anchors(anchors)
    if anno.ignore.any():
        log.warning('Found ignored annotations in the data. This might be erroneous')

    # Fit annotations
    log.debug('Preparing Data...')
    anno_og = anno.copy()
    if fit is not None:
        columns = [c for c in ('x_top_left', 'y_top_left', 'width', 'height', 'angle', 'segmentation') if c in anno.columns]
        anno = fit_annos(anno, fit, identify, columns)

    # Get correct boxes
    if anchors.values_per_anchor >= 3:
        log.info('OBB anchors found, computing OBB IoU')

        anno = bb.util.BoundingBoxTransformer(anno).get_obb_poly()
        anchors = anchors.as_input().numpy().astype(np.float64)
        anchors = pd.DataFrame({
            'x_top_left': [0] * anchors.shape[0],
            'y_top_left': [0] * anchors.shape[0],
            'width': anchors[:, 0],
            'height': anchors[:, 1],
            'angle': anchors[:, 2],
        })
        anchors = bb.util.BoundingBoxTransformer(anchors).get_obb_poly()

        # Center OBB around origin and only keep segmentation
        anno['segmentation'] -= anno[['x_top_left', 'y_top_left']] + anno[['width', 'height']] / 2
        anchors['segmentation'] -= anchors[['width', 'height']] / 2

        # Only keep segmentation polygons ; probably unnecesarry but at least we are sure IoU gets computed on polygons
        anno = anno[['segmentation']]
        anchors = anchors[['segmentation']]
    else:
        anchors = anchors.as_input().numpy().astype(np.float64)
        anchors = pd.DataFrame({
            'x_top_left': [0] * anchors.shape[0],
            'y_top_left': [0] * anchors.shape[0],
            'width': anchors[:, 0],
            'height': anchors[:, 1],
        })

        # Center HBB around origin
        anno['x_top_left'] -= anno['x_top_left'] + anno['width'] / 2
        anno['y_top_left'] -= anno['y_top_left'] + anno['height'] / 2
        anchors['x_top_left'] -= anchors['width'] / 2
        anchors['y_top_left'] -= anchors['height'] / 2

    # Compute
    log.debug('Computing IoU...')
    iou = np.asarray(bb.stat.coordinates.iou(anno, anchors)) * 100

    anchor = np.argmax(iou, axis=1)
    iou = np.choose(anchor, np.moveaxis(iou, 1, 0))
    log.info('Mean IoU: %.3f%%', iou.mean())

    anno_og['iou'] = iou
    anno_og['anchor'] = anchor
    return anno_og


def compute_anchors(
    anno,
    num_anchors,
    fit=None,
    identify=None,
    **kmeans_args,
):
    """ Computes custom anchors for your data, by performing K-means Clustering. |br|
    This transform first performs a fitting transform (Letterbox, Crop, Pad) to your data,
    after which it normalizes the different data columns (width, height, angle).
    Finally, it performs the KMeans clustering algorithm on this data and reports the unnormalized anchor results.

    Args:
        anno (pd.DataFrame): Brambox dataframe with the annotation bounding boxes (See Note)
        num_anchors (int): Number of anchors to compute
        fit (lightnet.data.transform.ImageAnnoTransform, optional):
            Fit transformation that will be used on the data prior to running the network; Default **None**
        identify (function, optional):
            Lambda/function to get image based of annotation filename or image id (only necessary when using ``fit``); Default **use image column**
        kmeans_args (kwargs):
            Extra arguments that are passed to the constructor of sklearn.cluster.KMeans; Default **{}**

    Returns:
        lightnet.utils.Anchors: The computed anchors

    Warning:
        Darknet anchors are inconsistent, because they get specified differently depending on whether the model is multiscale or not.
        This function works with input image sizes, but the returned :class:`~lightnet.util.Anchors` can easily be converted.

    Note:
        This function can work with :meth:`HBB <brambox.util.BoundingBoxTransformer.get_hbb>` or :meth:`OBB <brambox.util.BoundingBoxTransformer.get_obb>` style annotations.
        If you pass in HBB annotations, we perform K-Means clustering on the `width` and `height` columns.
        For OBB annotations, we take the `width`, `height` and `angle` columns. |br|
        Note that we normalize all columns with a :class:`sklearn.preprocessing.StandardScaler`.

    Example:
        In this example, we compute the anchors for YoloV2 on the Pascal VOC data.
        We assume the VOCDevkit folder is located in the `data` folder.

        .. doctest::
            :options: +SKIP

            >>> import brambox as bb
            >>> # Load training annotations
            >>> annos = bb.io.load('pandas', './data/traintest/train.h5')
            >>> # This function can take a while, so debug level logs will give us slightly more information on progress
            >>> ln.logger.setConsoleLevel(0)
            >>> # Run clustering
            >>> anchors = ln.util.compute_anchors(
            ...      # Annotations
            ...      annos,
            ...      # We want 5 anchors
            ...      5,
            ...      # The default YoloV2 VOC pipeline uses a Letterbox transform to 416x416 input dimensions
            ...      ln.data.transform.Letterbox((416, 416)),
            ...      # Function to get the image path from the image column names in the anno dataframe
            ...      lambda name: f'data/VOCdevkit/{name}.jpg',
            ... )
            DEBUG      Normalizing Data...
            DEBUG      Computing Clusters...
            INFO       Clustering Inertia: 0.318349
            >>> # Show anchor values compared to input size (see warning)
            >>> anchors
            Anchors(
              [
                (46.61156707800953, 54.51615885429828)
                (112.57644047055332, 135.85587458319162)
                (159.08053804322563, 255.6458805384609)
                (307.9858092293246, 155.70691605533122)
                (329.2256193937332, 297.06719675845284)
              ]
            )
            >>> # Show anchor values compared to output of YoloV2
            >>> # While not entirely identical, they closely match the values from darknet
            >>> anchors.as_output(ln.models.YoloV2)
            tensor([[ 1.4566,  1.7036],
                    [ 3.5180,  4.2455],
                    [ 4.9713,  7.9889],
                    [ 9.6246,  4.8658],
                    [10.2883,  9.2833]])
    """
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ModuleNotFoundError:
        raise ModuleNotFoundError('The scikit-learn package is required for this function.') from None

    # Parse arguments
    if anno.ignore.any():
        log.warning('Found ignored annotations in the data. This might be erroneous')
    anno = anno.copy()
    columns = ['width', 'height', 'angle'] if 'angle' in anno.columns else ['width', 'height']

    # Normalize data
    log.debug('Normalizing Data...')
    if fit is not None:
        anno = fit_annos(anno, fit, identify, columns)

    scaler = StandardScaler()
    data = scaler.fit_transform(anno[columns].to_numpy())

    # Clustering algorithm
    log.debug('Computing Clusters...')
    kmeans = KMeans(num_anchors, **kmeans_args).fit(data)
    anchors = kmeans.cluster_centers_
    log.info('Clustering Inertia: %.3f%%', 100 * (kmeans.inertia_ / data.shape[0]))

    # Reverse Normalization
    anchors = scaler.inverse_transform(anchors)

    # Sort by width to get consistent results
    anchors = anchors[anchors[:, 0].argsort()[::-1]]

    return Anchors(anchors.tolist())


def fit_annos(anno, fit, identify, columns=None):
    """ Fit annotations according to the pipeline """
    identify = identify or (lambda name: name)
    if not isinstance(fit, ImageAnnoTransform):
        log.error('Fit is assumed to be an ImageAnnoTransform, but is seemingly not [%s] - Skipping fit', type(fit))
        return anno

    def _fit(df):
        fit.get_parameters(*Image.open(identify(df.name)).size)
        _, df = fit(None, df)

        if columns is None:
            return df
        else:
            return df[columns]

    if tqdm:
        anno_size = anno.groupby('image').progress_apply(_fit)
    else:
        anno_size = anno.groupby('image').apply(_fit)

    anno = anno.copy()
    for c in columns:
        anno[c] = anno_size[c]

    return anno
