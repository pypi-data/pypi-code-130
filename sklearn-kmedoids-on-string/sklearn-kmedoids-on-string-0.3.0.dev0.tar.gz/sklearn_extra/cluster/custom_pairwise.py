import numpy as np

def pairwise_distances(X, Y, metric):
    import itertools
    # Only calculate metric for upper triangle
    if X is Y:
        # Only calculate metric for upper triangle
        out = np.zeros((X.shape[0], Y.shape[0]), dtype="float")
        iterator = itertools.combinations(range(X.shape[0]), 2)
        for i, j in iterator:
            out[i, j] = metric(X[i], Y[j])

        # Make symmetric
        # NB: out += out.T will produce incorrect results
        out = out + out.T

        # Calculate diagonal
        # NB: nonzero diagonals are allowed for both metrics and kernels
        for i in range(X.shape[0]):
            x = X[i]
            out[i, i] = metric(x, x)

    else:
        # Calculate all cells
        out = np.empty((X.shape[0], Y.shape[0]), dtype="float")
        iterator = itertools.product(range(X.shape[0]), range(Y.shape[0]))
        for i, j in iterator:
            out[i, j] = metric(X[i], Y[j])

    return out
