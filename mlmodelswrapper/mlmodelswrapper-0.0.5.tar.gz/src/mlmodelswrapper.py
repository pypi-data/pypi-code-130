import pandas as pd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


def regressors(X, y):
    """regression models

    Args:
        X (_type_): features
        y (_type_): label

    Returns:
        _type_: result
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                   random_state = 0)
    lr = LinearRegression().fit(X_train, y_train)
    lr_score = lr.score(X_test, y_test)

    lasso = Lasso().fit(X_train, y_train)
    lasso_score = lasso.score(X_test, y_test)

    ridge = Ridge().fit(X_train, y_train)
    ridge_score = ridge.score(X_test, y_test)

    elasticNet = ElasticNet().fit(X_train, y_train)
    elasticNet_score = elasticNet.score(X_test, y_test)

    randomForestregressor = RandomForestRegressor().fit(X_train, y_train)
    randomForestregressor_score = randomForestregressor.score(X_test, y_test)

    decisionTreeRegressor = DecisionTreeRegressor().fit(X_train, y_train)
    decisionTreeRegressor_score = decisionTreeRegressor.score(X_test, y_test)

    results = pd.DataFrame({
                          'lr_score': lr_score,
                          'lasso_score': lasso_score,
                          'ridge_score': ridge_score,
                          'elasticNet_score': elasticNet_score,
                          'randomForestregressor_score': randomForestregressor_score,
                          'decisionTreeRegressor_score': decisionTreeRegressor_score                          
                          },index=[0])
    return results


def classifiers(X, y):
    """classification models

    Args:
        X (_type_): features
        y (_type_): label

    Returns:
        _type_: accuracy
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                   random_state = 0)
    
    lr = LogisticRegression().fit(X_train, y_train)
    lr_score = lr.score(X_test, y_test)

    dt = DecisionTreeClassifier().fit(X_train, y_train)
    dt_score = dt.score(X_test, y_test)  

    knn = KNeighborsClassifier().fit(X_train, y_train)
    knn_score = knn.score(X_test, y_test)  

    rf = RandomForestClassifier().fit(X_train, y_train)
    rf_score = rf.score(X_test, y_test)

    results = pd.DataFrame({
                          'lr_score': lr_score,
                          'dt_score': dt_score,
                          'knn_score': knn_score,
                          'rf_score': rf_score                       
                          },index=[0])
    return results
