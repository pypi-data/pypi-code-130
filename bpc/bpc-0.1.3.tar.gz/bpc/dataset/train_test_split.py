import os
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold


def data_split(data, method, nsplits=10, splitsize=0.98, seed=42):
    """
    Split data into train and test sets.
    """
    if method == 'kfold':
        return kfold_split(data, nsplits=nsplits, fold=3, seed=seed)
    else:
        train_data = data.sample(frac=splitsize)
        val_test = data.drop(train_data.index)
        val_data = val_test.sample(frac=0.5)
        test_data = val_test.drop(val_data.index)
        return train_data, val_data, test_data

def kfold_split(data, nsplits=10, fold=3, seed=42):
    data = data.dropna()
    data = data.sample(frac=1).reset_index(drop=True)
    data['fold'] = -1
    y = data['spk']

    kf = StratifiedKFold(n_splits=nsplits, shuffle=True, random_state=seed)
    for f, (_, left) in enumerate(kf.split(data, y)):
        data.loc[left, 'fold'] = f

    train_data = data[data['fold'] != fold]
    val_test = data[data['fold'] == fold]
    val_data = val_test.sample(frac=0.6)
    test_data = val_test.drop(val_data.index)
    return train_data, val_data, test_data


def dataset(path, df):
    """
    Convert the csv to dataset.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    df = df.dropna()
    df = df.reset_index(drop=True)
    wav = df[['utt', 'wav']].copy()
    with open(os.path.join(path, 'wav.scp'), 'w') as f:
        for i in tqdm(range(len(wav)), desc=f'Writing {path}/wav.scp'):
            f.write(f"{wav.iloc[i, 0]} {wav.iloc[i, 1]}\n")
    utt2spk = df[['utt', 'spk']].copy()
    with open(os.path.join(path, 'utt2spk'), 'w') as f:
        for i in tqdm(range(len(utt2spk)), desc=f'Writing {path}/utt2spk'):
            f.write(f"{utt2spk.iloc[i, 0]} {utt2spk.iloc[i, 1]}\n")
    text = df[['utt', 'text']].copy()
    with open(os.path.join(path, 'text'), 'w') as f:
        for i in tqdm(range(len(text)), desc=f'Writing {path}/text'):
            f.write(f"{text.iloc[i, 0]} {text.iloc[i, 1]}\n")


