'''
This module implements various machine learning models for regression,
listed below (alongside their class name).

Linear regression (`LinearRegression`)
Decision tree (`DecisionTreeRegressor`)
K-nearest neighbors (`KNNRegressor`)
Gradient boosting regression trees (`GradientBoostingRegressor`)
Random forest (`RandomForestRegressor`)
Support vector machine (`SupportVectorRegressor`)
Kernel regression (`KernelRegression`)
'''

import numpy as np
import typing
import warnings
from time import time
from scipy.spatial.distance import cdist
from cvxopt import matrix, solvers

from rithml import base
from rithml.formatting import reformat

class LinearRegression(base.BaseModel):
    '''
    Class for performing linear (least squares) regression.
    This class supports both ordinary regression (no regularization)
    and ridge regression (L2 regularization).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        weight_ : numpy.ndarray of shape `(n_features,)`
            Weight term associated with model.
        bias_ : float
            Bias term associated with model.
            
    Methods:
        fit(X, y)
            Fits a linear regression model to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(self, alpha=0):
        '''
        Creates a linear regression object.
        
        Parameters:
            alpha : float, default 0
                Regularization coefficient (strength). The
                regularization type is L2 (ridge regression).
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.weight_ = None
        self.bias_ = None
    
    def fit(self, X, y):
        '''
        Fits a linear regression model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                
        Returns:
            self : LinearRegression
                Fitted linear regression model.
        '''
        
        X = reformat(X, bias=True)
        m, d = X.shape

        reg = self.alpha * m * np.identity(d)
        reg[-1, -1] = 0

        w0 = np.linalg.inv(X.T @ X + reg) @ X.T @ y
        self.weight_, self.bias_ = w0[:-1], w0[-1]
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        # Make predictions
        y_pred = X @ self.weight_ + self.bias_

        return y_pred

class _DTRNode():
    '''
    Internal class that represents a node in a decision tree
    (regression).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        depth : int
            Depth of node in tree.
        max_depth : int
            Maximum depth of tree.
        error : {'squared', 'absolute'}, default 'squared'
            Error function for assessing split quality.
        left : _DTRNode
            Left child of node, or None if the node is pure.
        right : _DTRNode
            Right child of node, or None if the node is pure.
        feature : int
            Index of the feature used in making the split for the node,
            or None if the node is pure.
        threshold : float
            Threshold of the split for the node, or None if the node is
            pure.
        label : float
            Label predicted by the node, or None if the node is pure.
            
    Methods:
        fit(X, y[, weights])
            Fits the node (and any child nodes, recursively) to data.
        predict(x)
            Predicts label given a single sample.
    '''
    
    def __init__(self, *, depth, max_depth, error='squared'):
        '''
        Creates a decision tree node.
        
        Parameters:
            depth : int
                Depth of node in tree.
            max_depth : int
                Maximum depth of tree.
            error : {'squared', 'absolute'}, default 'squared'
                Error function for assessing split quality.
            
        '''
        
        self.depth = depth
        self.max_depth = max_depth
        
        self.error = error  
                
        self.left = None
        self.right = None
        
        self.feature = None
        self.threshold = None
        self.label = None
    
    def fit(self, X, y, weights=None):
        '''
        Fits the node (and any child nodes, recursively) to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
            weights : numpy.ndarray of shape `(n_samples,)`, default
            None
                Weights for training samples.
                If None, then samples are weighted uniformly.
                These weights are used to influence calculations of node
                impurity.
        
        Returns:
            self : _DTRNode
                Fitted decision tree node.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        m = len(X)

        at_max = (self.max_depth != None) and (self.depth >= self.max_depth)

        # Set and scale weights
        w = np.full(len(X), 1) if weights is None else weights
        w = w / w.sum() * m
        
        # Determine if the node is pure (i.e. has homogeneous training
        # labels) or at the max depth
        if len(np.unique(y)) == 1 or at_max:
            self.label = y.dot(w / m)
        else:
            # Define absolute and squared error functions, given labels
            if self.error == 'absolute':
                error = lambda y, w, sum : np.dot(
                    w, np.abs(np.subtract(y, np.dot(y, w) / sum)))
            else:
                error = lambda y, w, sum : np.dot(
                    w, np.square(np.subtract(y, np.dot(y, w) / sum)))

            # Determine the best split among all possible splits for any
            # single feature
            best_score = float('inf')
            t = 0
            for f, c in enumerate(X.T):
                stacked = np.column_stack((c, y, w))
                sorted = stacked[stacked[:, 0].argsort()]
                c2, y2, w2 = sorted[:, 0], sorted[:, 1], sorted[:, 2] 
                cs = np.cumsum(w2)

                for i in range(1, m):
                    # Calculate weighted sums for both sides
                    l, r = cs[i - 1], m - cs[i - 1]
                    t0 = time()
                    # Calculate score of split
                    score = (l / m  * error(y2[:i], w2[:i], l)
                        + r / m * error(y2[i:], w2[i:], r))
                    t += time() - t0
                    
                    if score < best_score:
                        best_score = score
                        self.feature = f
                        self.threshold = np.mean([c2[i - 1], c2[i]])
            
            # Handle case where two samples have the same predictor
            # value
            if len(X[X[:, self.feature] > self.threshold]) == 0:
                self.label = y.dot(w / m)
                self.feature = None
                self.threshold = None
            else:
                # Create child nodes and recursively fit them based on
                # the best split
                self.left = _DTRNode(depth=self.depth + 1,
                    max_depth=self.max_depth, error=self.error)
                self.right = _DTRNode(depth=self.depth + 1,
                    max_depth=self.max_depth, error=self.error)
                indices_l = X[:, self.feature] <= self.threshold
                indices_r = X[:, self.feature] > self.threshold
                self.left.fit(X[indices_l], y[indices_l], w[indices_l])
                self.right.fit(X[indices_r], y[indices_r], w[indices_r])
        
        return self
                
    def predict(self, x):
        '''
        Predicts label given a single sample.
        
        Parameters:
            x : numpy.ndarray of shape `(n_features,)`
                Predictors (for a single sample) to compute a label for.
        
        Returns:
            y : (depends)
                Predicted label.
        '''
        
        # Check if node is pure; otherwise, recursively call predict on
        # the appropriate child node
        if not(self.label is None):
            return self.label
        elif x[self.feature] <= self.threshold:
            return self.left.predict(x)
        else:
            return self.right.predict(x)

class DecisionTreeRegressor(base.BaseModel):
    '''
    Class for performing regression via decision tree.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        root_ : _DTRNode
            Root node of underlying decision tree.
            
    Methods:
        fit(X, y[, weights])
            Fits a decision tree classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(self, max_depth=None, error='squared'):
        '''
        Creates a decision tree regressor.
        
        Parameters:
            max_depth : int, default None
                Maximum depth of tree.
            error : {'squared', 'absolute'}, default 'squared'
                Error function for assessing split quality.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.root_ = None
    
    def fit(self, X, y, weights=None):
        '''
        Fits a decision tree classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
            weights : numpy.ndarray of shape `(n_samples,)`, default
            None
                Weights for training samples.
                If None, then samples are weighted uniformly.
                    
        Returns:
            self : DecisionTreeRegressor
                Fitted decision tree regressor.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        self.root_ = _DTRNode(
            depth=0, max_depth=self.max_depth, error=self.error)
        self.root_.fit(X, y, weights=weights)
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Make predictions
        y_pred = np.array([self.root_.predict(x) for x in X])
        
        return y_pred

class KNNRegressor(base.BaseModel):
    '''
    Class for performing regression via k-nearest neighbors (k-NN).
    
    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
            
    Methods:
        fit(X, y)
            Fits a k-NN classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(self, n_neighbors=5, *, weights='uniform'):
        '''
        Creates a k-NN regressor.
        
        Parameters:
            n_neighbors : int, default 5
                Number of nearest neighbors to consider.
            weights : {'uniform', 'distance'}, default 'uniform'
                Weights assigned to k nearest neighbors, either uniform
                ('uniform') or based on inverse distance ('distance').
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize non-public attributes
        self._X = None
        self._y = None
    
    def fit(self, X, y):
        '''
        Fits a k-NN regressor to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : KNNRegressor
                Fitted k-NN regressor.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        self._X = reformat(X)
        self._y = np.copy(y)
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        warnings.filterwarnings('ignore', category=RuntimeWarning)

        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Obtain indices of `self.n_neighbors` nearest neighbors
        dists = cdist(X, self._X)
        indices = np.argpartition(
            dists, self.n_neighbors, axis=1)[:, :self.n_neighbors]
        labels = self._y[indices]
        
        # Make predictions based on weight type
        if self.weights == 'distance':
            weighted = np.reciprocal(
                dists[np.arange(len(X))[:, None], indices])
            y_pred = np.average(labels, axis=1, weights=weighted)

            # Handle cases where training samples have the same
            # predictors
            inf = (weighted == float('inf'))
            means_same = (labels * inf).sum(axis=1) / inf.sum(axis=1)
            y_pred = np.where(np.isnan(y_pred), means_same, y_pred)
        else:
            y_pred = np.mean(labels, axis=1)
        
        return y_pred

class GradientBoostingRegressor(base.BaseModel):
    '''
    Class for performing regression via gradient boosting (with
    regression trees as estimators).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        estimators_ : list
            List of estimators used by the model.
            
    Methods:
        fit(X, y)
            Fits a gradient boosting regressor to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_estimators=100, *, learning_rate=0.1, max_depth=3, 
        error='squared', verbose=None):
        '''
        Creates a gradient boosting regressor.
        
        Parameters:
            n_estimators : int, default 100
                Number of estimators used by the model.
            learning_rate : float, default 0.1
                Rate at which each additional estimator contributes to
                the model.
            max_depth : int, default 3
                Maximum depth of individual estimators.
            error : {'squared', 'absolute'}, default 'squared'
                Error function for assessing split quality.
            verbose : int, default None
                If not None, output details about progress and time
                elapsed during fitting.
                Additionally, if >0, then output when every `verbose`th
                estimator has been fitted.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.estimators_ = None
    
    def fit(self, X, y):
        '''
        Fits a gradient boosting regressor to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : GradientBoostingRegressor
                Fitted gradient boosting regressor.
        '''

        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        self.estimators_ = []
        self._mean = y.mean()
        labels = y - self._mean

        for t in range(self.n_estimators):
            h = DecisionTreeRegressor(
                max_depth=self.max_depth, error=self.error).fit(X, labels)
            self.estimators_.append(h)
            labels -= self.learning_rate * h.predict(X)

            if (self.verbose is not None and self.verbose > 0
                and (t + 1) % self.verbose == 0):
                print(f'{t + 1} of {self.n_estimators} estimators fitted.')
        
        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')
        
        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Make predictions
        y_pred = self._mean + self.learning_rate * np.array([h.predict(X) 
            for h in self.estimators_]).sum(axis=0)
        
        return y_pred

class RandomForestRegressor(base.BaseModel):
    '''
    Class for performing regression via random forest.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        estimators_ : dict
            Dictionary of all DecisionTreeRegressor estimators (keys)
            and arrays of features used (values).
            
    Methods:
        fit(X, y)
            Fits a random forest regressor to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_estimators=100, *, max_depth=None, error='squared',
        random_state=None, max_samples=None, max_features=None,
        bootstrap=True, verbose=None):
        '''
        Creates a random forest classifier.
        
        Parameters:
            n_estimators : int, default 100
                Number of estimators used by the model.
            max_depth : int, default None
                Maximum depth of individual estimators.
            error : {'squared', 'absolute'}, default 'squared'
                Error function for assessing split quality.
            bootstrap : bool, default True
                If True, use bootstrapping, i.e. re-sample new datasets
                for each estimator. If False, use the original dataset
                to fit each estimator (ignoring `max_samples`).
            random_state : int, numpy.random.RandomState, or
                numpy.random.Generator, default None
                Object used for random processes during fitting, i.e.
                    (1) drawing samples with replacement to create
                    `n_estimators` new datasets, based on `max_samples`
                    (when `bootstrap == True`)
                    (2) selecting a subset of features for each such
                    dataset, based on `max_features`
                If None, then a new Generator object is created (i.e.
                with a fresh seed).
                If int, then a new Generator object is created with the
                specified int as the seed.
                If RandomState or Generator, then that object is
                directly used.
            max_samples : callable or int, default None
                The number of samples to draw from the original dataset
                `X` to create each new dataset during bootstrapping
                (when `bootstrap == True`), one for each estimator.
                If None, then `n_samples` samples are drawn.
                If callable, then `max_samples(n_samples)` samples are
                drawn. (For example, this can be used to draw a
                specified proportion of `n_samples` samples.)
                If int, then `max_samples` samples are drawn.
            max_features : {
                'sqrt', 'log2'}, callable, or int, default None
                The number of features used by each estimator.
                If None, then `n_features` features are used.
                If 'sqrt', then `sqrt(n_features)` features are used.
                If 'log2', then `log2(n_features)` features are used.
                If callable, then `max_features(n_features)` features
                are used. (For example, this can be used to use a
                specified proportion of `n_features` features.)
                If int, then `max_features` are used.
            verbose : int, default None
                If not None, output details about progress and time
                elapsed during fitting.
                Additionally, if >0, then output when every `verbose`th
                estimator has been fitted.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.estimators_ = None

        # Initialize non-public attributes
        self._rng = None
        self._sample_func = None
        self._feature_func = None
    
    def fit(self, X, y):
        '''
        Fits a random forest regressor to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : RandomForestRegressor
                Fitted random forest regressor.
        '''

        # Handle various inputs for `random_state`
        if self.random_state is None or isinstance(self.random_state, int):
            self._rng = np.random.default_rng(self.random_state)
        elif (isinstance(self.random_state, np.random.RandomState)
            or isinstance(self.random_state, np.random.Generator)):
            self._rng = self.random_state
        else:
            self._rng = np.random.default_rng(None)
        
        # Handle various inputs for `max_samples`
        if self.max_samples is None:
            self._sample_func = lambda m : m
        elif isinstance(self.max_samples, typing.Callable):
            self._sample_func = self.max_samples
        elif isinstance(self.max_samples, int):
            self._sample_func = lambda _ : self.max_samples
        else:
            self._sample_func = lambda m : m
        
        # Handle various inputs for `max_features`
        if self.max_features == 'sqrt':
            self._feature_func = np.sqrt
        elif self.max_features == 'log2':
            self._feature_func = np.log2
        elif self.max_features is None:
            self._feature_func = lambda d : d
        elif isinstance(self.max_features, typing.Callable):
            self._feature_func = self.max_features
        elif isinstance(self.max_features, int):
            self._feature_func = lambda _ : self.max_features
        else:
            self._feature_func = lambda d : d
        
        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
            
        self.estimators_ = {}
        m, d = X.shape
        n_samples = max(1, int(self._sample_func(m)))
        n_features = max(1, int(self._feature_func(d)))
        
        # Draw samples and select features from input data, for each
        # estimator
        for t in range(self.n_estimators):
            samples = self._rng.choice(
                range(m), size=n_samples) if self.bootstrap else range(m)
            features = self._rng.choice(
                range(d), size=n_features, replace=False)
            features.sort()
            X2 = X[samples][:, features]
            y2 = y[samples]
            
            h = DecisionTreeRegressor(
                max_depth=self.max_depth, error=self.error).fit(X2, y2)
            self.estimators_[h] = np.copy(features)

            if (self.verbose is not None and self.verbose > 0
                and (t + 1) % self.verbose == 0):
                print(f'{t + 1} of {self.n_estimators} estimators fitted.')
        
        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')

        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Make predictions (select the most common prediction for each
        # sample)
        y_pred = np.array([h.predict(X[:, self.estimators_[h]])
                           for h in self.estimators_.keys()]).mean(axis=0)
        
        return y_pred

class SupportVectorRegressor(base.BaseModel):
    '''
    Class for performing regression via support vector machine (SVM).
    Note: The default parameter values may result in a poor model. If
    so, it is advised to change these values from their defaults,
    especially `C` or `gamma`.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Adapted from: Smola, Alex J.; Scholkopf, Bernhard (2004). "A
    tutorial on support vector regression" (PDF). Statistics and
    Computing. 14 (3): 199-222.
    (https://alex.smola.org/papers/2004/SmoSch04.pdf)
    
    Attributes:
        weight_ : callable
            Function for computing the weight term of a prediction (via
            the kernel trick). Takes in a feature vector and outputs a
            float.
        bias_ : float
            Bias term associated with the model.

    Methods:
        fit(X, y)
            Fits a support vector regressor to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, *, C=1.0, kernel='rbf', degree=3, gamma=1.0, coef0=1.0, 
        epsilon=1.0, error_coef=1e-6):
        '''
        Creates a support vector regressor.
        
        Parameters:
            C : float
                Regularization constant. Must be positive; lower value
                means more regularization.
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
                Constant term used in polynomial kernel. If
                `kernel` is not 'poly', then this parameter is ignored.
            epsilon : float, default 0.1
                Size of margin used by the model. Penalties are based
                only on the errors of predictions for training samples
                outside this margin, i.e. the support vectors.
            error_coef : float
                Coefficient for margin for error (`C * error_coef`) in
                determining support vectors when assessing coefficient
                values. A smaller value represents a stricter threshold
                and may result in less support vectors.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.weight_ = None
        self.bias_ = None

        # Initialize non-public attributes
        self._kernel = None
            
    def fit(self, X, y):
        '''
        Fits a support vector regressor to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : SupportVectorRegressor
                Fitted support vector regressor.
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
        half = 0.5 * np.identity(m)
        P0 = np.zeros((2 * m, 2 * m))
        P0[:m, :m] = self._kernel(X, X)
        
        # Optimize alphas (coefficients) via quadratic programming
        P = matrix(P0)
        q = matrix(np.concatenate((-y, np.full(m, self.epsilon))))
        G = matrix(np.hstack((np.vstack((half, -half, -half, half)),
                              np.vstack((half, half, -half, -half)))))
        h = matrix(np.concatenate((np.full(2 * m, self.C), np.zeros(2 * m))))
        A = matrix(
            np.concatenate((np.full(m, 1), np.zeros(m))).reshape(1, 2 * m))
        b = matrix(0.)
        solvers.options['show_progress'] = False
        
        alpha = np.array(solvers.qp(P, q, G, h, A, b)['x']).reshape(2 * m)
        
        # Determine the indices of support vectors (including those on
        # the margin)
        sv = np.argwhere(
            np.abs(alpha[:m]) > self.C * self.error_coef).flatten()
        sv1 = np.argwhere(
            np.abs(alpha[sv]) < self.C * (1 - self.error_coef)).flatten()
        
        # Filter `alpha`, `X`, and `y2` by the indices of support
        # vectors, and compute the weight and bias
        alpha_new = alpha[sv]
        X_new = X[sv]
        y_new = y[sv]
        
        self.weight_ = lambda Z : np.sum(
            alpha_new[:, None] * self._kernel(X_new, Z), axis=0)
        
        self.bias_ = (0 if len(sv1) == 0 
            else (y_new[sv1] - self.weight_(X_new[sv1])).mean())

        return self
    
    def predict(self, X):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Make predictions
        y_pred = self.weight_(X) + self.bias_
        
        return y_pred

class KernelRegression(base.BaseModel):
    '''
    Class for performing kernel regression.
    This class supports both ordinary regression (no regularization)
    and ridge regression (L2 regularization).

    Note: The default parameter values may result in a poor model. If
    so, it is advised to change these values from their defaults,
    especially `alpha` or `gamma`.

    Note that attempting to perform ordinary regression (with alpha=0)
    may result in a singular matrix error during fitting. For this
    reason, it may be better to use a very low alpha value instead.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.

    Adapted from: https://statinfer.wordpress.com/2013/08/05/undocumented-machine-learning-ii-kernel-regression/
    
    Attributes:
        weight_ : numpy.ndarray of shape `(n_samples,)`
            Weight term associated with model.
        bias_ : float
            Bias term associated with model.
        mean_ : numpy.ndarray of shape `(n_features,)`
            Mean of the training data.
            
    Methods:
        fit(X, y[, K])
            Fits a kernel regression model to data.
        predict(X[, K_pred])
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, *, alpha=1.0, kernel='rbf', degree=3, gamma=1.0,
        coef0=1.0, nonzero_bias=True):
        '''
        Creates a kernel regression object.
        
        Parameters:
            alpha : float, default 1.0
                Regularization coefficient (strength). The
                regularization type is L2 (ridge regression).
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
                Constant term used in polynomial kernel. If
                `kernel` is not 'poly', then this parameter is ignored.
            nonzero_bias : bool, default True
                If False, the model assumes a bias of 0.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.weight_ = None
        self.bias_ = None
        self.mean_ = None

        # Initialize non-public attributes
        self._X = None
        self._kernel = None
    
    def fit(self, X, y, K=None):
        '''
        Fits a kernel regression model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
            K : numpy.ndarray of shape `(n_samples, n_samples)`,
            default None
                Kernel matrix, i.e. kernel result for every pair of
                training samples.
                If `nonzero_bias` is True, then these training samples
                should be mean-centered before applying the kernel
                function to them.
                If None, the model computes the kernel matrix itself.
                
        Returns:
            self : KernelRegression
                Fitted kernel regression model.
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

        y = y.copy()
        self._X = reformat(X)
        m, d = self._X.shape
        
        # Mean-center training data if bias is not assumed to be zero
        if self.nonzero_bias:
            self.mean_ = self._X.mean(axis=0)
            self._X = self._X - self.mean_
            self.bias_ = y.mean()
            y = y - self.bias_
        else:
            self.mean_ = np.zeros(d)
            self.bias_ = 0

        # Compute kernel matrix (if not already provided)
        if K is None:
            K = self._kernel(self._X, self._X)

        # Compute weights
        self.weight_ = np.linalg.inv(K + self.alpha * np.identity(m)) @ y

        return self
    
    def predict(self, X, K_pred=None):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
            K_pred : numpy.ndarray of shape `(n_test_samples,
            n_samples)`, default None
                Kernel matrix, i.e. kernel result for every test sample
                with every training sample.
                If `nonzero_bias` is True, then all samples should be
                mean-centered (based on the training mean, i.e. the
                `mean_` attribute) before applying the kernel function
                to them.
                If None, the model computes the kernel matrix itself.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        X = X - self.mean_
        
        # Compute kernel matrix for input data (if not already provided)
        if K_pred is None:
            K_pred = self._kernel(X, self._X)

        # Make predictions
        y_pred = K_pred @ self.weight_ + self.bias_

        return y_pred