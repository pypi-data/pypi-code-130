import threading
from .process import process_until_completed, localdb, log
from .parallel_thread import track_availability

class Lean:

    def value_stream(value_stream, **decorator_kwargs):
        def wrapper(function):
            def applicator(*args, **function_kwargs):
                
                thread_1        =   threading.Thread(target=process_until_completed, args=(value_stream, function, decorator_kwargs, function_kwargs))
                start_thread_1  =   thread_1.start()

                thread_2        =   threading.Thread(target=track_availability)
                start_thread_2  =   thread_2.start()

            return applicator
        return wrapper

