"""Utility functions for data science projects."""
import logging
import random
import time

import pandas as pd
from scipy.stats import beta, norm
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler

from .io import insert_logs


def ulid(hash_project):
    """Create unique identifier every time it runs, with respect to the hash_project."""
    hash_time = f"{int(time.time() * 1e3):012x}"
    hash_rand = f"{random.getrandbits(48):012x}"
    hash_all = hash_time + hash_project + hash_rand
    ulid = f"{hash_all[:8]}-{hash_all[8:12]}-{hash_all[12:16]}-{hash_all[16:20]}-{hash_all[20:32]}"
    return ulid


def check_memory_consumption(params, df):
    """Log RAM occupation of a df."""
    msg = f"Df memory occupation = {df.memory_usage(index=True).sum() / 1e6:.2f} Mb"
    logging.info(msg)
    insert_logs(params, msg)
    return


def fit_beta(params, data_points):
    """Fit a beta distribution on data."""
    # Normalize data in [0,1]
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(data_points.values.reshape(-1, 1))

    # Fit beta distribution
    a, b, location, scale = beta.fit(data_norm)
    quantiles = pd.Series(
        beta.cdf(data_norm, a, b, location, scale)[:, 0], index=data_points.index
    )

    results = {
        "method": params["dist_fit"],
        "data_norm": data_norm,
        "quantiles": quantiles,
        "parameters": {
            "a": a,
            "b": b,
        },
    }

    return results


def gmm_cdf(x, model):
    """Compute the quantile of a Gaussian Mixture Cumulative Distribution."""
    cdf = 0.0
    for i in range(len(model.weights_)):
        cdf += model.weights_.flatten()[i] * norm.cdf(
            x, loc=model.means_.flatten()[i], scale=model.covariances_.flatten()[i]
        )
    return cdf


def fit_gmm(params, data_points):
    """Fit a gaussian mixture distribution on data."""
    data_norm = data_points.values.reshape(-1, 1)
    models = [
        GaussianMixture(
            n + 1, covariance_type="full", random_state=params["random_state"]
        ).fit(data_norm)
        for n in range(params["gmm_components_max"])
    ]
    AIC = [m.aic(data_norm) for m in models]
    min_value = min(AIC)
    best_n = AIC.index(min_value)
    model = models[best_n]
    quantiles = data_points.apply(lambda x: gmm_cdf(x, model))

    results = {
        "method": params["dist_fit"],
        "data_norm": data_norm,
        "quantiles": quantiles,
        "parameters": {"model": model},
    }

    return results
