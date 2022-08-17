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
import time
from typing import Callable, Any


def log_runtime(f: Callable) -> Callable:
    logger_name = f.__qualname__.rsplit('.', 1)[0]

    @functools.wraps(f)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = f(*args, **kwargs)
        runtime = time.time() - start_time

        logger = logging.getLogger(logger_name)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("{} ran in {:.6f} seconds".format(f.__name__, runtime))
        return result

    return wrapper
