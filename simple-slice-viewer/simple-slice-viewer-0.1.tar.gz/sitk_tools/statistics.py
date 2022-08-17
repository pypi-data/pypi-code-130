import SimpleITK as sitk
import numpy as np
import sitk_tools
import warnings

MEAN    = 'mean'
MAX     = 'max'
STD     = 'stdev'
MIN     = 'min'
COUNT   = 'count'
SUM     = 'sum'
COV     = 'cov'


def _statistics_filter(image, mask=None):

    if mask and np.sum(sitk.GetArrayFromImage(mask).flatten()) == 0:
        # force everything zero for empty mask!
        image = sitk_tools.zeros_like_image(image)
        mask = None
        warnings.warn('Empty mask encountered in statistic calculation!')
    if mask is None:
        mask = sitk_tools.ones_like_image(image)


    mask = sitk.Cast(mask, sitk.sitkUInt8)
    sitk_filter = sitk.LabelStatisticsImageFilter()
    sitk_filter.Execute(image, mask)

    return sitk_filter

def all_statistics(image, mask=None):
    """
    Return a dictionary with max, min, std, mean, sum and count

    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    dict
        dictionary with max, min, std, mean, sum and count.

    """

    statistics_filter = _statistics_filter(image, mask=mask)

    result = {}
    result[MAX]     =  statistics_filter.GetMaximum(1)
    result[MIN]     =  statistics_filter.GetMinimum(1)
    result[STD]     =  statistics_filter.GetSigma(1)
    result[MEAN]    =  statistics_filter.GetMean(1)
    result[SUM]     =  statistics_filter.GetSum(1)
    result[COUNT]   =  statistics_filter.GetCount(1)
    result[COV]     =  result[STD] / result[MEAN]

    if mask and sitk_tools.isempty(mask):
        result[COUNT] = 0

    return result

def min(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        minimum voxel value in image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return sitk_filter.GetMinimum(1)

def max(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        maximum voxel value in image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return sitk_filter.GetMaximum(1)

def mean(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        mean voxel value of image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return sitk_filter.GetMean(1)

def median(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        median voxel value of image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return sitk_filter.GetMedian(1)

def std(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        standard deviation of  voxel values in image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return  sitk_filter.GetSigma(1)

def sum(image, mask=None):
    """


    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image, optional
        Calculate value only for voxels where mask equals 1.

    Returns
    -------
    float
        sum of voxel values in image.

    """
    sitk_filter = _statistics_filter(image, mask = mask)
    return sitk_filter.GetSum(1)



