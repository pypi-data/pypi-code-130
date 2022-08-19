#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Functions for computing tide statistics
#   https://github.com/dbolya/tide
#
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
from tqdm.auto import tqdm as _tqdm
from .. import stat
from .. import util
from ..util._logaggregator import LogAggregator
from ._cache import Cache

__all__ = ['TIDE']
log = logging.getLogger(__name__)


class TIDE:
    """ Indetifies object detection errors, as defined in the `TIDE <tidecv_>`_ project. |br|
    This class caches results when computing them, so acessing them a second time is instant.

    Args:
        detection (pd.DataFrame): brambox detection dataframe
        annotation (pd.DataFrame): brambox annotation dataframe
        pos_thresh (float, optional): IoU threshold to count a detection as a true positive; Default **0.5**
        bg_thresh (float, optional): IoU threshold to count a detection as a background error (as opposed to a localisation error); Default **0.1**
        max_det (int, optional): Maximum number of detections per image (set to **None** to disable); Default **100**
        area_range(tuple of 2 numbers, optional): Area range to filter bounding boxes (See Note below); Default **None**
        tqdm (bool, optional): Whether to show a progress bar with tqdm; Default **True**

    Examples:
        >>> anno = bb.io.load(...)
        >>> det = bb.io.load(...)
        >>> tide = bb.eval.TIDE(det, anno)
        >>> print(tide.mdAP)
        mAP                    0.636573
        mdAP_localisation      0.067788
        mdAP_classification    0.024815
        mdAP_both              0.011547
        mdAP_duplicate         0.002132
        mdAP_background        0.040454
        mdAP_missed            0.075361
        mdAP_fp                0.166521
        mdAP_fn                0.137648

        You can also access the underlying dAP values for each class independently

        >>> anno = bb.io.load(...)
        >>> det = bb.io.load(...)
        >>> tide = bb.eval.TIDE(det, anno)
        >>> print(tide.dAP_duplicate)
        boat              0.003661
        umbrella          0.003789
        toaster           0.000000
        baseball glove    0.000135
        suitcase          0.001445
        cow               0.002164

        Note:
            For the case of `dAP_classification`,
            we sort the detections based on their corrected class labels and not the original class labels which were produced by the detector.

    Note:
        You can specify an minimum and maximum area to consider for detection, by using the `area_range` argument. |br|
        This works a lot like the small, medium and large area's when computing the COCO mAP.
        In fact it is so similar that this class has a `coco_areas` attribute, which you can use as area ranges:

        >>> anno = bb.io.load(...)
        >>> det = bb.io.load(...)
        >>> tide = bb.eval.TIDE(det, anno, area_range=bb.eval.TIDE.coco_areas['large'])
        >>> print(tide.mdAP)
        mAP                    0.770321
        mdAP_localisation      0.066165
        mdAP_classification    0.033556
        mdAP_both              0.014307
        mdAP_duplicate         0.002327
        mdAP_background        0.025024
        mdAP_missed            0.043250
        mdAP_fp                0.134258
        mdAP_fn                0.072322

    Warning:
        Since the official TIDE repo has not yet released there code to be able to filter bounding boxes on range,
        we cannot compare our code with theirs yet and thus have no way of validating our results.
    """
    coco_areas = {
        'small':    [None, 32**2],
        'medium':   [32**2, 96**2],
        'large':    [96**2, None],
    }                                                       #: Different coco area ranges which you can use with TIDE

    def __init__(self, detection, annotation, pos_thresh=0.5, bg_thresh=0.1, max_det=100, area_range=None, tqdm=True):
        self.pos_thresh = pos_thresh
        self.bg_thresh = bg_thresh
        self.area_range = area_range if area_range is not None else (None, None)
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

        if area_range is not None:
            self.annotation['area'] = self.annotation.width * self.annotation.height
            self.detection['area'] = self.detection.width * self.detection.height

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
            'error_detections',
            'error_annotations',
            'AP',
            'dAP_localisation',
            'dAP_classification',
            'dAP_both',
            'dAP_duplicate',
            'dAP_background',
            'dAP_missed',
            'dAP_fn',
            'dAP_fp',
        )

    def reset(self):
        """ Resets the cache. """
        self.cache.reset()

    def compute(self, *values):
        """
        Compute the different mdAP values.

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

        # Match detections and annotations
        dm, am = self.compute_matches(self.detection, self.annotation, self.pos_thresh)
        dm = dm.reset_index(drop=True)
        am = am.reset_index(drop=True)

        # Find Error Types
        err_det = util.DualGroupBy(dm, am, 'image', group_keys=False).apply(find_errors, pos_thresh=self.pos_thresh, bg_thresh=self.bg_thresh).set_index('index')
        if recompute['error_detections']:
            tmp = err_det.drop(['anno'], axis=1).fillna(value=True).astype('int')
            tmp['none'] = 0.1
            tmp = tmp.idxmax(axis=1)
            tmp[tmp == 'none'] = pd.NA
            error_detections = dm.drop(['tp', 'fp'], axis=1)
            error_detections['error'] = tmp
            self.cache['error_detections'] = error_detections
            recompute['error_detections'] = False

        err_det['anno_label'] = dm.class_label
        err_det.loc[err_det.anno.notnull(), 'anno_label'] = am.class_label[err_det.anno[err_det.anno.notnull()]].values

        fn_anno = list(set(am.detection[am.detection.isnull()].index) - set(err_det.anno[err_det.anno.notnull()].unique()))
        fn_anno = np.array(fn_anno, dtype='int')

        if recompute['error_annotations']:
            tmp = np.zeros(len(self.annotation.index), dtype='bool')
            tmp[fn_anno] = True

            error_annotations = am.drop(['detection', 'criteria'], axis=1)
            error_annotations['error'] = tmp
            error_annotations['error'] = error_annotations['error'].map({True: 'missed', False: pd.NA})
            self.cache['error_annotations'] = error_annotations
            recompute['error_annotations'] = False

        am_nofn = np.ones(len(am.index), dtype='bool')
        am_nofn[fn_anno] = False
        am_nofn = am[am_nofn]

        # No recomputes
        if not any(recompute.values()):
            return

        if 'AP' not in self.cache:
            self.cache['AP'] = {}
            recompute['AP'] = True

        # Fix Errors
        def fix_errors(error_type, mask, set_tp=True):
            err = err_det.loc[mask, error_type].copy()
            err_null = err.isnull()
            err[err_null] = False

            dc_err = dm.loc[mask].copy()
            dc_err.loc[(err | err_null), 'fp'] = False
            if set_tp:
                dc_err.loc[err, 'tp'] = True

            return self.compute_ap(dc_err, ac, self.pos_thresh)

        cl_iter = _tqdm(self.class_label, desc='Fixing Errors') if self.tqdm else self.class_label
        for label in cl_iter:
            if self.tqdm:
                cl_iter.set_postfix(label=label)

            det_label_mask = dm.class_label == label
            cls_label_mask = err_det.anno_label == label

            with LogAggregator(msg=f'[{label}] {{}}'):
                if recompute['AP']:
                    dc = dm.loc[det_label_mask]
                    ac = am.loc[am.class_label == label]
                    self.cache['AP'][label] = self.compute_ap(dc, ac, self.pos_thresh)

                if recompute['dAP_localisation']:
                    self.cache['dAP_localisation'][label] = fix_errors(
                        'localisation',
                        det_label_mask,
                    )
                if recompute['dAP_classification']:
                    self.cache['dAP_classification'][label] = fix_errors(
                        'classification',
                        cls_label_mask,
                    )
                if recompute['dAP_both']:
                    self.cache['dAP_both'][label] = fix_errors(
                        'both',
                        det_label_mask,     # IMO should be cls_label_mask, but det_label_mask gives similar results to tidecv
                        set_tp=False,
                    )
                if recompute['dAP_duplicate']:
                    self.cache['dAP_duplicate'][label] = fix_errors(
                        'duplicate',
                        det_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_background']:
                    self.cache['dAP_background'][label] = fix_errors(
                        'background',
                        det_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_missed']:
                    ac_err = am_nofn[am_nofn.class_label == label]
                    self.cache['dAP_missed'][label] = self.compute_ap(
                        dc,
                        ac_err,
                        self.pos_thresh,
                    )
                if recompute['dAP_fp']:
                    dc_fp = dc.copy()
                    dc_fp['fp'] = False
                    self.cache['dAP_fp'][label] = self.compute_ap(
                        dc_fp,
                        ac,
                        self.pos_thresh,
                    )
                if recompute['dAP_fn']:
                    ac_fn = ac.copy()
                    ac_fn = ac_fn[~(ac_fn.detection.isnull())]
                    self.cache['dAP_fn'][label] = self.compute_ap(
                        dc,
                        ac_fn,
                        self.pos_thresh,
                    )

        # Create dataframes
        if isinstance(self.cache['AP'], dict):
            self.cache['AP'] = pd.Series(self.cache['AP'])

        for name, value in recompute.items():
            if value and name != 'AP':
                self.cache[name] = pd.Series(self.cache[name]) - self.cache['AP']

    def compute_matches(self, det, anno, iou):
        """ This function performs the actual matching of detections and annotations.
        It returns TP/FP columns for the detections and detection/criteria for the annotations. |br|
        This has been implemented as a separate function, so that you can inherit from this class and only overwrite this method and provide your own.

        Args:
            det (pd.DataFrame): brambox detection dataframe of only one class
            anno (pd.DataFrame): brambox detection dataframe of only one class
            iou (float): Intersection over Union values between 0 and 1
        """
        # Prepare annotations
        # Existing ignore annotations are considered regions and thus are matched with IgnoreMethod.MULTIPLE
        # We set annotations whose areas dont fall within the range to ignore, but they should be matched with IgnoreMethod.SINGLE
        # This also means the pdollar criteria will compute IoA for existing ignore regions, but IoU for detections outside of range
        anno = anno.copy()
        anno['ignore_method'] = stat.IgnoreMethod.SINGLE
        anno.loc[anno.ignore, 'ignore_method'] = stat.IgnoreMethod.MULTIPLE
        if self.area_range[0] is not None:
            anno.loc[anno.area < self.area_range[0], 'ignore'] = True
        if self.area_range[1] is not None:
            anno.loc[anno.area > self.area_range[1], 'ignore'] = True

        # Match annotations and detections
        # Afterwards, we filter the remaining detection boxes which are outside of the range and were not matched
        dm, am = stat.match_box(det, anno, iou, class_label=True, ignore=stat.IgnoreMethod.INDIVIDUAL)
        if self.area_range[0] is not None:
            dm.loc[dm.area < self.area_range[0], 'fp'] = False
        if self.area_range[1] is not None:
            dm.loc[dm.area > self.area_range[1], 'fp'] = False

        return dm, am

    def compute_ap(self, det, anno, iou):
        """ This function does the actual AP computation for annotations and detections of a specific class_label. |br|
        This has been implemented as a separate function, so that you can inherit from this class and only overwrite this method and provide your own.

        Args:
            det (pd.DataFrame): brambox detection dataframe of only one class, which has already been matched
            anno (pd.DataFrame): brambox detection dataframe of only one class, which has already been matched
            iou (float): Intersection over Union values between 0 and 1
        """
        return stat.auc_interpolated(stat.pr(det, anno, iou, smooth=True))

    @property
    def mdAP(self):
        """ Compute and return all mdAP values, as wel as the mAP. """
        self.compute(
            'AP',
            'dAP_localisation',
            'dAP_classification',
            'dAP_both',
            'dAP_duplicate',
            'dAP_background',
            'dAP_missed',
            'dAP_fp',
            'dAP_fn',
        )

        return pd.Series({
            'mAP': self.cache['AP'].mean(skipna=True),
            'mdAP_localisation': self.cache['dAP_localisation'].mean(skipna=True),
            'mdAP_classification': self.cache['dAP_classification'].mean(skipna=True),
            'mdAP_both': self.cache['dAP_both'].mean(skipna=True),
            'mdAP_duplicate': self.cache['dAP_duplicate'].mean(skipna=True),
            'mdAP_background': self.cache['dAP_background'].mean(skipna=True),
            'mdAP_missed': self.cache['dAP_missed'].mean(skipna=True),
            'mdAP_fp': self.cache['dAP_fp'].mean(skipna=True),
            'mdAP_fn': self.cache['dAP_fn'].mean(skipna=True),
        })

    @property
    def AP(self):
        """ Per class average precision """
        self.compute('AP')
        return self.cache['AP'].copy()

    @property
    def dAP_localisation(self):
        """ Per class delta AP for localisation errors. """
        self.compute('dAP_localisation')
        return self.cache['dAP_localisation'].copy()

    @property
    def dAP_classification(self):
        """ Per class delta AP for classification errors. """
        self.compute('dAP_classification')
        return self.cache['dAP_classification'].copy()

    @property
    def dAP_both(self):
        """ Per class delta AP for both errors. """
        self.compute('dAP_both')
        return self.cache['dAP_both'].copy()

    @property
    def dAP_duplicate(self):
        """ Per class delta AP for duplicate errors. """
        self.compute('dAP_duplicate')
        return self.cache['dAP_duplicate'].copy()

    @property
    def dAP_background(self):
        """ Per class delta AP for background errors. """
        self.compute('dAP_background')
        return self.cache['dAP_background'].copy()

    @property
    def dAP_missed(self):
        """ Per class delta AP for missed errors. """
        self.compute('dAP_missed')
        return self.cache['dAP_missed'].copy()

    @property
    def dAP_fp(self):
        """ Per class delta AP for fp errors. """
        self.compute('dAP_fp')
        return self.cache['dAP_fp'].copy()

    @property
    def dAP_fn(self):
        """ Per class delta AP for fn errors. """
        self.compute('dAP_fn')
        return self.cache['dAP_fn'].copy()

    @property
    def errors(self):
        """
        Computes and returns the different error types. |br|
        This property returns your detection and annotation dataframe with an extra 'error' column,
        which explains the error type of that bounding box.
        If the bounding box is not an error, `pd.NA` is used.

        Return:
            tuple of 2 dataframes: (det, anno)
        """
        self.compute('error_detections', 'error_annotations')
        return self.cache['error_detections'].copy(), self.cache['error_annotations'].copy()


def find_errors(det, anno, pos_thresh, bg_thresh):
    det_idx = det.index
    anno_idx = anno.index
    det = det.reset_index(drop=True)
    anno = anno.reset_index(drop=True)

    dl = len(det_idx)
    anno_gt = anno[~anno.ignore]
    det_unmatched = det[~det.tp]

    # Create error df
    false_list = [False] * dl
    det_errors = pd.DataFrame({
        'localisation': false_list,
        'classification': false_list,
        'both': false_list,
        'duplicate': false_list,
        'background': false_list,
        'index': det_idx,
        'anno': np.nan,
    })

    # No regular ground truth annotations -> all background errors
    if len(anno_gt.index) == 0:
        det_errors['background'] = det.fp
        return det_errors

    # Compute IoU  [len(det) x len(anno_gt)]
    same_cls = util.np_col(det, 'class_label')[:, None] == util.np_col(anno_gt, 'class_label')[None, :]
    diff_cls = ~same_cls
    used_gt = anno_gt['detection'].notnull().values[None, :]

    iou = stat.coordinates.iou(det, anno_gt)
    iou_cls = iou * same_cls
    iou_nocls = iou * diff_cls
    iou_used_cls = iou_cls * used_gt

    # Find error type
    used_gt_loc, used_gt_cls = [], []
    for d in det_unmatched.itertuples():
        # Localisation
        idx = iou_cls[d.Index, :].argmax()
        if bg_thresh <= iou_cls[d.Index, idx] <= pos_thresh:
            if pd.notnull(anno.at[idx, 'detection']) or idx in used_gt_loc:
                det_errors.loc[d.Index, 'localisation'] = pd.NA
            else:
                det_errors.at[d.Index, 'localisation'] = True
                det_errors.at[d.Index, 'anno'] = anno_idx[idx]
                used_gt_loc.append(idx)
            continue

        # Class
        idx = iou_nocls[d.Index, :].argmax()
        if iou_nocls[d.Index, idx] >= pos_thresh:
            if pd.notnull(anno.at[idx, 'detection']) or idx in used_gt_cls:
                det_errors.loc[d.Index, 'classification'] = pd.NA
            else:
                det_errors.at[d.Index, 'classification'] = True
                det_errors.at[d.Index, 'anno'] = anno_idx[idx]
                used_gt_cls.append(idx)
            continue

        # Duplicate
        dup_iou = iou_used_cls[d.Index, :].max()
        if dup_iou >= pos_thresh:
            det_errors.at[d.Index, 'duplicate'] = True
            continue

        # Background
        bg_iou = iou[d.Index, :].max()
        if bg_iou <= bg_thresh:
            det_errors.at[d.Index, 'background'] = True
            continue

        # Both (Any other error is labeled as both)
        det_errors.at[d.Index, 'both'] = True

    return det_errors.astype({
        'localisation': 'boolean',
        'classification': 'boolean',
        'both': 'boolean',
        'duplicate': 'boolean',
        'background': 'boolean',
        'anno': 'Int64',
    })
