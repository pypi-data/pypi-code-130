# -*- coding: utf-8 -*-
import collections
import importlib
import math
import os
from datetime import datetime
from types import SimpleNamespace
from typing import Optional

import hao
import torch
import torchinfo
from hao.namespaces import attr, from_args
from tailors import move_to_device, off_tensor, set_seed
from tailors.exceptions import TailorsError
from tailors.metrics import classification_metrics
from tailors.models import Tailors
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from tailors_trainer import callbacks, losses, optimizers, schedulers
from tailors_trainer.data import DatasetConf, TailorDataset
from tailors_trainer.exceptions import StopTailorsTrainer

LOGGER = hao.logs.get_logger(__name__)


@from_args
class TrainConf:
    model: str = attr(str, required=True)
    corpus: str = attr(str, required=True)
    seed = attr(int, default=1000)
    max_epochs: int = attr(int, default=50)
    loss = attr(str, choices=tuple(losses.LOSSES))
    lr: float = attr(float, default=1e-4)
    optimizer = attr(str, choices=tuple(optimizers.OPTIMIZERS), default=list(optimizers.OPTIMIZERS)[0])
    weight_decay: float = attr(float, default=1e-2)
    scheduler: str = attr(str, choices=tuple(schedulers.SCHEDULERS), default=list(schedulers.SCHEDULERS)[0])
    clip_norm: float = attr(float, default=1.0, help='clip grad norm for NLP tasks, generally: 1.0')
    amp: bool = attr(bool, default=False)
    accumulation: int = attr(int, default=1)


@from_args
class TrainerConf:
    exp: str = attr(str, required=True)
    gpus: str = attr(str, help='gpu indices separated by comma, no spaces')
    logger: str = attr(str, default='tensorboard')
    log_summary: bool = attr(bool, default=True)
    resume_from: str = attr(str)
    early_stop_patience: int = attr(int, default=5)
    checkpoint_name: str = attr(str, default='{model}-{corpus}-{exp}-{ts}-epoch={epoch}-val_loss={loss_val}-f1={f1}.ckpt')
    save_top_n: int = attr(int, default=1)
    save_last: bool = attr(bool, default=False)


class TrainerState:
    def __init__(self) -> None:
        self.ts = datetime.now().strftime('%y%m%d-%H%M')
        self.bz = 0
        self.steps_per_epoch = {}
        self.epoch = -1
        self.batch_id = -1
        self.val_losses = []
        self.metrics = {}
        self.reports = {}
        self._ckpts = SimpleNamespace(top_n=[], last=None, should_save=False, new_path=None)
        self._resume_state_dict = None

    def set_metric(self, key, value):
        self.metrics[key] = value
        if key == 'loss/val':
            self.val_losses.append(value)

    def set_metrics(self, metrics: dict):
        for k, v in metrics.items():
            if 'report' in k.lower():
                self.reports[k] = v
            else:
                self.set_metric(k, v)

    def current_steps(self):
        return self.epoch * self.steps_per_epoch.get('train') + (self.batch_id + 1) * self.bz

    def state_dict(self):
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def load_state_dict(self, state_dict):
        for k, v in state_dict.items():
            setattr(self, k, v)


class Trainer:
    def __init__(self, trainer_conf: Optional[TrainerConf] = None, train_conf: Optional[TrainConf] = None) -> None:
        super().__init__()
        self.trainer_conf = trainer_conf or TrainerConf()
        self.train_conf = train_conf or TrainConf()
        LOGGER.info(self.trainer_conf)
        LOGGER.info(self.train_conf)
        self.device, self.rank, self.world_size = self.check_devices()
        self.state = TrainerState()
        self.callback_handler = callbacks.CallbackHandler(self.train_conf, self.trainer_conf, self.state)
        self.load_resume_from_state_dict()

        self.model: Tailors = self.get_model()
        self.dataloaders, self.state.steps_per_epoch = self.get_dataloaders()

        self.criteria = losses.get(self.train_conf.loss) if self.train_conf.loss else None
        self.scaler = self.get_scaler()
        self.optimizer = self.get_optimizer()
        self.scheduler = self.get_scheduler()

        self.go_thru_resume_from_state_dict()
        self.log_model_summary()

    def check_devices(self):
        gpus = [gpu for gpu in self.trainer_conf.gpus.split(',') if gpu and gpu.isdigit() and 0 <= int(gpu)]
        cuda_visible_devices = ','.join(gpus)
        os.environ['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices

        if self.trainer_conf.gpus is None or not torch.cuda.is_available():
            LOGGER.info(f"[device] {device}")
            return torch.device('cpu'), -1, -1

        n_devices = torch.cuda.device_count()
        gpus = [gpu for gpu in gpus if int(gpu) < n_devices]
        n_gpus = len(gpus)
        rank = 0
        device = torch.device(f"cuda:{rank}")
        LOGGER.info(f"[device] {device}, CUDA_VISIBLE_DEVICES={cuda_visible_devices}")
        return device, rank, n_gpus

    def load_resume_from_state_dict(self):
        checkpoint_path = hao.paths.get(self.trainer_conf.resume_from)
        if checkpoint_path is None or not os.path.isfile(checkpoint_path):
            return
        LOGGER.info(f"[resume from] {checkpoint_path}")
        self.state._resume_state_dict = torch.load(checkpoint_path)

    def go_thru_resume_from_state_dict(self):
        if self.state._resume_state_dict is None:
            return
        for key, attr in (
            ('state', 'state'),
            ('model_state_dict', 'model'),
            ('scaler_state_dict', 'scaler'),
            ('optimizer_state_dict', 'optimizer'),
            ('scheduler_state_dict', 'scheduler'),
        ):
            if (m := getattr(self, attr)) is None or (state_dict := self.state._resume_state_dict.get(key)) is None:
                continue
            m.load_state_dict(state_dict)

        self.state._resume_state_dict = None

    def get_model(self) -> Tailors:
        model_fqn = self.train_conf.model
        module_name, _, model_class_name = model_fqn.rpartition('.')
        module = importlib.import_module(module_name)
        model_class = getattr(module, model_class_name)

        if self.state._resume_state_dict is not None:
            model_conf = self.state._resume_state_dict.get('model_conf')
        else:
            model_conf_class = getattr(module, f"{model_class_name}Conf")
            meta = hao.config.get(f"corpora.{self.train_conf.corpus}", config='tailors.yml').get('meta')
            if meta is None or not isinstance(meta, dict) or len(meta) == 0:
                raise TailorsError(f"expecting `meta` dict in corpora.{self.train_conf.corpus}, in `tailors.yml`")
            model_conf = model_conf_class(meta=meta)
        model = model_class(model_conf).use_device(self.device)
        if self.world_size > 1:
            model = DistributedDataParallel(model, device_ids=[self.rank], output_device=self.rank)
        return model

    def get_dataloaders(self):
        datasets = hao.config.get(f"corpora.{self.train_conf.corpus}", config='tailors.yml').get('datasets')
        dataset_conf = DatasetConf()
        LOGGER.info(dataset_conf)
        self.state.bz = dataset_conf.bz
        dataloaders = {
            split: TailorDataset(self.model.io, self.train_conf.corpus, split, files, dataset_conf).dataloader()
            for split, files in datasets.items()
        }
        steps_per_epochs = {
            split: math.ceil(len(dataloader) / dataloader.batch_size)
            for split, dataloader in dataloaders.items()
        }
        return dataloaders, steps_per_epochs

    def get_scaler(self):
        return torch.cuda.amp.GradScaler() if self.train_conf.amp else None

    def get_optimizer(self):
        def get_bucket(name):
            for key in rates:
                if name.startswith(key):
                    return key
            return 'default'

        rates = {name: f.apply(self.train_conf.lr) for name, f in self.model.lr_factors().items()}

        no_decay = ['bias', 'gamma', 'beta', 'LayerNorm.weight', 'LayerNorm.bias']
        no_decay_suffix = '_no_decay'
        groups_default, groups_named, group_meta = collections.defaultdict(list), collections.defaultdict(list), dict()
        for n, p in self.model.named_parameters():
            if len(p) == 0:
                continue
            bucket = get_bucket(n)
            is_no_decay = any(nd in n for nd in no_decay)
            groups = groups_default if bucket == 'default' else groups_named
            key = f"{bucket}{no_decay_suffix}" if is_no_decay else bucket
            groups[key].append(p)
            if key not in group_meta:
                weight_decay = 0 if is_no_decay else self.train_conf.weight_decay
                lr = rates.get(bucket, self.train_conf.lr)
                group_meta[key] = {'weight_decay': weight_decay, 'lr': lr, 'name': key}

        grouped_parameters = []
        for key, params in groups_default.items():
            grouped_parameters.append({'params': params, **group_meta.get(key)})
        for key, params in groups_named.items():
            grouped_parameters.append({'params': params, **group_meta.get(key)})
        return optimizers.get(self.train_conf.optimizer, grouped_parameters)

    def get_scheduler(self):
        return schedulers.get(self.train_conf.scheduler, self.optimizer, steps_per_epoch=self.state.steps_per_epoch.get('train'))

    def log_model_summary(self):
        if self.trainer_conf.log_summary:
            summary = torchinfo.summary(self.model, col_names=('num_params', 'trainable'), mode='train', row_settings=('ascii_only',), verbose=0)
            LOGGER.info(f"[summary] {self.train_conf.model}\n{summary}")

    def get_lr(self):
        if hasattr(self.scheduler, 'get_lr'):
            return self.scheduler.get_lr()
        return self.get_lrs()[0]

    def get_lrs(self):
        return [group["lr"] for group in self.optimizer.param_groups]

    def fit(self):
        self.callback_handler.on_fit_start()
        try:
            dataloader_train, dataloader_val = self.dataloaders.get('train'), self.dataloaders.get('val')
            for epoch in range(self.state.epoch + 1, self.train_conf.max_epochs):
                self.state.epoch = epoch
                self.callback_handler.on_epoch_start()
                self.train_epoch(epoch, dataloader_train)
                self.val_epoch(epoch, dataloader_val)
                self.lr_scheduler_step()
                self.log_metrics()
                self.callback_handler.on_epoch_end()
                self.save_if_should()
        except StopTailorsTrainer:
            pass
        except KeyboardInterrupt:
            print('ctrl-c')
        finally:
            self.callback_handler.on_fit_end()
            self.save_model()

    def train_epoch(self, epoch: int, dataloader: DataLoader):
        self.model.train()
        self.callback_handler.on_train_epoch_start()
        losses = []
        acc = max(1, self.train_conf.accumulation)
        with logging_redirect_tqdm():
            batches = tqdm(dataloader, desc=f"[epoch {epoch}] training  ", ascii='―━', colour='blue')
            for batch_id, (data, target) in enumerate(batches):
                self.state.batch_id = batch_id
                self.callback_handler.on_train_batch_start()

                data, target = move_to_device(data, self.model.device), move_to_device(target, self.model.device)
                is_optimizer_step = acc == 1 or ((batch_id + 1) % acc == 0) or (batch_id + 1 == self.state.steps_per_epoch.get('train'))

                if self.scaler:
                    with torch.cuda.amp.autocast(True):
                        encoded = self.model.encode(data)
                        decoded = self.model.decode(encoded)
                        loss = self.compute_loss(encoded, decoded, target)
                        loss = loss / acc
                    self.scaler.scale(loss).backward()
                    loss = loss.item()
                    losses.append(loss)
                    if self.train_conf.clip_norm > 0:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.train_conf.clip_norm)
                    if is_optimizer_step:
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                        self.optimizer.zero_grad(set_to_none=True)
                        batches.set_postfix({'loss': f"{loss:.4f}", 'ts': self.state.ts})

                else:
                    encoded = self.model.encode(data)
                    decoded = self.model.decode(encoded)
                    loss = self.compute_loss(encoded, decoded, target)
                    loss = loss / acc
                    loss.backward()
                    loss = loss.item()
                    losses.append(loss)
                    if self.train_conf.clip_norm > 0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.train_conf.clip_norm)
                    if is_optimizer_step:
                        self.optimizer.step()
                        self.optimizer.zero_grad(set_to_none=True)
                        batches.set_postfix({'loss': f"{loss:.4f}", 'ts': self.state.ts})
                self.state.set_metric('loss/batch', loss)

                self.callback_handler.on_train_batch_end()

        self.state.set_metric('loss/train', sum(losses) / len(losses))
        self.callback_handler.on_train_epoch_end()

    def val_epoch(self, epoch: int, dataloader: DataLoader):
        def append_batch_result(items, batch):
            batch = off_tensor(batch)
            if isinstance(batch, tuple):
                hao.lists.add_tuple_to_list(items, batch)
            else:
                items.extend(batch)

        self.model.eval()
        self.callback_handler.on_val_epoch_start()
        losses, preds, targets = [], [], []
        with logging_redirect_tqdm(), torch.no_grad():
            batches = tqdm(dataloader, desc=f"[epoch {epoch}] validating", ascii='―━', colour='green')
            for batch_id, (data, target) in enumerate(batches):
                self.state.batch_id = batch_id
                self.callback_handler.on_eval_batch_start()

                data, target = move_to_device(data, self.model.device), move_to_device(target, self.model.device)
                encoded = self.model.encode(data)
                decoded = self.model.decode(encoded)
                loss = self.compute_loss(encoded, decoded, target)
                loss = loss.item()
                losses.append(loss)
                append_batch_result(preds, decoded)
                append_batch_result(targets, target)
                batches.set_postfix({'loss': f"{loss:.4f}", 'ts': self.state.ts})

                self.callback_handler.on_eval_batch_end()

        self.state.set_metric('loss/val', sum(losses) / len(losses))
        self.compute_metrics(preds, targets)
        self.callback_handler.on_val_epoch_end()

    def compute_loss(self, encoded, decoded, target):
        criteria = getattr(self.model, 'compute_loss', None)
        if criteria:
            return criteria(encoded, decoded, target)
        else:
            x = encoded[0] if isinstance(encoded, tuple) else encoded
            y = target[0] if isinstance(target, tuple) else target
            return self.criteria(x.view(-1, self.model.io.tags.n_tags), y.view(-1))  # ce

    def compute_metrics(self, preds, targets):
        if hasattr(self.model, 'compute_metrics'):
            metrics = getattr(self.model, 'compute_metrics')(preds, targets)
        else:
            metrics = classification_metrics.calculate(preds[0], targets[0])
        self.state.set_metrics(metrics)

    def lr_scheduler_step(self):
        scheduler_args = {'metrics': self.state.metrics.get('loss/train'), 'epoch': self.state.epoch}
        hao.invoker.invoke(self.scheduler.step, **scheduler_args)

        # get the new lrs
        lrs = self.get_lrs()
        self.state.set_metrics({'lr': lrs[0], 'lrs': lrs})

    def log_metrics(self):
        width = max([len(k) for k, _ in self.state.metrics.items()]) + 1
        metrics = '\n'.join([f"\t{k: <{width}}: {v}" for k, v in self.state.metrics.items()])
        LOGGER.info(f"{' metrics '.center(50, '━')}\n{metrics}")
        for k, v in self.state.reports.items():
            LOGGER.info(f"{f' {k} '.center(50, '━')}\n{v}")

    def save_if_should(self):
        if self.state._ckpts.should_save:
            self.model.on_save_checkpoint()
            self.state._ckpts.path_new = self.save()
            self.callback_handler.on_save_checkpoint()
            self.state._ckpts.should_save = False

    def save(self, name: Optional[str] = None):
        state_dict = {
            'train_conf': self.train_conf,
            'model_conf': self.model.model_conf,
            'state': self.state.state_dict(),
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
        }
        if self.scaler:
            state_dict['scaler_state_dict'] = self.scaler.state_dict()
        params = {
            'model': self.model.__class__.__name__,
            'corpus': self.train_conf.corpus,
            'exp': self.trainer_conf.exp or 'na',
            'epoch': self.state.epoch,
            'ts': self.state.ts,
            **{k.replace('/', '_'): f"{v:.4f}" for k, v in self.state.metrics.items() if isinstance(v, (str, int, float, bool))},
        }
        checkpoint_name = name or self.trainer_conf.checkpoint_name
        filename = checkpoint_name.format(**params)
        path = hao.paths.get('data/checkpoints/', filename)
        hao.paths.make_parent_dirs(path)
        torch.save(state_dict, path)
        LOGGER.debug(f"saved checkpoint: {path}")
        return path

    def save_model(self):
        if self.state.epoch <= 0:
            return
        checkpoint_path = self.state._ckpts.top_n[0][1]
        if not os.path.isfile(checkpoint_path):
            return
        path_base, _ = os.path.splitext(os.path.basename(checkpoint_path))
        model_path = hao.paths.get_path('data', 'model', f"{path_base}.bin")
        self.model.export_to_model(model_path)
        LOGGER.info(f"saved model: {model_path}")
