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
import wrapt

from typing import Callable, Any


def synchronized(f: Callable) -> Callable:
    """
    Decorator to acquire a service-level lock on gRPC endpoints. It internally uses wrapt.synchronized as the context manager
    for the service type so that all instances of the service share the same lock. Decorating a method (endpoint) in a
    service with `@synchronized` will make sure there is only one thread at any given time that can process requests for
    that endpoint. In other words, it will make sure that the decorated endpoint serves requests sequentially.

    For example: Decorating `FindAnswersForPassages` method in `ReadingComprehensionService` will make sure that the server
    can only process one request of type `FindAnswersForPassages` at any given time. So if the server is running with more
    than one worker threads, only one thread will process `FindAnswersForPassages` request at a given time regardless of
    the number of incoming requests to this endpoint. The remaining threads at that time can either process requests for
    other endpoints like health check (`Check`), server readiness (`Readiness`) etc. or wait the queue to process requests
    for `FindAnswersForPassages` endpoint.
    """
    @functools.wraps(f)
    def wrapper(service, *args, **kwargs) -> Any:
        logger = logging.getLogger(f.__name__)
        service_type = type(service)
        logger.debug("Acquiring service-level lock for {} endpoint in {}".format(f.__name__, service_type.__name__))
        with wrapt.synchronized(service_type):
            return f(service, *args, **kwargs)
    return wrapper
