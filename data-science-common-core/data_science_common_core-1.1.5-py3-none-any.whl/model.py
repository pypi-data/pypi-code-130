"""Machine learning model."""
import logging

from imblearn.over_sampling import SMOTENC
from imblearn.pipeline import Pipeline
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.multioutput import (
    MultiOutputClassifier,
    Parallel,
    _check_fit_params,
    _fit_estimator,
    check_classification_targets,
    delayed,
    has_fit_parameter,
    is_classifier,
)
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Dense, Dropout, Input, Normalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adamax

from .io import fetch_from_bucket


class MultiOutputSMOTEClassifier(MultiOutputClassifier):
    """Act like sklearn.multipoutput.MultiOutputClassifier."""

    def fit(self, X, y, smote_params: dict, sample_weight=None, **fit_params):
        """Like `MultiOutputClassifier.fit`. If `smote_params` for a field is not None, it will create a pipeline."""
        if not hasattr(self.estimator, "fit"):
            raise ValueError("The base estimator should implement a fit method")

        # Return True if the given estimator is (probably) a classifier.
        if is_classifier(self):
            check_classification_targets(y)

        if y.ndim == 1:
            raise ValueError(
                "y must have at least two dimensions for "
                "multi-output regression but has only one."
            )

        if sample_weight is not None and not has_fit_parameter(
            self.estimator, "sample_weight"
        ):
            raise ValueError("Underlying estimator does not support sample weights.")

        fit_params_validated = _check_fit_params(X, fit_params)

        self.estimators_ = []
        for field in y.columns:
            if smote_params[field] is None:
                self.estimators_.append(self.estimator)
            else:
                pipe = Pipeline(
                    [
                        ("scaler", MinMaxScaler()),
                        (
                            "sampler",
                            SMOTENC(
                                categorical_features=smote_params[
                                    "categorical_features"
                                ],
                                random_state=smote_params["random_state"],
                                **smote_params[field],
                            ),
                        ),
                        ("clf", self.estimator),
                    ]
                )
                self.estimators_.append(pipe)
        self.estimators_ = Parallel(n_jobs=self.n_jobs)(
            delayed(_fit_estimator)(
                self.estimators_[i],
                X,
                y.iloc[:, i],
                sample_weight,
                **fit_params_validated,
            )
            for i in range(y.shape[1])
        )

        if hasattr(self.estimators_[0], "n_features_in_"):
            self.n_features_in_ = self.estimators_[0].n_features_in_
        if hasattr(self.estimators_[0], "feature_names_in_"):
            self.feature_names_in_ = self.estimators_[0].feature_names_in_

        return self


def nn_model_setup(params, num_input, num_output, df_norm) -> Sequential:
    """Design the nn model architecture.

    Args:
        params (dict)       : NN parameters
        num_input (int)     : no. of input variables
        num_output (int)    : no. of output variables
        df_norm (dataframe) : chunk of data for normalization
    Returns:
        model (keras.models.Sequential): untrained NN model
    """
    # Model design
    model = Sequential()
    l_in = Input(num_input)
    model.add(l_in)
    l_n = Normalization(axis=1)
    l_n.adapt(df_norm)
    model.add(l_n)

    model_params = params["model_params_nn"]

    # Stack Dense layers
    for idx_layer in range(model_params["no_layers"]):
        # Set number of neurons for the current layer
        no_neurons = int(model_params["basic_neurons"] / (2**idx_layer))

        # Add Dense layer and dropout
        model.add(
            Dense(
                no_neurons,
                activation=model_params["activation"],
                kernel_initializer=model_params["kernel_init"],
            )
        )
        model.add(Dropout(model_params["dropout"]))

    # Last predictive layer
    if model_params["last_activation"] != "":
        model.add(Dense(num_output, activation=model_params["last_activation"]))
    else:
        model.add(Dense(num_output))

    # Compile model
    model.compile(
        loss=model_params["loss"],
        optimizer=Adamax(learning_rate=model_params["learning_rate"]),
        metrics=model_params["metrics"],
    )

    print(model.summary())

    return model


def nn_train(params, data) -> Sequential:
    """Train of the neural network model.

    Returns:
        model (keras.models.Sequential): trained NN model object
    """
    # Get model architecture
    model = nn_model_setup(
        params, data["data_num_input"], data["data_num_output"], data["df_train"][::10]
    )

    # # Generators
    # training_generator = DataGenerator(params, data, mode="train")
    # validation_generator = DataGenerator(params, data, mode="val")

    model_params = params["model_params_nn"]

    # Setup callbacks
    es = EarlyStopping(
        monitor=model_params["metric_monitor"],
        mode=model_params["metric_mode"],
        min_delta=model_params["early_stopping_min_delta"],
        verbose=model_params["verbose"],
        patience=model_params["patience"],
    )
    mc = ModelCheckpoint(
        filepath=model_params["path_model_file"],
        monitor=model_params["metric_monitor"],
        mode=model_params["metric_mode"],
        verbose=model_params["verbose"],
        save_best_only=True,
    )

    # Model training
    model.fit(
        x=data["df_train"],
        y=data["label_train"],
        validation_data=(data["df_val"], data["label_val"]),
        epochs=model_params["max_epochs"],
        batch_size=model_params["batch_size"],
        callbacks=[es, mc],
        workers=8,
        use_multiprocessing=True,
        max_queue_size=10,
        verbose=model_params["verbose"],
    )
    return model


def nn_load(params, data):
    """Load model file from blob storage and load weights."""
    logging.info("Download model file")

    model_file_path = fetch_from_bucket(params, "model")["model"]

    # Load Model
    logging.info("Set up and load model weights")
    model = nn_model_setup(
        params,
        data["data_num_input"],
        params["data_n_output"],
        data["df_test"],
    )
    model.load_weights(model_file_path)

    return model


def hgb_regressor_model_setup(params):
    """Create HistGradientBoosting Regressor."""
    # Select hgb parameters
    model_params = params["model_params_hgb"]

    # Set up HistGradientBoosting model
    model = HistGradientBoostingRegressor(
        max_iter=model_params["max_iter"],
        max_leaf_nodes=model_params["max_leaf_nodes"],
        l2_regularization=model_params["l2_regularization"],
        loss=model_params["loss"],
        learning_rate=model_params["learning_rate"],
        scoring=model_params["scoring"],
        early_stopping=model_params["early_stopping"],
        tol=model_params["tol"],
        random_state=model_params["random_state"],
        verbose=model_params["verbose"],
    )

    return model


def hgb_classification_model_setup(params):
    """Create HistGradientBoosting Regressor."""
    # Select hgb parameters
    model_params = params["model_params_hgb"]

    # Set up HistGradientBoosting model
    model = HistGradientBoostingClassifier(
        max_iter=model_params["max_iter"],
        max_leaf_nodes=model_params["max_leaf_nodes"],
        l2_regularization=model_params["l2_regularization"],
        loss=model_params["loss"],
        learning_rate=model_params["learning_rate"],
        scoring=model_params["scoring"],
        early_stopping=model_params["early_stopping"],
        tol=model_params["tol"],
        random_state=model_params["random_state"],
        verbose=model_params["verbose"],
    )

    return model
