from typing import Dict
from pydantic import BaseModel, Field


class TrainingConfig(BaseModel):
    batch_size: int
    epochs: int
    n_workers: int

    model_size: int
    lr_factor: int
    lr_warm_up: int
    clip_norm: float = 1.0

    def get_optimizer_config(self) -> Dict:
        return {
            "model_size": self.model_size,
            "lr_factor": self.lr_factor,
            "warmup": self.lr_warm_up
        }


class TrainingStatus(BaseModel):
    train_loss_epoch_mean: Dict[int, float] = Field(default_factory=dict)
    valid_loss_epoch_mean: Dict[int, float] = Field(default_factory=dict)

    step_record: int = 0
    epoch_record: int = 0
