#
#   Lightnet base pre-processing operators
#   Copyright EAVISE
#
import logging
import numpy as np
import torch
from lightnet._imports import Image

__all__ = ['ImageTransform', 'ImageAnnoTransform', 'AnnoTransform']
log = logging.getLogger(__name__)


class ImageTransform(torch.nn.Module):
    """ Base transform class for the pre-processing on images. |br|
    Any transformation that inherits from this transform, should -in theory- work with any of the following image formats:

    - Pillow :
      RGB or grayscale image from pillow
    - OpenCV :
      NumPy arrays with RGB or grayscale data ([H,W] or [H,W,C])
    - PyTorch :
      PyTorch tensors with RGB or grayscale data ([H,W] or [C,H,W] or [B,C,H,W])

    When implementing this class, you should overwrite the following methods:

    - :func:`~lightnet.data.transform.ImageTransform.__init__`:
      Initialize your transform, but dont forget to call `super().__init__()`
    - :func:`~lightnet.data.transform.ImageTransform.get_parameters` :
      Compute the necessary parameters for the transformation and store them on the object.
    - :func:`~lightnet.data.transform.ImageTransform._tf_pil` :
      Perform the transformation on a Pillow image
    - :func:`~lightnet.data.transform.ImageTransform._tf_cv` :
      Perform the transformation on an OpenCV NumPy image array
    - :func:`~lightnet.data.transform.ImageTransform._tf_torch` :
      Perform the transformation on a PyTorch image tensor

    Args:
        auto_recompute_params (bool, optional): Whether to automatically recompute augmentation parameters for each new image.

    Note:
        If you set `auto_recompute_params` to **False**, you need to call the :func:`~lightnet.data.transform.ImageTransform.get_parameters` method manually.
        This can be useful if you have multiple images which you want to augment in exactly the same manner (eg. frames of a video).

    Warning:
        These transformations are all subclasses from :class:`torch.nn.Module` in order to potentially allow tracing the entire pipeline.
        When implementing this class, you should thus call ``super().__init__()`` in order to intialize it properly.
    """
    def __init__(self, auto_recompute_params=True):
        super().__init__()
        self.auto_recompute_params = auto_recompute_params

    def forward(self, image):
        if isinstance(image, torch.Tensor):
            if self.auto_recompute_params:
                self.get_parameters(image.shape[-1], image.shape[-2])
            return self._tf_torch(image)
        elif isinstance(image, np.ndarray):
            if self.auto_recompute_params:
                self.get_parameters(image.shape[1], image.shape[0])
            return self._tf_cv(image)
        elif Image is not None and isinstance(image, Image.Image):
            if self.auto_recompute_params:
                self.get_parameters(*image.size)
            return self._tf_pil(image)
        elif image is not None:
            log.error('%s only works with <PIL images>, <OpenCV images> or <torch Tensors> [%s]', self.__class__.__name__, type(image))

        return image

    @classmethod
    @torch.jit.unused
    def apply(cls, image, **kwargs):
        """ Classmethod that applies the transformation once.

        .. deprecated:: 3.0.0
            |br| This method is deprecated. Simple create the object and run it: ``Transform(...)(image)``.

        Args:
            data: Data to transform (eg. image)
            **kwargs: Same arguments that are passed to the ``__init__`` function

        Returns:
            image: the transformed image
        """
        log.deprecated_once('Using the apply method on transforms is deprecated. Simply create the object and run it: `Transform(...)(image)`')
        obj = cls(**kwargs)
        return obj(image)

    @torch.jit.unused
    def get_parameters(self, img_width, img_height):
        """ This function gets the width and height of the image and should compute the necessary transformation parameters. |br|
        The reason for separating this is to reduce code duplication and to make sure that you would perform the exact same transformation, independent of which image format you choose.
        For the :class:`~lightnet.data.transform.ImageAnnoTransform` and :class:`~lightnet.data.transform.AnnoTransform` classes,
        it is very important to store all the details about a transformation on images, as you cannot get them afterwards.

        Implementations should store parameters of the transform on the object itself.
        If you care about pretty string/repr formats of your transformation objects, you should start the different parameter names with an underscore (otherwise they get shown in the repr).

        Args:
            img_width (int): The width of the image
            img_height (int): The height of the image
        """
        pass

    @torch.jit.unused
    def _tf_pil(self, img):
        """ Transformation for Pillow images.
        Implementations should overwrite this method and provide the correct transformation.
        The default implementation raises a ``NotImplementedError``.

        Args:
            img (PIL.Image): Image to transform

        Returns:
            any: Transformed image (most commonly a ``PIL.Image``, but you could return something else)
        """
        raise NotImplementedError('This transformation is not implemented for PIL images.')

    @torch.jit.unused
    def _tf_cv(self, img):
        """ Transformation for OpenCV NumPy images.
        Implementations should overwrite this method and provide the correct transformation.
        The default implementation raises a ``NotImplementedError``.

        Args:
            img (np.ndarray): Image to transform

        Returns:
            any: Transformed image (most commonly a ``np.ndarray``, but you could return something else)
        """
        raise NotImplementedError('This transformation is not implemented for OpenCV NumPy images.')

    @torch.jit.unused
    def _tf_torch(self, img):
        """ Transformation for PyTorch image tensors.
        Implementations should overwrite this method and provide the correct transformation.
        The default implementation raises a ``NotImplementedError``.

        Args:
            img (torch.Tensor): Image to transform

        Returns:
            any: Transformed image (most commonly a ``torch.Tensor``, but you could return something else)
        """
        raise NotImplementedError('This transformation is not implemented for PyTorch Tensor images.')

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        string = f'{self.__class__.__name__} (\n'

        for name in sorted(self.__dict__.keys()):
            if name.startswith('_') or name == 'training':
                continue
            val = self.__dict__[name]

            valrepr = repr(val)
            if '\n' in valrepr:
                valrepr = val.__class__.__name__

            string += f'  {name} = {valrepr},\n'

        return string + ')'


class ImageAnnoTransform(ImageTransform):
    """ Base transform class that for the joint pre-processing of images and annotations. |br|
    Any transformation that inherits from this transform, should -in theory- work with any of the following formats:

    - Pillow :
      RGB or grayscale image from pillow
    - OpenCV :
      NumPy arrays with RGB or grayscale data ([H,W] or [H,W,C])
    - PyTorch :
      PyTorch tensors with RGB or grayscale data ([H,W] or [C,H,W] or [B,C,H,W])
    - Pandas :
      Brambox pandas dataframes

    When implementing this class, you should overwrite the following methods:

    - :func:`~lightnet.data.transform.ImageTransform.get_parameters` :
      Compute the necessary parameters for the transformation and store them on the object.
    - :func:`~lightnet.data.transform.ImageTransform._tf_pil` :
      Perform the transformation on a Pillow image
    - :func:`~lightnet.data.transform.ImageTransform._tf_cv` :
      Perform the transformation on an OpenCV NumPy image array
    - :func:`~lightnet.data.transform.ImageTransform._tf_torch` :
      Perform the transformation on a PyTorch image tensor
    - :func:`~lightnet.data.transform.ImageTransform._tf_anno` :
      Perform the transformation on a brambox (annotation) dataframe

    Warning:
        These transformations are all subclasses from :class:`torch.nn.Module` in order to potentially allow tracing the entire pipeline.
        When implementing this class, you should thus call ``super().__init__()`` in order to intialize it properly.
    """
    def forward(self, image, anno=None):
        if isinstance(image, torch.Tensor):
            self.get_parameters(image.shape[-1], image.shape[-2])
            image = self._tf_torch(image)
        elif isinstance(image, np.ndarray):
            self.get_parameters(image.shape[1], image.shape[0])
            image = self._tf_cv(image)
        elif Image is not None and isinstance(image, Image.Image):
            self.get_parameters(*image.size)
            image = self._tf_pil(image)
        elif image is not None:
            log.error('%s only works with <PIL images>, <OpenCV images> or <torch Tensors> [%s]', self.__class__.__name__, type(image))

        if anno is None:
            return image
        else:
            anno = self._tf_anno(anno.copy())
            return image, anno

    @classmethod
    def apply(cls, image, anno=None, **kwargs):
        """ Classmethod that applies the transformation once.

        .. deprecated:: 3.0.0
            |br| This method is deprecated. Simple create the object and run it: ``Transform(...)(image, anno)``.

        Args:
            image: Image to transform
            anno (optional): ground truth for that image; Default **None**
            **kwargs: Same arguments that are passed to the ``__init__`` function

        Returns:
            tuple: Tuple containing the transformed image and annotation
        """
        log.deprecated_once('Using the apply method on transforms is deprecated. Simply create the object and run it: `Transform(...)(image, anno)`')
        obj = cls(**kwargs)
        return obj(image, anno)

    def _tf_anno(self, anno):
        """ Transformation for Brambox dataframes.
        Implementations should overwrite this method and provide the correct transformation.
        The default implementation raises a ``NotImplementedError``.

        Args:
            anno (pd.DataFrame): Annotations to transform

        Returns:
            any: Transformed annotations (most commonly a ``pd.DataFrame``, but you could return something else)

        Note:
            The dataframe gets copied before passing it to this function,
            so you can freely modify the dataframe, without worrying about overwriting the original data.
        """
        raise NotImplementedError('This transformation is not implemented for brambox dataframes.')

    def __repr__(self):
        string = f'{self.__class__.__name__} [MULTI-TF] (\n'

        for name in sorted(self.__dict__.keys()):
            if name.startswith('_') or name == 'training':
                continue
            val = self.__dict__[name]

            valrepr = repr(val)
            if '\n' in valrepr:
                valrepr = val.__class__.__name__

            string += f'  {name} = {valrepr},\n'

        return string + ')'


class AnnoTransform(ImageAnnoTransform):
    """ Base transform class for the pre-processing on annotations. |br|

    When implementing this class, you should overwrite the following methods:

    - :func:`~lightnet.data.transform.ImageTransform.get_parameters` :
      Compute the necessary parameters for the transformation and store them on the object.
      This method is optional and depends on whether your transformation requires parameters computed from the image size.
    - :func:`~lightnet.data.transform.ImageTransform._tf_anno` :
      Perform the transformation on a brambox (annotation) dataframe

    Warning:
       These transformations are all subclasses from :class:`torch.nn.Module` in order to potentially allow tracing the entire pipeline. |br|
        However, this class can be used straight away and thus already has a default init function that takes a callable.

        This does mean that you cannot simply call ``super().__init__()``, when implementing this class.
        If you inherit from this class, you should write ``super(AnnoTransform, self).__init__()`` to call the :class:`~torch.nn.Module` initializer.
    """
    def __init__(self, fn, *, auto_recompute_params=True, **kwargs):
        """ Instead of building your own transform with this class,
        you can also simply pass a callable object (function, lambda, etc.) as the first argument of the init function.
        The resulting object will then use this function to transform your annotation data.

        Args:
            fn (callable): Transformation function for your annotations.
            auto_recompute_params (bool, optional): Whether to automatically recompute augmentation parameters for each new image.
            kwargs: Extra arguments passed on to the transformation function.

        Note:
            If your function returns ``None``, we simply return the annotation dataframe.
            This allows your to perform inplace modifications.

        Examples:
            >>> # We create a transformation that only returns the non-ignored annotations
            >>> tf = ln.data.transform.AnnoTransform(lambda df: df[~df.ignore])     # doctest: +SKIP

            >>> # Inplace modifications, by returning nothing from the function
            >>> def transform(df):
            ...     df['x_top_left'] += 10
            ...     df['y_top_left'] += 10
            >>> tf = ln.data.transform.AnnoTransform(transform)     # doctest: +SKIP
        """
        super().__init__(auto_recompute_params=auto_recompute_params)
        self.fn = fn
        self.kwargs = kwargs

    def _tf_pil(self, img):
        """ Simply returns the image. """
        return img

    def _tf_cv(self, img):
        """ Simply returns the image. """
        return img

    def _tf_torch(self, img):
        """ Simply returns the image. """
        return img

    def _tf_anno(self, anno):
        """ Transformation for Brambox dataframes.
        Implementations should overwrite this method and provide the correct transformation.
        The default implementation runs ``self.fn`` on the dataframe if it exists (see :func:`~lightnet.data.trnasform.AnnoTransform.__init__`)
        or raises a ``NotImplementedError``.

        Args:
            anno (pd.DataFrame): Annotations to transform

        Returns:
            any: Transformed annotations (most commonly a ``pd.DataFrame``, but you could return something else)

        Note:
            The dataframe gets copied before passing it to this function,
            so you can freely modify the dataframe, without worrying about overwriting the original data.
        """
        fn = getattr(self, 'fn', None)
        if fn is not None:
            retval = fn(anno, **self.kwargs)

            # Allow inplace modification by the function -> return the input annotations
            if retval is None:
                return anno
            else:
                return retval
        else:
            raise NotImplementedError('This transformation is not implemented for brambox dataframes.')

    @property
    def __name__(self):
        """ Return a more suitable name. """
        fn = getattr(self, 'fn', None)
        if fn is not None:
            name = getattr(fn, '__name__', None)
            if name is None:
                name = getattr(fn, '__class__', {'__name__': None}).__name__
            if name is not None:
                return name.lower()

        return self.__class__.__name__
