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
import json
import sys

from iota.mrc.mnlp.data_models.natural_questions import NQInputFeatures
from iota.mrc.techqa.featurization import generate_features_for_example, _NULL_SPAN
from transformers import PreTrainedTokenizer

from gaama.business.featurizers.abstract_featurizer import AbstractFeaturizer
from gaama.business.data_models.gaama_example import GAAMAExample
from gaama.service.services.exceptions import InvalidArgumentException

import logging

class TechQAFeaturizer(AbstractFeaturizer):
    def __init__(self, tokenizer: PreTrainedTokenizer, 
                 max_seq_length: int,
                 max_query_length: int,
                 doc_stride: int,
                 add_doc_title_to_passage: bool,
                 use_query_title_only: bool,
                 use_query_body_only: bool,
                 drop_stop_words_from_query: bool,
                 passage_delimiter: str):
        super().__init__(tokenizer)
        self._max_seq_length = max_seq_length
        self._max_query_length = max_query_length
        self._doc_stride = doc_stride
        self._add_doc_title_to_passage = add_doc_title_to_passage
        self._use_query_title_only = use_query_title_only
        self._use_query_body_only = use_query_body_only
        self._drop_stop_words_from_query = drop_stop_words_from_query
        self._passage_delimiter = passage_delimiter

    def featurize(self, example: GAAMAExample) -> List[NQInputFeatures]:
        """
        :param GAAMAExample example: example to featurize
        :example.question: structured json string containing question_tile and question_text
        :'{ "question_title":"...", "question_text":"..."}'
        :example.passage: string concatenating TechQA document text and document title separated by passage_delimiter
        :'document_text passage_delimiter document_title' 
        :return: list of features in NQInputFeatures format
        """

        qid = example.example_id

        try:
            question = json.loads(example.question, strict = False)
        except Exception as ex:
            logging.error('Error parsing structured query from question json `%s`: %s' % (example.question, ex))
            raise 
        question_title = question.get("question_title", "")
        question_text = question.get("question_text", "")

        passage_fields = example.passage.split(self._passage_delimiter)
        if len(passage_fields) <= 1:
            document_text = example.passage
            document_title = ""
        else:
            document_text = " ".join(passage_fields[: len(passage_fields) - 1]).rstrip()
            document_title = passage_fields[-1].lstrip()

        if not question_title and not question_text:
            raise InvalidArgumentException("Both question title and question text are empty")
        if not document_text:
            raise InvalidArgumentException("Document text is empty")

        query = {"QUESTION_TITLE": question_title, "QUESTION_TEXT": question_text}
        doc = {"_id": "", "title": document_title, "text": document_text}

        features = generate_features_for_example(qid = qid, 
                                                 query = query, 
                                                 doc = doc,
                                                 doc_id = "",
                                                 answer_span = _NULL_SPAN,
                                                 tokenizer = self._tokenizer,
                                                 max_seq_length = self._max_seq_length,
                                                 doc_stride = self._doc_stride,
                                                 max_query_length = self._max_query_length,
                                                 negative_span_subsampling_probability = 1.0,
                                                 add_doc_title_to_passage = self._add_doc_title_to_passage,
                                                 use_query_title_only = self._use_query_title_only,
                                                 use_query_body_only = self._use_query_body_only,
                                                 drop_stop_words_from_query = self._drop_stop_words_from_query)

        return features
