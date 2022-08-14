import numpy as np
import pandas as pd

def mod(value):
    if value < 0:
        return value * -1
    return value


def calculate_auc(x: list, y: list):
    if len(x) != len(y):
        raise AttributeError("list lengths do not match")
    auc = 0.0
    for i in range(1, len(x)):
        auc += ((y[i-1]+y[i]) * mod(x[i]-x[i-1])) / 2.0
    return auc

def place_where_max(y_continous: np.ndarray):
    maximum = int()
    idx = int()
    for y in range(np.shape(y_continous)[0]):
        maximum = -1
        for i in range(np.shape(y_continous)[1]):
            if maximum < y_continous[y][i]:
                maximum = y_continous[y][i]
                idx = i
        y_continous[y] = [0, 0, 0]
        y_continous[y][idx] = 1
    return y_continous.astype(int)


def debinarize(y_predictions: np.ndarray, classes: list):
    result = list()
    if y_predictions.ndim == 1:
        for entry in y_predictions:
            result.append(classes[entry])
    elif y_predictions.ndim == 2:
        for row in y_predictions:
            for i in range(len(row)):
                if row[i] == 1:
                    result.append(classes[i])
                    break
    else:
        raise Exception("This array dimensions are not handled")

    return result


def get_measures(predicted, actual):
    P = TP = FP = N = TN = FN = 0
    PP = PN = 0.0
    for i, val in enumerate(predicted):
        if val == 1:
            PP += 1.0
        else:
            PN += 1.0

        if actual[i] == 1:
            P += 1
            if val == 1:
                TP += 1
            else:
                FN += 1
        else:
            N += 1
            if val == 1:
                FP += 1
            else:
                TN += 1
    PPV = NPV = TPR = FPR = 1.0
    if PP != 0:
        PPV = TP/PP
    if PN != 0:
        NPV = TN/PN
    if P != 0:
        TPR = TP/P
    if N != 0:
        FPR = FP/N
    return P, TP, FN, N, FP, TN, PPV, NPV, TPR, FPR


def precision_score_multi(confusion_matrix, classes: list):
    length = len(classes)
    df = pd.DataFrame(data=np.zeros(shape=(length, 4)).astype(int), index=classes,
                      columns=['TP', 'FP', 'TN', 'FN'])
    for y in range(length):
        for x in range(length):
            if x == y:
                df['TP'][classes[y]] = confusion_matrix[y][x]
            else:
                df['FN'][classes[y]] += confusion_matrix[y][x]
                df['FP'][classes[x]] += confusion_matrix[y][x]
            for i in range(length):
                if i != x and i != y:
                    df['TN'][classes[i]] += confusion_matrix[y][x]

    df.insert(4, 'TPR', np.zeros(shape=length), True)
    df.insert(5, 'TNR', np.zeros(shape=length), True)
    for i in range(length):
        df.loc[classes[i], 'TPR'] = df.loc[classes[i], 'TP'] / (df.loc[classes[i], 'TP'] + df.loc[classes[i], 'FN'])
        df.loc[classes[i], 'TNR'] = df.loc[classes[i], 'TN'] / (df.loc[classes[i], 'TN'] + df.loc[classes[i], 'FP'])
    return df
