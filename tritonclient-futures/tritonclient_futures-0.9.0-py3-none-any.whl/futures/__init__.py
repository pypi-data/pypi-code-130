#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2022/08/16 02:47:30
@Author  :   nicholas wu 
@Version :   v1.0
@Contact :   nicholas_wu@aliyun.com
'''
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, TimeoutError
from concurrent.futures.thread import _WorkItem, BrokenThreadPool, _global_shutdown_lock, _shutdown
from tritonclient_futures.utils import raise_error, _raise_if_error
from tritonclient_futures.data.outputs import InferResult

class TritonFuture(Future):
    def __init__(self, verbose=False) -> None:
        self._verbose = verbose
        super().__init__()
        
    def get_result(self, timeout=None):
        """Get the results of the associated asynchronous inference.
        Parameters
        ----------
        block : bool
            If block is True, the function will wait till the
            corresponding response is received from the server.
            Default value is True.
        timeout : int
            The maximum wait time for the function. This setting is
            ignored if the block is set False. Default is None,
            which means the function will block indefinitely till
            the corresponding response is received.

        Returns
        -------
        InferResult
            The object holding the result of the async inference.

        Raises
        ------
        InferenceServerException
            If server fails to perform inference or failed to respond
            within specified timeout.
        """

        try:
            response = self.result(timeout=timeout)
        except TimeoutError as e:
            raise_error("failed to obtain inference response")

        _raise_if_error(response)
        return InferResult(response, self._verbose)

class TritonThreadPoolExecutor(ThreadPoolExecutor):
    def submit(self, fn, /, *args, **kwargs):
        with self._shutdown_lock, _global_shutdown_lock:
            if self._broken:
                raise BrokenThreadPool(self._broken)

            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')
            if _shutdown:
                raise RuntimeError('cannot schedule new futures after '
                                   'interpreter shutdown')

            f = TritonFuture()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            self._adjust_thread_count()
            return f