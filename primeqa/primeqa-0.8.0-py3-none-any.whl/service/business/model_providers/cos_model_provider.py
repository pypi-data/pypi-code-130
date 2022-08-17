"""
BEGIN_COPYRIGHT

IBM Confidential
OCO Source Materials

5727-I17
(C) Copyright IBM Corp. 2020 All Rights Reserved.

The source code for this program is not published or otherwise
divested of its trade secrets, irrespective of what has been
deposited with the U.S. Copyright Office.

END_COPYRIGHT
"""
import ibm_boto3
import tarfile
import tempfile
import logging
from os import path
from hashlib import sha256
from typing import Type, Union, Optional

from transformers import PreTrainedTokenizer, AutoTokenizer
from transformers import PreTrainedModel

from gaama.logging_tools.function_loggers import log_runtime
from gaama.business.model_loaders.hf_model_loader import hf_model_loader
from gaama.business.tokenizer_loaders.hf_tokenizer_loader import hf_tokenizer_loader
from gaama.business.model_providers.abstract_model_provider import AbstractModelProvider


class CosModelProvider(AbstractModelProvider):
    def __init__(self, cos_endpoint: str, cos_access_key: str, cos_secret_key: str, cos_bucket_name: str,
                 model_class: Type[PreTrainedModel], cos_local_cache: str, cos_model_filename: str,
                 cos_tokenizer_filename: str,
                 tokenizer_class: Type[Union[AutoTokenizer, PreTrainedTokenizer]],
                 disable_space_prefix_in_gpt2_tokenizer: bool, logger: Optional[logging.Logger] = None):
        super().__init__(model_class, tokenizer_class, disable_space_prefix_in_gpt2_tokenizer, logger)
        self._cos_bucket_name = cos_bucket_name
        self._cos_model_filename = cos_model_filename
        self._cos_local_cache = cos_local_cache
        self._cos_tokenizer_filename = cos_tokenizer_filename
        self._cos_connection = ibm_boto3.resource('s3', endpoint_url=cos_endpoint,
                                                  aws_access_key_id=cos_access_key,
                                                  aws_secret_access_key=cos_secret_key)

    @staticmethod
    def _hash_filename(url: str):
        url_bytes = url.encode("utf-8")
        url_hash = sha256(url_bytes)
        filename = url_hash.hexdigest()
        return filename

    @log_runtime
    def pull_cos_model(self, cos_source_path: str) -> str:
        """
        Pull model from COS and downloads it locally with filename specified.
        Returns model path
        :param str cos_source_path: path to or filename of COS  object
        :return: path of downloaded model on local filesystem
        """
        filesys_destination_path = path.join(self._cos_local_cache, self._hash_filename(cos_source_path))

        # Pull object from Cloud Object Store if not present in filesystem
        if not path.exists(path.expanduser(filesys_destination_path)):
            self._logger.info("Cache does not exist - pulling object from COS")
            with tempfile.TemporaryDirectory() as temp_dir_path:
                download_path = temp_dir_path + self._hash_filename(cos_source_path)
                # TODO: The logging workaround for the download_file request is due to a bug in ibm_cos_sdk where if
                #  the root logger of the application is set to DEBUG, the code enters into infinite wait state. Remove
                #  this once the bug in ibm_cos_sdk is fixed.
                logging.getLogger().setLevel(logging.INFO)
                self._cos_connection.meta.client.download_file(self._cos_bucket_name, cos_source_path, download_path)
                logging.getLogger().setLevel(self._logger.level)
            with tarfile.open(download_path) as model_tar:
                model_tar.extractall(filesys_destination_path)  # specify which folder to extract to
            self._logger.info("Done with pulling object from COS")
        return filesys_destination_path

    def load_model(self) -> PreTrainedModel:
        filesys_destination_path = self.pull_cos_model(self._cos_model_filename)
        return hf_model_loader(self._model_class, filesys_destination_path)

    def load_tokenizer(self) -> PreTrainedTokenizer:
        filesys_destination_path = self.pull_cos_model(self._cos_tokenizer_filename)
        return hf_tokenizer_loader(self._tokenizer_class, filesys_destination_path,
                                   self._disable_space_prefix_in_gpt2_tokenizer)

