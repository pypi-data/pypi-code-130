import numpy as np
import os
import joblib
import logging


class Perceptron:
    def __init__(self, eta: float = None, epochs: int = None):
        self.weights = np.random.randn(3) * 1e-4  # small random weights
        training = (eta is not None) and (epochs is not None)
        # we can call the Perceptron class without giving any parameters if we don't want it to train but use one of its methods
        if training:
            # logging.infoing initial weights only when training otherwise not
            logging.info(f"initial weights before training: \n{self.weights}")
        self.eta = eta
        self.epochs = epochs

    def _z_outcome(self, inputs, weights):
        return np.dot(inputs, weights)  # product of weights time the inputs

    def activation_function(self, z):
        return np.where(z > 0, 1, 0)  # where z>0 return 1 otherwise return 0 (step function)

    def fit(self, X, y):
        self.X = X
        self.y = y

        X_with_bias = np.c_[self.X, -np.ones((len(self.X), 1))]  # concatenating our x with bias
        logging.info(f"X with bias: \n{X_with_bias}")

        for epoch in range(self.epochs):
            logging.info("--" * 10)
            logging.info(f"for epoch >> {epoch}")
            logging.info("--" * 10)

            z = self._z_outcome(X_with_bias, self.weights)
            y_hat = self.activation_function(z)  # predicted value
            logging.info(f"predicted value after forward pass: \n{y_hat}")

            self.error = self.y - y_hat  # true-predicted
            logging.info(f"error :\n{self.error}")

            self.weights = self.weights + self.eta * np.dot(X_with_bias.T, self.error)
            logging.info(f"updated weights after epoch: {epoch + 1}/{self.epochs} is \n{self.weights}")
            logging.info("##" * 10)

    def predict(self, X):  # X is input provided for prediction purpose
        X_with_bias = np.c_[X, -np.ones((len(X), 1))]
        z = self._z_outcome(X_with_bias, self.weights)  # the updated weights after all epochs
        return self.activation_function(z)

    def total_loss(self):
        total_loss = np.sum(self.error)
        logging.info(f"\n total loss: {total_loss}\n")
        return total_loss

    # before writing the model in a file we need to create a directory first
    def _create_dir_return_path(self, model_dir, filename):
        os.makedirs(model_dir, exist_ok=True)  # exist_ok=True so that if directory already present then overwrite it
        return os.path.join(model_dir, filename)

    def save(self, filename, model_dir=None):
        if model_dir is not None:
            model_file_path = self._create_dir_return_path(model_dir, filename)
            joblib.dump(self, model_file_path)
        else:
            # if model_dir not provided then creates a directory with name 'model'
            model_file_path = self._create_dir_return_path("model", filename)
            joblib.dump(self, model_file_path)
        logging.info(f"Model is saved at {model_file_path}")

    def load(self, filepath):
        return joblib.load(filepath)