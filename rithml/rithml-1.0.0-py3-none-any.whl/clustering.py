'''
This module implements various machine learning models for clustering,
listed below (alongside their class name).

K-means clustering (`KMeans`)
Gaussian mixture model (`GaussianMixture`)
'''

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import multivariate_normal as mv_norm
from time import time

from rithml import base
from rithml.formatting import reformat

class KMeans(base.BaseModel):
    '''
    Class for performing k-means clustering.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        centers_ : numpy.ndarray of shape `(n_clusters, n_features)`
            Array of all cluster centers of the fitted model, where
            `n_clusters` is the number of clusters assumed by the model
            (specified in the constructor).
        labels_ : numpy.ndarray of shape `(n_samples,)`
            Labels assigned by the fitted model to the training data.
        n_iter_ : int
            Number of iterations taken by the model before stopping.
        distortion_ : float
            Distortion of the training data, i.e. sum of all squared
            distances from corresponding cluster centers.
            
    Methods:
        fit(X)
            Fits a k-means clustering model to data.
        predict(X)
            Predicts labels for the input data.
        fit_predict(X)
            Fits the model to data and then predicts their labels.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_clusters=3, *, init='k-means++', max_iter=100,
        random_state=None, verbose=None):
        '''
        Creates a k-means clustering model.
        
        Parameters:
            n_clusters : int, default 3
                Number of clusters assumed by the model.
            init : {'k-means++', 'random'} or numpy.ndarray of shape
            `(n_clusters, n_features)`, default 'k-means++'
                Specifies how to initialize the means (cluster centers)
                for the model.
                If 'k-means++', then the k-means++ algorithm is used.
                If 'random', then a random sample of size n_clusters is
                selected without replacement from the training data.
                If numpy.ndarray, then the specified array (if the shape
                is correct) is used, i.e. assumed to be the array of
                means.
            max_iter : int, default 100
                Maximum number of iterations for the model to take
                before stopping.
                If None, then no maximum is used.
            random_state : int, numpy.random.RandomState, or
                numpy.random.Generator, default None
                Object used for random processes during fitting, i.e.
                randomly drawing samples from the training data during
                initialization, if `init` is 'k-means++' or 'random'.
                (If `init` is an array, then `random_state` is not
                used.)
                If None, then a new Generator object is created (i.e.
                with a fresh seed).
                If int, then a new Generator object is created with the
                specified int as the seed.
                If RandomState or Generator, then that object is
                directly used.
            verbose : int, default None
                If not None, output details about progress and time
                elapsed during fitting.
                Additionally, if >0, then output a progress message
                after every `verbose` iterations.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.centers_ = None
        self.labels_ = None
        self.n_iter_ = None
        self.distortion_ = None

        # Initialize non-public attributes
        self._max_iter = max_iter if max_iter is not None else float('inf')
        self._rng = None
    
    def fit(self, X):
        '''
        Fits a k-means clustering model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
                    
        Returns:
            self : KMeans
                Fitted k-means clustering model.
        '''
        
        # Handle various inputs for `random_state`
        if self.random_state is None or isinstance(self.random_state, int):
            self._rng = np.random.default_rng(self.random_state)
        elif (isinstance(self.random_state, np.random.RandomState)
            or isinstance(self.random_state, np.random.Generator)):
            self._rng = self.random_state
        else:
            self._rng = np.random.default_rng(None)

        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        m, d = X.shape

        # Initialize centers (based on `self.init`)
        if (isinstance(self.init, np.ndarray) 
            and self.init.shape == (self.n_clusters, d)):
            # Use given array (if of the correct size)
            self.centers_ = self.init.copy()
        elif self.init == 'random':
            # Randomly sample from training data without replacement
            self.centers_ = X[
                self._rng.choice(m, size=self.n_clusters, replace=False)]
        else:
            # Set up for the k-means++ algorithm
            X2 = X.copy()
            p = np.ones(m) / m
            centers = []

            # Randomly sample from training data without replacement,
            # using the distance from nearest center as a weight
            for _ in range(self.n_clusters):
                i = self._rng.choice(X2.shape[0], p=p)
                centers.append(X2[i])
                X2 = np.delete(X2, i, axis=0)
                p = cdist(X2, centers).min(axis=1) ** 2
                p /= p.sum()
            self.centers_ = np.array(centers)
        
        if self.verbose is not None:
            print('Initialization complete.')

        self.labels_ = np.full(m, None)
        labels_prev = None
        converge = False
        self.n_iter_ = 0

        # Repeat iterations until the model converges or the maximum
        # number of iterations is reached
        while not converge and self.n_iter_ < self._max_iter:
            # Compute labels by minimizing distance to cluster center
            self.labels_ = cdist(X, self.centers_).argmin(axis=1)

            # Check if model has converged, i.e. if labels have stayed
            # the same
            converge = np.array_equal(self.labels_, labels_prev)

            # Prepare for next iteration (i.e. recompute cluster
            # centers as means of their clusters)
            labels_prev = self.labels_
            self.centers_ = np.array([np.mean(X[self.labels_ == l], axis=0)
                for l in range(self.n_clusters)])
            self.n_iter_ += 1

            if (self.verbose is not None and self.verbose > 0
                and self.n_iter_ % self.verbose == 0):
                print(f'{self.n_iter_} iterations complete.')
        
        # Compute distortion (sum of squared distances to centers)
        dists = np.linalg.norm(X - self.centers_[self.labels_], axis=1)
        self.distortion_ = (dists ** 2).sum()

        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels for the input data, i.e. clusters the data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to predict labels of.
        
        Returns:
            labels : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Compute labels by minimizing distance to cluster center
        labels = cdist(X, self.centers_).argmin(axis=1)
        
        return labels
    
    def fit_predict(self, X):
        '''
        Fits the model to data and then predicts their labels, i.e.
        clusters the data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Data to fit to and predict labels of.
        
        Returns:
            labels : numpy.ndarray of shape `(n_samples,)`
                Predicted labels.
        '''
        
        return self.fit(X).labels_

class GaussianMixture(base.BaseModel):
    '''
    Class for performing clustering via a Gaussian mixture model (GMM).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_components`: Number of components assumed by the model (specified
    in the constructor).
    
    Attributes:
        weights_ : numpy.ndarray of shape `(n_components`,)
            Array of component weights.
        means_ : numpy.ndarray of shape `(n_components`, `n_features`)
            Array of component means.
        covariances_ : numpy.ndarray of shape `(n_components`,
        `n_features`, `n_features`)
            Array of component covariance matrices.
        labels_ : numpy.ndarray of shape `(n_samples,)`
            Labels assigned by the fitted model to the training data.
        log_likelihood_ : float
            Log-likelihood of the training data based on the fitted
            model.
        n_iter_ : int
            Number of iterations taken by the model before stopping.
        n_params_ : int
            Number of free parameters in the model. Depends on
            covariance_type. Used in calculation of AIC and BIC.
        aic_fit_ : float
            Akaike information criterion (AIC) of the model on the
            training data.
        bic_fit_ : float
            Bayesian information criterion (BIC) of the model on the
            training data.
        
    Methods:
        fit(X)
            Fits a Gaussian mixture model (GMM) to data using the
            expectation-maximiziation (EM) algorithm.
        predict(X)
            Predicts labels for the input data.
        fit_predict(X)
            Fits the model to data and then predicts their labels.
        aic(X)
            Computes the Akaike information criterion (AIC) of the model
            on the specified data.
        bic(X)
            Computes the Bayesian information criterion (BIC) of the
            model on the specified data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_components=3, *, covariance_type='full', tol=0.1,
        reg=1e-6, max_iter=100, init='k-means', weights_init=None,
        means_init=None, covariances_init=None, random_state=None,
        verbose=None):
        '''
        Creates a Gaussian mixture model (GMM).
        
        Parameters:
            n_components : int, default 3
                Number of components assumed by the model.
            covariance_type : {
                'full', 'tied', 'diag', 'tied_diag', 'spherical',
                'tied_spherical'}, default 'full'
                Specifies assumptions about component covariance
                matrices.
                If 'full', each component has its own covariance matrix.
                If 'tied', all components share the same covariance
                matrix.
                If 'diag', each component has its own covariance matrix,
                which is assumed to be diagonal.
                If 'tied_diag', all components share the same covariance
                matrix, which is assumed to be diagonal.
                If 'spherical', each component has its own covariance
                matrix, which is assumed to be a multiple of the
                identity matrix.
                If 'tied_spherical', all components share the same
                covariance matrix, which is assumed to be a multiple of
                the identity matrix.
            tol : float, default 0.1
                Tolerance level for assessing convergence. That is,
                iterations of the EM algorithm stop once the increase in
                log-likelihood is no longer above this level.
            reg : float, default 1e-6
                Regularization constant added to the diagonal of all
                component covariance matrices to ensure nonsingularity.
            max_iter : int, default 100
                Maximum number of iterations for the model to take
                before stopping.
                If None, then no maximum is used.
            init : {
                'k-means', 'k-means++', 'random_from_data', 'random'},
                default 'k-means'
                Specifies how to initialize the means of the components.
                If 'k-means++', then the k-means algorithm is used to
                cluster the data, and the resulting cluster centers are
                used as the means.
                If 'k-means++', then the k-means++ algorithm is used to
                initialize the means.
                If 'random_from_data', then a random sample of size
                `n_components` is selected without replacement from the
                training data.
                If 'random', then a random sample of size `n_components`
                is selected from a multivariate Gaussian distribution
                fitted to the training data.
            weights_init : list, default None
                List of initial component weights for the model to use.
                If None, the weights are initialized based on `init`.
            means_init : list, default None
                List of initial component means for the model to use.
                If None, the means are initialized based on `init`.
            covariances_init : list, default None
                List of initial component covariance matrices for the
                model to use.
                If None, the covariances are initialized based on
                `init`.
            random_state : int, numpy.random.RandomState, or
                numpy.random.Generator, default None
                Object used for random processes during fitting, i.e.
                randomly drawing samples from the training data during
                initialization.
                If None, then a new Generator object is created (i.e.
                with a fresh seed).
                If int, then a new Generator object is created with the
                specified int as the seed.
                If RandomState or Generator, then that object is
                directly used.
            verbose : int, default None
                If not None, output details about progress and time
                elapsed during fitting.
                Additionally, if >0, then output a progress message
                after every `verbose` iterations.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.weights_ = None
        self.means_ = None
        self.covariances_ = None
        self.labels_ = None
        self.log_likelihood_ = None
        self.n_iter_ = None
        self.n_params_ = None
        self.aic_fit_ = None
        self.bic_fit_ = None

        # Initialize non-public attributes
        self._max_iter = max_iter if max_iter is not None else float('inf')
        self._rng = None

    def fit(self, X):
        '''
        Fits a Gaussian mixture model (GMM) to data using the
        expectation-maximiziation (EM) algorithm.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
                    
        Returns:
            self : GaussianMixture
                Fitted GMM.
        '''

        # Handle various inputs for `random_state`
        if self.random_state is None or isinstance(self.random_state, int):
            self._rng = np.random.default_rng(self.random_state)
        elif (isinstance(self.random_state, np.random.RandomState)
            or isinstance(self.random_state, np.random.Generator)):
            self._rng = self.random_state
        else:
            self._rng = np.random.default_rng(None)
        
        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        m, d = X.shape

        # Initialize centers (based on `self.init`)
        if self.init == 'k-means++':
            # Set up for the k-means++ algorithm
            X2 = X.copy()
            p = np.ones(m) / m
            means = []

            # Randomly sample from training data without replacement,
            # using the distance from nearest center as a weight
            for _ in range(self.n_components):
                i = self.rng.choice(X2.shape[0], p=p)
                means.append(X2[i])
                X2 = np.delete(X2, i, axis=0)
                p = cdist(X2, means).min(axis=1) ** 2
                p /= p.sum()
            self.means_ = np.array(means)
        elif self.init == 'random_from_data':
            # Randomly sample from training data without replacement
            self.means_ = X[
                self._rng.choice(m, size=self.n_components, replace=False)]
        elif self.init == 'random':
            # Randomly sample from multivariate Gaussian distribution
            # fitted to the training data
            self.means_ = self._rng.multivariate_normal(
                X.mean(axis=0), np.cov(X, rowvar=False), 
                size=self.n_components)
        else:
            # Initialize means via k-means clustering
            self.means_ = KMeans(
                self.n_components, random_state=self._rng).fit(X).centers_
        
        # Assign labels to the training data (based on nearest mean) and
        # partition the data accordingly
        dists = cdist(X, self.means_)
        self.labels_ = dists.argmin(axis=1)
        argsort = self.labels_.argsort()
        X_sorted, labels_sorted = X[argsort], self.labels_[argsort]
        indices = np.unique(labels_sorted, return_index=True)[1]
        partition = np.split(X_sorted, indices[1:])

        # Define regularization term
        reg_term = np.diag(np.full(d, self.reg))

        # Initialize component weights and means based on labels
        self.weights_ = (np.array([len(arr) / m for arr in partition])
            if self.weights_init is None else self.weights_init)
        self.means_ = (np.array([arr.mean(axis=0) for arr in partition])
            if self.means_init is None else self.means_init)

        # Initialize component covariances
        if self.covariances_init is not None:
            self.covariances_ = self.covariances_init
        elif self.covariance_type == 'tied':
            # Fit covariance matrix to the training data after centering
            # samples to their respective means
            centered = np.concatenate(tuple(
                [arr - self.means_[i] for i, arr in enumerate(partition)]))
            self.covariances_ = np.array([np.cov(centered, rowvar=False)
                + reg_term] * self.n_components)
        elif self.covariance_type == 'diag':
            # Fit covariance matrix to each component and keep
            # only the diagonal entries
            self.covariances_ = np.array([np.diag(np.diag(
                np.cov(arr, rowvar=False))) + reg_term for arr in partition])
        elif self.covariance_type == 'tied_diag':
            # Fit covariance matrix to the training data after centering
            # samples to their respective means and keep only the
            # diagonal entries
            centered = np.concatenate(tuple(
                [arr - self.means_[i] for i, arr in enumerate(partition)]))
            self.covariances_ = np.array([np.diag(np.diag(
                np.cov(centered, rowvar=False))) + reg_term]
                * self.n_components)
        elif self.covariance_type == 'spherical':
            # Fit covariance matrix to each component by multiplying the
            # identity matrix by the variance of distances from the
            # component mean
            self.covariances_ = np.array([
                cdist(arr, self.means_[i].reshape(1, -1)).var()
                * np.identity(d) + reg_term
                for i, arr in enumerate(partition)])
        elif self.covariance_type == 'tied_spherical':
            # Fit covariance matrix by multiplying the identity matrix
            # by the variance of distances to the nearest mean
            self.covariances_ = np.array([dists.min(axis=1).var()
                * np.identity(d) + reg_term] * self.n_components)
        else:
            # Fit covariance matrix to each component
            self.covariances_ = np.array([np.cov(arr, rowvar=False) + reg_term
                for arr in partition])

        if self.verbose is not None:
            print('Initialization complete.')

        ll_prev = float('-inf')
        converge = False
        self.n_iter_ = 0

        # Repeat iterations until the model converges or the maximum
        # number of iterations is reached
        while not converge and self.n_iter_ < self._max_iter:

            # Calculate training data likelihoods for each component            
            p = np.array([self.weights_[i] * mv_norm(
                self.means_[i], self.covariances_[i]).pdf(X)
                for i in range(self.n_components)])

            # Choose maximum-likelihood labels
            self.labels_ = p.argmax(axis=0)

            # Calculate log-likelihood
            lls = [np.array(mv_norm(self.means_[i], self.covariances_[i])
                .logpdf(X[self.labels_ == i])).reshape(-1)
                for i in range(self.n_components)]
            self.log_likelihood_ = np.sum([item for row in lls for item in row])

            # Check if model has converged, i.e. if log-likelihood has
            # increased by an amount lower than the tolerance level
            if self.log_likelihood_ < ll_prev + self.tol:
                break

            ll_prev = self.log_likelihood_

            # E-step: Compute responsibilities (normalize probabilities)
            r = np.nan_to_num(p / p.sum(axis=0))

            # M-step: Update parameters based on responsibilities
            self.weights_ = r.sum(axis=1) / m
            self.means_ = r @ X / r.sum(axis=1)[:, None]

            # Update covariances based on `covariance_type`
            if self.covariance_type == 'tied':
                # Mean-center the data with responsibilities as weights,
                # then fit covariance matrix
                centered = X - (r.T @ self.means_)
                self.covariances_ = np.array([np.cov(centered, rowvar=False)
                    + reg_term] * self.n_components)
            elif self.covariance_type == 'diag':
                # Fit covariance matrix to each component with
                # responsibilities as weights and keep only the diagonal
                # entries
                self.covariances_ = np.array([np.diag(np.diag(np.cov(
                    X, rowvar=False, aweights=w, ddof=0))) + reg_term
                    for w in r])
            elif self.covariance_type == 'tied_diag':
                # Mean-center the data with responsibilities as weights,
                # then fit covariance matrix and keep only the diagonal
                # entries
                centered = X - (r.T @ self.means_)
                self.covariances_ = np.array([np.diag(np.diag(
                    np.cov(centered, rowvar=False))) + reg_term]
                    * self.n_components)
            elif self.covariance_type == 'spherical':
                # Fit covariance matrix to each component by multiplying
                # the identity matrix by the variance of distances from
                # the mean with responsibilities as weights
                self.covariances_ = np.array([
                    float(np.cov(cdist(X, mean.reshape(1, -1)),
                    rowvar=False, ddof=0, aweights=r[i])) * np.identity(d)
                    + reg_term for i, mean in enumerate(self.means_)])
            elif self.covariance_type == 'tied_spherical':
                # Fit covariance matrix by multiplying the identity
                # matrix by the variance of distances from all means
                # with responsibilities as weights
                dists = cdist(X, self.means_)
                dists_weighted = np.array(
                    [q.dot(dists[i]) for i, q in enumerate(r.T)])
                self.covariances_ = np.array([dists_weighted.var()
                    * np.identity(d) + reg_term] * self.n_components)
            else:
                # Fit covariance matrix to each component with
                # responsibilities as weights 
                self.covariances_ = np.array(
                    [np.cov(X, rowvar=False, aweights=w, ddof=0) + reg_term
                    for w in r])

            self.n_iter_ += 1

            if (self.verbose is not None and self.verbose > 0
                and self.n_iter_ % self.verbose == 0):
                print(f'{self.n_iter_} iterations complete.')

        # Compute number of parameters based on `covariance_type`
        if self.covariance_type == 'tied':
            self.n_params_ = self.n_components * (1 + d) + d * (d + 1) / 2 - 1
        elif self.covariance_type == 'diag':
            self.n_params_ = self.n_components * (1 + 2 * d) - 1
        elif self.covariance_type == 'tied_diag':
            self.n_params_ = self.n_components * (1 + d) + d - 1
        elif self.covariance_type == 'spherical':
            self.n_params_ = self.n_components * (2 + d) - 1
        elif self.covariance_type == 'tied_spherical':
            self.n_params_ = self.n_components * (1 + d)
        else:
            self.n_params_ = self.n_components * (1 + d + d * (d + 1) / 2) - 1

        # Compute AIC and BIC of model on the training data
        self.aic_fit_ = 2 * self.n_params_ - 2 * self.log_likelihood_
        self.bic_fit_ = self.n_params_ * np.log(m) - 2 * self.log_likelihood_

        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels for the input data, i.e. clusters the data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to predict labels of.
        
        Returns:
            labels : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Compute likelihoods and choose the maximum-likelihood labels
        p = np.array([self.weights_[i] * mv_norm(
                self.means_[i], self.covariances_[i]).pdf(X)
                for i in range(self.n_components)])
        labels = p.argmax(axis=0)
        
        return labels
    
    def fit_predict(self, X):
        '''
        Fits the model to data and then predicts their labels, i.e.
        clusters the data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Data to fit to and predict labels of.
        
        Returns:
            labels : numpy.ndarray of shape `(n_samples,)`
                Predicted labels.
        '''
        
        return self.fit(X).labels_
    
    def aic(self, X):
        '''
        Computes the Akaike information criterion (AIC) of the model on
        the specified data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to predict labels of and compute the AIC on, where
                `n_test_samples` is the number of samples in the input
                data.
        
        Returns:
            aic : float
                AIC of the model on the data. A lower value suggests a
                stronger model.
        '''

        # Use predicted labels to compute log-likelihood
        labels = self.predict(X)
        lls = [np.array(mv_norm(self.means_[i], self.covariances_[i])
                .logpdf(X[labels == i])).reshape(-1)
                for i in range(self.n_components)]
        ll = np.sum([item for row in lls for item in row])

        return 2 * self.n_params_ - 2 * ll
    
    def bic(self, X):
        '''
        Computes the Bayesian information criterion (BIC) of the model
        on the specified data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Data to predict labels of and compute the BIC on, where
                `n_test_samples` is the number of samples in the input
                data.
        
        Returns:
            bic : float
                BIC of the model on the data. A lower value suggests a
                stronger model.
        '''

        # Use predicted labels to compute log-likelihood
        labels = self.predict(X)
        lls = [np.array(mv_norm(self.means_[i], self.covariances_[i])
                .logpdf(X[labels == i])).reshape(-1)
                for i in range(self.n_components)]
        ll = np.sum([item for row in lls for item in row])

        return self.n_params_ * np.log(len(X)) - 2 * ll