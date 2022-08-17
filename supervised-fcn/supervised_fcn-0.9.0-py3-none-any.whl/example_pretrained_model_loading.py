import pandas as pd
import torch
from supervised_FCN.models.fcn import FCNBaseline
from utils import root_dir


def load_pretrained_FCN(subset_dataset_name: str, in_channels: int = 1):
    """
    load a pretrained FCN (Fully Convolutional Network)
    :param subset_dataset_name:
    :param in_channels: 1; univariate for the UCR subset datasets.
    :return:
    """
    ucr_summary = pd.read_csv(root_dir.joinpath('datasets', 'DataSummary_UCR.csv'))
    q = ucr_summary.query(f"Name == '{subset_dataset_name}'")
    n_classes = q['Class'].iloc[0]

    # build
    fcn = FCNBaseline(in_channels, n_classes)

    # load
    ckpt_fname = root_dir.joinpath('supervised_FCN', 'saved_models', f'{subset_dataset_name}.ckpt')
    fcn.load_state_dict(torch.load(ckpt_fname))
    return fcn


if __name__ == '__main__':
    fcn = load_pretrained_FCN('Adiac')
    print(fcn)
