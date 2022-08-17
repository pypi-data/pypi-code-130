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

from typing import Any, Dict, List, Optional

from google.protobuf.json_format import ParseDict
from grpc import ServicerContext

# from primeqa.service.business.gaama_system import GAAMASystem
from primeqa.pipelines.extractive_mrc_pipeline import MRCPipeline
from primeqa.service.configurations import Settings
from primeqa.service.grpc_generated.v1.primeqa_pb2 import Status, StatusCheckRequest, QueryPassagePair, FoundAnswers, \
    QueryWithPassages, FoundAnswersForPassages
from primeqa.service.grpc_generated.v1.primeqa_pb2_grpc import ReadingComprehensionServicer
from primeqa.service.logging_tools.error_loggers import run_with_error_mapper
from primeqa.service.logging_tools.request_loggers import record_request
from primeqa.service.metrics.metrics import MetricsLogger
from primeqa.service.services.exceptions import _map_exception_to_grpc_code
from primeqa.service.multiprocessing_tools.request_synchronizers import synchronized
from primeqa.service.logging_tools.request_loggers import get_txn_id_from_log_context


class ReadingComprehensionService(ReadingComprehensionServicer):
    def __init__(self, config: Settings, logger: Optional[logging.Logger] = None):
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger

        self._config = config
        self._rc_system = MRCPipeline(config)
        self._logger.info("Initialized an instance of {}".format(self.__class__.__name__))

    def _filter(self, answer_list, max_num_answers=-1, min_score_threshold=-1):
        res = []
        for answers in answer_list:
            if max_num_answers>0:
                answers = answers[:max_num_answers]
            ares = [ans for ans in answers if ans['confidence_score'] >= min_score_threshold]
            res.append(ares)
        return res

    @synchronized
    @run_with_error_mapper(_map_exception_to_grpc_code, FoundAnswers)
    @record_request
    def FindAnswers(self, request: QueryPassagePair, context: ServicerContext) -> FoundAnswers:
        """
        :param QueryPassagePair request: contains the following fields: question, passage, max_num_answers, and min_score_threshold
        :param ServicerContext context: gRPC context information for method call
        :return: answers response
        :rtype: FoundAnswers
        """
        predictions = self._rc_system.get_answers(request.question, request.passage)
        predictions = self.filter(predictions, request.max_num_answers, request.min_score_threshold)
        response = self._package_found_answers(predictions)
        MetricsLogger.record_request(self.FindAnswers.__name__, get_txn_id_from_log_context())
        return response

    @synchronized
    @run_with_error_mapper(_map_exception_to_grpc_code, FoundAnswersForPassages)
    @record_request
    def FindAnswersForPassages(self, request: QueryWithPassages, context: ServicerContext) -> FoundAnswersForPassages:
        """
        :param QueryWithPassages request: contains the following fields: question, passages, max_num_answers_per_passage, and min_score_threshold
        :param ServicerContext context: gRPC context information for method call
        :return: answers response for each passage
        :rtype: FoundAnswersForPassages
        """
        predictions_by_passage = self._rc_system.get_answers_for_passages(request.question, request.passages)
        predictions_by_passage = self.filter(predictions_by_passage)
        response = self._package_found_answers_for_passages(predictions_by_passage)
        MetricsLogger.record_request(self.FindAnswersForPassages.__name__, get_txn_id_from_log_context())
        return response

    @run_with_error_mapper(_map_exception_to_grpc_code, Status)
    @record_request
    def StatusCheck(self, request: StatusCheckRequest, context: ServicerContext) -> Status:
        """
        :param StatusCheckRequest request: request for status
        :param ServicerContext context: gRPC context information for method call
        :return: RC system status information
        :rtype: Status
        """
        status = self._rc_system.get_status()
        response = ParseDict(status, Status())
        return response

    @staticmethod
    def _package_found_answers(predictions: List[Dict[str, Any]]) -> FoundAnswers:
        response = ParseDict(dict(answer=predictions), FoundAnswers())
        return response

    @staticmethod
    def _package_found_answers_for_passages(predictions_by_passage: List[List[Dict[str, Any]]]) -> \
            FoundAnswersForPassages:
        response = ParseDict(dict(answers=[
            dict(answer=passage_predictions) for passage_predictions in predictions_by_passage
        ]), FoundAnswersForPassages())
        return response
