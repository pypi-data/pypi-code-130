'''
This module implements various machine learning models for
classification, listed below (alongside their class name).

Logistic regression (`LogisticRegression`)
Decision tree (`DecisionTreeClassifier`)
K-nearest neighbors (`KNNClassifier`)
Gradient boosting classification trees (`GradientBoostingClassifier`)
Random forest (`RandomForestClassifier`)
Support vector machine (`SupportVectorClassifier`)
Linear/quadratic discriminant analysis (`DiscriminantAnalysis`)
Gaussian naive Bayes (`GaussianNBClassifier`)
AdaBoost (`AdaBoostClassifier`)
'''

import numpy as np
from scipy.optimize import minimize
from scipy.stats import mode
from scipy.spatial.distance import cdist
import warnings
import typing
from time import time
from cvxopt import matrix, solvers

from rithml import base
from rithml.formatting import reformat

class LogisticRegression(base.BaseModel):
    '''
    Class for performing logistic regression.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_classes`: Number of classes in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
        weight_ : numpy.ndarray of shape `(n_classes, n_features)` or
        `(n_features,)`
            Feature weights used in the decision function.
            If the labels are not binary (i.e. `n_classes > 2`), then
            this is a 2-D array with weights for each class. Otherwise,
            its shape is `(n_features,)`.
        bias_ : numpy.ndarray of `(n_classes,)` or float
            Bias(es) used in the decision function.
            If the labels are not binary (i.e. `n_classes > 2`), then
            this is an array with a bias for each class. Otherwise,
            it is a single bias (float).

    Methods:
        fit(X, y)
            Fits a logistic regression model to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.        
    '''
    
    def __init__(self, *, alpha=0, tol=0.01, verbose=False):
        '''
        Creates a linear regression object.
        
        Parameters:
            alpha : float, default 0
                Regularization coefficient (strength). The
                regularization type is L2.
            tol : float, default 0.01
                Tolerance argument for logistic loss minimization. (A
                smaller value will increase runtime but may improve
                model performance.)
            verbose : bool, default False
                If True, output details about progress and time elapsed
                during fitting.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None
        self.weight_ = None
        self.bias_ = None

        # Initialize non-public attributes
        self._weight = None
    
    def _logistic_loss(self, w0, X, y):
        '''
        Computes the logistic loss of the model given input data.

        `n_samples_` and `n_features_` are the numbers of samples and
        features provided in the input data, respectively.
        
        Parameters:
            w0 : numpy.ndarray of shape `(n_features_,)`
                Feature weights.
            X : numpy.ndarray of shape `(n_samples_, n_features_,)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples_,)`
                Training labels.
        
        Returns:
            ll : float
                Computed logistic loss.
        '''
        
        reg = self.alpha * np.dot(w0[:-1], w0[:-1])
        loss = np.array([np.log2(1 + np.exp(-y[i] * np.dot(w0, X[i]))) 
            for i in range(len(X))])
        ll = np.mean(loss) + reg

        return ll
    
    def fit(self, X, y):
        '''
        Fits a logistic regression model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : LogisticRegression
                Fitted logistic regression model.
        '''

        if self.verbose:
            print('Fitting started...')
            start_main = time()
        
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        
        X = reformat(X, bias=True)
        m, d = X.shape
        
        u = np.unique(y)
        n_classes = len(u)

        # Check if labels are binary
        if n_classes == 2:
            y2 = np.array([1 if z == u[0] else -1 for z in y])
            self._dict = {True: u[0], False: u[1]}
            x0 = np.zeros(d)

            # Minimize logistic loss function
            self._weight = minimize(
                self._logistic_loss, x0, args=(X, y2), tol=self.tol,
                method='SLSQP')['x']
            self.weight_, self.bias_ = self._weight[:-1], self._weight[-1]
        else:
            self._weight = {}
            self.weight_ = []
            self.bias_ = []
            for i, c in enumerate(u):
                if self.verbose:
                    print(f'Fitting to class {i + 1} of {n_classes}...')
                    start = time()
                
                y2 = np.array([1 if z == c else -1 for z in y])
                x0 = np.zeros(d)

                # Minimize logistic loss function for each class
                w = minimize(
                    self._logistic_loss, x0, args=(X, y2), tol=self.tol,
                    method='SLSQP')['x']
                self._weight[c] = w

                self.weight_.append(w[:-1])
                self.bias_.append(w[-1])

                if self.verbose:
                    print(f'Class {i + 1} of {n_classes} fitted. \t\t\t\
Time (s): {(time() - start):.3f}')

            self.weight_ = np.array(self.weight_)
            self.bias_ = np.array(self.bias_)

        if self.verbose:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')

        # Set public attributes
        self.classes_ = u
        
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
        X = reformat(X, bias=True)

        # Make predictions
        if len(self.classes_) == 2:
            y_pred = np.array([self._dict[z >= 0] for z in X @ self._weight])
        else:
            y_pred = np.array(
                [max(self._weight, key=lambda key : 
                    np.dot(self._weight[key], x)) for x in X])

        return y_pred

class _DTCNode():
    '''
    Internal class that represents a node in a decision tree
    (classification).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_classes`: Number of classes in the training data (or as manually
        specified).
    
    Attributes:
        depth : int
            Depth of node in tree.
        max_depth : int
            Maximum depth of tree.
        impurity : {'entropy', 'gini'}, default 'entropy'
            Impurity function for assessing split quality.
        class_weight : dict
            Dictionary of classes (keys) and associated weights
            (values). For each specified class, the associated weight is
            applied to all corresponding training samples during
            fitting.
        classes : numpy.ndarray of `(n_classes,)`
            Array of all classes used by the tree. Only used to compute
            probability estimates.
        left : _DTCNode
            Left child of node, or None if the node is pure.
        right : _DTCNode
            Right child of node, or None if the node is pure.
        feature : int
            Index of the feature used in making the split for the node,
            or None if the node is pure.
        threshold : float
            Threshold of the split for the node, or None if the node is
            pure.
        label : (depends)
            Label predicted by the node, or None if the node is not
            pure.
        probabilities : dict
            Dictionary of classes and associated weighted probability
            estimate (between 0 and 1), or None if the node is not pure.
            
    Methods:
        fit(X, y[, weights])
            Fits the node (and any child nodes, recursively) to data.
        predict(x[, return_probabilities])
            Predicts label given a single sample.
    '''
    
    def __init__(
        self, *, depth, max_depth, impurity='entropy',
        class_weight=None, classes=None):
        '''
        Creates a decision tree node.
        
        Parameters:
            depth : int
                Depth of node in tree.
            max_depth : int
                Maximum depth of tree.
            impurity : {'entropy', 'gini'}, default 'entropy'
                Impurity function for assessing split quality.
            class_weight : dict, default None
                Dictionary of certain classes (keys) and associated
                weights (values). For each specified class, the
                associated weight is applied to all corresponding
                training samples during fitting.
            classes : numpy.ndarray of `(n_classes,)`, default
            None
                Array of all classes used by the tree. Only used to
                compute probability estimates.
        '''
        
        self.depth = depth
        self.max_depth = max_depth
        
        self.impurity = impurity 

        self.class_weight = class_weight
        self.classes = classes
                
        self.left = None
        self.right = None
        
        self.feature = None
        self.threshold = None
        self.label = None
        self.probabilities = None        

    @staticmethod
    def _freqs(labels, weights, classes, include_zeros=False):
        '''
        Computes weighted frequencies of classes, given labels and
        corresponding weights.

        `n_samples_` is the number of samples whose labels and weights
        are provided.
        `n_classes_`  is the number of possible classes.
        
        Parameters:
            labels : numpy.ndarray of shape `(n_samples_,)`
                Array of sample labels.
            weights : numpy.ndarray of shape `(n_samples_,)`
                Array of sample weights.
            classes : numpy.ndarray of shape `(n_classes_,)`
                Array of classes.
            include_zeros : bool, default False
                If True, include weighted frequency of a class even
                if it was not found in the given labels.
        
        Returns:
            freqs : numpy.ndarray of shape `(n_classes_,)` or
            `(n_classes_found,)`
                Array of weighted class frequencies, where
                `n_classes_found` is the number of classes found in the
                given labels.
        '''

        freqs = np.array([weights[labels == c].sum() 
            for c in classes]) / weights.sum()
        
        return freqs if include_zeros else freqs[freqs != 0]

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
                Weights for training samples. (This is different from
                the class_weight attribute, which applies weights by
                class instead of sample.)
                If None, then samples are weighted uniformly.
                These weights are combined with class weights to
                influence calculations of node impurity and probability
                estimates (if applicable).
        
        Returns:
            self : _DTCNode
                Fitted decision tree node.
        '''

        at_max = (self.max_depth != None) and (self.depth >= self.max_depth)
        u = np.unique(y)
        m = len(X)

        if self.classes is None:
            self.classes = u

        # Set and scale weights
        w = np.full(m, 1) if weights is None else np.copy(weights)
        if not(self.class_weight is None):
            w = w * np.array([self.class_weight[c] 
                if c in self.class_weight.keys() else 1 
                for c in y])
        w = w / w.sum() * m
        
        # Determine if the node is pure (i.e. has homogeneous label
        # data) or at the max depth
        if len(u) == 1 or at_max:
            freqs = _DTCNode._freqs(y, w, self.classes, include_zeros=True)

            # Set label prediction and weighted class probability
            # estimates
            self.label = self.classes[freqs.argmax()]
            self.probabilities = {
                c: (w[y == c].sum() + 1) / (m + len(self.classes))
                for c in self.classes}
        else:
            # Define Gini and entropy impurity functions, given label 
            # frequencies
            if self.impurity == 'gini':
                impurity = lambda freqs : 1 - np.sum(np.square(freqs))
            else:
                impurity = lambda freqs : -(freqs * np.log2(freqs)).sum()

            # Determine the best split among all possible splits for any
            # single feature
            best_score = float('inf')
            
            for f, c in enumerate(X.T):
                stacked = np.column_stack((c, y, w))
                sorted = stacked[stacked[:, 0].argsort()]
                y2, w2 = sorted[:, 1], sorted[:, 2]
                for i in range(1, m):
                    # Calculate weighted frequencies and sums for both
                    # sides
                    freqs_left = _DTCNode._freqs(y2[:i], w2[:i], self.classes)
                    freqs_right = _DTCNode._freqs(y2[i:], w2[i:], self.classes)
                    l, r = w2[:i].sum(), w2[i:].sum()

                    # Calculate score of split
                    score = (l * impurity(freqs_left) 
                        + r * impurity(freqs_right))
                    if score < best_score:
                        best_score = score
                        self.feature = f
                        self.threshold = np.mean(
                            [sorted[i - 1, 0], sorted[i, 0]])

            # Handle case where two samples have the same predictor
            # value
            if len(X[X[:, self.feature] > self.threshold]) == 0:
                freqs = _DTCNode._freqs(y, w, self.classes, include_zeros=True)

                # Set label prediction and weighted class probability
                # estimates
                self.label = self.classes[freqs.argmax()]
                self.feature = None
                self.threshold = None
                self.probabilities = {
                    c: (w[y == c].sum() + 1) / (m + len(self.classes))
                    for c in self.classes}
            else:
                # Create child nodes and recursively fit them based on
                # the best split
                self.left = _DTCNode(depth=self.depth + 1,
                    max_depth=self.max_depth, impurity=self.impurity,
                    classes=self.classes)
                self.right = _DTCNode(depth=self.depth + 1,
                    max_depth=self.max_depth, impurity=self.impurity,
                    classes=self.classes)
                indices_l = X[:, self.feature] <= self.threshold
                indices_r = X[:, self.feature] > self.threshold
                self.left.fit(X[indices_l], y[indices_l], w[indices_l])
                self.right.fit(X[indices_r], y[indices_r], w[indices_r])
                
    def predict(self, x, return_probabilities=False):
        '''
        Predicts label given a single sample.
        
        Parameters:
            x : numpy.ndarray of shape `(n_features,)`
                Predictors (for a single sample) to compute a label for.
            return_probabilities : bool, default False
                If True, also return the probability estimates for the
                prediction.
        
        Returns:
            y : (depends)
                Predicted label. If `return_probabilities` is True, then
                an array containing the label and the probability
                estimates for all classes (as a dictionary) is returned.
        '''
        
        # Check if node is pure; otherwise, recursively call `predict`
        # on the appropriate child node
        if not (self.label is None):
            return (np.array([self.label, self.probabilities])
                if return_probabilities else self.label)
        elif x[self.feature] <= self.threshold:
            return self.left.predict(x, return_probabilities)
        else:
            return self.right.predict(x, return_probabilities)

class DecisionTreeClassifier(base.BaseModel):
    '''
    Class for performing classification via decision tree.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
        root_ : _DTCNode
            Root node of underlying decision tree.
            
    Methods:
        fit(X, y[, weights])
            Fits a decision tree classifier to data.
        predict(X[, return_probabilities])
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, *, max_depth=None, impurity='entropy', class_weight=None):
        '''
        Creates a decision tree classifier.
        
        Parameters:
            max_depth : int, default None
                Maximum depth of tree.
            impurity : {'entropy', 'gini'}, default 'entropy'
                Impurity function for assessing split quality.
            class_weight : dict, default None
                Dictionary of certain classes (keys) and associated
                weights (values). For each specified class, the
                associated weight is applied to all corresponding
                training samples during fitting.
        '''

        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None
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
                Weights for training samples. (This is different from
                the class_weight attribute, which applies weights by
                class instead of sample.)
                If None, then samples are weighted uniformly.
                These weights are combined with class weights to
                influence calculations of node impurity and probability
                estimates (if applicable).
                    
        Returns:
            self : DecisionTreeClassifier
                Fitted decision tree classifier.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        # Set public attributes
        self.root_ = _DTCNode(depth=0, max_depth=self.max_depth,
            impurity=self.impurity, class_weight=self.class_weight)
        self.root_.fit(X, y, weights)
        self.classes_ = self.root_.classes

        return self
    
    def predict(self, X, return_probabilities=False):
        '''
        Predicts labels given input data.

        `n_test_samples` refers to the number of samples in the input
        data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_test_samples, n_features)`
                Predictors to predict labels for.
            return_probabilities : bool, default False
                If True, also return the probability estimates for the
                predictions.
        
        Returns:
            y_pred : numpy.ndarray of shape `(n_test_samples,)`
                Predicted labels.
            probabilities : numpy.ndarray of shape `(n_test_samples,)`,
            optional
                Probability estimates for predictions. That is, an array
                of dictionaries, where each dictionary contains classes
                (keys) and probability estimates (values) for a
                particular sample.
        '''
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        # Make predictions
        y_pred = np.array(
            [self.root_.predict(x, return_probabilities) for x in X])

        if return_probabilities:
            y_pred = (y_pred[:, 0], y_pred[:, 1])

        return y_pred

class KNNClassifier(base.BaseModel):
    '''
    Class for performing classification via k-nearest neighbors (k-NN).
    
    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
            
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
        Creates a k-NN classifier.
        
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

        # Initialize public attributes
        self.classes_ = None

        # Initialize non-public attributes
        self._X = None
        self._y = None
    
    def fit(self, X, y):
        '''
        Fits a k-NN classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : KNNClassifier
                Fitted k-NN classifier.
        '''
        
        # Ensure input array is a 2-D array of floats
        self._X = reformat(X)
        self._y = np.copy(y)

        # Set public attributes
        self.classes_ = np.unique(y)
        
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

        # Compute distances
        dists = cdist(X, self._X)
        indices = np.argpartition(
            dists, self.n_neighbors, axis=1)[:, :self.n_neighbors]
        labels = self._y[indices]
        
        # Make prediction based on weight type
        if self.weights == 'distance':
            weighted = np.reciprocal(
                dists[np.arange(len(X))[:, None], indices])
            classes = np.unique(labels)
            scores = np.nan_to_num([(weighted * (labels == c)).sum(axis=1)
                for c in classes])
            y_pred = classes[scores.argmax(axis=0)]
        else:
            y_pred = mode(labels, axis=1).mode
        
        return y_pred

class GradientBoostingClassifier(base.BaseModel):
    '''
    Class for performing classification via gradient boosting (with
    classification trees as estimators).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Adapted from:
    https://sefiks.com/2018/10/29/a-step-by-step-gradient-boosting-example-for-classification/
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
        estimators_ : dict
            Dictionary of all classes (keys) and estimator lists
            (values).
            
    Methods:
        fit(X, y)
            Fits a gradient boosting classifier to data.
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
        impurity='entropy', verbose=None):
        '''
        Creates a gradient boosting classifier.
        
        Parameters:
            n_estimators : int, default 100
                Number of estimators used by the model.
            learning_rate : float, default 0.1
                Rate at which each additional estimator contributes to
                the model.
            max_depth : int, default 3
                Maximum depth of individual estimators.
            impurity : {'entropy', 'gini'}, default 'entropy'
                Impurity function for assessing split quality.
            verbose : int, default None
                If not None, output details about progress and time
                elapsed during fitting.
                Additionally, if >0, then output when every `verbose`th
                estimator is being fitted (for each class).
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None
        self.estimators_ = None
    
    def fit(self, X, y):
        '''
        Fits a gradient boosting classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : GradientBoostingClassifier
                Fitted gradient boosting classifier.
        '''

        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)

        self.estimators_ = {}
        u = np.unique(y)
        
        # Fit gradient boosting classifiers for each class (one-vs-rest)
        for i, c in enumerate(u):
            if self.verbose is not None:
                print(f'Fitting to class {i + 1} of {len(u)}...')
                start = time()

            arr = []
            labels = (y == c).astype(float)

            for t in range(self.n_estimators):                
                h = DecisionTreeClassifier(
                    max_depth=self.max_depth, impurity=self.impurity).fit(
                        X, labels)
                arr.append(h)

                # Apply softmax function to predictions
                pred_exp = np.exp(h.predict(X))
                labels -= self.learning_rate * pred_exp / pred_exp.sum()
                
                if (self.verbose is not None and self.verbose > 0
                    and (t + 1) % self.verbose == 0):
                    print(f'{t + 1} of {self.n_estimators} estimators fitted.')

            self.estimators_[c] = arr
            if self.verbose is not None:
                print(f'Class {i + 1} of {len(u)} fitted. \t\t\t\
Time (s): {(time() - start):.3f}')

        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')
        
        # Set public attributes
        self.classes_ = u

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
        scores = {key: np.array(
            [h.predict(X) for h in self.estimators_[key]]).sum(axis=0) 
                  for key in self.estimators_.keys()}
        y_pred = np.array([max(scores, key=lambda key : scores[key][i]) 
            for i in range(len(X))])
        
        return y_pred

class RandomForestClassifier(base.BaseModel):
    '''
    Class for performing classification via random forest.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
        estimators_ : dict
            Dictionary of all DecisionTreeClassifier estimators (keys)
            and arrays of features used (values).
            
    Methods:
        fit(X, y)
            Fits a random forest classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_estimators=100, *, max_depth=None, impurity='entropy',
        random_state=None, max_samples=None, max_features='sqrt',
        bootstrap=True, verbose=None):
        '''
        Creates a random forest classifier.
        
        Parameters:
            n_estimators : int, default 100
                Number of estimators used by the model.
            max_depth : int, default None
                Maximum depth of individual estimators.
            impurity : {'entropy', 'gini'}, default 'entropy'
                Impurity function for assessing split quality.
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
        self.classes_ = None
        self.estimators_ = None

        # Initialize non-public attributes
        self._rng = None
        self._sample_func = None
        self._feature_func = None
    
    def fit(self, X, y):
        '''
        Fits a random forest classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : RandomForestClassifier
                Fitted random forest classifier.
        '''
        
        # Handle various cases for `self.random_state`
        if self.random_state is None or isinstance(self.random_state, int):
            self._rng = np.random.default_rng(self.random_state)
        elif (isinstance(self.random_state, np.random.RandomState)
            or isinstance(self.random_state, np.random.Generator)):
            self._rng = self.random_state
        else:
            self._rng = np.random.default_rng(None)
        
        # Handle various cases for `self.max_samples`
        if self.max_samples is None:
            self._sample_func = lambda m : m
        elif isinstance(self.max_samples, typing.Callable):
            self._sample_func = self.max_samples
        elif isinstance(self.max_samples, int):
            self._sample_func = lambda _ : self.max_samples
        else:
            self._sample_func = lambda m : m
        
        # Handle various cases for `self.max_features`
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
        
        # Draw examples and select features from input data, for each
        # estimator
        for t in range(self.n_estimators):
            samples = self._rng.choice(
                range(m), size=n_samples) if self.bootstrap else range(m)
            features = self._rng.choice(
                range(d), size=n_features, replace=False)
            features.sort()
            X2 = X[samples][:, features]
            y2 = y[samples]
            
            h = DecisionTreeClassifier(
                max_depth=self.max_depth, impurity=self.impurity).fit(X2, y2)
            self.estimators_[h] = features

            if (self.verbose is not None and self.verbose > 0
                and (t + 1) % self.verbose == 0):
                print(f'{t + 1} of {self.n_estimators} estimators fitted.')
        
        if self.verbose is not None:
            print(f'Fitting complete. \t\t\t\
Total time (s): {(time() - start_main):.3f}')

        # Set public attributes
        self.classes_ = np.unique(y)

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
        y_pred = mode(np.array([h.predict(X[:, self.estimators_[h]]) 
                                for h in self.estimators_.keys()])).mode[0]
        
        return y_pred

class _SVCBinary():
    '''
    Internal class for performing binary classification via support
    vector machine (SVM).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_sv`: Number of support vectors used by the model.
    
    Attributes:
        classes : list
            List containing the two classes to be fitted. All labels of
            `classes[0]` will be replaced with +1 during fitting (and
            all other labels with -1).
            If None, then the two classes are taken to be the two most
            common labels in the input data (in decreasing order of
            label frequency).
        C : float
            Regularization constant. Must be positive; lower value means
            more regularization.
        kernel : callable
            Kernel function used by the model. Takes in two arrays of
            feature vectors and computes an array of floats.
        sv_indices : numpy.ndarray of shape `(n_sv,)`
            Indices of support vectors (in the training data).
        support_vectors : numpy.ndarray of shape `(n_sv, n_features)`
            Support vectors used by the model.
        weight : callable
            Function for computing the weight terms of predictions (via
            the kernel trick). Takes in an array of feature vectors and
            outputs an array of floats.
        bias : float
            Bias term associated with the model.

    Methods:
        fit(X, y)
            Fits a support vector binary classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''

    def __init__(self, classes=None, *, C, kernel, error_coef):
        '''
        Creates a support vector binary classifier.
        
        Parameters:
            classes : list, default None
                List containing the two classes to be fitted. All labels
                of `classes[0]` will be replaced with +1 during fitting
                (and all other labels with -1).
                If None, then the two classes are taken to be the two
                most common labels in the input data (in decreasing
                order of label frequency).
            C : float
                Regularization constant. Must be positive; lower value
                means more regularization.
            kernel : callable
                Kernel function used by the model. Takes in two feature
                vectors and computes a float.
            error_coef : float
                Coefficient for margin for error (`C * error_coef`) in
                determining support vectors when assessing coefficient
                values. A smaller value represents a stricter threshold
                and may result in less support vectors.
        '''

        self.classes = classes
        self.C = C
        self.kernel = kernel
        self.error_coef = error_coef
        
        self.sv_indices = None
        self.support_vectors = None
        self.weight = None
        self.bias = None
        self._dict = None
            
    def fit(self, X, y):
        '''
        Fits a support vector binary classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : _SVCBinary
                Fitted support vector binary classifier.
        '''
                
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        m = len(X)
        
        # Transform labels into {+1, -1} according to `self.classes`
        classes = np.unique(y) if self.classes is None else self.classes
        y2 = np.array([1. if i == classes[0] else -1. for i in y])
        
        self._dict = {True: classes[0], False: classes[1]}
        
        # Optimize alphas (coefficients) via quadratic programming
        P = matrix(np.outer(y2, y2) * self.kernel(X, X))
        q = matrix([-1.] * m)
        G = matrix(np.vstack((np.identity(m), -np.identity(m))))
        h = matrix(np.concatenate((np.full(m, self.C), np.zeros(m))))
        A = matrix(y2.reshape(1, m))
        b = matrix(0.)
        solvers.options['show_progress'] = False
        
        alpha = np.array(solvers.qp(P, q, G, h, A, b)['x']).reshape(m)
        
        # Determine the indices of support vectors (including those on
        # the margin)
        sv = np.argwhere(alpha > self.C * self.error_coef).flatten()
        sv1 = np.argwhere(alpha[sv] < self.C * (1 - self.error_coef)).flatten()
        
        # Filter `alpha`, `X`, and `y2` by the indices of support
        # vectors, and compute the weight and bias
        alpha_new = alpha[sv]
        X_new = X[sv]
        y_new = y2[sv]
        
        self.weight = lambda Z : np.sum(
            alpha_new[:, None] * y_new[:, None] * self.kernel(X_new, Z), axis=0)

        self.bias = (0 if len(sv1) == 0 
            else (y_new[sv1] - self.weight(X_new[sv1])).mean())
        
        self.sv_indices = sv.copy()
        self.support_vectors = X_new.copy()

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
        y_pred = np.array([self._dict[k] 
            for k in (self.weight(X) + self.bias >= 0)])
        
        return y_pred

class SupportVectorClassifier(base.BaseModel):
    '''
    Class for performing classification via support vector machine
    (SVM).
    Note: The default parameter values may result in a poor model. If
    so, it is advised to change these values from their defaults,
    especially `C` or `gamma`.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_classes`: Number of classes in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model.
            
    Methods:
        fit(X, y)
            Fits a support vector classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''

    def __init__(
        self, *, kind='ovr', C=1.0, kernel='rbf', degree=3, gamma=1.0,
        coef0=1.0, error_coef=1e-6, verbose=False):
        '''
        Creates a support vector classifier.
        
        Parameters:
            kind : {'ovr', 'ovo'}, default 'ovr'
                Specifies how to create the model's underlying binary
                classifier(s).
                If 'ovr', then the model uses one-vs-rest
                classification. That is, for each class, the model
                transforms the labels to binary data based on that class
                and fits a binary classifier to the new data, resulting
                in a total of `n_classes` underlying binary classifiers.
                If 'ovo', then the model uses one-vs-one classification.
                That is, for each pair of classes, the model fits a
                binary classifier to the subset of input data
                corresponding to those two classes, resulting in a total
                of `n_classes * (n_classes - 1) / 2` underlying binary
                classifiers. Note that this may still be faster than
                'ovr' due to smaller training sets.
                If the labels are binary (i.e. `n_classes == 2`), then 
                this parameter is ignored, and the model fits a single
                binary classifier.
            C : float
                Regularization constant. Must be positive; lower value
                means more regularization. Used by all underlying binary
                classifiers.
            kernel : {
                'rbf', 'linear', 'poly'} or callable, default 'rbf'
                Determines kernel function used by all underlying binary
                classifiers. If a function is provided, then it must
                take in two arrays of feature vectors and compute an
                array of floats.
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
            error_coef : float, default 1e-6
                Coefficient for margin for error (`C * error_coef`) in
                determining support vectors when assessing coefficient
                values. A smaller value represents a stricter threshold
                and may result in less support vectors.
            verbose : bool, default False
                If True, output details about progress and time elapsed
                during fitting.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None

        # Initialize non-public attributes
        self._kernel = None
        self._svcb = None        
            
    def fit(self, X, y):
        '''
        Fits a support vector classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : SupportVectorClassifier
                Fitted support vector classifier.
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

        if self.verbose:
            print('Fitting started...')
            start_main = time()

        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        u = np.unique(y)
        n_classes = len(u)
        
        # Fit single binary classifier if 'binary'
        if n_classes == 2:
            self._svcb = _SVCBinary(C=self.C, kernel=self._kernel,
                error_coef=self.error_coef).fit(X, y)
        
        # Fit binary classifiers for each pair of classes if 'ovo'
        elif self.kind == 'ovo':
            self._svcb = []
            n_svcb = int(n_classes * (n_classes - 1) / 2)
            k = 0
            for i, c1 in enumerate(u):
                for c2 in u[i + 1:]:
                    k += 1
                    if self.verbose:
                        print(f'Fitting binary classifier {k} of {n_svcb}...')
                        start = time()
                    
                    indices = np.where(np.logical_or(y == c1, y == c2))
                    X2 = X[indices]
                    y2 = y[indices]
                    self._svcb.append(
                        _SVCBinary(C=self.C, kernel=self._kernel,
                        error_coef=self.error_coef).fit(X2, y2))
                    
                    if self.verbose:
                        print(f'Binary classifier {k} of {n_svcb} fitted. \
\t\tTime (s): {(time() - start):.3f}')
                    
        # Fit binary classifiers for each class if 'ovr' (default)
        else:
            self._svcb = {}
            for i, c in enumerate(u):
                if self.verbose:
                    print(f'Fitting binary classifier {i + 1} of \
{n_classes}...')
                    start = time()

                self._svcb[c] = (_SVCBinary(
                    [True, False], C=self.C,kernel=self._kernel,
                    error_coef=self.error_coef).fit(X, y == c))
                
                if self.verbose:
                    print(f'Binary classifier {i + 1} of {n_classes} fitted. \
\t\tTime (s): {(time() - start):.3f}')
        
        if self.verbose:
            print(f'Fitting complete. \t\t\t\t\
Total time (s): {(time() - start_main):.3f}')

        # Set public attributes
        self.classes_ = u
        
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
        
        # Use the single binary classifier to predict if 'binary'
        if len(self.classes_) == 2:
            y_pred = self._svcb.predict(X)
            
        # Predict the most common class for each sample if 'ovo'
        elif self.kind == 'ovo':
            y_pred = mode(
                np.array([svcb.predict(X) for svcb in self._svcb]))[0][0]
        
        # Predict the class that maximizes confidence (i.e. distance
        # from decision boundary) for each sample if 'ovr' (default)
        else:
            scores = np.array([self._svcb[c].weight(X) + self._svcb[c].bias
                for c in self.classes_])
            y_pred = self.classes_[scores.argmax(axis=0)]
        
        return y_pred

class DiscriminantAnalysis(base.BaseModel):
    '''
    Class for performing classification via linear/quadratic
    discriminant analysis.

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of shape `(n_classes,)`
            Array of all classes assumed by the model, where `n_classes`
            is the number of classes.
        probabilities_ : numpy.ndarray of shape `(n_classes,)`
            Array of probabilities (priors) of each class.
        means_ : numpy.ndarray of shape `(n_classes, n_features)`
            Array of means of each class.
        covariances_ : numpy.ndarray of shape `(n_classes, n_features,
        n_features)`
            Covariance matrices used by the model, depending on the
            `kind` parameter (specified in the constructor).
            If `kind == 'linear'`, then all covariance matrices are the
            same (by assumption).
            
    Methods:
        fit(X, y)
            Fits a discriminant analysis model to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''

    def __init__(self, kind='linear'):
        '''
        Creates a discriminant analysis model.
        
        Parameters:
            kind : {'linear', 'quadratic'}, default 'linear'
                Type of discriminant analysis performed by the model.
                If 'linear', the model assumes equal covariance matrices 
                for each class.
                If 'quadratic', the model assumes distinct covariance
                matrices for each class.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None
        self.probabilities_ = None
        self.means_ = None
        self.covariances_ = None

        # Initialize non-public attributes
        self._predict_one = None
            
    def fit(self, X, y):
        '''
        Fits a discriminant analysis model to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : DiscriminantAnalysis
                Fitted discriminant analysis model.
        '''
                
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        m, d = X.shape
        u = np.unique(y)

        # Handle case for binary classification
        if len(u) == 2:

            # Compute proportion and mean of all samples in each class
            plus, minus = X[y == u[0]], X[y != u[0]]
            self.probabilities_ = np.array([len(plus) / m, len(minus) / m])
            self.means_ = np.array([plus.mean(axis=0), minus.mean(axis=0)])
            
            # Compute covariance matrices for each class (based on
            # `self.kind`)
            if self.kind == 'linear':
                plus = plus - self.means_[0]
                minus = minus - self.means_[1]
                sigma = (X[:, :, None] * X[:, None, :]).mean(axis=0)
                self.covariances_ = np.array([sigma, sigma])
            else:
                self.covariances_ = np.array([
                    np.cov(plus.T, bias=False), np.cov(minus.T, bias=False)])
            
            # Compute intermediary terms
            inv_plus = np.linalg.inv(self.covariances_[0])
            inv_minus = np.linalg.inv(self.covariances_[1])
            temp_plus = inv_plus @ self.means_[0]
            temp_minus = inv_minus @ self.means_[1]
            term = (1 if self.kind == 'linear' else 
                np.log(np.linalg.det(self.covariances_[1])
                / np.linalg.det(self.covariances_[0])))
            term -= 2 * np.log(len(minus) / len(plus))
            
            # Compute terms for prediction expression
            A = inv_minus - inv_plus
            b = -2 * (temp_minus - temp_plus)
            c = (self.means_[1] @ temp_minus - self.means_[0] @ temp_plus
                + term)
            
            # Save terms used in prediction function
            self._terms = (A, b, c)

        # Handle case for multiclass classification
        else:

            # Compute proportion and mean of all samples in each class
            subsets = [X[y == c] for c in u]
            self.probabilities_ = np.array([len(arr) / m for arr in subsets])
            self.means_ = np.array([arr.mean(axis=0) for arr in subsets])
            
            # Compute covariance matrices for each class (based on
            # self.kind)
            if self.kind == 'linear':
                for i in range(len(subsets)):
                    X[y == u[i]] = subsets[i] - self.means_[i]
                sigma = (X[:, :, None] * X[:, None, :]).mean(axis=0)
                self.covariances_ = np.array([sigma] * len(u))
            else:
                self.covariances_ = np.array([
                    np.cov(arr, rowvar=False, bias=False) for arr in subsets])
        
        # Set public attributes
        self.classes_ = u

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
        
        # Make predictions (based on whether the classification is
        # binary or multiclass)
        if len(self.classes_) == 2:
            A, b, c = self._terms
            scores = X @ b + c + (
                0 if self.kind == 'linear' else np.sum(X @ A * X, axis=1))
            y_pred = np.where(scores >= 0, self.classes_[0], self.classes_[1])
        else:
            term1 = 0.5 * np.log(np.linalg.det(self.covariances_))[:, None]
            X_centered = X - self.means_[:, None, :]
            term2 = (0.5 * np.sum(X_centered @ np.linalg.inv(self.covariances_)
                * X_centered, axis=2))
            scores = np.log(self.probabilities_)[:, None] - term1 - term2
            y_pred = self.classes_[scores.argmax(axis=0)]
        
        return y_pred

class GaussianNBClassifier(base.BaseModel):
    '''
    Class for performing classification via Gaussian naive Bayes.
    
    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    
    Attributes:
        classes_ : numpy.ndarray of `(n_classes,)`
            List of all classes assumed by the model, where `n_classes`
            is the number of classes.
        probabilities_ : numpy.ndarray of `(n_classes,)`
            Array of probabilities (priors) of each class.
        means_ : numpy.ndarray of shape `(n_classes, n_features)`
            Array of means of each class.
        variances_ : numpy.ndarray of shape `(n_classes, n_features)`
            Array of feature variances of each class, depending on the
            `equal_variances` parameter (specified in the constructor).
            If `equal_variances` is True, then feature variances are the
            same across all classes (by assumption).
            
    Methods:
        fit(X, y)
            Fits a Gaussian naive Bayes classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''

    def __init__(self, *, equal_variances=False):
        '''
        Creates a Gaussian naive Bayes classifier.

        Parameters:
            equal_variances : bool, default False
                If True, assume that each feature has the same variance
                for all classes.
        '''
        
        # Set parameters as attributes
        params = locals()
        del params['self']
        del params['__class__']
        super().__init__(**params)

        # Initialize public attributes
        self.classes_ = None
        self.probabilities_ = None
        self.means_ = None
        self.variances_ = None

        # Initialize non-public attributes
        self._predict_one = None
            
    def fit(self, X, y):
        '''
        Fits a Gaussian naive Bayes classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : GaussianNBClassifier
                Fitted Gaussian naive Bayes classifier.
        '''
                
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        m, d = X.shape
        u = np.unique(y)

        # Handle case for binary classification
        if len(u) == 2:

            # Compute proportion and mean for each feature in each class
            plus, minus = X[y == u[0]], X[y == u[1]]
            self.probabilities_ = np.array([len(plus) / m, len(minus) / m])
            self.means_ = np.array([plus.mean(axis=0), minus.mean(axis=0)])

            # Compute variance for each feature in each class (based on
            # `self.equal_variances`)
            if self.equal_variances:
                plus = plus - self.means_[0]
                minus = minus - self.means_[1]
                var = X.var(axis=0)
                self.variances_ = np.array([var, var])
            else:
                self.variances_ = np.array([plus.var(axis=0), minus.var(axis=0)])
            
            # Compute components for prediction expression
            A = np.diag(0.5 / self.variances_[1] - 0.5 / self.variances_[0])
            b = (self.means_[0] / self.variances_[0]
                - self.means_[1] / self.variances_[1])
            arr = (0.5 * np.square(self.means_[1]) / self.variances_[1]
                - 0.5 * np.square(self.means_[0]) / self.variances_[0]
                + np.log(np.sqrt(self.variances_[1]) 
                / np.sqrt(self.variances_[0])))
            c = arr.sum() - np.log(len(minus) / len(plus))

        # Handle case for multiclass classification
        else:

            # Compute proportion and mean for each feature in each class
            subsets = [X[y == c] for c in u]
            self.probabilities_ = np.array([len(arr) / m for arr in subsets])
            self.means_ = np.array([arr.mean(axis=0) for arr in subsets]) 

            # Compute variance for each feature in each class (based on
            # `self.equal_variances`)
            if self.equal_variances:
                for i in range(len(subsets)):
                    X[y == u[i]] = subsets[i] - self.means_[i]
                var = X.var(axis=0)
                self.variances_ = np.array([var] * len(u))
            else:
                self.variances_ = np.array([
                    arr.var(axis=0) for arr in subsets])
            
            A = np.identity(d) * -0.5 / self.variances_[:, None, :]
            b = self.means_ / self.variances_
            arr = (np.log(np.sqrt(2 * np.pi * self.variances_))
                + 0.5 * np.square(self.means_) / self.variances_)
            c = np.log(self.probabilities_) - arr.sum(axis=1)
        
        # Save terms used in prediction function
        self._terms = (A, b, c)

        # Set public attributes
        self.classes_ = u
        
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
        
        A, b, c = self._terms
        
        # Make predictions (based on whether the classification is
        # binary or multiclass)
        if len(self.classes_) == 2:
            scores = X @ b + c + np.sum(X @ A * X, axis=1)
            y_pred = np.where(scores >= 0, self.classes_[0], self.classes_[1])
        else:
            scores = b @ X.T + c[:, None] + np.sum(X @ A * X, axis=2)
            y_pred = self.classes_[scores.argmax(axis=0)]
        
        return y_pred

class AdaBoostClassifier(base.BaseModel):
    '''
    Class for performing classification via AdaBoost (with
    classification trees as estimators).

    The following variable names are used in this class's documentation:
    `n_samples`: Number of samples in the training data.
    `n_features`: Number of features in the training data.
    `n_classes`: Number of classes in the training data.

    Source: https://hastie.su.domains/Papers/samme.pdf
    
    Attributes:
        classes_ :  numpy.ndarray of `(n_classes,)`
            Array of classes used by the model.
        estimators_ : list
            List of all estimators used by the model.
        estimator_weights_ : numpy.ndarray of shape `(n_estimators,)`
            Array of weights of estimators used by the model, where
            `n_estimators` is the number of estimators used by the
            model (specified in the constructor).
            
    Methods:
        fit(X, y)
            Fits an AdaBoost classifier to data.
        predict(X)
            Predicts labels given input data.
        get_params([deep])
            Gets `__init__` parameter names and corresponding arguments.
        set_params(**params)
            Sets the specified `__init__` parameters to the specified
            values.
    '''
    
    def __init__(
        self, n_estimators=20, *, max_depth=1, impurity='entropy',
        algorithm='SAMME.R', verbose=None):
        '''
        Creates an AdaBoost classifier.
        
        Parameters:
            n_estimators : int, default 20
                Number of estimators used by the model.
            max_depth : int, default 1
                Maximum depth of individual estimators (classification
                trees).
            impurity : {'entropy', 'gini'}, default 'entropy'
                Impurity function for assessing split quality.
            algorithm : {'SAMME.R', 'SAMME'}, default 'SAMME.R'
                Algorithm used by the model during fitting. The SAMME
                algorithm uses classifications to fit the model,
                whereas the SAMME.R algorithm uses weighted class
                probability estimates. The latter typically converges
                more quickly.
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
        self.classes_ = None
        self.estimators_ = None
        self.estimator_weights_ = None
    
    def _class_scores(self, wcpe):
        '''
        Computes class scores for an estimator's predictions.

        `n_samples_` is the number of samples in the input data.
        
        Parameters:
            wcpe : numpy.ndarray of shape `(n_samples_,)`
                Array of dictionaries, where each dictionary contains
                weighted class probability estimates for a sample.
                    
        Returns:
            scores : dict
                Dictionary of classes (keys) and arrays of shape
                `(n_samples_,)` (values), where each array contains the
                samples' scores for the corresponding class.
        '''
        
        classes = list(wcpe[0].keys())
        k = len(classes)
        scores = {c: [] for c in classes}
        
        # Compute scores for each sample
        for z in wcpe:
            log_p = {c: np.log(z[c]) for c in z.keys()}
            mean = np.array(list(log_p.values())).mean()
            for c in classes:
                scores[c].append((k - 1) * (log_p[c] - mean))
        
        scores = {c: np.array(scores[c]) for c in scores.keys()}

        return scores

    def fit(self, X, y):
        '''
        Fits an AdaBoost classifier to data.
        
        Parameters:
            X : numpy.ndarray of shape `(n_samples, n_features)`
                Training predictors.
            y : numpy.ndarray of shape `(n_samples,)`
                Training labels.
                    
        Returns:
            self : AdaBoostClassifier
                Fitted AdaBoost classifier.
        '''
        
        if self.verbose is not None:
            print('Fitting started...')
            start_main = time()
        
        # Ensure input array is a 2-D array of floats
        X = reformat(X)
        
        # Setup
        self.estimators_ = []
        self.estimator_weights_ = []
        self.classes_ = np.unique(y)

        k = len(self.classes_)
        m = len(X)
        w = np.full(m, 1 / m, dtype=float)
        Y = np.array([[1 if l == c else 1 / (1 - k)
            for c in self.classes_] 
            for l in y])

        # Create and fit each estimator
        for t in range(self.n_estimators):
            clf = DecisionTreeClassifier(
                max_depth=self.max_depth, impurity=self.impurity).fit(X, y, w)
            y_pred, wcpe = clf.predict(X, return_probabilities=True)

            if self.algorithm == 'SAMME':
                # Determine estimator's classification error and weight
                arr = (y != y_pred)
                err = w[arr].sum()
                alpha = (np.log((1 - err) / err) + np.log(k - 1)
                    if err != 0 else float('inf'))
                self.estimator_weights_.append(alpha)

                # Handle case where estimator has zero error
                if alpha == float('inf'):
                    self.estimators_.append(clf)
                    break
                else:
                    w *= np.exp(alpha * arr.astype(float))
            else:
                # Compute multiplier for SAMME.R algorithm
                multiplier = np.exp((1 / k - 1) * np.array(
                    [np.dot(Y[i], 
                    np.log(np.array([p[key] for key in sorted(p.keys())]))) 
                    for i, p in enumerate(wcpe)]))
                w *= multiplier
            
            # Normalize weights and add estimator to list
            w /= w.sum()
            self.estimators_.append(clf)

            if (self.verbose is not None and self.verbose > 0
                and (t + 1) % self.verbose == 0):
                print(f'{t + 1} of {self.n_estimators} estimators fitted.')

        # Prioritize any estimator with zero error    
        self.estimator_weights_ = np.array(self.estimator_weights_)
        if float('inf') in self.estimator_weights_:
            self.estimator_weights_ = (
                self.estimator_weights_ == float('inf')).astype(float)

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

        # Compute scores (based on `self.algorithm`)
        if self.algorithm == 'SAMME':
            preds = np.array([dtc.predict(X) for dtc in self.estimators_]).T  
            scores = {
                c: np.array([np.dot(self.estimator_weights_,
                (pred == c).astype(float)) for pred in preds])
                for c in self.classes_}
        else:
            arr = np.array([self._class_scores(
                    dtc.predict(X, return_probabilities=True)[1])
                for dtc in self.estimators_])
            scores = {c: np.array([z[c] for z in arr]).sum(axis=0)
                for c in self.classes_}

        # Make predictions by maximizing scores
        y_pred = np.array([max(scores, key=lambda key : scores[key][i]) 
            for i in range(len(X))])
        
        return y_pred