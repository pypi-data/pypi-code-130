import numpy
import pandas
from datetime import datetime
from sklearn.metrics import cohen_kappa_score, jaccard_score, accuracy_score, balanced_accuracy_score, recall_score, precision_score, matthews_corrcoef, f1_score, fbeta_score, classification_report
from sklearn.metrics import explained_variance_score, max_error, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, r2_score, mean_poisson_deviance, mean_gamma_deviance, mean_absolute_percentage_error

class BinaryClassification:
    @classmethod
    def evaluation(cls, y_true, y_pred, y_prob):
        evaluation = dict(evaluation_time=datetime.now())
        comparison = pandas.DataFrame({'y_true':y_true, 'y_pred':y_pred})
        metric = dict()

        metric['cohen_kappa_score'] = [ cohen_kappa_score(comparison['y_true'], comparison['y_pred'], weights=None) ]
        metric['cohen_kappa_score_with_linear_weight'] = [cohen_kappa_score(comparison['y_true'], comparison['y_pred'], weights='linear')]
        metric['cohen_kappa_score_with_quadratic_weight'] = [cohen_kappa_score(comparison['y_true'], comparison['y_pred'], weights='quadratic')]
        metric['jaccard_score_with_micro_average'] = [jaccard_score(comparison['y_true'], comparison['y_pred'], average='micro')]
        metric['jaccard_score_with_macro_average'] = [jaccard_score(comparison['y_true'], comparison['y_pred'], average='macro')]
        metric['jaccard_score_with_weighted_average'] = [jaccard_score(comparison['y_true'], comparison['y_pred'], average='weighted')]
        metric['accuracy'] = [accuracy_score(comparison['y_true'], comparison['y_pred'], normalize=True)]
        metric['balanced_accuracy_score'] = [balanced_accuracy_score(comparison['y_true'], comparison['y_pred'])]
        metric['precision_with_micro_average'] = [precision_score(comparison['y_true'], comparison['y_pred'], average='micro')]
        metric['precision_with_macro_average'] = [precision_score(comparison['y_true'], comparison['y_pred'], average='macro')]
        metric['precision_with_weighted_average'] = [precision_score(comparison['y_true'], comparison['y_pred'], average='weighted')]
        metric['recall_with_micro_average'] = [recall_score(comparison['y_true'], comparison['y_pred'], average='micro')]
        metric['recall_with_macro_average'] = [recall_score(comparison['y_true'], comparison['y_pred'], average='macro')]
        metric['recall_with_weighted_average'] = [recall_score(comparison['y_true'], comparison['y_pred'], average='weighted')]
        metric['f1_with_micro_average'] = [f1_score(comparison['y_true'], comparison['y_pred'], average='micro')]
        metric['f1_with_macro_average'] = [f1_score(comparison['y_true'], comparison['y_pred'], average='macro')]
        metric['f1_with_weighted_average'] = [f1_score(comparison['y_true'], comparison['y_pred'], average='weighted')]
        metric['fbeta1_score_with_micro_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=1, average='micro')]
        metric['fbeta1_score_with_macro_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=1, average='macro')]
        metric['fbeta1_score_with_weighted_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=1, average='weighted')]
        metric['fbeta2_score_with_micro_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=2, average='micro')]
        metric['fbeta2_score_with_macro_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=2, average='macro')]
        metric['fbeta2_score_with_weighted_average'] = [fbeta_score(comparison['y_true'], comparison['y_pred'], beta=2, average='weighted')]
        metric['matthews_corrcoef'] = [matthews_corrcoef(comparison['y_true'], comparison['y_pred'])]
        evaluation.update(metric)

        return pandas.DataFrame(data=evaluation)
        

class MultiClassification:
    def __init__(self, y_true, y_pred, y_prob=None):
        pass

class MultiLabelClassification:
    def __init__(self, y_true, y_pred, y_prob=None):
        pass

class Regression:
    def __init__(self, y_true, y_pred):
        pass





def classification(y_true, y_pred, y_prob=None):
    assert isinstance(y_true, pandas.DataFrame) or isinstance(y_true, pandas.Series) or isinstance(y_true, numpy.ndarray)
    assert isinstance(y_pred, pandas.DataFrame) or isinstance(y_pred, pandas.Series) or isinstance(y_pred, numpy.ndarray)
    if y_prob is not None:
        assert isinstance(y_prob, pandas.DataFrame) or isinstance(y_prob, pandas.Series) or isinstance(y_prob, numpy.ndarray)
    
    if isinstance(y_true, pandas.Series):
        # [for pandas.Series]: Uni-Label classification
        if y_true.unique().shape[0] == 2:
            # [binary-class] classification
            BinarayClassification.evaluation(y_true, y_pred, y_prob)
        else:
            # [multi-class] classification
            MultiClassification.evaluation(y_true, y_pred, y_prob)
    else:
        # [for pandas.DataFrame]: Uni-Label classification, Multi-Label classification
        if y_true.shape[1] == 1:
            # [Uni-Label] classification
            y_true = y_true.iloc[:, 0]

            if y_true.shape[0] == 2:
                # [binary-class] classification
                BinarayClassification.evaluation(y_true, y_pred, y_prob)
            else:
                # [multi-class] classification
                MultiClassification.evaluation(y_true, y_pred, y_prob)
        else:
            # [Multi-Label] classification
            raise NotImplementedError()

    return 

def regression(y_true, y_pred):
    assert isinstance(y_true, pandas.DataFrame) or isinstance(y_true, pandas.Series)
    assert isinstance(y_pred, pandas.DataFrame) or isinstance(y_pred, pandas.Series)
    Regression(y_true, y_pred)


