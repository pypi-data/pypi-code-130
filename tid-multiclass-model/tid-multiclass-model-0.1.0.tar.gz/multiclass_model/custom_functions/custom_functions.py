import collections
import itertools
import re

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def my_train_test_split_with_balance(data, test_size, n, threshold, seed):
    data["weigth_vector"] = data.groupby("Map_Product_Category").Inv_Id.transform(
        "count"
    )

    samples = list()
    for ind_target in data[
        data.weigth_vector >= threshold
    ].Map_Product_Category.unique():
        df = data[data.Map_Product_Category == ind_target].sample(
            n=n, random_state=seed
        )
        samples.append(df)

    df = data[data.weigth_vector < threshold].sample(frac=test_size, random_state=seed)
    samples.append(df)
    data_validation = pd.concat(samples)
    data_train = data[~data.Inv_Id.isin(data_validation.Inv_Id)]

    return data_train, data_validation


def find_pattern(text, regex):
    x = re.search(regex, text, re.IGNORECASE)
    x = x.group(0) if x else None
    return f"{x}"


def get_date(text, regx1, regx2):
    x = re.search(regx1, text, re.IGNORECASE)
    y = re.search(regx2, text, re.IGNORECASE)
    x = x.group(0) if x else None
    y = y.group(0) if x else None
    return f"{x}-{y}"


class splitter(BaseEstimator, TransformerMixin):
    def __init__(self, variables, new_variable_names):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.new_variable_names = new_variable_names

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature, feature_name in zip(self.variables, self.new_variable_names):
            X[[feature, feature_name]] = X[feature].str.split("-", expand=True)

        return X


class Mapper(BaseEstimator, TransformerMixin):
    def __init__(self, variables, mappings):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.mappings = mappings

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].map(self.mappings)

        return X


class Custom_Fillna(BaseEstimator, TransformerMixin):
    def __init__(self, variables, fill_value):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.fill_value = fill_value

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].fillna(self.fill_value)

        return X


## function to get the countings
def count_character(x, value):
    return x.count(value)


class get_items_in_description(BaseEstimator, TransformerMixin):
    def __init__(self, variables, new_variable_names):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.new_variable_names = new_variable_names

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature, feature_name in zip(self.variables, self.new_variable_names):
            X[feature_name] = (
                X.apply(lambda x: count_character(x[feature], "/"), axis=1) + 1
            )
        return X


class get_keywords_from_description(BaseEstimator, TransformerMixin):
    def __init__(self, variables, new_variable_names, keywords):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.new_variable_names = new_variable_names
        self.keywords = keywords

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature, feature_name, regex in zip(
            self.variables, self.new_variable_names, self.keywords
        ):
            X[feature_name] = X.apply(lambda x: find_pattern(x[feature], regex), axis=1)
        return X


class get_date_features(BaseEstimator, TransformerMixin):
    def __init__(self, variables, date_regex, year_regex, moth_regex):

        if not isinstance(variables, list):
            raise ValueError("variables should be a list")

        self.variables = variables
        self.date_regex = date_regex
        self.year_regex = year_regex
        self.moth_regex = moth_regex

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X["DateFound"] = X.apply(
                lambda x: find_pattern(x.Item_Description, self.date_regex), axis=1
            )
            X["DateFound"] = X.apply(
                lambda x: get_date(x.DateFound, self.year_regex, self.moth_regex),
                axis=1,
            )
            X["DateFound_format"] = pd.to_datetime(
                X["DateFound"], format="%Y-%b"
            )  ## drop for a while
            X["YearFound"] = X["DateFound_format"].dt.year
            X["MonthFound"] = X["DateFound_format"].dt.month
            X = X.drop(columns=["DateFound", "DateFound_format"])
        return X
