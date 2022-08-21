'''
This module implements various machine learning models for
dimensionality reduction, listed below (alongside their class name).

Principal components analysis (`PCA`)
Kernel principal components analysis (`KernelPCA`)
'''

import numpy as np

from rithml import base
from rithml.formatting import reformat
from rithml.regression import KernelRegression

class PCA(base.BaseModel):
    '''
    Class for performing principal components analysis (PCA).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        components_ : numpy.ndarray of shape `(n_components,
        n_features)`
            Array of components used by the model, where `n_components`
            is the number of components (specified in the constructor).
            
    Methods:
        fit(X)
            Fits a PCA model to data.
        transform(X)
            Reduces the dimension of data using the model.
        fit_transform(X)
            Fits the model to data and then reduces their dimension.
        inverse_transform(Z)
            Reconstructs transformed data into their original dimension.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(self, n_components=None):
        '''
        Creates a PCA model.
        
        Parameters:
            n_components : int, default None
                Number of principal components kept and used by the
                model.
                If None, then all components are kept.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.components_ = None
    
    def fit(self, X):
        '''
        Fits a PCA model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
                    
        Returns:
            self : PCA
                Fitted PCA model.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        m = len(X)

        if self.n_components is None:
            self.n_components = m
        
        # Compute principal components
        self.components_ = np.linalg.svd(
            X - X.mean(axis=0), full_matrices=False)[2][:self.n_components]

        return self
    
    def transform(self, X):
        '''
        Reduces the dimension of data using the model.
        
        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to reduce dimension of.
        
        Returns:
            Z : numpy.ndarray of shape `(n_test_samples,
            n_components)`
                Transformed data.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        V = self.components_.T
        
        return X @ V
    
    def fit_transform(self, X):
        '''
        Fits the model to data and then reduces their dimension.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Data to fit to and reduce dimension of.
        
        Returns:
            Z : numpy.ndarray of shape `(n_samples, n_components)`
                Transformed data.
        '''
        
        return self.fit(X).transform(X)

    def inverse_transform(self, Z):
        '''
        Reconstructs transformed data into their original dimension.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            Z : numpy.ndarray of shape `(n_test_samples,
            n_components)`
                Transformed data to reconstruct.
        
        Returns:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Reconstructed data.
        '''
        
        # Ensure input array is a 2-D array of floats
        Z = reformat(Z)

        return Z @ self.components_

class KernelPCA(base.BaseModel):
    '''
    Class for performing principal components analysis (PCA) using
    kernel methods.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        components_ : numpy.ndarray of shape `(n_components, n_samples)`
            Array of components used by the model, where `n_components`
            is the number of components (specified in the constructor).
        regressors_ : list
            List of regressors (see
            `rithml.regression.KernelRegression`) used for inverse
            transformation. Only created if
            `fit_inverse_transform == True`.
            
    Methods:
        fit(X)
            Fits a kernel PCA model to data.
        transform(X)
            Reduces the dimension of data using the model.
        fit_transform(X)
            Fits the model to data and then reduces their dimension.
        inverse_transform(Z)
            If applicable, reconstructs transformed data into their
            original dimension.
            This is performed via kernel regression (see
            `rithml.regression.KernelRegression`), where the
            regressors are fitted to the original training data using
            the transformed training data as features.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_components=None, *, kernel='rbf', degree=3, gamma=1.0,
        coef0=1.0, fit_inverse_transform=False, alpha=1.0):
        '''
        Creates a kernel PCA model.
        
        Parameters:
            n_components : int, default None
                Number of principal components kept and used by the
                model.
                If None, then all components are kept.
            kernel : {
                'rbf', 'linear', 'poly'} or callable, default 'rbf'
                Determines kernel function used by all underlying binary
                classifiers. If a function is provided, then it must
                take in two feature vectors and compute a float.
            degree : int, default 3
                Degree of polynomial kernel. If `kernel` is not 'poly', 
                then this parameter is ignored.
            gamma : float, default 1.0
                Gamma parameter for polynomial and radial basis function
                (RBF) kernels. If `kernel` is not 'poly' or 'rbf', then
                this parameter is ignored.
            coef0 : float, default 1.0
                Constant term used in polynomial kernel. If `kernel` is
                not 'poly', then this parameter is ignored.
            fit_inverse_transform : bool, default False
                If True, fit the regressors for inverse transformation
                during fitting. Note that this takes additional time.
            alpha : float, default 1.0
                Regularization coefficient (strength) for regressors
                used for inverse transformation.
                If `fit_inverse_transform=False`, then this is ignored.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.components_ = None
        self.regressors_ = None

        # Initialize non-public attributes
        self._X = None
        self._X_proj = None
        self._proj_mean = None
        self._means = None
        self._sum = None

    def fit(self, X):
        '''
        Fits a kernel PCA model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
                    
        Returns:
            self : PCA
                Fitted PCA model.
        '''
        
        # Set kernel function
        kernels = {'rbf': lambda x, z :
                    np.exp(-self.gamma * np.square(
                        np.linalg.norm(x[:, None, :] - z, axis=2))),
                   'linear': lambda x, z : x @ z.T,
                   'poly': lambda x, z : 
                    (self.gamma * x @ z.T + self.coef0) ** self.degree}
        self._kernel = (kernels[self.kernel]
            if self.kernel in kernels.keys() else self.kernel)

        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        m = len(X)
        self._X = X

        if self.n_components is None:
            self.n_components = m
            
        # Compute kernel matrix
        K = self._kernel(self._X, self._X)

        # Compute attributes used in transformation
        self._means = K.mean(axis=1)
        self._sum = K.sum() / (m ** 2)

        # Compute mean-centered kernel matrix
        K_centered = K - self._means - self._means[:, None] + self._sum
        
        # Compute principal components
        e = np.linalg.eigh(K_centered)
        self.components_ = e[1].T[-self.n_components:]

        self._X_proj = K_centered @ self.components_.T
        
        # Fit regressors for inverse transformation (if needed)
        if self.fit_inverse_transform:
            # Compute kernel matrix for transformed input data
            self._proj_mean = self._X_proj.mean(axis=0)
            X_proj_centered = self._X_proj - self._proj_mean
            K_proj = self._kernel(X_proj_centered, X_proj_centered)

            # Fit regressors for kernel regression
            self.regressors_ = [KernelRegression(
                alpha=self.alpha, kernel=self._kernel)
                .fit(self._X_proj, y, K=K_proj)
                for y in X.T]

        return self
    
    def transform(self, X):
        '''
        Reduces the dimension of data using the model.
        
        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to reduce dimension of.
        
        Returns:
            Z : numpy.ndarray of shape `(n_test_samples, n_components)`
                Transformed data.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Compute kernel functions for input data
        K_pred = self._kernel(X, self._X)
        mean = K_pred.mean(axis=1)[:, None]
        K_pred = K_pred - self._means - mean + self._sum
        
        return K_pred @ self.components_.T
    
    def fit_transform(self, X):
        '''
        Fits the model to data and then reduces their dimension.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Data to fit to and reduce dimension of.
        
        Returns:
            Z : numpy.ndarray of shape `(n_samples, n_components)`
                Transformed data.
        '''
        
        return self.fit(X)._X_proj

    def inverse_transform(self, Z):
        '''
        If applicable, reconstructs transformed data into their original
        dimension.
        This is performed via kernel regression (see
        `rithml.regression.KernelRegression`), where the
        regressors are fitted to the original training data using the
        transformed training data as features.
        
        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            Z : numpy.ndarray of shape `(n_test_samples,
            n_components)`
                Transformed data to reconstruct.
        
        Returns:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Reconstructed data.
        '''
        
        # Raise error if inverse transformation is not supported
        if self.alpha is None:
            raise RuntimeError('Must allow inverse transform by initializing \
                with `fit_inverse_transform=True`.')

        # Ensure input array is a 2-D array of floats
        Z = reformat(Z)

        # Compute kernel functions for input data
        X_proj_centered = self._X_proj - self._proj_mean
        Z_centered = Z - self._proj_mean
        K_pred = self._kernel(Z_centered, X_proj_centered)

        # Compute reconstructed data
        X = np.array([
            reg.predict(Z, K_pred=K_pred) for reg in self.regressors_]).T

        return X