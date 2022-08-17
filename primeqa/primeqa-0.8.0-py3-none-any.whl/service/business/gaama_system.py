"""
BEGIN_COPYRIGHT

IBM Confidential
OCO Source Materials

5727-I17
(C) Copyright IBM Corp. 2019 All Rights Reserved.
 
The source code for this program is not published or otherwise
divested of its trade secrets, irrespective of what has been
deposited with the U.S. Copyright Office.

END_COPYRIGHT
"""
import logging
from itertools import chain
from operator import itemgetter
from typing import Any, List, Dict, Optional
import math

import torch
from iota.mrc.mnlp.modeling.common import apply_fp16_and_distributed_gpu_settings
from iota.mrc.mnlp.torch_setup import setup_cuda_device, set_random_seed

from gaama.business.data_models.gaama_example import GAAMAExample
from gaama.business.featurizers.abstract_featurizer import AbstractFeaturizer
from gaama.business.featurizers.featurizer_factory import load_featurizer_from_config
from gaama.business.predictors.predictor_factory import load_predictor_from_config
from gaama.configurations import Settings
from gaama.logging_tools.function_loggers import log_runtime
from gaama.multiprocessing_tools.pool_helpers import create_pool_and_schedule_cleanup
from gaama.service.services.exceptions import InvalidArgumentException
from gaama.business.model_providers.model_provider_factory import load_model_and_tokenizer_from_config
from gaama.metrics.metrics import MetricsLogger
from gaama.logging_tools.request_loggers import get_txn_id_from_log_context


class GAAMASystem(object):
    """
    Interactive question answering system utilizing a model developed for Google's Natural Questions challenge.
    """

    def __init__(self, config: Settings, logger: Optional[logging.Logger] = None):
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger

        self._config = config
        self._local_rank = -1
        self._device, self._n_gpu, _, _ = setup_cuda_device(self._local_rank, self._config.no_cuda)
        self._logger.info("Using pytorch device {} with {} GPUs".format(self._device, self._n_gpu))
        self._initialize_device_settings_for_deterministic_behavior()

        self._model, tokenizer = load_model_and_tokenizer_from_config(self._config, self._logger)
        self._model = self._model.to(self._device)
        self._model.eval()
        self._model = apply_fp16_and_distributed_gpu_settings(model=self._model, distributed_training=False,
                                                              fp16=self._config.fp16, n_gpu=self._n_gpu,
                                                              local_rank=self._local_rank)

        self._featurizer = load_featurizer_from_config(self._config, tokenizer)
        self._predictor = load_predictor_from_config(self._config, self._device)
        self._featurizer_pool = create_pool_and_schedule_cleanup(self, self._config.num_worker_processes,
                                                                 initializer=self._bind_featurizer_to_featurization_method,
                                                                 initargs=(self._featurizer,))

    def get_answers(self, question: str, passage: str, num_answers: int,
                    minimum_score_threshold: float) -> List[Dict[str, Any]]:
        """
                Computes the answers to the question in the passage
                :param str question: the question, cannot be None
                :param str passage: the passage, cannot be None
                :param int num_answers: the maximum number of answers returned by the method
                :param float minimum_score_threshold: the minimum score for an answer to be returned
                :return: Candidate answers in descending score order
                :rtype: List[Dict[str, Any]]
        """
        return self.get_answers_for_passages(question, [passage], num_answers, minimum_score_threshold)[0]

    def get_answers_for_passages(self, question: str, passages: List[str], num_answers_per_passage: int,
                                 minimum_score_threshold: float) -> List[List[Dict[str, Any]]]:
        """
                Computes the answers to the question in the passage
                :param str question: the question, cannot be None
                :param List[str] passages: the passage, cannot be None
                :param int num_answers_per_passage: the maximum number of answers returned per passage
                :param float minimum_score_threshold: the minimum score for an answer to be returned
                :return: Candidate answers in descending score order for each passage
                :rtype: List[List[Dict[str, Any]]]
        """
        if num_answers_per_passage <= 0:
            raise InvalidArgumentException("Number of answers must be positive, not {}".format(num_answers_per_passage))

        examples = self._create_examples_for_question_and_passages(question, passages)
        features = self._featurize(examples)
        predictions_by_passage = self._predict(features, num_answers_per_passage)
        return self._post_process_predictions(predictions_by_passage, passages,
                                              num_answers_per_passage, minimum_score_threshold)

    def get_status(self) -> Dict[str, Any]:
        """
        :return: Status of the system
        :rtype: Dict[str, Any]
        """
        return dict(model_description=repr(self._model), modeling_notes=self._config.modeling_notes)

    def _initialize_device_settings_for_deterministic_behavior(self):
        # Set seeds so answer is the same across all runs
        set_random_seed(self._config.seed, self._n_gpu)

        # Deterministic mode
        if self._config.deterministic and self._device.type != "cpu":
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            self._logger.info(
                "Setting deterministic mode in CUDNN - this may incur a runtime penalty")
        elif self._config.deterministic and self._device.type == "cpu":
            self._logger.info("Deterministic mode set but Pytorch is using the CPU -- ignoring")
        else:
            self._logger.info("Deterministic mode not set -- you may see non-deterministic results")

        # Num Pytorch threads
        if self._device.type == "cpu":
            if self._config.num_pytorch_threads:
                torch.set_num_threads(self._config.num_pytorch_threads)
                actual_num_threads = torch.get_num_threads()
                if self._config.num_pytorch_threads != actual_num_threads:
                    self._logger.warning("Requested Pytorch use {} threads but is actually using {}".format(
                        self._config.num_pytorch_threads, actual_num_threads))

            self._logger.info("Using {} CPU threads for Pytorch".format(torch.get_num_threads()))
        elif self._config.num_pytorch_threads is not None:
            self._logger.info(
                "Config set for {} Pytorch CPU threads but using GPU -- ignoring".format(
                    self._config.num_pytorch_threads))

    @staticmethod
    @log_runtime
    def _create_examples_for_question_and_passages(question: str, passages: List[str]) -> List[GAAMAExample]:
        if not question:
            raise InvalidArgumentException("Question should not be empty")

        examples = []
        for i, passage in enumerate(passages, 1):
            if not passage:
                raise InvalidArgumentException("Passage {} of {} should not be empty".format(i, len(passages)))

            examples.append(GAAMAExample(question, passage))

        return examples

    @log_runtime
    def _featurize(self, examples: List[GAAMAExample]) -> list:
        return list(chain.from_iterable(self._featurizer_pool.map(self._featurize_with_bound_featurizer, examples)))

    # Functions to bind featurizer and do featurization - DO NOT MAKE THESE CLASSMETHODS - will cause errors

    @staticmethod
    def _bind_featurizer_to_featurization_method(featurizer: AbstractFeaturizer):
        GAAMASystem._featurize_with_bound_featurizer.featurizer = featurizer

    @staticmethod
    def _featurize_with_bound_featurizer(example: GAAMAExample) -> List[object]:
        return GAAMASystem._featurize_with_bound_featurizer.featurizer.featurize(example)

    # End of binding/bound functions

    @log_runtime
    def _predict(self, features: list, num_answers_per_passage: int) -> list:
        return self._predictor.predict(self._model, features, num_answers_per_passage)

    def _normalize_score(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        BETA0 = self._config.normalization_beta0
        BETA1 = self._config.normalization_beta1
        normalized_score = 1 / (1. + math.exp(-BETA0 - (BETA1 * prediction['confidence_score'])))
        self._logger.debug(
                    "Prediction score ({:.3f}) Normalized ({:.3f}) ".format(
                        prediction['confidence_score'], normalized_score))
        prediction['confidence_score'] = normalized_score
        return prediction

    @log_runtime
    def _post_process_predictions(self, predictions_by_passage: List[List[Dict[str, Any]]], passages: List[str],
                                  num_answers_per_passage: int, minimum_score_threshold: float) -> \
            List[List[Dict[str, Any]]]:
        num_total_predictions = 0
        confidence_score_getter = itemgetter('confidence_score')
        _total_passage_length = 0
        for i, (predictions, passage) in enumerate(zip(predictions_by_passage, passages)):
            _total_passage_length += len(passage)
            num_initial_predictions = len(predictions)

            # confidence scores for Reading Comprehension to be bounded b/w 0 and 1
            if self._config.use_score_normalization:
                predictions = map(self._normalize_score, predictions)

            predictions = filter(lambda pred: pred['confidence_score'] >= minimum_score_threshold, predictions)
            predictions = sorted(predictions, key=confidence_score_getter, reverse=True)
            num_total_predictions += len(predictions)

            num_filtered_predictions = num_initial_predictions - len(predictions)
            if num_filtered_predictions:
                self._logger.debug(
                    "Filtered {} predictions from passage {} of {} below minimum score threshold ({:.3f})".format(
                        num_filtered_predictions, i + 1, len(passages), minimum_score_threshold))

            for prediction in predictions:
                prediction['text'] = passage[prediction['start_char_offset']: prediction['end_char_offset']]
            predictions_by_passage[i] = predictions
            self._logger.debug(
                "Found {} predictions ({} were requested) in passage {} of {} ".format(len(predictions),
                                                                                       num_answers_per_passage,
                                                                                       i + 1, len(passages)))
        self._logger.info("Found {} predictions from {} passages".format(num_total_predictions, len(passages)))
        self._logger.info("Average passage length was {} characters".format(_total_passage_length // len(passages)))
        txn_id = get_txn_id_from_log_context()
        MetricsLogger.record_custom_metric("request-size-answers-returned", num_total_predictions, txn_id)
        MetricsLogger.record_custom_metric("request-size-num-passages", len(passages), txn_id)
        MetricsLogger.record_custom_metric("request-size-average-passage-length", _total_passage_length // len(passages), txn_id)
        return predictions_by_passage
