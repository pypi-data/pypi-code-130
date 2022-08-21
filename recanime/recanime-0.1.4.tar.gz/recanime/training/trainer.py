import logging
from typing import Text
from tqdm import tqdm

import torch
import numpy as np
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from torch.optim import optimizer
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast


from recanime.schema.training import TrainingStatus


logger = logging.getLogger(__name__)


class NoamOpt():
    "Optim wrapper that implements rate."
    def __init__(
        self,
        model_size: int,
        lr_factor: float,
        warmup: int,
        optimizer: optimizer.Optimizer
    ):
        self.optimizer = optimizer
        self._step = 0
        self.warmup = warmup
        self.lr_factor = lr_factor
        self.model_size = model_size
        self._rate = 0
    
    @property
    def param_groups(self):
        return self.optimizer.param_groups
        
    def multiply_grads(self, c):
        """Multiplies grads by a constant *c*."""                
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is not None:
                    p.grad.data.mul_(c)
        
    def step(self):
        "Update parameters and rate"
        self._step += 1
        rate = self.rate()
        for p in self.param_groups:
            p['lr'] = rate
        self._rate = rate
        self.optimizer.step()
        
    def rate(self, step = None):
        "Implement `lrate` above"
        if step is None:
            step = self._step
        return 0 if not step else self.lr_factor * \
            (self.model_size ** (-0.5) *
            min(step ** (-0.5), step * self.warmup ** (-1.5)))


class ModelTrainer():
    def __init__(
        self,
        train_loader: DataLoader,
        valid_loader: DataLoader,
        model: nn.Module,
        loss_criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: Text,
        training_status: TrainingStatus = TrainingStatus(),
        model_save_path: Text = "./model/model.pt"
    ) -> None:
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.training_status = training_status
        self.model = model.to(device=device)
        self.loss_criterion = loss_criterion.to(device=device)
        self.optimizer = optimizer
        self.optimizer._step = self.training_status.step_record
        self.epoch = self.training_status.epoch_record
        self.step = self.training_status.step_record
        self.device = device
        self.model_save_path = model_save_path
        self.min_loss = float('inf')
    
    def training_one_epoch(self) -> None:
        self.epoch += 1
        self.model.train()
        loss_step = []
        progress = tqdm(self.train_loader, desc=f"train epoch {self.epoch}", leave=True)
        for data in progress:
            self.step += 1
            self.model.zero_grad()
            scaler = GradScaler()
            data = [i.to(self.device) for i in data]
            accum_loss = 0
            src = data[0]
            tgt = data[1]
            
            with autocast(): 
                out = self.model(src)
                loss = self.loss_criterion(out, tgt)
                # logging
                accum_loss += loss.item()
                # back-prop
                scaler.scale(loss).backward()
                
            scaler.unscale_(self.optimizer)
            scaler.step(self.optimizer)
            scaler.update()
            
            # self.step += 1
            # data = [i.to(self.device) for i in data]
            # src = data[0]
            # tgt = data[1]
            # out = self.model(src)
            # loss = self.loss_criterion(out, tgt)
            # self.model.zero_grad()
            # loss.backward()
            # self.optimizer.step()
            # accum_loss = loss.item()
            
            # logging
            loss_print = accum_loss
            loss_step.append(loss_print)
            progress.set_postfix({'loss': loss_print, 'step': self.step})
            
        loss_epoch_mean = np.mean(loss_step)
        self.training_status.train_loss_epoch_mean[self.epoch] = loss_epoch_mean
        logger.info(f"training loss: {loss_epoch_mean:.4f}")
        valid_loss = self._validation()
        self._training_checkpoint(valid_loss)
    
    def _validation(self) -> float:
        loss_step = []
        self.model.eval()

        with torch.no_grad():
            for data in tqdm(self.valid_loader, desc=f"validation epoch {self.epoch}", leave=True):
                data = [i.to(self.device) for i in data]
                accum_loss = 0
                
                src = data[0]
                tgt = data[1]
                
                out = self.model(src)
                loss = self.loss_criterion(out, tgt)
                # logging
                accum_loss += loss.item()
                loss_print = accum_loss
                loss_step.append(loss_print)
            
        loss_epoch_mean = np.mean(loss_step)
        self.training_status.valid_loss_epoch_mean[self.epoch] = loss_epoch_mean
        logger.info(f"validation loss: {loss_epoch_mean:.4f}")

        return loss_epoch_mean
    
    def _training_checkpoint(self, loss: float) -> None:
        if loss < self.min_loss:
            self.min_loss = loss
            torch.save(self.model.state_dict(), self.model_save_path)
            logger.info(f"Save the model.")
    
    def test(self, test_loader: DataLoader) -> float:
        loss_step = []
        self.model.eval()
        roc_targets, roc_predicts = [], []

        with torch.no_grad():
            for data in tqdm(test_loader, desc=f"test epoch {self.epoch}", leave=True):
                data = [i.to(self.device) for i in data]
                accum_loss = 0
                
                src = data[0]
                tgt = data[1]
                
                out = self.model(src)
                loss = self.loss_criterion(out, tgt)
                # logging
                accum_loss += loss.item()
                loss_print = accum_loss
                loss_step.append(loss_print)
            
                roc_predicts.extend(out.tolist())
                roc_targets.extend(tgt.tolist())
            
        loss_epoch_mean = np.mean(loss_step)
        model_score = roc_auc_score(roc_targets, roc_predicts)
        logger.info(f"Testing loss: {loss_epoch_mean:.4f}")
        logger.info(f"ROC AUC score: {model_score:.4f}")

        return loss_epoch_mean, model_score
    
    def export_training_status(self) -> TrainingStatus:
        self.training_status.epoch_record = self.epoch
        self.training_status.step_record = self.step
        
        return self.training_status