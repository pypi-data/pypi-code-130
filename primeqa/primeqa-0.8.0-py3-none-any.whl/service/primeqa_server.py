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
import logging.config
import time
import os
from concurrent import futures
from distutils.util import strtobool

import grpc
from pkg_resources import resource_filename

from primeqa.service.configurations import Settings
from primeqa.service.grpc_generated import health_check_pb2_grpc
from primeqa.service.grpc_generated.v1 import primeqa_pb2_grpc
from primeqa.service.logging_tools.request_log_factory import RequestLogFactory
from primeqa.service.metrics.metrics import MetricsLogger
from primeqa.service.cred_helpers import get_server_credentials
from primeqa.service.services.health_servicer import HealthService
from primeqa.service.services.reading_comprehension_servicer import ReadingComprehensionService


class PrimeQAServer:
    def __init__(self, config: Settings = None, logger: logging.Logger = None):
        try:
            log_config_file = "logging_config.ini"
            verbose = os.getenv("verbose")
            if verbose and bool(strtobool(verbose)):
                log_config_file = "verbose_logging_config.ini"
            logging.config.fileConfig(resource_filename("config", log_config_file))
            logging.setLogRecordFactory(RequestLogFactory(logging.getLogRecordFactory()))

            if logger is None:
                self._logger = logging.getLogger(self.__class__.__name__)
            else:
                self._logger = logger

            if config is None:
                self._config = Settings()
            else:
                self._config = config

            self._server = None

            # Instantiate global MetricsLogger
            MetricsLogger.initialize_statsd_client(self._config)

            # SSL authentication
            self._server_credentials = get_server_credentials(self._config.use_research_ssl_cert, self._logger)
        except Exception as ex:
            self._logger.exception("Error configuring server: {}".format(ex))
            raise

    def run(self) -> None:
        try:
            start_t = time.time()

            # creating the servers and running it
            max_conn_age_option = ("grpc.max_connection_age_ms", self._config.grpc_max_connection_age_secs * 1000)
            max_conn_age_grace_option = ("grpc.max_connection_age_grace_ms", self._config.grpc_max_connection_age_grace_secs * 1000)
            server_options = (max_conn_age_option, max_conn_age_grace_option, )

            self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=self._config.num_server_threads), options=server_options)
            self._logger.info('Starting %s' % ReadingComprehensionService.__name__)
            primeqa_pb2_grpc.add_ReadingComprehensionServicer_to_server(ReadingComprehensionService(self._config),
                                                                      self._server)
            health_check_pb2_grpc.add_HealthServiceServicer_to_server(HealthService(self._config), self._server)
            self._logger.info('grpc will operate on port {}'.format(self._config.port))
            self._server.add_secure_port('[::]:{}'.format(self._config.port), self._server_credentials)
            self._server.start()
            self._logger.info('server started - initialization took {:.6f} seconds '.format(time.time() - start_t))
        except Exception as ex:
            self._logger.exception("Error starting server: {}".format(ex))
            raise

        _ONE_DAY_IN_SECONDS = 60 * 60 * 24
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self._server.stop(0)
            self._logger.info('received keyboard interrupt --- EXITING!')


def main():
    PrimeQAServer().run()


if __name__ == "__main__":
    main()
