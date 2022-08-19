# -*- coding: utf-8 -*-
import os
from typing import List

import hao
from hao.namespaces import attr, from_args
from hao.singleton import Singleton
from tailors.models import TailorsIO
from torch.utils.data import Dataset
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm

LOGGER = hao.logs.get_logger(__name__)


@from_args
class DatasetConf(metaclass=Singleton):
    shuffle: bool = attr(bool, default=True)
    drop_last: bool = attr(bool, default=True)
    bz = attr(int, default=128)
    pin_mem: bool = attr(bool, default=True)
    n_workers = attr(int, default=0)


class TailorDataset(Dataset):
    def __init__(self, io: TailorsIO, name: str, split: str, files: List[str], dataset_conf: DatasetConf) -> None:
        super().__init__()
        self.io = io
        self.name = name
        self.split = split
        self.files = files if isinstance(files, list) else [files]
        self.items = []
        self.dataset_conf = dataset_conf

    def load(self):
        self.items = list(self.from_files())
        LOGGER.info(f"[{self.split}] {self.__len__()}")
        return self

    def from_files(self):
        for file in self.files:
            yield from self.from_file(file)

    def from_file(self, file):
        file = hao.paths.get(file)
        if not os.path.exists(file):
            LOGGER.warning(f"[dataset] file not found: {file}")
            return
        n_lines = hao.files.count_lines(file)
        with open(file, "r") as f:
            for line in tqdm(f, total=n_lines, desc=f"[dataset] {os.path.basename(file): <20}", ascii='░▒▓', colour='cyan'):
                line = hao.strings.strip_to_none(line)
                if line is None:
                    continue
                items = self.from_line(line)
                for item in items:
                    yield item

    def from_line(self, line: str):
        return self.io.from_line(line)

    def __getitem__(self, index: int):
        return self.items[index]

    def __len__(self) -> int:
        return len(self.items)

    def dataloader(self):
        return DataLoader(
            self.load(),
            batch_size=self.dataset_conf.bz,
            num_workers=self.dataset_conf.n_workers,
            pin_memory=self.dataset_conf.pin_mem,
            drop_last=self.dataset_conf.drop_last,
            shuffle=self.dataset_conf.shuffle,
            collate_fn=self.io.collate,
        )





