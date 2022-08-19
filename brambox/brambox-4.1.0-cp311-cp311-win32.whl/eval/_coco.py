#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Functions for computing coco statistics
#   https://github.com/cocodataset/cocoapi
#
import logging
from statistics import mean
import pandas as pd
from collections import defaultdict
from tqdm.auto import tqdm as _tqdm
from .. import stat
from ..util._logaggregator import LogAggregator
from ._cache import Cache

__all__ = ['COCO']
log = logging.getLogger(__name__)


class COCO:
    """ Computes the Average Precision values as defined in `COCO <cocoapi_>`_. |br|
    This class caches results when computing them, so acessing them a second time is instant.

    Args:
        detection (pd.DataFrame): brambox detection dataframe
        annotation (pd.DataFrame): brambox annotation dataframe
        max_det (int, optional): Maximum number of detections per image (set to **None** to disable); Default **100**
        tqdm (bool, optional): Whether to show a progress bar with tqdm; Default **True**

    Example:
        >>> anno = bb.io.load(...)
        >>> det = bb.io.load(...)
        >>> coco = bb.eval.COCO(det, anno)
        >>> print(coco.mAP)
        mAP_50        0.636573
        mAP_75        0.446958
        mAP_coco      0.412408
        mAP_small     0.191750
        mAP_medium    0.392910
        mAP_large     0.518912

        You can also acess the underlying AP values for each class independently

        >>> anno = bb.io.load(...)
        >>> det = bb.io.load(...)
        >>> coco = bb.eval.COCO(det, anno)
        >>> print(coco.AP_75)
        carrot      0.215381
        boat        0.262389
        train       0.688132
        keyboard    0.537184
        sink        0.378610

    Warning:
        Compared to the pycocotools, the area is computed differently here. |br|
        In pycocotools, they compute the area of the annotations as the area of the segmentation mask
        as opposed to the area of the bounding box, which is used here.
    """
    iou_range = [iou/100 for iou in (range(50, 100, 5))]    #: IoU range for AP_coco, AP_small, AP_medium and AP_large
    areas = {
        'small':    [None, 32**2],
        'medium':   [32**2, 96**2],
        'large':    [96**2, None],
    }                                                       #: Different area ranges for AP_small, AP_medium and AP_large

    def __init__(self, detection, annotation, max_det=100, tqdm=True):
        self.tqdm = tqdm

        # Get dataframes
        self.annotation = annotation.copy()
        if max_det is not None:
            self.detection = (
                detection
                .sort_values('confidence', ascending=False)
                .groupby('image', sort=False)
                .head(max_det)
                .reset_index(drop=True)
            )
        else:
            self.detection = detection.copy()

        # Compute areas
        self.detection['area'] = self.detection.width * self.detection.height
        self.annotation['area'] = self.annotation.width * self.annotation.height

        # Get class labels
        anno_label = set(self.annotation.class_label.unique())
        det_label = set(self.detection.class_label.unique())
        self.class_label = anno_label | det_label
        if anno_label != det_label:
            log.error('Annotations and Detections do not contain the same class labels! Computing all labels.')

        # Check images
        if set(self.annotation.image.cat.categories) != set(self.detection.image.cat.categories):
            log.error('Annotation and Detection dataframe do not contain the same image categories! Computing for all images.')

        # Initialize private fields
        self.cache = Cache(
            'AP_50',
            'AP_75',
            'AP_coco',
            'AP_small',
            'AP_medium',
            'AP_large',
        )

    def reset(self):
        """ Resets the cache. """
        self.cache.reset()

    def compute(self, *values):
        """
        Compute and return the different mAP values.

        Args:
            values (string): Which values to recompute (names from cache)

        Warning:
            This function performs the actual computation, but returns nothing.
            You should probably never call this function, but instead access the various properties of this class,
            as they automatically call compute with the right values.
        """
        # Check if recompute is necessary
        recompute = defaultdict(bool, {val: val not in self.cache for val in values})
        if not any(recompute.values()):
            return

        # Setup dictionaries
        for name in recompute.keys():
            self.cache[name] = {}

        # Compute AP values
        cl_iter = _tqdm(self.class_label, desc='Computing AP') if self.tqdm else self.class_label
        for label in cl_iter:
            if self.tqdm:
                cl_iter.set_postfix(label=label)

            ac = self.annotation[self.annotation.class_label == label]
            dc = self.detection[self.detection.class_label == label]

            with LogAggregator(msg=f'[{label}] {{}}'):
                if recompute['AP_50']:
                    self.cache['AP_50'][label] = self.compute_ap(dc, ac, [0.50])
                if recompute['AP_75']:
                    self.cache['AP_75'][label] = self.compute_ap(dc, ac, [0.75])
                if recompute['AP_coco']:
                    self.cache['AP_coco'][label] = self.compute_ap(dc, ac, self.iou_range)
                if recompute['AP_small']:
                    self.cache['AP_small'][label] = self.compute_ap(dc, ac, self.iou_range, *self.areas['small'])
                if recompute['AP_medium']:
                    self.cache['AP_medium'][label] = self.compute_ap(dc, ac, self.iou_range, *self.areas['medium'])
                if recompute['AP_large']:
                    self.cache['AP_large'][label] = self.compute_ap(dc, ac, self.iou_range, *self.areas['large'])

        # Create dataframes
        for name, value in recompute.items():
            if value:
                self.cache[name] = pd.Series(self.cache[name])

    def compute_ap(self, det, anno, ious, areamin=None, areamax=None):
        """ This function does the actual AP computation for annotations and detections of a specific class_label. |br|
        This has been implemented as a separate function, so that you can inherit from this class and only overwrite this method and provide your own.

        Args:
            det (pd.DataFrame): brambox detection dataframe of only one class
            anno (pd.DataFrame): brambox detection dataframe of only one class
            ious (list of floats): Intersection over Union values between 0 and 1
            areamin (int | None, optional): Minimal area objects should have to count for the AP; Default **None**
            areamax (int | None, optional): Maximal area objects should have to count for the AP; Default **None**
        """
        # Prepare annotations
        # Existing ignore annotations are considered regions and thus are matched with IgnoreMethod.MULTIPLE
        # We set annotations whose areas dont fall within the range to ignore, but they should be matched with IgnoreMethod.SINGLE
        # This also means the pdollar criteria will compute IoA for existing ignore regions, but IoU for detections outside of range
        anno = anno.copy()
        anno['ignore_method'] = stat.IgnoreMethod.SINGLE
        anno.loc[anno.ignore, 'ignore_method'] = stat.IgnoreMethod.MULTIPLE
        if areamin is not None:
            anno.loc[anno.area < areamin, 'ignore'] = True
        if areamax is not None:
            anno.loc[anno.area > areamax, 'ignore'] = True

        # Compute matches
        # This is done separately so that we can remove detections that dont fall within the area range and are false positives
        matches = stat.match_det(det, anno, ious, class_label=False, ignore=stat.IgnoreMethod.INDIVIDUAL)

        aps = []
        li = len(ious)
        for iou in ious:
            # If multiple IoUs are selected, we need compute the PR-func for each by setting the TP/FP columns manually
            if li > 1:
                matches['tp'] = matches[f'tp-{iou}']
                matches['fp'] = matches[f'fp-{iou}']

            # Ignore any detection that did not match with an annotation and is not within the area range
            if areamin is not None:
                matches.loc[matches.area < areamin, 'fp'] = False
            if areamax is not None:
                matches.loc[matches.area > areamax, 'fp'] = False

            # Compute PR
            # The COCOAPI computes smoothed PR-curves, so we do the same
            pr = stat.pr(matches, anno, iou, smooth=True)

            # Compute AP
            # The COCOAPI computes this using an interpolated Riemann Sum.
            aps.append(stat.auc_interpolated(pr))

        return mean(aps)

    @property
    def mAP(self):
        """ Compute and return all mAP values. """
        self.compute(
            'AP_50',
            'AP_75',
            'AP_coco',
            'AP_small',
            'AP_medium',
            'AP_large',
        )

        return pd.Series({
            'mAP_50': self.cache['AP_50'].mean(skipna=True),
            'mAP_75': self.cache['AP_75'].mean(skipna=True),
            'mAP_coco': self.cache['AP_coco'].mean(skipna=True),
            'mAP_small': self.cache['AP_small'].mean(skipna=True),
            'mAP_medium': self.cache['AP_medium'].mean(skipna=True),
            'mAP_large': self.cache['AP_large'].mean(skipna=True),
        })

    @property
    def AP_50(self):
        """ Computes and returns the AP of each class at an IoU threshold of 50%. """
        self.compute('AP_50')
        return self.cache['AP_50'].copy()

    @property
    def AP_75(self):
        """ Computes and returns the AP of each class at an IoU threshold of 75%. """
        self.compute('AP_75')
        return self.cache['AP_75'].copy()

    @property
    def AP_coco(self):
        """ Computes and returns the averaged AP of each class at an IoU threshold of {50%, 55%, 60%, ..., 95%}. """
        self.compute('AP_coco')
        return self.cache['AP_coco'].copy()

    @property
    def AP_small(self):
        """ Computes and returns the averaged AP of each class at an IoU threshold of {50%, 55%, 60%, ..., 95%},
        while only considering small objects: :math:`area < 32^2`.
        """
        self.compute('AP_small')
        return self.cache['AP_small'].copy()

    @property
    def AP_medium(self):
        """ Computes and returns the averaged AP of each class at an IoU threshold of {50%, 55%, 60%, ..., 95%},
        while only considering medium objects: :math:`32^2 < area < 96^2`.
        """
        self.compute('AP_medium')
        return self.cache['AP_medium'].copy()

    @property
    def AP_large(self):
        """ Computes and returns the averaged AP of each class at an IoU threshold of {50%, 55%, 60%, ..., 95%},
        while only considering large objects: :math:`area > 96^2`.
        """
        self.compute('AP_large')
        return self.cache['AP_large'].copy()
