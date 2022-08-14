def CV_tune(df, Ycol, cols_to_drop, model_obj, tp):
    """
                 Data Science Library
    method name: Cv_tune
    desc: CV Tune is nothing but our grid search cv that library is created bcz of
          to find the best params of the algorithms
    author name: TinCharlie
    :param df: DataFrame
    :param Ycol: Target Varaible
    :param cols_to_drop: Columns which you want to drop
    :param model_obj: Algorithm whichever we are using for the further processing
    :param tp: Tuninig Parameter that you have to create any how
    :return: Return the best value for your model that you can put
    and get the best predction
    """

    import pandas as pd
    df = df.drop(labels=cols_to_drop, axis=1)
    from src.replacer import mean_mode_replacer

    df = mean_mode_replacer.replace_mmr(df)
    Y = df[Ycol]
    X = df.drop(labels=Ycol, axis=1)
    from src.PreprocessData import preprocessing
    X_new = preprocessing.preprocess_data(X)
    from sklearn.model_selection import train_test_split
    xtrain, xtest, ytrain, ytest = train_test_split(X_new, Y, test_size=0.2, random_state=31)
    if ytrain[Ycol[0]].dtypes == "object":
        from sklearn.model_selection import GridSearchCV
        cv = GridSearchCV(model_obj, tp, scoring="accuracy", cv=4)
        cvmodel = cv.fit(xtrain, ytrain)
        print(cvmodel.best_params_)
        return cvmodel.best_params_
    else:
        from sklearn.model_selection import GridSearchCV
        cv = GridSearchCV(model_obj, tp, scoring="neg_mean_absolute_error", cv=4)
        cvmodel = cv.fit(xtrain, ytrain)
        print(cvmodel.best_params_)
        return cvmodel.best_params_
