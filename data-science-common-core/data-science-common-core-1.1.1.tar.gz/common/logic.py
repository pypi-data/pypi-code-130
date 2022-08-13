"""Contains module logic."""
import concurrent.futures
import gc
import logging
from functools import reduce

import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.ensemble import IsolationForest
from tqdm import tqdm

from .ft import FeatureTransformer
from .io import insert_logs


def clean_data(params, var_data):
    """Identify column types, downcast numericals and reformat NaNs.

    - var_data: Data to clean and extract the data type.

        Returns:
    - Var data: Cleaned data after type inference
    - Var type (dict): {feature name: feature type}
    """
    # Get the column name
    col_name = var_data.name
    var_type = {col_name: None}

    # Extract column data type
    col_type = var_data.dtype.name

    # Check if column is a datetime or dbdate, extract relevant features and join them
    if ("datetime" in col_type) or ("dbdate" in col_type):
        # Convert datetime type to make it uniform
        var_data = pd.to_datetime(var_data)

        # Add to list of variable types
        var_type = {col_name: "datetime"}

    # if infer column type
    elif col_type == "bool":
        var_type = {col_name: "bool"}

    # Otherwise, the column is either a numerical or a categorical
    else:

        # Assess it is a numerical
        try:
            # Fill the None values with NaNs and downcast float
            var_data = var_data.astype(np.float32).fillna(value=np.nan)

            # Add to list of variable types
            var_type = {col_name: "numeric"}

        # Treat it as a categorical
        except (ValueError, TypeError):
            # Skip the index!
            if not col_name == params["id_field"]:

                # Try to check if it is string-typed BOOL
                is_bool = var_data.dropna().str.lower().isin(["true", "false"]).all()

                if is_bool:
                    var_data = var_data.str.lower().map({"true": True, "false": False})
                    var_type = {col_name: "bool"}

                else:
                    # Fill the empty strings with None
                    var_data = var_data.replace(
                        r"^\s*$", None, regex=True, inplace=False
                    )

                    # Add to list of variable types
                    var_type = {col_name: "categorical"}

    return var_data, var_type


def parallelize_clean_data(params, data, parallelization=True):
    """Parallelized clean data.

    - data: Pass the data frame.
    - parallelization: Boolean if parallelization is required or not.
    """
    # If parallelization is applied
    if parallelization:
        result = []
        with tqdm(total=data.shape[1]) as pbar:
            # Push all function calls with ThreadPoolexecutor that runs only 8 in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                features = {
                    executor.submit(clean_data, params, data[col])
                    for col in data.columns
                }
                for res in concurrent.futures.as_completed(features):
                    result.append(res.result())
                    pbar.update()

    else:
        # Clean data without parallelization
        result = [clean_data(params, data.iloc[:, i]) for i in range(data.shape[1])]

    # Merge the results
    df_clean = pd.concat([i[0] for i in result if i and len(i[0])], axis=1)
    dtype_list = [i[1] for i in result if i and len(i[1])]

    # combine a list of {name: data type} dictionaries into one
    cat_list = reduce(lambda a, b: {**a, **b}, dtype_list)

    return df_clean, cat_list


def filter_data(params, data, cat_list):
    """Filter categorical columns using Cramér's V association.

    https://en.wikipedia.org/wiki/Cramér's_V
    """
    # Init results
    categoricals = [cat["name"] for cat in cat_list if cat["type"] == "categorical"]
    col_remove = []

    # Run along pairs of categorical columns
    for cat_idx_i, cat_name_i in enumerate(categoricals):
        for cat_idx_j, cat_name_j in enumerate(
            categoricals[cat_idx_i + 1 :]  # noqa E203
        ):

            # Save time: process columns only if not removed yet
            if cat_name_i not in col_remove and cat_name_j not in col_remove:

                # Extract data
                paired_data = data[[cat_name_i, cat_name_j]].dropna()

                # If the df contains sth
                if paired_data.shape[0]:

                    # Compute contingency table
                    cat_contingency = pd.crosstab(
                        paired_data[cat_name_i], paired_data[cat_name_j]
                    )

                    # Chi-squared test statistic
                    chi_sq = stats.chi2_contingency(cat_contingency, correction=False)[
                        0
                    ]

                    # Try to remove column categories, only if the feature has multiple ones
                    if cat_contingency.shape[1] > 1:
                        # Compute Cramer's V for the pair of categoricals
                        cramer_v = np.sqrt(
                            (chi_sq / paired_data.shape[0])
                            / (cat_contingency.shape[1] - 1)
                        )

                        # Store columns to be removed
                        if cramer_v > params["abs_corr_collinearity"]:
                            col_remove.append(cat_name_j)

    cat_valid = [cat for cat in categoricals if cat not in col_remove]

    return cat_valid


def data_transformation(params, data):
    """Clean data and perform basic feature extraction."""
    msg = "Cleaning data..."
    logging.info(msg)
    insert_logs(params, msg)
    data, cat_list = parallelize_clean_data(params, data)

    msg = "Filtering data..."
    logging.info(msg)
    insert_logs(params, msg)
    # cat_valid = filter_data(params, data, cat_list)

    msg = "Feature extraction..."
    logging.info(msg)
    insert_logs(params, msg)
    # data = feat_extraction(params, data, cat_list, cat_valid)

    return data, cat_list


def feat_extraction(params, data, col_list, cat_valid):
    """Perform feature extraction depending on data type."""
    # Init results
    cols_to_add_bool = []
    cols_to_add_no_bool = []
    cols_to_remove = []

    # Run across features
    for col in tqdm(col_list, total=len(col_list)):

        # If column is a datetime, extract relevant features
        if col["type"] == "datetime":

            # Create dataframe with new datetime features
            dt_split = FeatureTransformer.extract_date_features(
                data[col["name"]]
            ).astype(int)

            # Add dataframe to list
            cols_to_add_no_bool.append(dt_split)

        # Otherwise, a numeric column might contain NAs
        elif col["type"] == "numeric":
            # Create dataframe with new numeric features
            col_is_na, col_no_na = FeatureTransformer.extract_num_features(
                params, data[col["name"]]
            )

            # Add dataframes to lists
            # cols_to_add_bool.append(col_is_na)
            cols_to_add_no_bool.append(col_no_na)

            # Add feature to list of removable ones
            cols_to_remove.append(col["name"])

        # Otherwise, a categorical column might or not be valid
        elif col["type"] == "categorical":

            # Valid categorical columns are one-hot encoded into dummies
            if col["name"] in cat_valid:

                # Create dataframe with one-hot encoded features
                data_dummies = pd.get_dummies(data[col["name"]], prefix=col["name"])

                # Add dataframe to list
                cols_to_add_bool.append(data_dummies)

            # Add feature to list of removable ones
            cols_to_remove.append(col["name"])

    # Drop the columns to be removed
    data.drop(columns=cols_to_remove, axis=1, inplace=True)

    # Define column names and decide if boolean
    col_bool = [col for df in cols_to_add_bool for col in df.columns]
    col_no_bool = [col for df in cols_to_add_no_bool for col in df.columns]

    # Update dataframe with columns_to_add
    df_to_add_bool = pd.DataFrame(np.hstack(cols_to_add_bool), columns=col_bool)
    df_to_add_no_bool = pd.DataFrame(
        np.hstack(cols_to_add_no_bool), columns=col_no_bool
    ).astype("float32")

    # Join dataframes
    data = data.join(df_to_add_no_bool).join(df_to_add_bool)

    return data


def train_val_split(params, data, df):
    """Split randomly train and validation sets + assign targets.

    - data: Data dictionary.
    -df: Data frame to split train and validation data.
    """
    # Initialise the splitting index
    split_index = params["id_field"]

    # Split data randomly between train and validation
    data["s_id_all"] = df[split_index].drop_duplicates().sort_values()
    data["s_id_train"] = list(
        data["s_id_all"]
        .sample(frac=params["train_test_split"], random_state=params["random_state"])
        .values
    )
    data["s_id_val"] = list(set(data["s_id_all"]) - set(data["s_id_train"]))

    # Loop over train and validation segments
    for segment in ["train", "val"]:
        # Select the index of a selected shipments of a segment
        idx = df[split_index].isin(data[f"s_id_{segment}"])

        # Assign segment data
        data[f"df_{segment}"] = df[idx].reset_index(drop=True)

        # Drop inserted values to conserve memory
        df = df[~idx]

    gc.collect()

    return data


def apply_if_train(params, data, cat_list):
    """Apply Isolation Forest outlier detection on training data."""
    msg = "Filtering outliers with IsolationForest..."
    logging.info(msg)

    # Extract numeric features and drop null columns
    df_numeric = data[
        [var for var in cat_list if cat_list[var] == "numeric" and var in data.columns]
    ]
    df_numeric = df_numeric.fillna(df_numeric.median()).dropna(axis=1, how="all")

    # Make a run of IsolationForest with auto best-fit contamination
    contamination = (
        params["if_contamination"] if "if_contamination" in params else "auto"
    )
    if_model = IsolationForest(
        n_estimators=params["if_n_estimators"],
        max_samples=params["if_sr_isolation"],
        max_features=1.0,
        random_state=params["random_state"],
        contamination=contamination,
        n_jobs=-1,
    )
    if_model.fit(df_numeric)
    if_pred = if_model.predict(df_numeric)

    contamination = ((1 - if_pred) / 2).mean()
    logging.info(f"The current run has contamination = {contamination:.4f}")

    # Perform IsolationForest outlier detection
    data = data[if_pred == 1]

    return data
