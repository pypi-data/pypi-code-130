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
import logging
from typing import Optional, Tuple
from transformers import PreTrainedTokenizer, PreTrainedModel

from gaama.configurations import Settings
from gaama.business.model_providers import HfModelProvider, CosModelProvider


class ModelProviderNotFoundError(NotImplementedError):
    pass


def load_model_and_tokenizer_from_config(config: Settings, logger: Optional[logging.Logger] = None) \
        -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """
    :param Settings config: global config object
    :param Optional[logging.Logger] logger: logging object
    :return: model and tokenizer objects
    """
    model_provider_name = config.model_provider_class.__name__

    if model_provider_name == HfModelProvider.__name__:

        model_provider = config.model_provider_class(config.model_class, config.model_name_or_path,
                                                     config.tokenizer_class, config.tokenizer_name_or_path,
                                                     config.disable_space_prefix_in_gpt2_tokenizer, logger)

    elif model_provider_name == CosModelProvider.__name__:

        model_provider = config.model_provider_class(config.cos_endpoint, config.cos_access_key, config.cos_secret_key,
                                                     config.cos_bucket, config.model_class, config.cos_local_cache,
                                                     config.cos_model_filename, config.cos_tokenizer_filename,
                                                     config.tokenizer_class,
                                                     config.disable_space_prefix_in_gpt2_tokenizer, logger)
    else:
        raise ModelProviderNotFoundError(
            "No model provider named {} found: {}".format(model_provider_name, config.model_provider_class))

    return model_provider.load_model(), model_provider.load_tokenizer()
