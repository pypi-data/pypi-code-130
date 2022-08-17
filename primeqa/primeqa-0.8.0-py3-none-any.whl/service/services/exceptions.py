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

from grpc import ServicerContext, StatusCode, RpcError
from typing import Callable, Optional
from gaama.logging_tools.request_loggers import get_txn_id_from_log_context

from gaama.metrics.metrics import MetricsLogger


def _map_exception_to_grpc_code(ex: Exception, method: str, context: ServicerContext,
                                response_type: Optional[Callable] = None) -> StatusCode:
    context.set_details(str(ex))
    status_code = StatusCode.INTERNAL
    if isinstance(ex, InvalidArgumentException):
        status_code = StatusCode.INVALID_ARGUMENT
    elif isinstance(ex, RpcError):
        status_code = ex.code()
        context.set_details(ex.details())

    context.set_code(status_code)
    MetricsLogger.record_status_code(method, status_code, get_txn_id_from_log_context())
    if response_type:
        return response_type()


class InvalidArgumentException(ValueError):
    pass
