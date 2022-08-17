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
from abc import ABCMeta, abstractmethod
import logging
from typing import Optional, Type, Union

from transformers import PreTrainedTokenizer, AutoTokenizer, PreTrainedModel


class AbstractModelProvider(object, metaclass=ABCMeta):
    def __init__(self, model_class: Type[PreTrainedModel],
                 tokenizer_class: Type[Union[AutoTokenizer, PreTrainedTokenizer]],
                 disable_space_prefix_in_gpt2_tokenizer: bool, logger: Optional[logging.Logger] = None):
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger
        self._model_class = model_class
        self._tokenizer_class = tokenizer_class
        self._disable_space_prefix_in_gpt2_tokenizer = disable_space_prefix_in_gpt2_tokenizer

    @abstractmethod
    def load_model(self) -> PreTrainedModel:
        """
        :return: PreTrainedModel
        """
        pass

    @abstractmethod
    def load_tokenizer(self) -> PreTrainedTokenizer:
        """
        :return: PreTrainedTokenizer
        """
        pass