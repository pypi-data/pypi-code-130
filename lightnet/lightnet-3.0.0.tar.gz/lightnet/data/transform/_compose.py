#
#   Lightnet Compose
#   Copyright EAVISE
#
import logging
from inspect import signature
from collections.abc import MutableSequence, Sequence
from lightnet._imports import tqdm

__all__ = ['Compose']
log = logging.getLogger(__name__)


class Compose(MutableSequence):
    """
    This is lightnet's own version of :class:`torchvision.transforms.Compose`, which has some extra bells and whistles. |br|
    The main advantage this class offers compared to the PyTorch version,
    is that this class will inspect the call signatures of the transformations and feed it the correct amount of arguments.

    Check out the `tutorial <../notes/02-A-basics.html#Pre-processing-pipeline>`_ for more information.

    Args:
        transforms (args): A list of all your transformations in the right order.

    Example:
        Variable number of arguments:

        >>> tf = ln.data.transform.Compose(
        ...     # 10,20,1  -> 30,21,11
        ...     lambda a,b,c: (a+b, b+c, c+a),
        ...     # 30,21    -> 630,1
        ...     lambda a,b: (a*b, round(a/b)),
        ...     # 630      -> 30
        ...     lambda a: a - 600,
        ...     # 30,1,11  -> 42
        ...     lambda a,b,c: a+b+c,
        ... )
        >>> tf(10, 20, 1)
        42

        Adding and removing transformations on the fly, using list methods:

        >>> tf = ln.data.transform.Compose(lambda n: n+1)
        >>> tf(10)  # 10+1
        11
        >>> # We can append using the append method
        >>> tf.append(lambda n: n*2)
        >>> tf(10)  # (10+1)*2
        22
        >>> # We can also add any iterable
        >>> tf += [lambda n: n**2, lambda n: n-1]
        >>> tf(10)  # (((10+1)*2)**2)-1
        483
        >>> # Inserting at a random place in the list
        >>> tf.insert(0, lambda n: n//2)
        >>> tf(10)  # ((((10//2)+1)*2)**2)-1
        143
        >>> # Removing an operator
        >>> del tf[2]
        >>> tf(10)  # (((10//2)+1)**2)-1
        35

        Combining pipelines:

        >>> pipeline1 = ln.data.transform.Compose(lambda n: n+1)
        >>> pipeline1(10)   # 10+1
        11
        >>> pipeline2 = ln.data.transform.Compose(lambda n: n-1)
        >>> pipeline2(10)   # 10-1
        9
        >>> pipeline = pipeline1 + pipeline2
        >>> pipeline(10)    # (10+1)-1
        10
    """
    def __init__(self, *transforms, enabled=True):
        # Old API, allow to define transforms as a list instead of *args
        if len(transforms) == 1 and isinstance(transforms[0], Sequence):
            transforms = transforms[0]

        self._tqdm = False
        self._transforms = [tf for tf in transforms if tf is not None]
        self._parameters = [self._introspect(tf) for tf in self._transforms]
        if isinstance(enabled, bool):
            self._enabled = [enabled for _ in self._transforms]
        else:
            self._enabled = list(enabled)[:len(self._transforms)]

    @property
    def tqdm(self):
        """ Returns whether the TQDM loading bar is enabled or not. """
        return bool(self._tqdm)

    @tqdm.setter
    def tqdm(self, value):
        """
        Enable or disable the TQDM loading bar.

        Args:
            value (str or bool): Whether to enable the TQDM loading bar and its name if you pass a string
        """
        if value and tqdm is None:
            raise ImportError('TQDM is not installed')
        self._tqdm = value if isinstance(value, str) else bool(value)

    @property
    def transform_names(self):
        """
        Returns the name of each transform. |br|

        Note:
            This function returns `tf.__name__` or `tf.__class__.__name__` if one of them exists.
            Ohterwise it returns None as name.

        Example:
            >>> pipeline = ln.data.transform.Compose(
            ...     ln.data.transform.RandomHSV(hue=1, saturation=2, value=2),
            ...     ln.data.transform.Letterbox(dimension=(416, 416)),
            ...     lambda img: img,
            ... )
            >>> print(pipeline)
            Compose [randomhsv, letterbox, <lambda>]
            >>> # Get all transform names
            >>> print(pipeline.transform_names)
            ('randomhsv', 'letterbox', '<lambda>')
            >>> # Access transforms by index
            >>> print(pipeline[1])
            Letterbox
            >>> # Access transforms by name (casing does not matter)
            >>> print(pipeline['randomhsv'])
            RandomHSV
            >>> # Check if a certain transformation is in this pipeline
            >>> 'Letterbox' in pipeline
            True
            >>> 'RandomCrop' in pipeline
            False
        """
        return tuple(ComposeSelector(self).names)

    @property
    def enabled(self):
        """
        This property allows you to view and change which transforms are enabled or not.

        Examples:
            >>> pipeline = ln.data.transform.Compose(
            ...     ln.data.transform.RandomHSV(hue=1, saturation=2, value=2),
            ...     ln.data.transform.Letterbox(dimension=(416, 416)),
            ... )
            >>> print(pipeline)
            Compose [randomhsv, letterbox]
            >>> # View enabled status
            >>> print(pipeline.enabled)
            [True, True]
            >>> # Set enabled status by index
            >>> pipeline.enabled[1] = False
            >>> pipeline.enabled[1]
            False
            >>> # Set enabled status by name
            >>> pipeline.enabled['randomhsv'] = False
            >>> pipeline.enabled
            [
              0 - randomhsv: False
              1 - letterbox: False
            ]
            >>> # Repr also shows disabled transforms
            >>> pipeline
            Compose [
              <disabled> RandomHSV (
                auto_recompute_params = True,
                hue = 1,
                saturation = 2,
                value = 2,
              )
              <disabled> Letterbox [MULTI-TF] (
                auto_recompute_params = True,
                dataset = None,
                dimension = (416, 416),
                fill_color = 0.5,
              )
            ]
        """
        return ComposeSelector(self, self._enabled)

    def __call__(self, *args, **kwargs):
        """
        Run your data through the transformation pipeline. |br|
        Note that this will only run through :func:`~lightnet.data.transform.Compose.enabled` items!

        Args:
            *args: The data to run through your transformation pipeline
            **kwargs: Keyword arguments that are added to the correct transformation functions

        Note:
            In order to use keyword arguments in your transform, the argument in your function should only be accessible as a keyword:

            >>> def transform(a, b, *, keyword_arg1, keyword_arg2=None):
            ...     pass
            >>> pipeline = ln.data.transform.Compose([transform])
            >>> pipeline(1, 2, keyword_arg1='bla', keyword_arg2=666)
        """
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]

        for tf, enabled, (num_args, keywords) in self:
            if enabled:
                if num_args < 0:
                    args = tf(*args, **{kw: kwargs[kw] for kw in keywords if kw in kwargs})
                    if not isinstance(args, tuple):
                        args = (args,)
                else:
                    tf_args = tf(*args[:num_args], **{kw: kwargs[kw] for kw in keywords if kw in kwargs})
                    if not isinstance(tf_args, tuple):
                        args = (tf_args,) + args[num_args:]
                    else:
                        args = tf_args + args[num_args:]

        # Unwrap args if only one item was given
        return args[0] if len(args) == 1 else args

    def __len__(self):
        """ Returns the number of transforms in this compose. """
        return len(self._transforms)

    def __iter__(self):
        """
        Iterate over the transforms. |br|
        This iterator returns `transform, enabled, (num_args, keyword_args)` for each of the transforms.
        If we could not deduce the number of arguments (eg. it takes a variable number of args), its value is set to -1.

        It you enabled :func:~lightnet.data.transform.Compose.tqdm`, it will be shown whilst iterating.
        """
        iter = zip(self._transforms, self._enabled, self._parameters)

        if self.tqdm:
            with tqdm(iter, total=len(self._transforms), desc=self._tqdm if isinstance(self._tqdm, str) else 'Compose') as tqdm_iter:
                for val in tqdm_iter:
                    name = ComposeSelector._get_name(val[0])
                    if name is not None:
                        tqdm_iter.set_postfix(tf=name)
                    yield val
                    tqdm_iter.set_postfix()
        else:
            yield from iter

    def __contains__(self, item):
        """
        Check if a class or function is in this compose list.

        Args:
            item (str or obj): Item to check for

        Note:
            If item is a string, we compare it against the :func:`~lightnet.data.transform.Compose.transform_names`.
            Otherwise, we simply check whether the value is in the list of transforms.
        """
        if isinstance(item, str):
            keys = tuple(n for n in ComposeSelector(self).names if n is not None)
            return item.lower() in keys
        else:
            return item in self._transforms

    def __getitem__(self, index):
        """
        Get a specific item from the transformation list.

        Args:
            index (str or int): Index of the transform

        Note:
            If index is a string, we compare it against the :func:`~lightnet.data.transform.Compose.transform_names`.
            If there are multiple transforms with the same name, we return the first match.
            Otherwise, we simply use the integer index to access the transform list.
        """
        return ComposeSelector(self, self._transforms)[index]

    def __setitem__(self, index, item):
        """
        Set a specific item from the transformation list.

        Args:
            index (str or int): Index of the transform
            item (callable): Your transform

        Note:
            If index is a string, we compare it against the :func:`~lightnet.data.transform.Compose.transform_names`.
            If there are multiple transforms with the same name, we return the first match.
            Otherwise, we simply use the integer index to access the transform list.
        """
        index = ComposeSelector(self)._get_index(index)
        self._transforms[index] = item
        self._parameters[index] = self._introspect(item)
        self._enabled[index] = True

    def __delitem__(self, index):
        """
        Delete a specific item from the transformation list.

        Args:
            index (str or int): Index of the transform

        Note:
            If index is a string, we compare it against the :func:`~lightnet.data.transform.Compose.transform_names`.
            If there are multiple transforms with the same name, we return the first match.
            Otherwise, we simply use the integer index to access the transform list.
        """
        index = ComposeSelector(self)._get_index(index)
        del self._transforms[index]
        del self._parameters[index]
        del self._enabled[index]

    def insert(self, index, item):
        """
        Insert an item at a specific place in the Compose list.

        Args:
            index (str or int): Index of the transform
            item (callable): Your transform

        Note:
            If index is a string, we compare it against the :func:`~lightnet.data.transform.Compose.transform_names`.
            If there are multiple transforms with the same name, we return the first match.
            Otherwise, we simply use the integer index to access the transform list.
        """
        index = ComposeSelector(self)._get_index(index)
        self._transforms.insert(index, item)
        self._parameters.insert(index, self._introspect(item))
        self._enabled.insert(index, True)

    def __add__(self, other):
        if isinstance(other, Compose):
            other_tf = other._transforms
            other_enabled = other._enabled
        else:
            other_tf = other
            other_enabled = [True] * len(other)

        return Compose(self._transforms + other_tf, enabled=self._enabled + other_enabled)

    def __radd__(self, other):
        if isinstance(other, Compose):
            other_tf = other._transforms
            other_enabled = other._enabled
        else:
            other_tf = other
            other_enabled = [True] * len(other)

        return Compose(other_tf + self._transforms, enabled=other_enabled + self._enabled)

    def __str__(self):
        tf = ', '.join(name if name is not None else 'Unnamed' for name in self.transform_names)
        return f'{self.__class__.__name__} [{tf}]'

    def __repr__(self):
        tf = (repr(tf).replace('\n', '\n  ') for tf in self._transforms)
        tf = (t if self._enabled[idx] else '<disabled> ' + t for idx, t in enumerate(tf))
        tf = '\n  '.join(tf)
        return f'{self.__class__.__name__} [\n  {tf}\n]'

    @staticmethod
    def _introspect(item):
        forward = getattr(item, 'forward', None)
        if callable(forward):
            item = forward

        try:
            params = signature(item).parameters
            kw = tuple(p.name for p in params.values() if p.kind == p.KEYWORD_ONLY)

            if any(p.kind == p.VAR_POSITIONAL for p in params.values()):
                return -1, kw
            else:
                return max(-1, len(params) - len(kw)), kw
        except (ValueError, TypeError):
            log.error('Could not introspect [%s], it will receive all arguments', item)
            return -1, ()


class ComposeSelector:
    """ Internal class to access Compose items by name or index. """
    __slots__ = ('names', 'access_list')

    def __init__(self, compose, access_list=None):
        self.names = (self._get_name(tf) for tf in compose._transforms)
        self.access_list = access_list

    def __getitem__(self, idx_or_name):
        idx = self._get_index(idx_or_name)
        return self.access_list[idx]

    def __setitem__(self, idx_or_name, value):
        idx = self._get_index(idx_or_name)
        self.access_list[idx] = value

    def __str__(self):
        return str(self.access_list)

    def __repr__(self):
        access_list = '\n  '.join(f'{idx} - {name}: {value}' for idx, (name, value) in enumerate(zip(self.names, self.access_list)))
        return '[\n  ' + access_list + '\n]'

    def _get_index(self, idx_or_name):
        if isinstance(idx_or_name, str):
            keys = tuple(n for n in self.names if n is not None)
            name = idx_or_name.lower()
            if name not in keys:
                raise KeyError(f'[{name}] not found in transforms')
            return keys.index(name)

        return idx_or_name

    @staticmethod
    def _get_name(item):
        name = getattr(item, '__name__', None)
        if name is None:
            name = getattr(item, '__class__', {'__name__': None}).__name__

        if name is not None:
            return name.lower()
        else:
            return None
