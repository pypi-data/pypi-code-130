# -*- coding: utf-8 -*-
import abc
import os
from typing import List

import hao
from tailors.domains import Derivable

import tailors_trainer
from tailors_trainer.exceptions import StopTailorsTrainer

LOGGER = hao.logs.get_logger(__name__)


class Callback(abc.ABC, Derivable):

    def __init__(self,
                 train_conf: 'tailors_trainer.trainer.TrainConf',
                 trainer_conf: 'tailors_trainer.trainer.TrainerConf',
                 state: 'tailors_trainer.trainer.TrainerState') -> None:
        super().__init__()
        self.train_conf = train_conf
        self.trainer_conf = trainer_conf
        self.state = state

    def on_fit_start(self):
        pass

    def on_fit_end(self):
        pass

    def on_epoch_start(self):
        pass

    def on_epoch_end(self):
        pass

    def on_train_epoch_start(self):
        pass

    def on_train_epoch_end(self):
        pass

    def on_val_epoch_start(self):
        pass

    def on_val_epoch_end(self):
        pass

    def on_test_epoch_start(self):
        pass

    def on_test_epoch_end(self):
        pass

    def on_train_batch_start(self):
        pass

    def on_train_batch_end(self):
        pass

    def on_eval_batch_start(self):
        pass

    def on_eval_batch_end(self):
        pass

    def on_test_batch_start(self):
        pass

    def on_test_batch_end(self):
        pass

    def on_save_checkpoint(self):
        pass

    def load_state_dict(self, state_dict):
        pass


class CallbackHandler:

    def __init__(self,
                 train_conf: 'tailors_trainer.trainer.TrainConf',
                 trainer_conf: 'tailors_trainer.trainer.TrainerConf',
                 state: 'tailors_trainer.trainer.TrainerState') -> None:
        self.train_conf = train_conf
        self.trainer_conf = trainer_conf
        self.state = state
        self.callbacks: List[Callback] = [clz(train_conf, trainer_conf, state) for clz in Callback.subclasses()]
        LOGGER.info(f"callbacks: {[f'{c.__class__.__name__}' for c in self.callbacks]}")

    def _on_event(self, event: str, **kwargs):
        for callback in self.callbacks:
            fn = getattr(callback, event, None)
            if fn is None:
                continue
            hao.invoker.invoke(fn, **kwargs)

    def on_fit_start(self):
        self._on_event('on_fit_start')

    def on_fit_end(self):
        self._on_event('on_fit_end')

    def on_epoch_start(self):
        self._on_event('on_epoch_start')

    def on_epoch_end(self):
        self._on_event('on_epoch_end')

    def on_train_epoch_start(self):
        self._on_event('on_train_epoch_start')

    def on_train_epoch_end(self):
        self._on_event('on_train_epoch_end')

    def on_val_epoch_start(self):
        self._on_event('on_val_epoch_start')

    def on_val_epoch_end(self):
        self._on_event('on_val_epoch_end')

    def on_test_epoch_start(self):
        self._on_event('on_test_epoch_start')

    def on_test_epoch_end(self):
        self._on_event('on_test_epoch_end')

    def on_train_batch_start(self):
        self._on_event('on_train_batch_start')

    def on_train_batch_end(self):
        self._on_event('on_train_batch_end')

    def on_eval_batch_start(self):
        self._on_event('on_eval_batch_start')

    def on_eval_batch_end(self):
        self._on_event('on_eval_batch_end')

    def on_test_batch_start(self):
        self._on_event('on_test_batch_start')

    def on_test_batch_end(self):
        self._on_event('on_test_batch_end')

    def on_save_checkpoint(self):
        self._on_event('on_save_checkpoint')

    def load_state_dict(self, state_dict):
        self._on_event('load_state_dict', state_dict)


class TensorboardWriterCallback(Callback):
    def __init__(self,
                 train_conf: 'tailors_trainer.trainer.TrainConf',
                 trainer_conf: 'tailors_trainer.trainer.TrainerConf',
                 state: 'tailors_trainer.trainer.TrainerState') -> None:
        from torch.utils.tensorboard import SummaryWriter
        super().__init__(train_conf, trainer_conf, state)
        self.writer = SummaryWriter(hao.paths.get(f"data/logs/{train_conf.model}", train_conf.corpus, trainer_conf.exp or state.exp_timestamp))

    def write_scalar(self, k, v, step=None):
        if not isinstance(v, (int, float)):
            return
        if step is None:
            step = self.epoch * self.steps_per_epoch_train
        self.writer.add_scalar(k, v, step)

    def on_train_batch_end(self):
        step = self.state.current_steps()
        self.write_scalar('loss/loss', self.state.metrics.get('loss/loss'), step)

    def on_epoch_end(self):
        step = self.state.current_steps()
        for k, v in self.state.metrics.items():
            self.write_scalar(k, v, step)


class EarlyStopCallback(Callback):
    def __init__(self,
                 train_conf: 'tailors_trainer.trainer.TrainConf',
                 trainer_conf: 'tailors_trainer.trainer.TrainerConf',
                 state: 'tailors_trainer.trainer.TrainerState') -> None:
        super().__init__(train_conf, trainer_conf, state)
        self.consec_increases = 0

    def should_stop(self):
        if self.state.epoch < 1:
            return False
        if self.state.val_losses[-1] <= self.state.val_losses[-2]:
            self.consec_increases = 0
            return False
        self.consec_increases += 1
        return self.consec_increases >= self.trainer_conf.early_stop_patience

    def on_epoch_end(self):
        if self.should_stop():
            LOGGER.info(f"[early-stop] val loss increased for {self.consec_increases} consecutive epochs")
            raise StopTailorsTrainer()


class CheckpointCallback(Callback):

    def on_epoch_end(self):
        if self.state.epoch == 0 or self.trainer_conf.save_last or self.state.val_losses[-1] <= self.state._ckpts.top_n[0][0]:
            self.state._ckpts.should_save = True

    def on_save_checkpoint(self):
        path_new = self.state._ckpts.path_new
        if path_new is None:
            return

        to_deletes = []
        if self.state.epoch == 0 or self.state.val_losses[-1] <= self.state.val_losses[-2]:
            i = self.get_insert_index()
            self.state._ckpts.top_n.insert(i, (self.state.val_losses[-1], path_new))
            while len(self.state._ckpts.top_n) > self.trainer_conf.save_top_n:
                _, path = self.state._ckpts.top_n.pop()
                to_deletes.append(path)
        if self.trainer_conf.save_last:
            if self.state._ckpts.last and all(self.state._ckpts.last != path for _, path in self.state._ckpts.top_n):
                to_deletes.append(self.state._ckpts.last)
            self.state._ckpts.last = path_new
        for to_delete in to_deletes:
            if os.path.isfile(to_delete):
                os.remove(to_delete)

        LOGGER.debug(self.top_n_msg())
        if self.trainer_conf.save_last:
            LOGGER.debug(f"[checkpoint] last: {self.state._ckpts.last}")

    def on_fit_end(self):
        LOGGER.info(self.top_n_msg())
        if self.trainer_conf.save_last:
            LOGGER.info(f"[checkpoint] last: {self.state._ckpts.last}")

    def top_n_msg(self):
        if len(self.state._ckpts.top_n) == 0:
            top_n = 'n/a'
        else:
            top_n = ''.join([f"\n\t[{i}] {p}" for i, (_, p) in enumerate(self.state._ckpts.top_n)])
        return f"[checkpoint] top n (n={self.trainer_conf.save_top_n}): {top_n}"

    def get_insert_index(self):
        if len(self.state._ckpts.top_n) == 0:
            return 0
        val_loss = self.state.val_losses[-1]
        for i, (loss, _) in enumerate(self.state._ckpts.top_n):
            if val_loss <= loss:
                return i
        return i + 1
