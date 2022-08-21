'''
This module contains a helper function for formatting data.
'''

import numpy as np

def reformat(X, bias=False):
    '''
    Reformats an array of numeric data by:
    (1) Making a copy of the array so that changes can be made
    (2) Ensuring that the copy is 2-D (if the original is 1-D)
    (3) Ensuring that the elements of the new array are floats
    (4) Appending a column of ones to support a bias term (if specified)

    `(n_rows, n_columns)` refers to the shape of the input array.
    
    Parameters:
        X : numpy.ndarray of shape `(n_rows, n_columns)`
            Feature weights.
        bias : bool, default False
            If True, appending a column of ones to support a bias term
            (used in linear regression, logistic regression, etc.).
    
    Returns:
        X2 : numpy.ndarray of shape `(n_rows, n_columns)` or `(n_rows,
        n_columns + 1)`
            2-D copy of the input array with elements as floats and an
            additional column of ones (if specified).
    '''

    X2 = X.copy()
    m = len(X2)
    if X2.ndim == 1:
        X2 = np.reshape(X, (m, 1))
    X2 = X2.astype('float')
    if bias:
        X2 = np.concatenate((X2, np.ones((m, 1))), axis=1)
    
    return X2