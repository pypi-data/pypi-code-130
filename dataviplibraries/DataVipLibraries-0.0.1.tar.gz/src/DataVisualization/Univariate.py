def Univariate(A, figsize, rows, columns):
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


def Bivariate(A, Y, figsize, rows, columns):
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
