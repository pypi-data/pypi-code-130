import lightgbm as lgb
import pandas as pd

from scoringmodel.config.core import config


def gen_fullpay_l6m(data: pd.DataFrame):
    """
    """
    fullpay_l6m = (data.pay_1 == -1).astype(int) + \
                  (data.pay_2 == -1).astype(int) + \
                  (data.pay_3 == -1).astype(int) + \
                  (data.pay_4 == -1).astype(int) + \
                  (data.pay_5 == -1).astype(int) + \
                  (data.pay_6 == -1).astype(int)
    fullpay_l6m.name = "fullpay_l6m"
    return fullpay_l6m


def gen_revolve_l6m(data: pd.DataFrame):
    """
    """
    revolve_l6m = (data.pay_1 == 0).astype(int) + \
                  (data.pay_2 == 0).astype(int) + \
                  (data.pay_3 == 0).astype(int) + \
                  (data.pay_4 == 0).astype(int) + \
                  (data.pay_5 == 0).astype(int) + \
                  (data.pay_6 == 0).astype(int)
    revolve_l6m.name = "revolve_l6m"
    return revolve_l6m

def gen_revolve_l3m(data: pd.DataFrame):
    """
    """
    revolve_l3m = (data.pay_1 == 0).astype(int) + \
                  (data.pay_2 == 0).astype(int) + \
                  (data.pay_3 == 0).astype(int)
    revolve_l3m.name = "revolve_l3m"
    return revolve_l3m

def gen_revolve_l1m(data: pd.DataFrame):
    """
    """
    revolve_l1m = (data.pay_1 == 0).astype(int)
    revolve_l1m.name = "revolve_l1m"
    return revolve_l1m

def gen_nobill_l6m(data: pd.DataFrame):
    """
    """
    nobill_l6m = (data.pay_1 == -2).astype(int) + \
                 (data.pay_2 == -2).astype(int) + \
                 (data.pay_3 == -2).astype(int) + \
                 (data.pay_4 == -2).astype(int) + \
                 (data.pay_5 == -2).astype(int) + \
                 (data.pay_6 == -2).astype(int)
    nobill_l6m.name = "nobill_l6m"
    return nobill_l6m

def gen_default_l6m(data: pd.DataFrame):
    """
    """
    default_l6m = (data.pay_1 >= 1).astype(int) + \
                  (data.pay_2 >= 1).astype(int) + \
                  (data.pay_3 >= 1).astype(int) + \
                  (data.pay_4 >= 1).astype(int) + \
                  (data.pay_5 >= 1).astype(int) + \
                  (data.pay_6 >= 1).astype(int)
    default_l6m.name = "default_l6m"
    return default_l6m

def gen_default_l3m(data: pd.DataFrame):
    """
    """
    default_l3m = (data.pay_1 >= 1).astype(int) + \
                  (data.pay_2 >= 1).astype(int) + \
                  (data.pay_3 >= 1).astype(int)
    default_l3m.name = "default_l3m"
    return default_l3m

def gen_default_l1m(data: pd.DataFrame):
    """
    """
    default_l1m = (data.pay_1 >= 1).astype(int)
    default_l1m.name = "default_l1m"
    return default_l1m

def concat_features(feature_arrays: list):
    """
    """
    concated = pd.concat(feature_arrays, axis=1)
    return concated

def feature_pipeline(data: pd.DataFrame):
    """
    """
    fullpay_l6m = gen_fullpay_l6m(data)
    revolve_l6m = gen_revolve_l6m(data)
    revolve_l3m = gen_revolve_l3m(data)
    revolve_l1m = gen_revolve_l1m(data)
    nobill_l6m  = gen_nobill_l6m(data)
    default_l6m = gen_default_l6m(data)
    default_l3m = gen_default_l3m(data)
    default_l1m = gen_default_l1m(data)

    concated = concat_features([data, 
                                fullpay_l6m,
                                revolve_l3m,
                                revolve_l6m,
                                revolve_l1m,
                                nobill_l6m,
                                default_l6m,
                                default_l3m,
                                default_l1m])

    return concated


def modeling(x_train, x_valid, y_train, y_valid):
    """
    """
    categorical_features = config.model_config.categorical_features

    train_data = lgb.Dataset(x_train, 
                             label=y_train,
                             feature_name=config.model_config.features
                 )

    valid_data = lgb.Dataset(x_valid, 
                             label=y_valid,
                             feature_name=config.model_config.features
                 )

    params = config.model_config.train_params

    model = lgb.train(params, 
                      train_data, 
                      num_boost_round=config.model_config.num_round, 
                      valid_sets=[train_data, valid_data], 
                      valid_names=['train','valid'],
                      categorical_feature=categorical_features,
                      callbacks=[lgb.early_stopping(stopping_rounds=config.model_config.stopping_rounds)]
            )

    return model


