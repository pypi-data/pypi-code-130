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

import logging

from statsd import StatsClient

from primeqa.service.configurations import Settings
from grpc import StatusCode


class MetricsLogger(object):
    """
    Provides a wrapper for Statsd Metrics Logging
    """

    _STATSD_COUNT_PREFIX = "count."
    _STATSD_TIME_PREFIX = "time."

    # global statsd client (defined as a static class variable), should be initialized once
    _statsd_client = None
    _logger = None
    _txn_ids_to_exclude = set()

    @classmethod
    def initialize_statsd_client(cls, config: Settings):
        cls._logger = logging.getLogger(cls.__name__)
        cls._txn_ids_to_exclude |= config.exclude_metrics_for_txn_ids
        if config.submit_metrics:
            cls._statsd_client = StatsClient(host=config.statsd_host, port=config.statsd_port, prefix=config.statsd_prefix)
            cls._logger.info("Intialized Statsd client")

    @classmethod
    def record_response_time(cls, method: str, time: float, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            cls._record_time(method + "-execution-time", time * 1000, txn_id)

    @classmethod
    def record_request(cls, method: str, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            cls._count(method + "-request-received", 1, txn_id)

    @classmethod
    def record_status_code(cls, method: str, code: StatusCode, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            codestr = str(code)
            if codestr == "StatusCode.OK":
                cls._count(method + "-status-" + codestr, 1, txn_id)
            else:
                cls._count(method + "-status-unexpected-error-" + codestr, 1, txn_id)

    @classmethod
    def record_custom_metric(cls, method: str, size: int, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            cls._count(method, size, txn_id)

    @classmethod
    def _record_time(cls, aspect: str, time_in_ms: float, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            if cls._statsd_client is not None:
                cls._statsd_client.timing(cls._STATSD_TIME_PREFIX + aspect, time_in_ms)

    @classmethod
    def _count(cls, aspect: str, delta: int, txn_id: str):
        if txn_id not in cls._txn_ids_to_exclude:
            if cls._statsd_client is not None:
                cls._statsd_client.incr(cls._STATSD_COUNT_PREFIX + aspect, delta)

    @classmethod
    def _record_count_by_timestamp(cls, aspect: str, count: int, txn_id: str):
        """
        The statsd timer computes multiple statistics for a given metric, including max, min, sum, mean.
        The 'time' name is misleading because it is not just for timing, but for any metric that you want
        all those stats for, including counts. Counts multiplied by 1000 to convert to seconds for display.
        :param aspect: the metric being counted
        :param count:
        :param txn_id: the transaction id of the request
        :return:
        """
        if txn_id not in cls._txn_ids_to_exclude:
            cls._record_time(aspect, count * 1000, txn_id)