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
from functools import partial

import torch
from iota.mrc.mnlp.modeling.natural_questions.tracker import BestSpanTracker as NQBestSpanTracker
from iota.mrc.mnlp.modeling.natural_questions.scorers import initialize_scorer

from gaama.business.predictors.abstract_predictor import AbstractPredictor
from gaama.business.predictors.standard_predictor.standard_predictor import StandardPredictor
from gaama.configurations import Settings


class PredictorNotFoundError(NotImplementedError):
    pass


class SpanTrackerNotFoundError(NotImplementedError):
    pass


def load_predictor_from_config(config: Settings, device: torch.device) -> AbstractPredictor:
    """
    :param Settings config: global config object
    :param torch.device device: pytorch device to do predictions on
    :return: predictor object
    """
    predictor_name = config.predictor_class.__name__

    if predictor_name == StandardPredictor.__name__:
        span_tracker_closure = _load_span_tracker_from_config(config)
        predictor = config.predictor_class(config.predict_batch_size, device,
                                           span_tracker_closure,
                                           initialize_scorer(config.final_short_answer_scorer,
                                                             config.target_type_weight),
                                           config.num_worker_processes)
    else:
        raise PredictorNotFoundError(
            "No predictor named {} found: {}".format(predictor_name, config.predictor_class))
    return predictor


def _load_span_tracker_from_config(config: Settings):
    span_tracker_name = config.predictor_span_tracker.__name__

    if span_tracker_name == NQBestSpanTracker.__name__:
        span_tracker = partial(NQBestSpanTracker, n_logits_to_search=config.n_best_size,
                               max_answer_length=config.max_answer_length,
                               score_calculator=initialize_scorer(config.span_tracker_type,
                                                                  config.target_type_weight))
    else:
        raise SpanTrackerNotFoundError(
            "No span tracker named {} found: {}".format(span_tracker_name,
                                                        config.predictor_span_tracker)
        )
    return span_tracker
