# -*- coding: utf-8 -*-
import abc
import tempfile

import hao
from transformers import (
    BertModel,
    BertTokenizerFast,
    ElectraModel,
    ElectraTokenizerFast,
    PreTrainedModel,
    PreTrainedTokenizerFast,
    XLNetModel,
    XLNetTokenizerFast,
)

from tailors import freeze
from tailors.domains import Derivable


class Embedder(abc.ABC, Derivable):
    def __init__(self, model_conf) -> None:
        super().__init__(model_conf)
        self.model_conf = model_conf
        self.tokenizer = self.build_tokenizer()
        self.embedding = self.build_embedding()

    def get_additional_tokens_for_tokenizer(self):
        return []

    @abc.abstractmethod
    def build_tokenizer(self) -> PreTrainedTokenizerFast:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_embedding(self) -> PreTrainedModel:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_embedding_size(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def on_save_checkpoint(self, checkpoint) -> None:
        raise NotImplementedError()

    @staticmethod
    def get_pretrained_model_path(model: str):
        # hao.oss.init(f"pretrained.{model}", config='tailors.yml')
        return hao.config.get_path(f"pretrained.{model}.local", config='tailors.yml')


class Bert(Embedder):

    def build_tokenizer(self):
        if hasattr(self.model_conf, 'vocab'):
            with tempfile.NamedTemporaryFile() as f:
                f.write(self.model_conf.vocab.encode())
                tokenizer = BertTokenizerFast(vocab_file=f.name)
                if hasattr(self.model_conf, 'additional_special_tokens'):
                    tokenizer.add_special_tokens({'additional_special_tokens': self.model_conf.additional_special_tokens})
                return tokenizer
        else:
            pretrained_model_path = self.get_pretrained_model_path('bert')
            tokenizer = BertTokenizerFast.from_pretrained(pretrained_model_path)
            additional_special_tokens = self.get_additional_tokens_for_tokenizer()
            if additional_special_tokens is not None and len(additional_special_tokens) > 0:
                tokenizer.add_special_tokens({'additional_special_tokens': additional_special_tokens})
            return tokenizer

    def build_embedding(self):
        if hasattr(self.model_conf, 'bert_config'):
            bert = BertModel(self.model_conf.bert_config)
        else:
            pretrained_model_path = self.get_pretrained_model_path('bert')
            bert = BertModel.from_pretrained(pretrained_model_path)
        if self.model_conf.freeze_embedding:
            freeze(bert)
        return bert

    def get_embedding_size(self):
        return self.embedding.config.hidden_size

    def on_save_checkpoint(self) -> None:
        if not hasattr(self.model_conf, 'vocab'):
            pretrained_model_path = self.get_pretrained_model_path('bert')
            path_vocab_file = hao.paths.get_path(pretrained_model_path, 'vocab.txt')
            self.model_conf.vocab = open(path_vocab_file).read()
        if len(self.tokenizer.additional_special_tokens) > 0:
            self.model_conf.additional_special_tokens = self.tokenizer.additional_special_tokens
        self.model_conf.bert_config = self.embedding.config


class XLNet(Embedder):

    def build_tokenizer(self):
        if hasattr(self.model_conf, 'vocab'):
            with tempfile.NamedTemporaryFile() as f:
                f.write(self.model_conf.vocab)
                tokenizer = XLNetTokenizerFast(vocab_file=f.name)
                if hasattr(self.model_conf, 'additional_special_tokens'):
                    tokenizer.add_special_tokens({'additional_special_tokens': self.model_conf.additional_special_tokens})
                return tokenizer
        else:
            pretrained_model_path = self.get_pretrained_model_path('xlnet')
            tokenizer = XLNetTokenizerFast.from_pretrained(pretrained_model_path)
            additional_special_tokens = self.get_additional_tokens_for_tokenizer()
            if additional_special_tokens is not None and len(additional_special_tokens) > 0:
                tokenizer.add_special_tokens({'additional_special_tokens': additional_special_tokens})
            return tokenizer

    def build_embedding(self):
        if hasattr(self.model_conf, 'xlnet_config'):
            xlnet = XLNetModel(self.model_conf.xlnet_config)
        else:
            pretrained_model_path = self.get_pretrained_model_path('xlnet')
            xlnet = XLNetModel.from_pretrained(pretrained_model_path)
        if self.model_conf.freeze_embedding:
            freeze(xlnet)
        return xlnet

    def get_embedding_size(self):
        return self.embedding.config.d_model

    def on_save_checkpoint(self) -> None:
        if not hasattr(self.model_conf, 'vocab'):
            pretrained_model_path = self.get_pretrained_model_path('xlnet')
            path_vocab_file = hao.paths.get_path(pretrained_model_path, 'spiece.model')
            self.model_conf.vocab = open(path_vocab_file, 'rb').read()
        if len(self.tokenizer.additional_special_tokens) > 0:
            self.model_conf.additional_special_tokens = self.tokenizer.additional_special_tokens
        self.model_conf.xlnet_config = self.embedding.config


class Electra(Embedder):

    def build_tokenizer(self):
        if hasattr(self.model_conf, 'vocab'):
            with tempfile.NamedTemporaryFile() as f:
                f.write(self.model_conf.vocab.encode())
                tokenizer = ElectraTokenizerFast(vocab_file=f.name)
                if hasattr(self.model_conf, 'additional_special_tokens'):
                    tokenizer.add_special_tokens({'additional_special_tokens': self.model_conf.additional_special_tokens})
                return tokenizer
        else:
            pretrained_model_path = self.get_pretrained_model_path('electra')
            tokenizer = ElectraTokenizerFast.from_pretrained(pretrained_model_path)
            additional_special_tokens = self.get_additional_tokens_for_tokenizer()
            if additional_special_tokens is not None and len(additional_special_tokens) > 0:
                tokenizer.add_special_tokens({'additional_special_tokens': additional_special_tokens})
            return tokenizer

    def build_embedding(self):
        if hasattr(self.model_conf, 'electra_config'):
            electra = ElectraModel(self.model_conf.electra_config)
        else:
            pretrained_model_path = self.get_pretrained_model_path('electra')
            electra = ElectraModel.from_pretrained(pretrained_model_path)
        if self.model_conf.freeze_embedding:
            freeze(electra)
        return electra

    def get_embedding_size(self):
        return self.embedding.config.hidden_size

    def on_save_checkpoint(self) -> None:
        if not hasattr(self.model_conf, 'vocab'):
            pretrained_model_path = self.get_pretrained_model_path('electra')
            path_vocab_file = hao.paths.get_path(pretrained_model_path, 'vocab.txt')
            self.model_conf.vocab = open(path_vocab_file).read()
        if len(self.tokenizer.additional_special_tokens) > 0:
            self.model_conf.additional_special_tokens = self.tokenizer.additional_special_tokens
        self.model_conf.electra_config = self.embedding.config


def list_embedders():
    return Embedder.subclasses()
