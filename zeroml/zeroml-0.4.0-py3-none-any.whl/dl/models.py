from torch import nn


def build_fastai_classification_head(in_features: int, out_features: int) -> nn.Module:
    """
    Improved classification head, similar to the one used in fastai baseline models.

    """
    return nn.Sequential(
        nn.BatchNorm1d(in_features, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True),
        nn.Dropout(p=0.25, inplace=False),
        nn.Linear(in_features=in_features, out_features=512, bias=True),
        nn.ReLU(inplace=True),
        nn.BatchNorm1d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True),
        nn.Dropout(p=0.5, inplace=False),
        nn.Linear(in_features=512, out_features=out_features, bias=True),
    )
