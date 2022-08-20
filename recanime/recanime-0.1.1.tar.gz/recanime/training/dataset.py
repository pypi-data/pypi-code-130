import torch
import pandas as pd
from torch.utils.data import Dataset


class MyDataSet(Dataset):
    def __init__(self, df_x: pd.DataFrame, df_y: pd.DataFrame) -> None:
        super().__init__()
        self.df_x = df_x.copy(deep=False)
        self.df_y = df_y.copy(deep=False)
        assert len(self.df_x) == len(self.df_y), "The length of x and y should be same."
    
    def __len__(self):
        return len(self.df_x)
    
    def __getitem__(self, index):
        return torch.LongTensor(self.df_x.iloc[index]), torch.FloatTensor(self.df_y.iloc[index])        