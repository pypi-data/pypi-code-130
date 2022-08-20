import random

def random_digits(length):
    """Get random digits at given length

    .. code-block:: python
        :linenos:

        random_digits(4)
        >>> '2359'
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))