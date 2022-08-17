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
import threading
from logging import LogRecord


class RequestLogFactory():
    thread_local = threading.local()
    expected_headers = ["tenant-id","collection-ids","project-id","txn-id"]

    def __init__(self, original_factory: LogRecord, log_context: dict = None):
        if log_context is None:
            log_context = dict()
        self.original_factory = original_factory
        self.thread_local.log_context = log_context

    def __call__(self, *args, **kwargs):
        record = self.original_factory(*args, **kwargs)
        for key in self.expected_headers:
            try:
                setattr(record, key, self.thread_local.log_context.get(key, ""))
            except AttributeError:
                setattr(record, key, "")
        return record

    def set_log_context(self, log_context: dict):
        self.thread_local.log_context = log_context

