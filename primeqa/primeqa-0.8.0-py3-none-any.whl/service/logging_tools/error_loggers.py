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

from traceback import format_exc

import functools
import logging
from grpc import RpcError
from typing import Any, Callable, Optional


def run_with_error_mapper(error_mapper: Callable, response_type: Optional[Callable] = None) -> Callable:
    def outer_wrapper(f: Callable) -> Callable:
        @functools.wraps(f)
        def inner_wrapper(service, request, context, *args, **kwargs) -> Any:
            try:
                response = f(service, request, context, *args, **kwargs)
            except Exception as ex:
                logger = logging.getLogger(f.__name__)
                _ex_repr = isinstance(ex, RpcError) and format_grpc_error(ex) or repr(ex)
                logger.error("Caught exception: {}".format(_ex_repr))
                logging.debug('Exception trace: {}'.format(format_exc()))
                response = error_mapper(ex, f.__name__, context, response_type)
            return response

        return inner_wrapper
    return outer_wrapper


def format_grpc_error(ex: RpcError) -> str:
    return "gRPC error {}; {}".format(ex.code(), ex.details())
