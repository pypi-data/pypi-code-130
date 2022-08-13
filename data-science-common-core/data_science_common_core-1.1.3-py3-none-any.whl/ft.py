"""Feature Extraction and Transformation functionalities."""
import concurrent.futures
import logging
from collections import OrderedDict

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from tqdm import tqdm

from .io import insert_logs


def extract_date_features(ds, date_time=True):
    """Extract date features from a column.

    - ds: data series of datetime/date type to extract features.
    - date_time: Boolean input.
        if date_time=True: Extract all the features
        if date_time=False: Extract only day and dayofweek features.
    """
    # Extract day and dayofweek
    res = [
        ds.dt.day,
        ds.dt.dayofweek,
    ]

    # Column names
    res_columns = [
        f"{ds.name}_day",
        f"{ds.name}_day_of_week",
    ]

    # Extract all the features if the condition is true
    if date_time:
        res += [
            ds.dt.year,
            ds.dt.month,
            ds.dt.hour,
            ds.dt.minute,
            ds.dt.dayofyear,
            ds.dt.isocalendar().week,
            ds.dt.days_in_month,
        ]

        res_columns += [
            f"{ds.name}_year",
            f"{ds.name}_month",
            f"{ds.name}_hour",
            f"{ds.name}_minute",
            f"{ds.name}_day_of_year",
            f"{ds.name}_week_of_year",
            f"{ds.name}_days_in_month",
        ]

    res = pd.concat(res, axis=1)
    res.columns = res_columns

    return res.astype(float)


def extract_num_features(params, ds):
    """Extract and replace NaNs from numeric feature."""
    # Check where NAs are
    find_na = ds.isna()
    col_is_na = pd.DataFrame(find_na.astype("uint8")).rename(
        columns={f"{ds.name}": f"{ds.name}_isna"}
    )

    # Replace NA values with default constant
    col_no_na = ds.copy()
    col_no_na[find_na] = np.float32(params["NA_replace_val"])
    col_no_na = pd.DataFrame(col_no_na)

    return col_is_na, col_no_na


def extract_feature_per_shipment(
    df: pd.DataFrame,
    numeric_features: list,
    cat_features: list,
) -> pd.DataFrame:
    """Extract latest record and history statistics for each shipment."""
    # Generate statistics of history for each var and each shipment
    num_stats = df.groupby("shipment_id")[numeric_features].agg(
        ["min", "max", "mean", "std"],
    )
    num_stats.columns = ["_".join(col).strip() for col in num_stats.columns.values]

    cat_stats = df.groupby("shipment_id")[cat_features].nunique().add_suffix("_nunique")
    # Get latest record for each shipment
    latest_records = df.groupby("shipment_id").apply(
        lambda x: x.sort_values("upload_date").tail(1)
    )

    return latest_records.join(num_stats).join(cat_stats)


class FeatureTransformer:
    """FeatureTransformer class with ordinal encoder."""

    def __init__(
        self,
        fixed_columns=[],
        json_columns=[],
        category_cross=False,
        detect_gap=5,
        verbose=0,
        parallelization=False,
    ):
        """Class initializer."""
        self.fixed_columns = fixed_columns
        self.json_columns = json_columns
        self.category_cross = category_cross
        self.detect_gap = detect_gap
        self.verbose = verbose
        self.columns = OrderedDict()
        self.parallelization = parallelization

    def fit(self, params, df, col_dtypes):
        """Fit transformer with data."""
        # Select the categorical columns
        self.cat_cols = [c for c, t in col_dtypes.items() if t == "categorical"]
        if "label" in self.cat_cols:
            self.cat_cols.remove("label")

        # Perform feature crossing between categorical columns
        self.combined_cols = []
        if self.category_cross:
            msg = f"Feature Crossing between {len(self.cat_cols)} columns"
            logging.info(msg)
            insert_logs(params, msg)
            for i1 in tqdm(range(len(self.cat_cols) - 1)):
                for i2 in range(i1 + 1, len(self.cat_cols)):
                    c1, c2 = self.cat_cols[i1], self.cat_cols[i2]
                    new_col = f"{c1}___{c2}"
                    df.loc[:, new_col] = df[c1].astype(str) + "___" + df[c2].astype(str)
                    self.combined_cols += [new_col]
            self.cat_cols += self.combined_cols

        # Fit the ordinal encoders
        msg = "Fitting Ordinal Encoder on Categorical Columns"
        logging.info(msg)
        insert_logs(params, msg)
        self.enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        self.enc.fit(df[self.cat_cols])

        return self

    # Extract features from numeric and datetime columns
    def _process_one_column(self, col_data, col_type):
        ret = pd.DataFrame(index=col_data.index)

        if col_type == "numeric":
            ret = pd.to_numeric(col_data, errors="coerce", downcast="float").fillna(-1)

        elif col_type == "datetime":
            dt = col_data.apply(lambda x: np.datetime64(str(x))).astype(str)
            dt = pd.to_datetime(dt, errors="coerce", utc=True)
            ret = extract_date_features(dt).fillna(-1.0)

        return ret

    # Transform only works on the same df format, considering same columns with same order
    def transform(self, params, df, col_dtypes):
        """Transform input data with fitted transformer."""
        features = []

        # Filter the fixed columns
        col_dtypes = {
            key: col_dtypes[key] for key in col_dtypes if key not in self.fixed_columns
        }

        # Feature transform on numeric and datetime columns with parallelization
        if self.parallelization:
            res = []

            logging.info(
                "With parallelization, Extracting numerical and datetime features..."
            )
            with tqdm(total=len(col_dtypes)) as pbar:
                # Feature transform on numeric and datetime columns
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    res += [
                        executor.submit(self._process_one_column, df[c], t)
                        for c, t in col_dtypes.items()
                    ]
                    for i in concurrent.futures.as_completed(res):
                        features += [i._result]
                        pbar.update()

        else:
            # Feature transform on numeric and datetime columns without parallelization
            logging.info("Extracting numerical and datetime features...")
            features += [
                self._process_one_column(df[c], t) for c, t in col_dtypes.items()
            ]

        for new_col in tqdm(self.combined_cols):
            c1, c2 = new_col.split("___")
            df.loc[:, new_col] = df[c1].astype(str) + "___" + df[c2].astype(str)

        # Transform the ordinal encoders
        df_cat = self.enc.transform(df[self.cat_cols])

        # Create categorical and numerical features into a dataframe
        df_cat = pd.DataFrame(df_cat, columns=self.cat_cols, index=df.index)
        features = pd.concat([*features], axis=1)

        msg = f"categorical: {df_cat.shape}"
        logging.info(msg)
        insert_logs(params, msg)

        msg = f"numeric+date: {features.shape}"
        logging.info(msg)
        insert_logs(params, msg)

        # Concatinate fixed columns, numerical, datetime and categorical features
        ret = pd.concat(
            [df.loc[:, df.columns.isin(self.fixed_columns)], features, df_cat], axis=1
        )

        # Select numerical columns
        numeric_features = [col for col in col_dtypes if col_dtypes[col] == "numeric"]

        # Extract features per shipment
        logging.info("extracting features per shipment...")
        ret = extract_feature_per_shipment(ret, numeric_features, self.cat_cols)
        logging.info("...Finished extracting")
        logging.info(f"Data shape: {ret.shape[0]} rows, {ret.shape[1]} cols")

        return ret.reset_index(drop=True)

    # transform_features works independent of the same df format such as same order in both training and testing
    # noqa E501
    def transform_features(self, params, df, feature_dtypes):
        """Minimal transformation to input data.

        - Date features: apply extract_date_features
        - Categorical features: fill missing values with "nan"
        - Extract feature per shipment based on history
        """
        # Filter out non_features
        feature_dtypes = {
            col: dtype
            for col, dtype in feature_dtypes.items()
            if col not in self.fixed_columns
        }

        # Select the datetime columns
        datetime_features = [
            col for col in feature_dtypes if feature_dtypes[col] == "datetime"
        ]
        # Select the categorical columns
        cat_features = [
            col for col in feature_dtypes if feature_dtypes[col] == "categorical"
        ]
        # Select the numerical columns
        num_features = [
            col for col in feature_dtypes if feature_dtypes[col] == "numeric"
        ]

        # Extract date features for columns of datetime type
        df_dt = pd.concat(
            [
                extract_date_features(df[col], date_time=False)
                for col in datetime_features
            ],
            axis=1,
        ).set_index(df.index)

        # Fill categorical missing values with nan
        df[cat_features] = df[cat_features].fillna("nan")

        msg = f"Number of datetime features: {len(datetime_features)}"
        logging.info(msg)
        insert_logs(params, msg)

        msg = f"Number of numerical features: {len(num_features)}"
        logging.info(msg)
        insert_logs(params, msg)

        msg = f"Number of categorical features: {len(cat_features)}"
        logging.info(msg)
        insert_logs(params, msg)

        # Concat non-datetime features with newly transform datetime features
        ret = pd.concat([df.drop(columns=datetime_features), df_dt], axis=1)
        # Extract features per shipment based on history
        # Reducing multiple rows for each shipment to one per shipment
        ret = extract_feature_per_shipment(
            ret, numeric_features=num_features, cat_features=cat_features
        )
        return ret

    # Fit and transform the featuretransformer
    def fit_transform(self, params, df):
        """Apply fit and transform to data."""
        self.fit(params, df)
        return self.transform(params, df)
