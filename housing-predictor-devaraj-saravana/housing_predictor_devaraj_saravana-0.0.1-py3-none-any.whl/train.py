import argparse
import logging
import os
import pickle

import pandas as pd
from scipy.stats import randint
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.tree import DecisionTreeRegressor

if __name__ == "__main__":

    PATH = os.path.dirname(os.path.abspath(__file__))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

    file_handler = logging.FileHandler(os.path.join(PATH, "../logs/train.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    parser = argparse.ArgumentParser(
        description="train the models with prepared dataset"
    )
    parser.add_argument(
        "-x",
        "--depend",
        type=str,
        metavar="",
        nargs="?",
        default="housing_prepared.csv",
    )

    parser.add_argument(
        "-y",
        "--independ",
        type=str,
        metavar="",
        nargs="?",
        default="housing_labels.csv",
    )

    args = parser.parse_args()

    def load_train_data():
        housing_prepared = pd.read_csv(
            os.path.join(os.path.join(PATH, "../data/processed/"), args.depend)
        )
        logger.debug(
            "prepared dataset LOADED from {}".format(
                os.path.join(
                    os.path.join(PATH, "../data/processed/"), args.depend
                )
            )
        )
        housing_labels = pd.read_csv(
            os.path.join(
                os.path.join(PATH, "../data/processed/"), args.independ
            )
        )
        logger.debug(
            "prepared dataset labels LOADED from {}".format(
                os.path.join(
                    os.path.join(PATH, "../data/processed/"), args.independ
                )
            )
        )
        return housing_prepared, housing_labels

    housing_prepared, housing_labels = load_train_data()

    if __name__ == "__main__":

        def train(housing_prepared, housing_labels):

            # Linear Regression
            lin_reg = LinearRegression()
            lin_reg.fit(housing_prepared, housing_labels)
            with open(
                os.path.join(PATH, "../deploy/conda/linear_reg.pkl"), "wb"
            ) as f:
                pickle.dump(lin_reg, f)
            logger.debug(
                "trained linear regression model STORED in {}".format(
                    (os.path.join(PATH, "../deploy/conda/linear_reg.pkl"))
                )
            )
            # #DecisionTree Regression
            tree_reg = DecisionTreeRegressor(random_state=42)
            tree_reg.fit(housing_prepared, housing_labels)

            with open(
                os.path.join(PATH, "../deploy/conda/tree_reg.pkl"), "wb"
            ) as f:
                pickle.dump(tree_reg, f)
            logger.debug(
                "trained DecisionTree regressor model STORED in {}".format(
                    (os.path.join(PATH, "../deploy/conda/tree_reg.pkl"))
                )
            )
            # #RandomizedSearchCV in RandomForest
            param_distribs = {
                "n_estimators": randint(low=1, high=200),
                "max_features": randint(low=1, high=8),
            }

            forest_reg = RandomForestRegressor(random_state=42)
            rnd_search = RandomizedSearchCV(
                forest_reg,
                param_distributions=param_distribs,
                n_iter=10,
                cv=5,
                scoring="neg_mean_squared_error",
                random_state=42,
            )
            rnd_search.fit(housing_prepared, housing_labels.values.ravel())

            with open(
                os.path.join(PATH, "../deploy/conda/rnd_search_forest.pkl"),
                "wb",
            ) as f:
                pickle.dump(rnd_search, f)
            logger.debug(
                "trained RandomizedSearchCV in RandomForest model\
                    STORED in {}".format(
                    (
                        os.path.join(
                            PATH, "../deploy/conda/rnd_search_forest.pkl"
                        )
                    )
                )
            )
            # GridSearchCV in RandomForest
            param_grid = [
                {"n_estimators": [3, 10, 30], "max_features": [2, 4, 6, 8]},
                {
                    "bootstrap": [False],
                    "n_estimators": [3, 10],
                    "max_features": [2, 3, 4],
                },
            ]

            forest_reg = RandomForestRegressor(random_state=42)
            grid_search = GridSearchCV(
                forest_reg,
                param_grid,
                cv=5,
                scoring="neg_mean_squared_error",
                return_train_score=True,
            )
            grid_search.fit(housing_prepared, housing_labels.values.ravel())

            with open(
                os.path.join(PATH, "../deploy/conda/final_model.pkl"), "wb"
            ) as f:
                pickle.dump(grid_search, f)
            logger.debug(
                "trained GridSearchCV in RandomForest\
                     model STORED in {}".format(
                    (os.path.join(PATH, "../deploy/conda/final_model.pkl"))
                )
            )

        train(housing_prepared, housing_labels)
