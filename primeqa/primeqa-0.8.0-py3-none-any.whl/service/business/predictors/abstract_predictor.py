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
from typing import Iterable, List, Dict, Any

import torch


class AbstractPredictor(metaclass=ABCMeta):

    @abstractmethod
    def predict(self, model: torch.nn.Module, input_features: Iterable[object],
                num_answers: int) -> List[List[Dict[str, Any]]]:
        """
        :param torch.nn.Module model: Pytorch Model
        :param Iterable[object] input_features: model input features
        :param int num_answers: number of answers to return
        :return: Model predictions for the provided inputs for each example id
        :rtype: List[List[Dict[str, Any]]]
        """
        pass
