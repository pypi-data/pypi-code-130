import numpy as np
import SimpleITK as sitk
import sitk_tools


def imsize_phys(image):

    
    """
    Returns the size of the image in mm.

    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    imsize : vector float
        Image Size in mm.

    """

    imsize = [ii * jj for ii, jj in zip(image.GetSize(), image.GetSpacing())]
    return imsize


def round_geometry(image, decimals=3):

    
    image.SetSpacing([round(ii, decimals) for ii in image.GetSpacing()])
    image.SetOrigin([round(ii, decimals) for ii in image.GetOrigin()])
    image.SetDirection([round(ii, decimals) for ii in image.GetDirection()])
    
    return image
    
    
    
    


def isempty(image):
    """
    Check if image contains all zero voxels.

    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    isempty : bool
        True if image is all zeros.

    """
    isempty = sitk_tools.sum(image) == 0
    return isempty

def center_phys(image):
    """
    Physical center of an SimpleIKT image.

    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    center : tuple
        Physical center of image.

    """
    centerI = np.asarray(image.GetSize())/2
    center = image.TransformContinuousIndexToPhysicalPoint(centerI.tolist())
    return center

def centerI(image):
    """
    Index center of an SimpleIKT image.

    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    center : tuple
        Physical center of image.
    """

    centerI = np.asarray(image.GetSize())/2
    return centerI.tolist()

def centroid(image, mask = None):
  """
    Centroid of SimpleIKT Image. If mask is specified, the centroid of the
    masked image is calculated.

    Parameters
    ----------
    image : sitk.Image

    mask : sitk.Image, optional
       The default is None.

    Raises
    ------
    ArithmeticError
        Is raised when mask is all zero.

    Returns
    -------
    None.

    """
  image = sitk.Cast(image, sitk.sitkFloat64)

  if mask and sitk_tools.sum(mask) == 0:
        raise ArithmeticError('Mask should not be empty!')

  if mask is not None:
      image = sitk.Mask(image, mask)

  imgrid = sitk_tools.grid(image)

  w = [g * image for g in imgrid]

  sum_im = sitk_tools.sum(image)

  centroid = []
  for wi in w:
      wi_sum = sitk_tools.sum(wi)
      centroid += [wi_sum/sum_im]

  return centroid

def find_phys(image, value = 1, mask = None):
    """
    Find physical coordinates of voxels with a specified value. If mask is
    specified only voxels inside the mask are considered.

    Parameters
    ----------
    image : sitk.Image

    value : numeric, optional
        Value to find. The default is 1.
    mask : sitk.Image, optional
        The default is None.


    Returns
    -------
    list
        list of physical points for voxels that have the specified value.

    """
    index = find(image, value=value, mask=mask)

    loc = [image.TransformContinuousIndexToPhysicalPoint(i) for i in index]
    return loc


def find(image, value = 1, mask = None):
    """
    Find indices of voxels with a specified value. If mask is
    specified only voxels inside the mask are considered.

    Parameters
    ----------
    image : sitk.Image

    value : numeric, optional
        Value to find. The default is 1.
    mask : sitk.Image, optional
        The default is None.


    Returns
    -------
    list
        list of indices for voxels that have the specified value.
    """

    if value == 0 and mask:
        # mask are used by multiplication everyging outside mask is 0 asw ell
        raise NotImplementedError('When using mask value must be <> 0')
    if mask is not None:
        image = sitk.Mask(image, mask)

    im_array = sitk.GetArrayFromImage(image)

    if value == 'min':
        value = np.min(im_array)
    if value == 'max':
        value = np.max(im_array)

    index = np.where(im_array == value)

    z, y, x  = ([*index[0]], [*index[1]], [*index[2]])

    x = [int(xi) for xi in x]
    y = [int(yi) for yi in y]
    z = [int(zi) for zi in z]

    return tuple(zip(x, y, z))


def voxel_volume_mm3(image):
    """
    Volume of a voxel for image in mm3

    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    float
        Volume of a voxel for image in mm3.

    """
    return np.prod(image.GetSpacing())

def voxel_volume_ml(image):
    """
    Volume of a voxel for image in ml
    Parameters
    ----------
    image : sitk.Image


    Returns
    -------
    float
        Volume of a voxel for image in ml.

    """
    return voxel_volume_mm3(image) * 1e-3

# def volume_mm3(image):
#     return voxel_volume_mm3(image) * voxel_count(image)

# def volume_ml(image):
#     return voxel_volume_ml(image) * voxel_count(image)

# def voxel_count(image):
#     count = sitk_tools.sum(image>0)
#     return count

def gaussian_filter(image, FWHM=None):
    """
    Apply a Gaussian filter to an image. Specify the kernel size by Full
    Width Half Max (FWHM) in mm.

    Parameters
    ----------
    image : sitk.Image

    FWHM : float, optional


    Returns
    -------
    image : sitk.Image
        Filtered image.

    """
    if FWHM:
        sigma = FWHM/(2*np.sqrt(2*np.log(2)))
        image = sitk.RecursiveGaussian(image, sigma=sigma)
    return image


# def cast(image, pixid):

#     if image.GetPixelIDValue() != pixid:
#         image = sitk.Cast(image, pixid)
#     return image



def product(image1, image2):
    """
    Voxel wise product of two images. If images do not have same PixelID. The
    image with the lower PixelID will be casted to the higher PixelID prior to
    multiplication. E.g (sitk.sikUInt8, sitk.sitkFloat32) --> sitk.sitkFloat32

    Parameters
    ----------
    image1 : sitk.Image

    image2 : sitk.Image


    Returns
    -------
    image


    """
    type1 = image1.GetPixelIDValue()
    type2 = image2.GetPixelIDValue()

    if type1 != type2:
        maxtype = max((type1, type2))
        if type1 != maxtype:
            image1 = sitk.Cast(image1, maxtype)
        if type2 != maxtype:
            image2 = sitk.Cast(image2, maxtype)

    return image1 * image2




def extract_frame(image, index=0, axis=3):
    # To Do write doc
    if axis >= image.GetDimension():
       msg = 'Cannot get a slice along axis {0} for an image with dimension {1}'
       raise ValueError(msg.format(axis, image.GetDimension()))


    multi_index = [0] * image.GetDimension()
    multi_index[axis] = index
    new_size = list(image.GetSize())
    new_size[axis] = 0
    frame = sitk.Extract(image, new_size, multi_index)
    return frame

def apply_mask(image, mask, mask_value=0, outside_value=0):
    """
    Wrapper for sitk.Mask.

    Parameters
    ----------
    image : sitk.Image
    mask : sitk.Image
        sitk Image representing a (label) mask.
    mask_value : float, optional
        The default is 0.
    outside_value : float, optional
        The default is 0.

    Returns
    -------
    sitk.Image
        Masked Image.

    """
    return sitk.Mask(image, mask, outsideValue=outside_value,
                     maskingValue=mask_value)

def zeros_like_image(image):
    """
    Similar to numpy.zeros. Returns an sitk Image with all zeros occupying the
    exact same space as image and has same type as image.

    Parameters
    ----------
    image : sitk.Image

    Returns
    -------
    image : sitk.Image
        Image with all zeros.

    """
    zero_image = sitk.Image(image.GetSize(), sitk.sitkUInt8)
    zero_image.CopyInformation(image)
    return zero_image

def ones_like_image(image):
    """
    Similar to numpy.ones. Returns an sitk Image with all ones occupying the
    exact same space as image and has same type as image.

    Parameters
    ----------
    image : sitk.Image

    Returns
    -------
    image : sitk.Image
        Image with all ones.

    """
    return zeros_like_image(image) + 1

def random_like_image(image):
    """
    Similar to numpy.random.rand. Returns an sitk Image with all random values
    between 0 and 1. Output occupies the exact same space as image and has
    the same type as image.

    Parameters
    ----------
    image : sitk.Image

    Returns
    -------
    image : sitk.Image
        Image with all random values.

    """
    size = image.GetSize()[::-1]

    np_random_image = np.random.rand(*size)

    random_image = sitk.GetImageFromArray(np_random_image)

    random_image.CopyInformation(image)

    return random_image




def grid(image):
    """ Similar to numpy.meshgrid using sitk. Grids will be in world (physical)
    space. Returns three sitk images, X, Y an Z. Each voxel in the image will
    be equal to their corresponding coordinate."""

    imsize = image.GetSize()
    spacing = image.GetSpacing()
    origin = image.GetOrigin()
    direction = image.GetDirection()
    grid = sitk.PhysicalPointSource(sitk.sitkVectorFloat64, imsize,
                                    origin, spacing,  direction)

    dim =  image.GetDimension()
    grid = [sitk.VectorIndexSelectionCast(grid, i) \
                         for i in range(0, dim)]

    for gi in grid:
        gi.CopyInformation(image)
    return grid

def crop_phys(image, lower_bound=None, upper_bound=None):
    """
    Crop image by Index. Boundaries are adjusted so that they don't exceed
    the physical space of the image.


    image: sitk.Image or numpy.ndarray
    lower_bound: [x1, y1, z1]
    upper_bound: [x2, y2, z2]
    """

    if lower_bound:
        lower_boundI = image.TransformPhysicalPointToIndex(lower_bound)
    if upper_bound:
        upper_boundI = image.TransformPhysicalPointToIndex(upper_bound)
    cropped = crop(image, lower_bound=lower_boundI, upper_bound=upper_boundI)
    return cropped

def crop(image, lower_bound=None, upper_bound=None):
    """
    Crop image by Index. Boundaries are adjusted so that they don't exceed
    the image size

    image: sitk.Image or numpy.ndarray
    lower_bound: [x1, y1, z1]
    upper_bound: [x2, y2, z2]
    """

    imsize = image.GetSize()

    if lower_bound is None:
        lower_bound = (0, 0, 0)

    # image indices may not be negative
    lower_bound = [max(0, li) for li in lower_bound]

    if upper_bound is None:
        upper_bound = imsize

    # image indices may not exceed the image size
    upper_bound = [min(mi, ui) for mi, ui in zip(imsize, upper_bound)]

    upper_bound = [mi - ui for mi, ui in zip(imsize, upper_bound)]

    image = sitk.Crop(image, lower_bound, upper_bound)

    return image

def crop_by_mask(image, mask, margin=0):
    """
    Crop an image by a mask. The image extends to the largest span of ones
    in the mask in all dimensions. If margin is specified, an additional
    border in mm is included aswell

    Parameters
    ----------
    image : sitk.Image

    mask : sitk.Image
[]
    margin : float, optional
        Add border to cropped image. The default is 0.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    crop_image : TYPE
        DESCRIPTION.

    """
    voxels = sitk_tools.find_phys(mask)

    if len(voxels) == 0:
        raise ValueError('empty region specified!')


    x, y, z = zip(*voxels)

    minx, miny, minz = (min(x), min(y), min(z))
    maxx, maxy, maxz = (max(x), max(y), max(z))

    minx -= margin
    maxx += margin
    miny -= margin
    maxy += margin
    minz -= margin
    maxz += margin

    crop_image = crop_phys(image, lower_bound=(minx, miny, minz),
                           upper_bound=(maxx, maxy, maxz))

    return crop_image


def crop_axis(image, lower, upper, axis=0):
    """
    Crop an image along a single axis by lower and upper indices.

    Parameters
    ----------
    image : sitk.Image

    lower : int
        lower index.
    upper : int
        upper index.
    axis : int, optional
        Axis that will be cropped. The default is 0.

    Returns
    -------
    sitk.Image
        cropped image.

    """

    print(lower, upper)

    lower_bound = [0, 0, 0]
    upper_bound = list(image.GetSize())
    lower_bound[axis] = lower
    upper_bound[axis] = upper
    return crop(image, lower_bound, upper_bound)

def crop_axis_phys(image, lower, upper, axis=0):
    """
    Crop an image along a single axis by lower and upper physical units.

    Parameters
    ----------
    image : sitk.Image

    lower : float
        lower border in mm.
    upper : int
        upper border in mm.
    axis : int, optional
        Axis that will be cropped. The default is 0.

    Returns
    -------
    sitk.Image
        cropped image.

    """

    lower_bound = list(image.TransformIndexToPhysicalPoint((0, 0, 0)))
    upper_bound = list(image.TransformIndexToPhysicalPoint(image.GetSize()))
    lower_bound[axis] = lower
    upper_bound[axis] = upper
    return crop_phys(image, lower_bound, upper_bound)


def cast_same_type(*images, pixelidvalue=None):
    """
    Cast a list of images the same pixelidvalue / datatype. If datatype is 
    None the highest pixelidvalue will be automatically selected.

    Parameters
    ----------
    images : list
        list of sitk images.
    pixelidvalue : int, optional
        SimpleITK PixelIDValue. The default is None.

    Returns
    -------
    images : list of sitk images
       

    """
    if len(images) == 1 and isinstance(images[0], (list, tuple)):
        images = images[0]
    
    if pixelidvalue is None:
        pixelidvalues = [image.GetPixelIDValue() for image in images]
        pixelidvalue = max(pixelidvalues)
    
    same_type_images = []
    for image in images:
        if image is None:
            same_type_images += [None]
        else:
            same_type_images += [sitk.Cast(image, pixelidvalue)]
    
    return same_type_images
        



def rotate(image, center=None, angle=None,
           interpolator=sitk.sitkNearestNeighbor,
           default_pixel_value=0):
    """
    Rotate a 2D or 2D image around a center for a specified angle. If the
    image is 3D the angle must be an Euler angle represented by a 3-vector.

    Parameters
    ----------
    image : sitk.Image

    center : physical point, optional
        Physical point around which the image is rotated. If None, center is
        set to the center of the image.
    angle : float or Euler angle, optional
        Angle to rotate.
    interpolator : sitk interpolator, optional
        Interpolator used for resampling the image. The default is
        sitk.sitkNearestNeighbor.
    default_pixel_value: Value for voxels that were outside of the image prior
    to rotation.

    Returns
    -------
    rimage : sitk.Image
        rotated image that occupies the same physical space as imge

    """


    if center is None:
        center = center_phys(image)
    if angle is None:
        angle = [np.pi/2] * len(image.GetSize())
    if interpolator is None:
        interpolator = sitk.sitkNearestNeighbor

    if all([ai==0 for ai in angle]): return image


    if image.GetDimension() == 2:

      transform = sitk.Euler2DTransform()
      transform.SetAngle(angle)
      transform.SetTranslation(center)

    elif image.GetDimension() == 3:

      parameters = (*angle,0,0,0)
      transform = sitk.Euler3DTransform()
      transform.SetParameters(parameters)
      transform.SetCenter(center)

    rimage = apply_sitk_transform(image=image, ref_image=image,
                                  transform=transform,
                                  default_pixel_value=default_pixel_value,
                                  interpolator=interpolator)

    #rimage = sitk.Resample(image, transform, interpolator)
    return rimage

def match_pixel_id(image, ref_image):
    """
    Cast pixel id of image to the pixel id of ref_image

    Parameters
    ----------
    image : sitk.Image

    ref_image : sitk.Image
        DESCRIPTION.

    Returns
    -------
    pimage : Casted Image

    """
    if ref_image.GetPixelID() != image.GetPixelID():
        print('casting')
        image = sitk.Cast(image, ref_image.GetPixelID())
    return image

def apply_sitk_transform(image = None,
                         ref_image= None,
                         transform = None,
                         default_pixel_value = -1000,
                         interpolator=sitk.sitkBSpline):
    """
    Apply a transform to an SimpleITK image

    Parameters
    ----------
    image: sitk.Image
        image to apply transform to.
    ref_image: sitk.Image
        match resampled image to the physical space of this image.
    default_pixel_value: float, optional
        Value for voxels that were outside of the image prior to rotation.
        The Default is -1000
    interpolator : sitk interpolator, optional
        Interpolator used for resampling the image.
        The default is sitk.sitkBSpline.

    Returns
    -------
    rimage. sitk.Image

    Resampled image after transformation.


    """

    if type(image) is str:
        image = sitk.ReadImage(image)
    if type(ref_image) is str:
        image = sitk.ReadImage(image)
        
    if isinstance(transform, (tuple, list)):
        apply_transform = sitk.CompositeTransform(3)
        for T in transform:
            apply_transform.AddTransform(T)
    elif isinstance(transform, sitk.Transform):
        apply_transform = transform
    else:
        raise TypeError(f'Expected sikt Transform got {type(transform)}')
        
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(interpolator)
    if ref_image is not None:
        pix_id=ref_image.GetPixelIDValue()
    else:
        pix_id = image.GetPixelIDValue()
        
    resampler.SetOutputPixelType(pix_id)
    resampler.SetTransform(apply_transform)
    if ref_image:
        resampler.SetReferenceImage(ref_image)
    resampler.SetDefaultPixelValue(default_pixel_value)

    rimage = resampler.Execute(image)


    return rimage

def resample_to_image(image, ref_image, default_pixel_value=0,
                      interpolator=sitk.sitkLinear, copy_pixel_id=False):
    """
    Resample an image to match the physical space of a reference image. Image
    is automatically cropped. Voxels that lie outside the physical space of
    image are assigned the default_pixel_value. If copy_pixel_id is True. THe
    pixel_id of the output image is also matched to the ref_image by casting.

    Parameters
    ----------
    image : sitk.Image

    ref_image : sikt.Image

    default_pixel_value : int, optional
        Default value for voxels outside the physicial bounds of image.
        The default is 0.
    interpolator : int, optional
        SimpleIKT interpolator. The default is sitk.sitkLinear.
    copy_pixel_id : bool, optional
        Match pixel id as well. The default is False.

    Returns
    -------
    rimage : sitk.Image
        Resampled image that matches the physical space of ref_image.

    """



    ndim = image.GetDimension()
    dummy_T = sitk.TranslationTransform(ndim, [0]*ndim)
    rimage = sitk.Resample(image, ref_image, dummy_T, interpolator,
                           default_pixel_value)

    if copy_pixel_id:
        rimage = match_pixel_id(rimage, ref_image)
    return rimage

def interpolate(image, new_pixel_size=(4,4,4),
                interpolator=sitk.sitkLinear):
    """
    Interpolate an image to a specified pixel/voxel size.

    Parameters
    ----------
    sitk_image : sitk.Image

    new_pixel_size : 2 or 3 elements, optional
        New pixel / voxel size for interpolated image. The default is (4,4,4).
    interpolator : int, optional
        Simple ITK interpolator. The default is sitk.sitkLinear.

    Returns
    -------
    new_image : sitk.Image
        Interpolated Image.

    """

    ndim = image.GetDimension()
    new_pixel_size = np.asarray(new_pixel_size, dtype=float)

    # create an empty image that has the desired pixel size
    T = image.TransformIndexToPhysicalPoint
    llb = np.asarray(T([0]*ndim))
    urt = np.asarray(T(image.GetSize()))
    span = urt - llb

    # number of pixels in each dimension
    n = [int(ni) for ni in np.floor(span/new_pixel_size)]

    # make sitk
    template_image = sitk.Image(n, image.GetPixelID())
    template_image.SetOrigin(image.GetOrigin())
    template_image.SetSpacing(tuple(new_pixel_size))
    template_image.SetDirection(image.GetDirection())

    # sitk resample needs a transform, use a translation transform with 0
    # translation
    dummy_T = sitk.TranslationTransform(ndim, [0]*ndim)

    # do interpolation/resampling
    new_image = sitk.Resample(image, template_image, dummy_T,
                              interpolator)

    return new_image




def same_space(*images):
    """
    Test if images occupy the exact same physical space

    Parameters
    ----------
    *images : list of sitk.Image
        Two or more sitk images.

    Returns
    -------
    same_space : bool
        True if images are in the same space.

    """
    if None in images:
        return False
    
    images = cast_same_type(*images)
    
        
    try:
        for image in images:
            _ = images[0] - image
        same_space = True
    except:
        same_space = False
    return same_space

        
def deep_equal(*images, tolerance=1E-6, allow_different_pixel_id=True):
    """
    Test if images have the same pixel value type
    Test if images occupy the exact same physical space
    Test if all pixel values are the same

    Parameters
    ----------
    *images : list of sitk.Image
        Two or more sitk images.

    Returns
    -------
    same_space : bool
        True if images are in the same space.

    """

    pixel_ids = [image.GetPixelID() for image in images]
    
    if not allow_different_pixel_id:
        if len(set(pixel_ids)) > 1:
            return False
    else:
        images = cast_same_type(*images)
    
    images = [round_geometry(image) for image in images]
    
    if not same_space(*images):
        return False
    
    
    abs_tolerance = min([sitk_tools.sum(sitk.Abs(ii)) for ii in images]) * tolerance
    for image in images[1:]:
        diff = sitk_tools.max(sitk.Abs(images[0] - image)) / sitk_tools.max(sitk.Abs(images[0] + image))
        print(diff)
        if diff > abs_tolerance:
            return False
    
    return True

def safe_divide(image1, image2):
    """
    Divide one image by onother image. If images contain integer values, 
    the result is rounded and returned as integer values.
    
    Parameters
    ----------
    *images : list of sitk.Image
        Two or more sitk images.

    Returns
    -------
    image : sitk.Image
        result after (voxel-wise) division

    """

    im1, im2 = sitk_tools.cast_same_type(image1, image2)
         
    if im1.GetPixelID() >= 8:
        image = im1 / im2
    else:
        image = sitk.Cast(image1, 8) / sitk.Cast(image2, 8)
         
    if image1.GetPixelID() < 8:
        image = sitk.Cast(sitk.Round(image), image1.GetPixelID())
         
    return image
         
 
def join_images(*images, default_pixel_value=0):
    """
    Join images that do not occupy the same physical space. Images are
    resampled to the smallest physical space that would contain all images.
    
    If images (partly) overlap, the mean voxel value is taken.
    
    
    Parameters
    ----------
    *images : list of sitk.Image
        Two or more sitk images.

    Returns
    -------
    image : sitk.Image
        the result after joining all images

    """
    
    images = cast_same_type(*images)
    
    
    if len(images) > 2:
        joined_image = join_images(images[0], images[1], 
                                   default_pixel_value=default_pixel_value)
        
        return join_images(joined_image, *images[2:])
    
    image1, image2 = images
    
    
    pixel_size1 = image1.GetSpacing()
    pixel_size2 = image2.GetSpacing()
    
    size1 = image1.GetSize()
    size2 = image2.GetSize()
    
    origin1 = image1.GetOrigin()
    origin2 = image2.GetOrigin()
    
    span1 = [oi + szi*spi for oi, szi, spi in zip(origin1, pixel_size1, size1)]
    span2 = [oi + szi*spi for oi, szi, spi in zip(origin2, pixel_size2, size2)]
    
    if not all([p1==p2 for p1, p2 in zip(pixel_size1, pixel_size2)]):
        raise ValueError('Images must have same pixel spacing!')
        
    if not all([d1==d2] for d1, d2 in zip(image1.GetDirection(),
                                          image2.GetDirection())):
        raise ValueError('Images must have same direction!')
    
    if not image1.GetPixelID() == image2.GetPixelID():
        raise ValueError('Images must have same PixelID!')
        
    origin = [min(xi) for xi in zip(origin1, origin2)]
    span = [max(xi) for xi in zip(span1, span2)]
    
    nvoxels = [int(round((si-oi)/pi))\
               for oi, si, pi in zip(origin, span, pixel_size1)]
    
    
    # dummy volume for the space that contains both images
    empty_joined_image = sitk.Image(*nvoxels, image1.GetPixelID())
    empty_joined_image.SetSpacing(pixel_size1)
    empty_joined_image.SetOrigin(origin)
    empty_joined_image.SetDirection(image1.GetDirection())
    
    # resample image1 and image2 to the joined volume and then add
    joined_image1 = resample_to_image(image1, empty_joined_image, 
                                      default_pixel_value=default_pixel_value)
    
    joined_image2 = resample_to_image(image2, empty_joined_image, 
                                      default_pixel_value=default_pixel_value)
    
    joined_image = joined_image1 + joined_image2
    
    
    # calculate the overlap of both images
    overlap1 = ones_like_image(image1)
    overlap2 = ones_like_image(image2)
    
    overlap1 = resample_to_image(overlap1, empty_joined_image)
    overlap2 = resample_to_image(overlap2, empty_joined_image)
    
    temp_overlap = overlap1 + overlap2
    
    # avoid zero division
    overlap_array = sitk.GetArrayFromImage(temp_overlap)
    overlap_array[overlap_array==0] = 1
    overlap = sitk.GetImageFromArray(overlap_array)
    overlap.CopyInformation(temp_overlap)
    
    # divides overlapping voxels by two, taking the mean
    joined_image = safe_divide(joined_image, overlap)
    return joined_image



def axis_range(image, axis=0):
    min_val = image.TransformIndexToPhysicalPoint((0, 0, 0))[axis]
    max_val = image.TransformIndexToPhysicalPoint(image.GetSize())[axis]
    if min_val > max_val:
        dummy = min_val
        min_val = max_val
        max_val = dummy
    return min_val, max_val


