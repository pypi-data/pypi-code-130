# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import numpy as np
import json


class Transaction():
    """Transaction for which explanation needs to be computed."""

    def __init__(self, config, data_row):
        self.config = config
        self.row = np.asarray([data_row[k]
                               for k in self.config.feature_columns])
        self.prediction = data_row[config.prediction_column]
        self.probabilities = data_row[config.probability_column] if config.probability_column else None
        self.probability = max(
            self.probabilities) if self.probabilities else None

    def get_labels(self):
        """Get all the indexes with max probability value in probabilities array."""
        max_probability = np.max(self.probabilities)
        return [i for i, prob in enumerate(self.probabilities) if prob == max_probability]
