import time

def print_duration(method):
    """Prints out the runtime duration of a method in seconds

    .. code-block:: python
        :linenos:

        @print_duration
        def test_func():
            pass

        test_func()

    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%s cost %2.2f second(s)' % (method.__name__, te - ts))
        return result
    return timed
