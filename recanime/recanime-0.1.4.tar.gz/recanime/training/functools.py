from typing import List, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from torch.utils.data import Dataset, DataLoader, random_split

from recanime.training.dataset import MyDataSet


def get_dataloader(
    dataset: Dataset,
    batch_size: int,
    n_workers: int,
    valid_ratio: float,
    test_ratio: float,
) -> Sequence[DataLoader]:
    """Generate dataloader"""
    # Split dataset into training dataset and validation dataset
    train_len = int((1 - valid_ratio - test_ratio) * len(dataset))
    valid_len = int(valid_ratio * len(dataset))
    test_len = len(dataset) - train_len - valid_len
    lengths = [train_len, valid_len, test_len]
    
    train_set, valid_set, test_set = random_split(dataset, lengths)
   
    train_loader = DataLoader(
        train_set,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=n_workers,
        pin_memory=True
    )
    
    valid_loader = DataLoader(
        valid_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=n_workers,
        drop_last=True,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=n_workers,
        drop_last=True,
        pin_memory=True
    )

    return train_loader, valid_loader, test_loader


def get_dataloader_df(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    batch_size: int,
    n_workers: int,
    valid_ratio: float,
    test_ratio: float,
) -> Sequence[DataLoader]:
    """Generate dataloader"""
    # Split dataset into training dataset and validation dataset
    data_len = len(df_x)
    train_len = int((1 - valid_ratio - test_ratio) * data_len)
    valid_len = int(valid_ratio * data_len)
    
    train_set = MyDataSet(df_x=df_x[:train_len], df_y=df_y[:train_len])
    valid_set = MyDataSet(
        df_x=df_x[train_len:train_len+valid_len],
        df_y=df_y[train_len:train_len+valid_len]
    )
    test_set = MyDataSet(
        df_x=df_x[train_len+valid_len:],
        df_y=df_y[train_len+valid_len:]
    )

    train_loader = DataLoader(
        train_set,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=n_workers,
        pin_memory=True
    )
    
    valid_loader = DataLoader(
        valid_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=n_workers,
        drop_last=True,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=n_workers,
        drop_last=True,
        pin_memory=True
    )

    return train_loader, valid_loader, test_loader


def training_loss_epoch_mean_visualization(
    epoch_x: List[int],
    train_loss_y: List[float],
    valid_loss_y: List[float]
):
    """Visualize the training history when training and validation loss
    share the same epoch_x dimension. 
    """
    plt.plot(epoch_x, train_loss_y, label = 'train loss')
    plt.plot(epoch_x, valid_loss_y, label = 'valid loss')
    plt.title("Loss History")
    plt.xlabel("Epoch Iteration")
    plt.ylabel("Loss")
    plt.legend(loc="best", ncol=2)
    plt.show()
    
    
def training_loss_epoch_mean_visualization_subplot(
    train_epoch_x: List[int],
    train_loss_y: List[float],
    valid_epoch_x: List[int],
    valid_loss_y: List[float]
):
    """Visualize the training history when training and validation loss
    has the different epoch dimension.
    """
    #TODO: Add indent between two fig

    fig, axs = plt.subplots(2,1)
    axs[0].plot(train_epoch_x, train_loss_y)
    axs[0].set_title("training loss")
    axs[0].set_xlabel("Epoch Iteration")
    axs[1].plot(valid_epoch_x, valid_loss_y)
    axs[1].set_title("validation loss")
    axs[1].set_xlabel("Epoch Iteration")