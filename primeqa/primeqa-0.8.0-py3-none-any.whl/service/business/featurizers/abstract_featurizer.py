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
from typing import List

from transformers import PreTrainedTokenizer

from gaama.business.data_models.gaama_example import GAAMAExample


class AbstractFeaturizer(object, metaclass=ABCMeta):
    def __init__(self, tokenizer: PreTrainedTokenizer):
        self._tokenizer = tokenizer

    @abstractmethod
    def featurize(self, example: GAAMAExample) -> List[object]:
        """

        :param GAAMAExample example: example to featurize
        :return: List of features
        """
        pass
