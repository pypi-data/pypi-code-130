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
import os
from typing import Optional, Tuple

import grpc
from Crypto.PublicKey import RSA
from pkg_resources import resource_filename


def _get_cert_package(use_research_ssl_cert: bool) -> str:
    return 'security.{}'.format('research' if use_research_ssl_cert else 'wire')


def get_server_credentials(use_research_ssl_cert: bool,
                           logger: Optional[logging.Logger] = None) -> grpc.ServerCredentials:
    """
    Function which parses the public and private key files and returns the gRPC server credentials object
    :param bool use_research_ssl_cert: whether to use research ssl cert (or default wire cert)
    :param Optional[logging.Logger] logger: logger for logging, will create logger with same name as function otherwise
    :return: server_credentials
    :rtype: grpc.ServerCredentials
    """
    if logger is None:
        logger = logging.getLogger(get_server_credentials.__name__)
    cert_package = _get_cert_package(use_research_ssl_cert)
    logger.info("Loading server credentials from {}".format(cert_package))
    private_key = resource_filename(cert_package, 'server.pem')
    public_key = resource_filename(cert_package, 'server.crt')

    with open(private_key, 'rb') as f:
        private_key = f.read()
    with open(public_key, 'rb') as f:
        certificate_chain = f.read()

    wire_passphrase = "WIRE_PRIVATE_KEY_PASSPHRASE"

    password = os.getenv(wire_passphrase)
    if not password:
        logger.error("{} not found".format(wire_passphrase))
        raise RuntimeError("{} not found".format(wire_passphrase))

    unencrypted_pem = RSA.importKey(private_key, passphrase=password).exportKey()

    server_credentials = grpc.ssl_server_credentials(((unencrypted_pem, certificate_chain,),))
    return server_credentials


def get_client_credentials(use_research_ssl_cert: bool,
                           logger: Optional[logging.Logger] = None) -> grpc.ChannelCredentials:
    """
    Function which parses the public key files and returns the gRPC client credentials object
    :param bool use_research_ssl_cert: whether to use research ssl cert (or default wire cert)
    :param Optional[logging.Logger] logger: logger for logging, will create logger with same name as function otherwise
    :return: client_credentials
    :rtype: grpc.ChannelCredentials
    """
    if logger is None:
        logger = logging.getLogger(get_client_credentials.__name__)
    cert_package = _get_cert_package(use_research_ssl_cert)
    logger.info("Loading server credentials from {}".format(cert_package))
    public_key = resource_filename(cert_package, 'server.crt')
    with open(public_key, 'rb') as f:
        trusted_certs = f.read()
    client_credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
    return client_credentials


def get_target_name_override() -> Tuple[str, str]:
    """
    :return: SSL Target Name Override for use in grpc secure channel options arg
    :rtype: Tuple[str, str]
    """
    return 'grpc.ssl_target_name_override', "WIRE"
