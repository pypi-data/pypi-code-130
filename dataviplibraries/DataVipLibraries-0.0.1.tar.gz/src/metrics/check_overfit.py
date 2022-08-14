def find_overfit_cat(model_obj, xtrain, xtest, ytrain, ytest):
    """
                     Data Science Library
     method name: find_overfit_cat
    desc: This is to find an overfit of model. Means sometimes we have faced
    the overfit and underfit and best fit model issue that shows this mobel
    author name: TinCharlie
    :param model_obj: Algorithm which we are using for the prediction
    :param xtrain: around 80 % data for training contains x no. of columns
    :param xtest: around 20 % data for testing contains x no. of columns
    :param ytrain: around 80 % data for training contains y column
    :param ytest: around 20 % data for testing contains y column
    :return: It will show the model is overfiting or not
    """
    model = model_obj.fit(xtrain, ytrain)
    pred_ts = model.predict(xtest)
    pred_tr = model.predict(xtrain)
    from sklearn.metrics import accuracy_score
    print("training Accuracy: ", accuracy_score(ytrain, pred_tr))
    print("testing Accuracy: ", accuracy_score(ytest, pred_ts))

def find_overfit_con(model_obj, xtrain, xtest, ytrain, ytest):
    """
                     Data Science Library
     method name: find_overfit_con
    desc: This is to find an overfit of model. Means sometimes we have faced
    the overfit and underfit and best fit model issue that shows this mobel
    author name: TinCharlie
    :param model_obj: Algorithm which we are using for the prediction
    :param xtrain: around 80 % data for training contains x no. of columns
    :param xtest: around 20 % data for testing contains x no. of columns
    :param ytrain: around 80 % data for training contains y column
    :param ytest: around 20 % data for testing contains y column
    :return: It will show the model is overfiting or not
    """
    model = model_obj.fit(xtrain, ytrain)
    pred_ts = model.predict(xtest)
    pred_tr = model.predict(xtrain)
    from sklearn.metrics import mean_absolute_error
    print("training error: ", mean_absolute_error(ytrain, pred_tr))
    print("testing error: ", mean_absolute_error(ytest, pred_ts))