import time

def time_def(func):
    """
    This function is a decorator
    It will run the function the decorator is applied to, and return its result
    Printing the execution time

    eg.

    @time_it
    def time_max(A):
        return max(A)

    time_max([1,2,3,4,6]) # will return max value and print execution time

    """

    def inner_def(*args, **kwargs):
        # storing time before function execution
        begin = time.time()

        r = func(*args, **kwargs)

        # storing time after function execution
        end = time.time()
        print(f"{end - begin} time taken in : {func.__name__}" )

        return r

    return inner_def
