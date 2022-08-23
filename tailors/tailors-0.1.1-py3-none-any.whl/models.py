# -*- coding: utf-8 -*-
import abc
import importlib
import inspect
import os
from typing import Dict, Iterator, List, Optional, Tuple, Union

import hao
import torch
import torch.nn as nn
from hao.namespaces import attr, from_args
from hao.stopwatch import Stopwatch
from torch.nn import DataParallel
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data.dataloader import default_collate
from transformers import PreTrainedModel, PreTrainedTokenizerFast

import tailors
from tailors.domains import Factor, Tags
from tailors.exceptions import TailorsError

LOGGER = hao.logs.get_logger(__name__)


@from_args
class TailorsConf:
    meta: dict = None
    freeze_embedding: bool = attr(bool, default=False)
    seq_len = attr(int, default=128)


class TailorsIO(abc.ABC):
    def __init__(self, model_conf: TailorsConf, tokenizer: PreTrainedTokenizerFast) -> None:
        self.model_conf = model_conf
        self.tokenizer = tokenizer
        self.tags: Tags = self.build_tags()
        self.empty_sample = self.encode('', self.tokenizer, self.model_conf.seq_len)
        self.init()
        self.empty_input = self.build_empty_input()

    def init(self):
        pass

    @abc.abstractmethod
    def build_tags(self) -> Tags:
        raise NotImplementedError()

    @staticmethod
    def encode(text: str,
               tokenizer: PreTrainedTokenizerFast,
               seq_len: int,
               add_special_tokens=True,
               padding: Union[bool, str] = 'max_length',
               truncation: Union[bool, str] = True,
               return_tensors: Optional[str] = 'pt'):
        encoder = tokenizer.encode_plus if isinstance(text, str) else tokenizer.prepare_for_model
        encoded = encoder(
            text,
            add_special_tokens=add_special_tokens,
            max_length=seq_len,
            padding=padding,
            truncation=truncation,
            return_attention_mask=True,
            return_token_type_ids=True,
            return_offsets_mapping=True,
            return_tensors=return_tensors,
        )
        input_ids = encoded.get("input_ids")
        attention_mask = encoded.get("attention_mask")
        token_type_ids = encoded.get("token_type_ids")
        offset_mapping = encoded.get("offset_mapping")

        if return_tensors:
            input_ids = input_ids.squeeze()
            attention_mask = attention_mask.squeeze()
            token_type_ids = token_type_ids.squeeze()
            offset_mapping = offset_mapping.tolist() if offset_mapping is not None else None

        return input_ids, attention_mask, token_type_ids, offset_mapping

    @abc.abstractmethod
    def build_empty_input(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def from_line(self, line: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def for_inference(self, lines: List[str], bz: int = 32, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def post_inference(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def for_eval(self, lines: Iterator[str], bz: int = 32, *args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def collate(batch):
        return default_collate(batch)


class Tailors(nn.Module, abc.ABC):

    def __init__(self, model_conf: TailorsConf):
        super().__init__()
        self.device = None
        assert model_conf.meta is not None, '`meta` must be populated manually'
        self.model_conf = model_conf

        self.io: TailorsIO = self.get_io()
        self.embedding = self.build_embedding()

    def freeze(self):
        tailors.freeze(self)
        self.eval()

    def unfreeze(self) -> None:
        tailors.unfreeze(self)
        self.train()

    def use_device(self, device):
        if device:
            self.to(device)
            self.device = device
        return self

    @abc.abstractmethod
    def build_tokenizer(self) -> PreTrainedTokenizerFast:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_embedding(self) -> PreTrainedModel:
        raise NotImplementedError()

    def on_save_checkpoint(self):
        pass

    def get_io(self):
        class_name = f"{self.__class__.__name__}IO"
        module_name = self.__class__.__module__
        try:
            module = importlib.import_module(module_name)
            io_class = getattr(module, class_name)
        except AttributeError:
            raise TailorsError(f"[io] expecting io class: `{module_name}.{class_name}`")
        except Exception as e:
            raise TailorsError(f"[io] failed to init io class: `{module_name}.{class_name}`", e)
        tokenizer = self.build_tokenizer()
        return io_class(self.model_conf, tokenizer)

    def forward(self, *args, **kwargs):
        features, = args
        logits, mask = self.encode(features)
        return self.decode(logits, mask)

    @abc.abstractmethod
    def encode(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def decode(self, *args, **kwargs):
        raise NotImplementedError()

    def lr_factors(self) -> Dict[str, Factor]:
        return {
            'embedding': Factor(factor=0.1, max_val=1e-4),
            'crf': Factor(factor=1000, max_val=5e-2),
        }

    @classmethod
    def load(cls, path_or_key: str, use_gpu = True):
        if inspect.isabstract(cls):
            raise TailorsError(f"Not supported call from abstract class: {cls.__name__}")

        if ".local" in path_or_key:  # do not use SEQUE_CONFIG, since it's not called in this lib project
            hao.oss.init(path_or_key[: path_or_key.rfind(".")])
            model_path = hao.config.get_path(path_or_key)
        else:
            model_path = hao.paths.get_path(path_or_key)

        if model_path is None or not os.path.isfile(model_path):
            raise TailorsError(f"model not found: {model_path}")

        LOGGER.info(f"[{cls.__name__}] loading from: {model_path}")
        sw = Stopwatch()
        state_dict = torch.load(model_path)
        model = cls(state_dict.get('model_conf'))
        model.load_state_dict(state_dict.get('model_state_dict'))
        model.freeze()
        LOGGER.info(f"[{cls.__name__}] loaded, took: {sw.took()}")

        if use_gpu:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model.use_device(device)
        return model

    @abc.abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError()

    def export_to_model(self, output_path):
        is_dp_module = isinstance(self, (DistributedDataParallel, DataParallel))
        model = self.module if is_dp_module else self

        model.on_save_checkpoint()
        checkpoint = {'state_dict': model.state_dict(), 'model_conf': model.model_conf}
        hao.paths.make_parent_dirs(output_path)
        torch.save(checkpoint, output_path)

    def export_to_onnx(self, output_path):
        torch.onnx.export(
            self,
            self.io.empty_input,
            output_path,
            verbose=False,
            input_names=['input_ids', 'attention_mask', 'token_type_id'],
            output_names=['tag', 'score'],
            dynamic_axes={
                'input_ids': {0: 'batch'},  # 第0维是batch dimension
                'attention_mask': {0: 'batch'},  # 第0维是batch dimension
                'token_type_id': {0: 'batch'},  # 第0维是batch dimension
                'tag': {0: 'batch'},
                'score': {0: 'batch'},
            },
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
        )
        LOGGER.info(f'saved onnx to: {output_path}')

    @classmethod
    def to_model(cls, model_path, output_path=None):
        if model_path is None:
            raise TailorsError('empty output_path')
        model_path = hao.paths.get_path(model_path)
        if not os.path.exists(model_path):
            raise TailorsError(f'model_path not exist: {model_path}')

        model = cls.load(model_path)
        if output_path is None:
            path_base, _ = os.path.splitext(os.path.basename(model_path))
            output_path = hao.paths.get_path('data', 'model', f"{path_base}.bin")
        hao.paths.make_parent_dirs(output_path)
        model.export_to_model(output_path)
        return output_path

    @classmethod
    def to_onnx(cls, model_path, output_path=None):
        if model_path is None:
            raise TailorsError('empty output_path')
        model_path = hao.paths.get_path(model_path)
        if not os.path.exists(model_path):
            raise TailorsError(f'model_path not exist: {model_path}')

        model = cls.load(model_path)
        if output_path is None:
            path_base, _ = os.path.splitext(os.path.basename(model_path))
            output_path = hao.paths.get_path('data', 'model', f"{path_base}.onnx")
        hao.paths.make_parent_dirs(output_path)
        model.export_to_onnx(output_path)
        return output_path
