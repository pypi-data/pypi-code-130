import pathlib

import numpy as np
import PIL.Image
from albumentations.core.composition import Compose
from torch.utils.data import Dataset


class ImageClfAlbuDataset(Dataset):
    def __init__(
        self,
        df,
        base_path,
        transform: Compose,
        file_column="file_name",
        label_column="encoded_id",
    ):
        self.df = df
        self.file_column = file_column
        self.label_column = label_column
        self.transform = transform
        self.base_path = pathlib.Path(base_path)
        self.targets = df[label_column].tolist()

    def __len__(self):
        return len(self.df)

    def load(self, ix):
        f = self.base_path / self.df.iloc[ix][self.file_column]
        image = np.array(PIL.Image.open(f).convert("RGB"))
        label = self.df.iloc[ix][self.label_column]
        if self.transform is not None:
            image = self.transform(image=image)["image"]

        return image, label

    def __getitem__(self, ix):
        return self.load(ix)
