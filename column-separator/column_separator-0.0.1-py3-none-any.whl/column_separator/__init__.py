def columns_separator(data, discrete_counts = 15):
    """The function column_seperator is used to seperate the continuous, discrete 
       and category column name from the given data.
       This function consist of two parameters,
                1. data -> Pass the entire dataset (pandas dataframe).
                2. discrete_counts -> (default value is 15) Used to get the discrete column names based on their unique counts.
                
       This function returns three output,
                1.Discrete column names
                2.Continuous column names
                3.Category column names

            E.G. : columns_seperator(data = dataframe)
                   columns_seperator(data = dataframe, discrete_counts = 10)"""

    import pandas as pd
    import numpy as np
    
    if type(data) == pd.core.frame.DataFrame and type(discrete_counts) == int:
        continuous_column = []
        discrete_column = []
        category_column = []
    
        for i in list(data.columns):
            counts = len(data[i].value_counts())
        
            if counts > 0 and counts <= discrete_counts:
                discrete_column.append(i)
                
        else:
            for i in list(data.columns):
                if data[i].dtypes == np.object_ and i not in discrete_column:
                    discrete_column.append(i)
                elif data[i].dtypes in [np.int8, np.int16, np.int32, np.int64, np.uint, np.uint8, np.uint16, np.uint32, np.uint64, np.float16, np.float32, np.float64] and i not in discrete_column:
                    continuous_column.append(i)
        
        for i in list(data.columns):
            if data[i].dtypes in [np.object0, np.object_]:
                category_column.append(i)
                
        for i in category_column:
            if i in discrete_column:
                discrete_column.remove(i)
        
        print("The Number of Discrete column present in the given data is {}.".format(len(discrete_column)))
        print("")
        print("The Number of Continuous column present in the given data is {}.".format(len(continuous_column)))
        print("")
        print("The Number of Category column present in the given data is {}.".format(len(category_column)))
        print("")
        
        return discrete_column, continuous_column, category_column
        
    else:
        return "The given data is not a pandas dataframe or discrete_counts is not an integer."