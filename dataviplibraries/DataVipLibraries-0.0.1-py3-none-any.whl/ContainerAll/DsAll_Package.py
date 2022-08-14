class find_best_features:
    def ANOVA(self, df, cat, con):
        """
                         Data Science Library
         method name: ANOVA
         desc: IIt Shows the relation bw categorical and Continous columns.
               You have to use this method at the time of cat vs con conditjion
               If you need to create the and find the best calumns out all related to
                your target columns. That you should use.
         author name: TinCharlie
        :param df: DataFrame
        :param cat: Categorical Data
        :param con: Continous Data
        :return: This returns the p value which should be lesser
        """
        from pandas import DataFrame
        from statsmodels.api import OLS
        from statsmodels.formula.api import ols
        rel = con + " ~ " + cat
        model = ols(rel, df).fit()
        from statsmodels.stats.anova import anova_lm
        anova_results = anova_lm(model)
        Q = DataFrame(anova_results)
        a = Q['PR(>F)'][cat]
        return round(a, 3)


class visualization:

    def Univariate(self, A, figsize, rows, columns):
        """
                 Data Science Library
         method name: Univariate
         desc: It is used to create the univariate data visuals.
                To create and whole dashboard of charts,Like bar and dist
         author name: TinCharlie
        :param figsize: FigureSize means put size of the chart in terms of sys size eg: (10,10)
        :param rows: rows and columns count for creating those charts
        :param columns: rows and columns count for creating those charts
        :return: Return all the charts and visuals
        """
        import seaborn as sns
        import matplotlib.pyplot as plt
        x = 1
        plt.figure(figsize=figsize)
        for i in A.columns:
            if A[i].dtypes == 'object':
                plt.subplot(rows, columns, x)
                sns.countplot(A[i])
                x = x + 1
            else:
                plt.subplot(rows, columns, x)
                sns.distplot(A[i])
                x = x + 1

    def Bivariate(self, A, Y, figsize, rows, columns):
        """
        Data Science Library
        :method name: Bivariate
        :desc: It is used to create the Bivariate data visuals.
                To create and whole dashboard of charts,Like bar and dist
        :author name: TinCharlie
        :param A: A is basically your data frame
        :param Y: Y is target Variable
        :param figsize: FigureSize means put size of the chart in terms of sys size eg: (10,10)
        :param rows: rows and columns count for creating those charts
        :param columns: rows and columns count for creating those charts
        :return: Return all the charts and visuals Target Variable Vs All
        """
        import seaborn as sns
        import matplotlib.pyplot as plt
        x = 1
        plt.figure(figsize=figsize)
        for i in A.columns:
            if A[i].dtypes == 'object':
                plt.subplot(rows, columns, x)
                sns.boxplot(A[i], A[Y])
                x = x + 1
            else:
                plt.subplot(rows, columns, x)
                sns.scatterplot(A[i], A[Y])
                x = x + 1


class replace:

    def Mean_mode_replacer(self, df):
        """
        Data Science Library
        method name: Mean_mode_replacer
        desc: It replace the missing value by using of the mean and mode.
                We need the data which does contains to the known data
        author name: TinCharlie
        :param df: df stands for DataFrame
        :return: replace data nan or null values
        """
        try:
            import pandas as pd
            Q = pd.DataFrame(df.isna().sum(), columns=["ct"])
            ## ct is for just to give the name of missing columns head
            for i in Q[Q.ct > 0].index:
                if df[i].dtypes == "object":
                    x = df[i].mode()[0]
                    df[i] = df[i].fillna(x)
                else:
                    x = df[i].mean()
                    df[i] = df[i].fillna(x)
        except TypeError:
            print("Data Contains unknown data dtypes")
        return df

class preprocess:
    def __init__(self, df):
        self.df = df
        print("Constructor Build")

    def preprocess_data(self, df):
        """
                         Data Science Library
         method name: preprocess_data
         desc: Here my main aim is to convert the cat into con and merge into the standardized data
         author name: TinCharlie
        :param df: Data Frame
        :return: It will return the processed columns of the Cat and COn Standardized
        """

        import pandas as pd
        cat = []
        con = []
        for i in df.columns:
            if df[i].dtypes == "object":
                cat.append(i)
            else:
                con.append(i)
        X1 = pd.get_dummies(df[cat])
        from sklearn.preprocessing import StandardScaler
        ss = StandardScaler()
        X2 = pd.DataFrame(ss.fit_transform(df[con]), columns=con)
        X3 = X2.join(X1)
        return X3


class overfit_or_not:
    def __init__(self, df):
        self.df = df
        print("Constructor Build")

    def find_overfit_cat(self, model_obj, xtrain, xtest, ytrain, ytest):
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
        if accuracy_score(ytrain, pred_tr) <= accuracy_score(ytest, pred_ts):
            print("U can use model")
            return model
        else:
            print("U cant use model bcz of over fitting")
            return

    def find_overfit_con(self, model_obj, xtrain, xtest, ytrain, ytest):
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
        if mean_absolute_error(ytrain, pred_tr) <= mean_absolute_error(ytest, pred_ts):
            print("U can use model")
            return model
        else:
            print("U cant use model bcz of over fitting")
            return


class model_creation:
    def __init__(self, df):
        self.df = df
        print("Constructor Build")

    def model_builder(self, df, Ycol, cols_to_drop, model_obj):
        """
                         Data Science Library
         method name: model Builder
        desc: Here we are created the whole model on the basis of previous library;
        In terms of preprocessing, cvtune, datavisualization, anova etc we are come up to
        this conclusion and this code is used to create the model directly from the calling
        the library only.
        author name: TinCharlie

        :param df: Passing DataFrame
        :param Ycol: Target COlumns
        :param cols_to_drop: Columns whichever we want to delete
        :param model_obj: Applying the algorithms for finishing the model.
        :return: Return the accuracy of your model.
        """
        import pandas as pd
        df = df.drop(labels=cols_to_drop, axis=1)
        replace.Mean_mode_replacer(df)
        Y = df[Ycol]
        X = df.drop(labels=Ycol, axis=1)
        X_new = preprocess.preprocess_data(X)
        from sklearn.model_selection import train_test_split
        xtrain, xtest, ytrain, ytest = train_test_split(X_new, Y, test_size=0.2, random_state=31)
        if ytrain[Ycol[0]].dtypes == "object":
            print(overfit_or_not.find_overfit_cat(model_obj, xtrain, xtest, ytrain, ytest))
            return "Categorical Data"
        else:
            print(overfit_or_not.find_overfit_con(model_obj, xtrain, xtest, ytrain, ytest))
            return "Continous Data"


class grid_tune:
    def __init__(self, df):
        self.df = df
        print("Constructor Build")

    def CV_tune(self, df, Ycol, cols_to_drop, model_obj, tp):
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
        replace.Mean_mode_replacer(df)
        Y = df[Ycol]
        X = df.drop(labels=Ycol, axis=1)
        X_new = preprocess.preprocess_data(X)
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
