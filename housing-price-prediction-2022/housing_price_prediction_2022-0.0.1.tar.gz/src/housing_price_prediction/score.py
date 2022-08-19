import argparse
import logging
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error

PATH = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(os.path.join(PATH, "../logs/score.log"))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def prepare(data):
    X_num = data.drop("ocean_proximity", axis=1)
    imputer = SimpleImputer(strategy="median")
    imputer.fit(X_num)

    X_imputed = imputer.transform(X_num)

    X_tr = pd.DataFrame(X_imputed, columns=X_num.columns, index=data.index)

    X_tr["rooms_per_household"] = X_tr["total_rooms"] / X_tr["households"]
    X_tr["bedrooms_per_room"] = X_tr["total_bedrooms"] / X_tr["total_rooms"]
    X_tr["population_per_household"] = X_tr["population"] / X_tr["households"]
    X_cat = data[["ocean_proximity"]]
    X_final = X_tr.join(pd.get_dummies(X_cat, drop_first=True))
    return X_final


parser = argparse.ArgumentParser(
    description="load model and predict some values"
)
parser.add_argument(
    "-m",
    "--model",
    type=str,
    metavar="",
    nargs="?",
    default="final_model.pkl",
)

parser.add_argument(
    "-d",
    "--dataset",
    type=str,
    metavar="",
    nargs="?",
    default="test_set.csv",
)
args = parser.parse_args()

filename = parser.parse_args().model
with open(os.path.join(PATH, "../deploy/conda", filename), "rb") as f:
    trained_model = pickle.load(f)

if trained_model == "final_model.pkl":
    model = trained_model
    model = model.best_estimator_
else:
    model = trained_model
logger.debug(
    "trained model LOADED from {}".format(
        os.path.join(PATH, "../deploy/conda", filename)
    )
)

dataset = pd.read_csv(
    os.path.join(PATH, "../data/raw", parser.parse_args().dataset)
)
logger.debug(
    "dataset LOADED from {}".format(
        os.path.join(PATH, "../data/raw", parser.parse_args().dataset)
    )
)


def score_metrics(data=dataset):
    x = data.drop("median_house_value", axis=1)
    y = data["median_house_value"].copy()

    x_prepared = prepare(x)

    predicted = model.predict(x_prepared)

    mse = mean_squared_error(predicted, y)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(predicted, y)
    logger.debug(" mse: {}, rmse: {}, mae: {}".format(mse, rmse, mae))
    return mse, rmse, mae


score_metrics()
