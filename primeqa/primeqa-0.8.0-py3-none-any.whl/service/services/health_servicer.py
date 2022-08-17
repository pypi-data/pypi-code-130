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
import grpc

from os import path
from subprocess import run, CalledProcessError
from grpc import ServicerContext, RpcError
from retry import retry

from gaama.grpc_generated.health_check_pb2 import HealthCheckRequest, HealthCheckResponse, Empty, ReadinessStatus
from gaama.grpc_generated.health_check_pb2_grpc import HealthServiceServicer
from gaama.grpc_generated.v1.gaama_pb2_grpc import ReadingComprehensionStub
from gaama.grpc_generated.v1.gaama_pb2 import QueryWithPassages, FoundAnswersForPassages
from gaama.configurations import Settings
from gaama.logging_tools.error_loggers import run_with_error_mapper
from gaama.service.cred_helpers import get_client_credentials, get_target_name_override
from gaama.service.services.exceptions import _map_exception_to_grpc_code


class HealthService(HealthServiceServicer):
    """
    Implementation for the Health Check Service
    """
    QUERY_WITH_PASSAGES_REQUEST = QueryWithPassages(question="What is his name?",
                                                    passages=["His name is Watson"],
                                                    max_num_answers_per_passage=1,
                                                    min_score_threshold=-100)

    def __init__(self, config: Settings):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._health_check_script = config.health_check_script
        if not path.isfile(self._health_check_script):
            self._logger.error("Health check script not found")
            raise RuntimeError("Health check script not found")
        self._gaama_client = HealthService._get_gaama_client(config.use_research_ssl_cert, config.port)
        self._logger.info("Initialized an instance of {}".format(self.__class__.__name__))

    @staticmethod
    def _get_gaama_client(use_research_ssl_cert: bool, server_port: int) -> ReadingComprehensionStub:
        credentials = get_client_credentials(use_research_ssl_cert)
        channel = grpc.secure_channel("localhost:{}".format(server_port), credentials, options=[get_target_name_override()])
        return ReadingComprehensionStub(channel)

    @run_with_error_mapper(_map_exception_to_grpc_code, HealthCheckResponse)
    def Check(self, request: HealthCheckRequest, context: ServicerContext) -> HealthCheckResponse:
        """
        Returns HealthCheckResponse.status as `SERVING` if Nvidia Tesla V100 GPU is available otherwise returns `NOT_SERVING`.
        Kubernetes liveness probes are configured to call this endpoint

        :param HealthCheckRequest request:
        :param ServicerContext context:
        :return: status of service
        :rtype: HealthCheckResponse
        """
        logging.getLogRecordFactory().set_log_context({})

        if request.service:
            # In the future, the health check service might support validations of underlying dependencies
            # referenced by request.service but currently it is not supported, so we don't expect to receive
            # a non-empty value for request.service
            self._logger.error("Received non-empty value for request.service: {}".format(request.service))
            return HealthCheckResponse(status=HealthCheckResponse.NOT_SERVING)

        gpu_available = self._check_gpu_available()
        if gpu_available:
            return HealthCheckResponse(status=HealthCheckResponse.SERVING)
        else:
            return HealthCheckResponse(status=HealthCheckResponse.NOT_SERVING)

    @run_with_error_mapper(_map_exception_to_grpc_code, ReadinessStatus)
    def Readiness(self, request: Empty, context: ServicerContext) -> ReadinessStatus:
        """
        Returns ReadinessStatus.is_ready as `True` if both the following conditions are satisfied othwewise returns `False`
        - Nvidia Tesla V100 GPU is available
        - GAAMA server can process a tiny FindAnswersForPassages request

        Kubernetes readiness probes are configured to call this endpoint

        :param Empty request:
        :param ServicerContext context:
        :return: status of service
        :rtype: ReadinessStatus
        """
        logging.getLogRecordFactory().set_log_context({})
        gpu_available = self._check_gpu_available()
        if gpu_available:
            status = self._check_server_ready()
            return ReadinessStatus(is_ready=status)
        return ReadinessStatus(is_ready=False)

    def _check_gpu_available(self) -> bool:
        """
        Runs a shell script that exits with code 0 if an Nvidia Tesla V100 GPU is available otherwise exits with code 1.
        If the script exits with code 0, this method returns True otherwise returns False
        """
        try:
            run(self._health_check_script, check=True, timeout=1)
            return True
        except CalledProcessError as cpe:
            self._logger.error("Health check script returned non-zero exit code: {}".format(cpe.returncode))
        except Exception as e:
            self._logger.error("Unknown error encountered while checking GPU availability: {}".format(e))
        return False

    def _check_server_ready(self) -> bool:
        """
        Sends a tiny FindAnswersForPassages request to the GAAMA server and returns True if the response contains
        expected answer otherwise returns False
        """
        try:
            response = self._send_answer_finding_request()
            if len(response.answers) > 0:
                answer_text = response.answers[0].answer[0].text
                if "Watson" not in answer_text:
                    self._logger.info("Expected answer not found in the answer text: {}; GAAMA server is not ready".format(answer_text))
                    return False
                return True
            self._logger.info("Readiness check did not return any answers; GAAMA server is not ready")
        except Exception as e:
            if isinstance(e, RpcError):
                error_details = "Internal readiness request failed with error - {}".format(e.details())
                e.details = lambda: error_details
                raise
            self._logger.error("Unknown error encountered while checking server status: {}".format(e))
        return False

    @retry(RpcError, tries=2)
    def _send_answer_finding_request(self) -> FoundAnswersForPassages:
        self._logger.debug("Sending internal Answer Finding request for readiness")
        return self._gaama_client.FindAnswersForPassages(request=self.QUERY_WITH_PASSAGES_REQUEST,
                                                         metadata=(("txn-id", "readiness"),))
