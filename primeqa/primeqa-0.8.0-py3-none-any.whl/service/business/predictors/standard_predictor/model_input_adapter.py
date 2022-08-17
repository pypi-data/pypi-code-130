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
from typing import Dict

import torch
from iota.mrc.mnlp.modeling.natural_questions.models import DistilBertForQuestionAnswering, \
    RobertaForNaturalQuestions, PRobertaForNaturalQuestions


def adapt_inputs_for_model(model: torch.nn.Module, **kwargs: torch.Tensor) -> Dict[str, torch.Tensor]:
    """
    :param torch.nn.Module model: PyTorch model
    :param torch.Tensor kwargs: input tensors
    :return: dict of input tensors for the given model
    """
    inputs = dict(input_ids=kwargs['input_ids'],
                  attention_mask=kwargs['input_mask'],
                  token_type_ids=kwargs['segment_ids'])

    if isinstance(model, (DistilBertForQuestionAnswering, RobertaForNaturalQuestions, PRobertaForNaturalQuestions)):
        del inputs['token_type_ids']

    return inputs
