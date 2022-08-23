# -*- coding: utf-8 -*-
import os
import sys
import warnings

import hao
import regex

from tailors_trainer.exceptions import TailorsTrainerError
from tailors_trainer.trainer import Trainer

warnings.filterwarnings("ignore")
LOGGER = hao.logs.get_logger(__name__)


def log_cmdline():
    cmdline = " \\\n\t".join(hao.regexes.split_with_sep(' '.join(sys.argv[1:]), regex.compile(r'\s+\-'), False))
    LOGGER.info(f"\n{'━' * 50}\ntailors-train \\\n\t{cmdline}\n{'━' * 50}")


def set_envs():
    # ignore tokenizer fork warning
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'

def train():
    try:
        log_cmdline()
        trainer = Trainer()
        set_envs()
        trainer.fit()
    except KeyboardInterrupt:
        print("[ctrl-c] stopped")
    except TailorsTrainerError as err:
        LOGGER.error(err)
    except Exception as err:
        LOGGER.exception(err)


if __name__ == "__main__":
    train()
