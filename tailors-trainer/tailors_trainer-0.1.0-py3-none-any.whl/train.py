# -*- coding: utf-8 -*-
import os
import random
import sys
import warnings

import hao
import regex
import torch.backends.cudnn

from tailors_trainer.exceptions import TailorsTrainerError
from tailors_trainer.trainer import TrainConf, Trainer

warnings.filterwarnings("ignore")
LOGGER = hao.logs.get_logger(__name__)


def log_cmdline():
    cmdline = " \\\n\t".join(hao.regexes.split_with_sep(' '.join(sys.argv[1:]), regex.compile(r'\s+\-'), False))
    LOGGER.info(f"\n{'━' * 50}\ntailors-train \\\n\t{cmdline}\n{'━' * 50}")


def train():
    train_conf = TrainConf()
    LOGGER.info(train_conf)

    set_seed(train_conf.seed)
    trainer = Trainer(train_conf)
    trainer.fit()


def set_seed(seed):
    if seed is None:
        seed = random.randint(0, 10000)
        LOGGER.info(f"[seed] using random generated seed: {seed}")
    else:
        LOGGER.info(f"[seed] using random seed: {seed}")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


if __name__ == "__main__":
    try:
        log_cmdline()
        train()
    except KeyboardInterrupt:
        print("[ctrl-c] stopped")
    except TailorsTrainerError as err:
        LOGGER.error(err)
    except Exception as err:
        LOGGER.exception(err)
