
import numpy as np

def detect_outlier(dataset:list or tuple, threshold=3) -> list:
    """
        Description:
            Method is used to detect the outliers. 
            Its using Z-score to detect the outliers. 
            threshold z-score value set as 3 by default. 
            If the z-score is greather than threshold, it will be considered as a outlier
        parameters:
            dataset: datset must be list or tuple. Values must be integer or float 
        
        response:
            outlier : outlier list is send back to the caller , empt if there is no outlier
        
         raise:
            if the dataset is not tuple or list, it will raise "Accepts only list or tuple"
            if the items in the dataset is not integers or float, it will raise "Dataset must have int or float type"
    """
    outliers = []
    if type(dataset) == list or type(dataset) == tuple:
        is_number = all( isinstance(x, int) or isinstance(x, float) for x in dataset)
        if is_number:
            mean = np.mean(dataset)
            std = np.std(dataset)
            
            if std == 0:
                raise Exception("something went wrong. may be distribution is not correct")

            for x in dataset:
                z_score = ((x - mean) / std)
                if np.absolute(z_score) > threshold:
                    outliers.append(x)
            return outliers
        else:
            raise Exception("Dataset must have int or float type")
    else:
        raise Exception("Accepts only list or tuple")
    