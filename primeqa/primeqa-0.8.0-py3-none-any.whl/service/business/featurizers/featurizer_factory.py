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
from transformers import PreTrainedTokenizer

from gaama.business.featurizers.abstract_featurizer import AbstractFeaturizer
from gaama.business.featurizers.nq_featurizer import NQFeaturizer
from gaama.business.featurizers.techqa_featurizer import TechQAFeaturizer
from gaama.configurations import Settings

class FeaturizerNotFoundError(NotImplementedError):
    pass

def load_featurizer_from_config(config: Settings, tokenizer: PreTrainedTokenizer) -> AbstractFeaturizer:
    """
    :param Settings config: global config object
    :param PreTrainedTokenizer tokenizer: tokenizer to use for featurization
    :return: featurizer object
    """
    featurizer_name = config.featurizer_class.__name__

    if featurizer_name == NQFeaturizer.__name__:
        featurizer = config.featurizer_class(tokenizer, config.max_seq_length,
                                             config.max_query_length, config.doc_stride)
    elif featurizer_name == TechQAFeaturizer.__name__:
        featurizer = config.featurizer_class(tokenizer, config.max_seq_length,
                                             config.max_query_length, config.doc_stride,
                                             config.add_doc_title_to_passage,
                                             config.use_query_title_only,
                                             config.use_query_body_only,
                                             config.drop_stop_words_from_query,
                                             config.passage_delimiter)
    else:
        raise FeaturizerNotFoundError(
            "No featurizer named {} found: {}".format(featurizer_name, config.featurizer_class))
    return featurizer
