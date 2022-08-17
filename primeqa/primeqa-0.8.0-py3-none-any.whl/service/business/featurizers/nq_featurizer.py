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
from typing import List

from iota.mrc.mnlp.data_models.natural_questions import NQExample, NQInputFeatures
from iota.mrc.mnlp.featurization.natural_questions import NQFeaturizer as _NQFeaturizer, \
    LongAnswerCandidateSelectionStrategy
from transformers import PreTrainedTokenizer

from gaama.business.featurizers.abstract_featurizer import AbstractFeaturizer
from gaama.business.data_models.gaama_example import GAAMAExample


class NQFeaturizer(AbstractFeaturizer):
    def __init__(self, tokenizer: PreTrainedTokenizer, max_seq_length: int, max_query_length: int, doc_stride: int):
        super().__init__(tokenizer)
        self._max_seq_length = max_seq_length
        self._max_query_length = max_query_length
        self._doc_stride = doc_stride

    def featurize(self, example: GAAMAExample) -> List[NQInputFeatures]:
        """
        :param GAAMAExample example: example to featurize
        :return: list of nq features
        """
        nq_example = NQExample(example_id=example.example_id,
                               url="", title="",
                               question_text=example.question, question_tokens=[],
                               document_text=example.passage, document_tokens=[],
                               annotations=[], long_answer_candidates=[])
        features = _NQFeaturizer.generate_features_for_example(
            example=nq_example,
            tokenizer=self._tokenizer,
            max_seq_length=self._max_seq_length,
            doc_stride=self._doc_stride,
            max_query_length=self._max_query_length,
            keep_html_tokens=False,
            track_long_candidates=False,
            max_top_level_html_spans_to_consider=-1,
            la_candidate_selection_strategy=LongAnswerCandidateSelectionStrategy.ALL)
        return features
