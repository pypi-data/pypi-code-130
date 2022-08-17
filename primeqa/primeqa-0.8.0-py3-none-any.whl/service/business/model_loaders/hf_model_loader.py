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
from typing import Type

from transformers import PreTrainedModel

def hf_model_loader(model_class: Type[PreTrainedModel], model_name_or_path: str) -> PreTrainedModel:
    """
    Loads a huggingface pretrained model
    :param Type[PreTrainedModel] model_class: pretrained model class to load
    :param str model_name_or_path: model name (e.g. roberta-large) or path to directory which contains model
    :return: a pretrained model of type model_class instantiated from model_name_or_path
    :rtype: PreTrainedModel
    """
    return model_class.from_pretrained(model_name_or_path)
