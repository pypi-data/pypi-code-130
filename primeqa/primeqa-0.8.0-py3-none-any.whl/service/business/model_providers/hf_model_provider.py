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
from typing import Type, Union, Optional
from transformers import PreTrainedTokenizer, AutoTokenizer, PreTrainedModel

from gaama.business.model_loaders.hf_model_loader import hf_model_loader
from gaama.business.tokenizer_loaders.hf_tokenizer_loader import hf_tokenizer_loader
from gaama.business.model_providers.abstract_model_provider import AbstractModelProvider


class HfModelProvider(AbstractModelProvider):
    def __init__(self, model_class: Type[PreTrainedModel], model_name_or_path: str,
                 tokenizer_class: Type[Union[AutoTokenizer, PreTrainedTokenizer]], tokenizer_name_or_path: str,
                 disable_space_prefix_in_gpt2_tokenizer: bool, logger: Optional[logging.Logger] = None):
        super().__init__(model_class, tokenizer_class, disable_space_prefix_in_gpt2_tokenizer, logger)
        self._model_name_or_path = model_name_or_path
        self._tokenizer_name_or_path = tokenizer_name_or_path

    def load_model(self) -> PreTrainedModel:
        return hf_model_loader(self._model_class, self._model_name_or_path)

    def load_tokenizer(self) -> PreTrainedTokenizer:
        return hf_tokenizer_loader(self._tokenizer_class, self._tokenizer_name_or_path,
                                   self._disable_space_prefix_in_gpt2_tokenizer)
