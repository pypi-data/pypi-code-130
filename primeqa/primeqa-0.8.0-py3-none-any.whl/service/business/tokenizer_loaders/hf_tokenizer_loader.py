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
from typing import Type, Union

from transformers import PreTrainedTokenizer, AutoTokenizer
from iota.mrc.mnlp.modeling.factories.tokenizer import fix_fast_roberta_tokenizer


def hf_tokenizer_loader(tokenizer_class: Type[Union[AutoTokenizer, PreTrainedTokenizer]], tokenizer_name_or_path: str,
                        disable_space_prefix_in_gpt2_tokenizer: bool) -> PreTrainedTokenizer:
    """
    Load a pretrained huggingface tokenizer
    :param Type[PreTrainedTokenizer] tokenizer_class:  pretrained tokenizer class to load
    :param str tokenizer_name_or_path: tokenizer name (e.g. roberta-large) or path to directory which contains tokenizer
    :param bool disable_space_prefix_in_gpt2_tokenizer: Indicate whether prefix space should be added or not for GPT2 tokenizers
    :return: a pretrained tokenizer of type tokenizer_class instantiated from tokenizer_name_or_path
    :rtype: PreTrainedTokenizer
    """
    tokenize_kwargs = dict(add_prefix_space=not disable_space_prefix_in_gpt2_tokenizer)
    tokenizer = tokenizer_class.from_pretrained(tokenizer_name_or_path, use_fast=True, **tokenize_kwargs)
    if tokenize_kwargs['add_prefix_space']:
        tokenizer = fix_fast_roberta_tokenizer(tokenizer)
    return tokenizer
