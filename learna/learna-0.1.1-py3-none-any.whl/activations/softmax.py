# Softmax turns logits, the numeric output of the last linear layer of a
# multi-class classification neural network into probabilities.
import numpy as np


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)
