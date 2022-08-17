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
from collections import OrderedDict
from functools import partial
from typing import Iterable, List, Dict, Any, Optional

import torch
from iota.mrc.mnlp.modeling.common import to_list
from iota.mrc.mnlp.data_models.natural_questions import NQInputFeatures
from iota.mrc.mnlp.featurization.common import convert_to_tensor_dataset
from iota.mrc.mnlp.data_manipulation.batching import batch
from torch.utils.data import DataLoader, SequentialSampler

from gaama.business.predictors.abstract_predictor import AbstractPredictor
from gaama.business.predictors.standard_predictor.model_input_adapter import adapt_inputs_for_model
from gaama.logging_tools.function_loggers import log_runtime
from gaama.multiprocessing_tools.pool_helpers import create_pool_and_schedule_cleanup


class StandardPredictor(AbstractPredictor):
    def __init__(self, predict_batch_size: int, device: torch.device, span_tracker, final_short_answer_scorer,
                 num_workers: int, logger: Optional[logging.Logger] = None):
        super().__init__()
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger
        self._predict_batch_size = predict_batch_size
        self._device = device
        self._span_tracker = span_tracker
        self._final_short_answer_scorer = final_short_answer_scorer
        self._num_workers = num_workers
        self._worker_pool = create_pool_and_schedule_cleanup(self, self._num_workers)

    def predict(self, model: torch.nn.Module, input_features: Iterable[NQInputFeatures],
                num_answers: int) -> List[List[Dict[str, Any]]]:
        """
        :param torch.nn.Module model: PyTorch model
        :param input_features: Iterable of NQ features
        :param int num_answers: number of answers to return
        :return: Predictions for each example_id in the order received (through input_features)
        :rtype: List[List[Dict[str, Any]]]
        """

        start_end_logits_by_example_id = self._compute_start_end_probabilities(model, input_features)
        n_best_spans_for_examples = self._find_best_spans(start_end_logits_by_example_id, num_answers)
        return self._extract_predictions_from_best_spans(n_best_spans_for_examples)

    @log_runtime
    def _compute_start_end_probabilities(self, model: torch.nn.Module, input_features: Iterable[NQInputFeatures]) -> \
            Dict[Any, List[Dict[str, Any]]]:
        start_end_logits_by_example_id = OrderedDict()

        for mini_batch in batch(input_features, self._predict_batch_size):
            tensorized_mini_batch = convert_to_tensor_dataset(mini_batch, input_ids=True,
                                                              input_mask=True,
                                                              segment_ids=True,
                                                              feature_vector_indeces=True)
            for input_ids, input_mask, segment_ids, feature_vector_indices in DataLoader(
                    tensorized_mini_batch,
                    sampler=SequentialSampler(tensorized_mini_batch),
                    batch_size=self._predict_batch_size):
                self._logger.debug("Processing batch of size {} "
                                   "(predict_batch_size is {})".format(input_ids.shape[0], self._predict_batch_size))

                all_inputs = dict(
                    input_ids=input_ids,
                    input_mask=input_mask,
                    segment_ids=segment_ids)
                inputs = adapt_inputs_for_model(model, **all_inputs)

                for name, tensor in inputs.items():
                    inputs[name] = tensor.to(self._device)

                with torch.no_grad():
                    outputs = model(**inputs)

                for i, feature_index in enumerate(feature_vector_indices):
                    start_logits = to_list(outputs[0][i])
                    end_logits = to_list(outputs[1][i])
                    target_type_logits = to_list(outputs[2][i])
                    input_feature = mini_batch[feature_index.item()]
                    example_id = input_feature.example_id
                    if example_id not in start_end_logits_by_example_id:
                        start_end_logits_by_example_id[example_id] = []

                    start_end_logits_by_example_id[example_id].append(dict(start_logits=start_logits,
                                                                           end_logits=end_logits,
                                                                           target_type_logits=target_type_logits,
                                                                           feature=input_feature))
        return start_end_logits_by_example_id

    @log_runtime
    def _find_best_spans(self, span_tracker_kwargs_by_example_id: Dict[Any, List[Dict[str, Any]]], num_answers: int) \
            -> List[list]:
        track_spans_for_example = partial(self._find_best_spans_for_example,
                                          span_tracker_constructor=self._span_tracker,
                                          span_tracker_constructor_kwargs=dict(max_spans_to_track=num_answers),
                                          num_answers=num_answers)
        return self._worker_pool.map(track_spans_for_example, span_tracker_kwargs_by_example_id.values())

    @staticmethod
    def _find_best_spans_for_example(collect_best_spans_kwargs: List[Dict[str, Any]], span_tracker_constructor,
                                     span_tracker_constructor_kwargs: Dict[str, Any], num_answers: int) -> \
            List[object]:
        span_tracker = span_tracker_constructor(**span_tracker_constructor_kwargs)
        for these_kwargs in collect_best_spans_kwargs:
            span_tracker.collect_best_non_null_spans(**these_kwargs)
        return span_tracker.get_nbest_spans(n=num_answers)

    @log_runtime
    def _extract_predictions_from_best_spans(self, n_best_spans_for_examples: List[list]) -> List[List[Dict[str, Any]]]:
        predictions_by_example_id = []
        for predictions_data in n_best_spans_for_examples:
            predictions = []
            for prediction in predictions_data:
                span = prediction.short_span
                score = self._final_short_answer_scorer(span_score=span.score,
                                                        null_span_score=prediction.baseline_cls_score,
                                                        target_type_logits=prediction.target_type_logits)
                predictions.append(dict(start_char_offset=span.start_byte,
                                        end_char_offset=span.end_byte,
                                        confidence_score=score))
            predictions_by_example_id.append(predictions)
        return predictions_by_example_id
