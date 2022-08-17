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
import sys
import time
from typing import Any, Callable

from gaama.logging_tools.request_log_factory import RequestLogFactory
from gaama.metrics.metrics import MetricsLogger


def add_log_context_to_logrecords(log_context):
    factory = logging.getLogRecordFactory()
    if isinstance(factory, RequestLogFactory):
        factory.set_log_context(log_context)
    else:
        logging.setLogRecordFactory(RequestLogFactory(factory, log_context))


def record_request(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(service, request, context, *args, **kwargs) -> Any:
        start = time.time()

        log_context = {}
        for (key, value) in context.invocation_metadata():
            log_context[key] = value

        logger = logging.getLogger(f.__name__)
        logging.getLogRecordFactory().set_log_context(log_context)
        logger.info("Attaching metadata {}".format(log_context))
        add_log_context_to_logrecords(log_context)

        request_size = request.ByteSize() if callable(getattr(request, "ByteSize", None)) else sys.getsizeof(request)
        logger.info("Received new request of type {} and size {} bytes".format(f.__name__, request_size))
        MetricsLogger.record_custom_metric(f.__name__ + "-request-size-bytes", request_size,
                                           get_txn_id_from_log_context())
        try:
            response = f(service, request, context, *args, **kwargs)
            response_size = response.ByteSize() if callable(getattr(response, "ByteSize", None)) \
                else sys.getsizeof(response)
            logger.info("Succeeded running {} and generated response of size {} bytes".format(f.__name__,
                                                                                                response_size))
        finally:
            time_taken = time.time() - start
            logger.info("Request of type {} processed in {:.6f} seconds".format(f.__name__, time_taken))
            MetricsLogger.record_response_time(f.__name__, time_taken, get_txn_id_from_log_context())
        return response

    return wrapper


def get_txn_id_from_log_context():
    try:
        txn_id = logging.getLogRecordFactory().thread_local.log_context.get('txn-id', "")
    except AttributeError:
        txn_id = ""
    return txn_id
