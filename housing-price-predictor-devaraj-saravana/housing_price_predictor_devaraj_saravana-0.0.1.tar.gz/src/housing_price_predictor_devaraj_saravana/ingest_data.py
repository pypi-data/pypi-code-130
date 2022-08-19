import argparse
import logging
import os.path
import tarfile

import numpy as np
import pandas as pd
from six.moves import urllib
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedShuffleSplit

if __name__ == "__main__":

    PATH = os.path.dirname(os.path.abspath(__file__))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

    file_handler = logging.FileHandler(
        os.path.join(PATH, "../logs/ingest_data.log")
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    parser = argparse.ArgumentParser(
        description="download and create training and validation datasets"
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        metavar="raw/processed",
        nargs="?",
        default="raw",
    )
    args = parser.parse_args()

DOWNLOAD_ROOT = "https://raw.githubusercontent.com/ageron/handson-ml/master/"
HOUSING_URL = DOWNLOAD_ROOT + "datasets/housing/housing.tgz"
HOUSING_PATH = os.path.join("../data/", args.path)


def fetch_housing_data(housing_url=HOUSING_URL, housing_path=HOUSING_PATH):
    os.makedirs(housing_path, exist_ok=True)
    tgz_path = os.path.join(housing_path, "housing.tgz")
    urllib.request.urlretrieve(housing_url, tgz_path)
    housing_tgz = tarfile.open(tgz_path)
    housing_tgz.extractall(path=housing_path)
    housing_tgz.close()
    logger.debug(
        "downloaded dataset STORED in {}".format(os.path.join(PATH, args.path))
    )


fetch_housing_data()


def load_housing_data(housing_path=HOUSING_PATH):
    csv_path = os.path.join(housing_path, "housing.csv")
    return pd.read_csv(csv_path)


housing = load_housing_data()
logger.debug(
    "dataset LOADED from {}".format(os.path.join(HOUSING_PATH, "housing.csv"))
)

housing["income_cat"] = pd.cut(
    housing["median_income"],
    bins=[0.0, 1.5, 3.0, 4.5, 6.0, np.inf],
    labels=[1, 2, 3, 4, 5],
)


def train_test_split(data=housing):
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(data, data["income_cat"]):
        strat_train_set = data.loc[train_index]
        strat_test_set = data.loc[test_index]

    for set_ in (strat_train_set, strat_test_set):
        set_.drop("income_cat", axis=1, inplace=True)

    strat_test_set.to_csv(
        os.path.join(PATH, "../data/raw/test_set.csv"),
        index=False,
        encoding="utf-8",
    )
    logger.debug(
        "testing dataset STORED in {}".format(
            os.path.join(PATH, "../data/raw/test_set.csv")
        )
    )
    strat_train_set.to_csv(
        os.path.join(PATH, "../data/raw/train_set.csv"),
        index=False,
        encoding="utf-8",
    )
    logger.debug(
        "training dataset STORED in {}".format(
            os.path.join(PATH, "../data/raw/train_set.csv")
        )
    )
    return strat_train_set, strat_test_set


strat_train_set, strat_test_set = train_test_split()


def data_preparation(train=strat_train_set):

    strat_train_set = train

    housing = strat_train_set.drop("median_house_value", axis=1)
    housing_num = housing.drop("ocean_proximity", axis=1)

    imputer = SimpleImputer(strategy="median")
    imputer.fit(housing_num)
    X = imputer.transform(housing_num)

    housing_tr = pd.DataFrame(
        X, columns=housing_num.columns, index=housing.index
    )
    housing_tr["rooms_per_household"] = (
        housing_tr["total_rooms"] / housing_tr["households"]
    )
    housing_tr["bedrooms_per_room"] = (
        housing_tr["total_bedrooms"] / housing_tr["total_rooms"]
    )
    housing_tr["population_per_household"] = (
        housing_tr["population"] / housing_tr["households"]
    )
    housing_cat = housing[["ocean_proximity"]]
    housing_prepared = housing_tr.join(
        pd.get_dummies(housing_cat, drop_first=True)
    )

    return housing_prepared, housing_cat


housing_prepared, housing_labels = data_preparation(strat_train_set)

housing_prepared.to_csv(
    os.path.join(PATH, "../data/processed/housing_prepared.csv"),
    index=False,
    encoding="utf-8",
)
logger.debug(
    "prepared dataset STORED in {}".format(
        os.path.join(PATH, "../data/processed/housing_prepared.csv")
    )
)
housing_labels = strat_train_set["median_house_value"].copy()
housing_labels.to_csv(
    os.path.join(PATH, "../data/processed/housing_labels.csv"),
    index=False,
    encoding="utf-8",
)
logger.debug(
    "prepared dataset labels STORED in {}".format(
        os.path.join(PATH, "../data/processed/housing_labels.csv")
    )
)
