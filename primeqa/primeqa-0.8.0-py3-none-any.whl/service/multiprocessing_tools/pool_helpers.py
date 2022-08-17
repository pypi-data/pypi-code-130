# Copyright 2022 The PrimeQA Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import logging
import multiprocessing
import signal
from multiprocessing.dummy import Pool as DummyPool
from multiprocessing.pool import Pool
from typing import Optional, Type, Callable
from weakref import finalize


def _get_pool_constructor(num_workers: int) -> Type[Pool]:
    if num_workers > 1:
        return Pool
    elif num_workers == 1:
        return DummyPool
    else:
        raise ValueError("Number of workers must be >= 1, not {}".format(num_workers))


def _no_op(*args):
    pass


def _ignore_sigint():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _cleanup_pool(pool: Pool, logger_name: Optional[str] = None):
    pool.terminate()
    logger = logging.getLogger(logger_name)
    logger.info("Terminated worker pool")


def create_pool_and_schedule_cleanup(owner: object, num_workers: int, initializer: Callable[..., None] = _no_op,
                                     initargs: tuple = tuple(), *args, **kwargs) -> Pool:
    """
    Create a pool (multiprocessing if more than one worker, else "dummy" i.e. thread) that is cleaned up when
    its owner is garbage collected.

    The Python documentation specifies that multiprocessing.Pool objects need to be cleaned up manually if
    not using them with in a context manager (with statement), and that it is not correct to rely on
    garbage collection to take care of the cleanup for you:
    https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.  Since these pools
    need to be alive for the duration of the server, using them in a context manager is not feasible.

    SIGINT (i.e. KeyboardInterrupt), which is used to signal the main server process to shutdown,
    is ignored in the worker processes.  This is done as the signal is propagated from the main process to the
    workers, which results in unhandled signals causing KeyboardInterrupt tracebacks for each worker process.

    :param object owner: when the owener is garbage collected the pool is cleaned up
    :param int num_workers: number of workers in the pool (if 1 use dummy pool else use multiprocessing pool)
    :param Callable[..., None] initializer: initializer function for the pool
    :param tuple initargs: initargs for the pool
    :param args: args for the pool constructor
    :param kwargs: kwargs for the pool constructor
    :return: pool of num_workers workers which will be cleaned up when owner is garbage collected
    :rtype: Pool
    """
    pool_constructor = _get_pool_constructor(num_workers)

    @functools.wraps(initializer)
    def initialize_pool(*_args):
        if pool_constructor == Pool:
            _ignore_sigint()
        initializer(*_args)

    logger_name = owner.__class__.__name__
    pool = None
    try:
        pool = pool_constructor(num_workers, initializer=initialize_pool, initargs=initargs, *args, **kwargs)

        # Neither the cleanup function, nor its (kw)args, can own any references to owner, or it will never be gc'd
        finalize(owner, _cleanup_pool, pool=pool, logger_name=logger_name)
    except Exception:
        if pool:
            _cleanup_pool(pool=pool, logger_name=logger_name)
        raise

    return pool
