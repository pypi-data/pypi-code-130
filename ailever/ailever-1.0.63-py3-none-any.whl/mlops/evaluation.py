from ..logging_system import logger

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
        
        metric['true_positive'] =   ((comparison['y_true'] == 1)&(comparison['y_pred'] == 1)).sum()
        metric['true_negative'] =   ((comparison['y_true'] == 0)&(comparison['y_pred'] == 0)).sum()
        metric['false_positive'] =  ((comparison['y_true'] == 0)&(comparison['y_pred'] == 1)).sum()
        metric['falese_negative'] = ((comparison['y_true'] == 1)&(comparison['y_pred'] == 0)).sum()
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
        
        # AUC Display
        if y_prob is not None:
            import matplotlib.pyplot as plt
            from sklearn.metrics import confusion_matrix, classification_report
            from sklearn.metrics import roc_curve, precision_recall_curve, auc

            confusion_matrix = confusion_matrix(y_true, y_pred)
            recall = confusion_matrix[1, 1]/(confusion_matrix[1, 0]+confusion_matrix[1, 1])
            fallout = confusion_matrix[0, 1]/(confusion_matrix[0, 0]+confusion_matrix[0, 1])
            precision = confusion_matrix[0, 0]/(confusion_matrix[0, 0]+confusion_matrix[1, 0])
            fpr, tpr1, thresholds1 = roc_curve(y_true, y_prob[:,1])
            ppv, tpr2, thresholds2 = precision_recall_curve(y_true, y_prob[:,1])

            # visualization
            logger['mlops'].info('- ROC AUC:' + f'{auc(fpr, tpr1)}')
            logger['mlops'].info('- PR AUC:', f'{auc(tpr2, ppv)}')
            print(classification_report(y_true, y_pred, target_names=['down', 'up']))
            plt.figure(figsize=(30, 5))

            ax0 = plt.subplot2grid((1,2), (0,0))
            ax1 = plt.subplot2grid((1,2), (0,1))

            ax0.plot(fpr, tpr1, 'ko-') # X-axis(fpr): fall-out / y-axis(tpr): recall
            ax0.plot([fallout], [recall], 'ko', ms=10)
            ax0.plot([0, 1], [0, 1], 'k--')
            ax0.set_xlabel('Fall-Out')
            ax0.set_ylabel('Recall')
            ax0.set_title('ROC AUC')
            ax0.grid(True)

            ax1.plot(tpr2, ppv, 'ko-') # X-axis(tpr): recall / y-axis(ppv): precision
            ax1.plot([recall], [precision], 'ko', ms=10)
            ax1.plot([0, 1], [1, 0], 'k--')
            ax1.set_xlabel('Recall')
            ax1.set_ylabel('Precision')
            ax1.set_title('PR AUC')
            ax1.grid(True)

            plt.tight_layout()

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
            return BinaryClassification.evaluation(y_true, y_pred, y_prob)
        else:
            # [multi-class] classification
            return MultiClassification.evaluation(y_true, y_pred, y_prob)
    else:
        # [for pandas.DataFrame]: Uni-Label classification, Multi-Label classification
        if y_true.shape[1] == 1:
            # [Uni-Label] classification
            y_true = y_true.iloc[:, 0]

            if y_true.unique().shape[0] == 2:
                # [binary-class] classification
                return BinaryClassification.evaluation(y_true, y_pred, y_prob)
            else:
                # [multi-class] classification
                return MultiClassification.evaluation(y_true, y_pred, y_prob)
        else:
            # [Multi-Label] classification
            raise NotImplementedError()

def regression(y_true, y_pred):
    assert isinstance(y_true, pandas.DataFrame) or isinstance(y_true, pandas.Series)
    assert isinstance(y_pred, pandas.DataFrame) or isinstance(y_pred, pandas.Series)
    return Regression(y_true, y_pred)


