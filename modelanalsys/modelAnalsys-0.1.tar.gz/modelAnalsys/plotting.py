import os
import matplotlib.pyplot as plt
import numpy as np
from modelAnalsys import functions as fn
import seaborn as sns
import os
import matplotlib.figure
from sklearn.metrics import roc_curve, auc
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
s_roc = 0.2

class PlotLearning(keras.callbacks.Callback):
    """
    Callback to plot the learning curves of the model during training.
    """

    x = list()
    y = list()
    metrics = dict()
    f = matplotlib.figure.Figure()
    axs = np.ndarray((1, 2))

    def on_train_begin(self, logs=None):
        self.metrics = {}
        plt.tight_layout()
        for metric in logs:
            self.metrics[metric] = []

    def on_epoch_end(self, epoch, logs=None):
        # Storing metrics
        for metric in logs:
            if metric in self.metrics:
                self.metrics[metric].append(logs.get(metric))
            else:
                self.metrics[metric] = [logs.get(metric)]

        # Plotting
        metrics = [x for x in logs if 'val' not in x]
        if epoch == 0:
            self.f, self.axs = plt.subplots(1, len(metrics), figsize=(15, 5))
            self.f.show()

        for i, metric in enumerate(metrics):
            self.axs[i].plot(range(1, epoch + 2), self.metrics[metric], label=metric)
            if logs['val_' + metric]:
                self.axs[i].plot(range(1, epoch + 2), self.metrics['val_' + metric], label='val_' + metric)

            self.axs[i].legend()
            self.axs[i].grid()

        self.f.canvas.draw()
        self.f.canvas.flush_events()

        for ax in self.axs:
            ax.clear()

def get_measures(actual: list, expected: list):
    tp, p, fp, n = 0, 0, 0, 0
    for i, val in enumerate(actual):
        if expected[i] == 1:
            p = p + 1
            if val == 1:
                tp = tp + 1
        else:
            n = n + 1
            if val == 0:
                fp = fp + 1
    return tp, p, fp, n


# ROC and threshold calculation
class BestThreshold:
    idx = -1
    distance = -1

    def __init__(self):
        self.idx = -1
        self.distance = -1


def distance(x, y):
    return abs(x - y) / 1.414213562373095


def confusion_matrix(conf_mx, classes, in_percent=False):
    if in_percent:
        conf_mx = conf_mx.astype(float)
        rows, columns = conf_mx.shape

        for x in range(columns):
            column_sum = 0.0
            for y in conf_mx[:, x]:
                column_sum += y
            for y in range(rows):
                conf_mx[y, x] = "{:.2f}".format((conf_mx[y, x]/column_sum)*100)

        # -------------------- Percent for rows --------------------
        # for y in range(rows):
        #     row_sum = 0.0
        #     for x in conf_mx[y]:
        #         row_sum += x
        #     print(row_sum)
        #     for x in range(columns):
        #         conf_mx[y, x] = round((conf_mx[y, x]/row_sum)*100)
        # print(conf_mx)

    plt.figure("Confusion Matrix")
    ax = sns.heatmap(conf_mx, annot=True, yticklabels=classes, xticklabels=classes, fmt='g', cmap="rocket_r", vmin=0,
                     vmax=100)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    for i in range(conf_mx.shape[1] + 1):
        ax.axvline(i, color='white', lw=10)
    plt.ylabel("Output Class", fontsize=15)
    plt.xlabel("Target Class", fontsize=15)
    plt.draw()


# Receiver operating characteristic
def roc_curve_multi(predicted_dummy_y: np.ndarray, correct_dummy_y: np.ndarray, classes: list, result_sub_folder=""):
    plt.figure("ROC")
    ax = plt.gca()
    lw = 2
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    best_thresholds = list()
    area_under_curve = float()
    for c in range(len(classes)):
        tpr_roc = list()
        fpr_roc = list()
        steps = 1000
        BT = BestThreshold()
        for i in range(1, steps, 1):
            if i % 100 == 0:
                os.system('cls')
                # print(f"Calculating {int((i/steps)*100)}%")
            y_predicted_for_roc = [0 if val < (i/steps) else 1 for val in predicted_dummy_y[:, c]]
            tp, p, fp, n = get_measures(y_predicted_for_roc, correct_dummy_y[:, c].tolist())
            y = tp/p
            x = 1.0 - fp/n
            tpr_roc.append(y)
            fpr_roc.append(x)
            dist = distance(x, y)
            if dist > BT.distance:
                BT.distance = dist
                BT.idx = i

        area_under_curve += fn.calculate_auc(fpr_roc, tpr_roc)
        best_threshold = BT.idx / steps
        best_thresholds.append(best_threshold)
        if classes[c] == 'covid':
            plt.plot(fpr_roc, tpr_roc, color='red', lw=lw, marker='o', markersize=s_roc)
        elif classes[c] == 'pneumonia':
            plt.plot(fpr_roc, tpr_roc, color='blue', lw=lw, marker='o', markersize=s_roc)
        else:
            plt.plot(fpr_roc, tpr_roc, color='green', lw=lw, marker='o', markersize=s_roc)
        plt.plot(fpr_roc[BT.idx-1], tpr_roc[BT.idx-1], marker='o', color='orange', markersize=1)
        ax.annotate(best_threshold, (fpr_roc[BT.idx-1], tpr_roc[BT.idx-1]))
        del BT
    area_under_curve /= len(classes)
    # print("AUC: ", area_under_curve)

    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.savefig(result_sub_folder + "roc.png")
    plt.draw()
    return best_thresholds, area_under_curve


# Receiver operating characteristic
def roc_curve_custom(y_predicted, y_correct, show=True, save=True, result_sub_folder="", output_name="roc"):
    if result_sub_folder != "":
        result_sub_folder += "/"

    tpr_roc = list()
    fpr_roc = list()
    steps = 1000
    for i in range(1, steps, 1):
        if i % 100 == 0:
            if show:
                print(f"Calculating {int((i/steps)*100)}%")
        y_predicted_for_roc = [0 if val < (i/steps) else 1 for val in y_predicted]
        tp, p, fp, n = get_measures(y_predicted_for_roc, y_correct.tolist())
        y = tp/p
        x = 1.0 - fp/n
        tpr_roc.append(y)
        fpr_roc.append(x)
        dist = distance(x, y)
        if dist > BestThreshold.distance:
            BestThreshold.distance = dist
            BestThreshold.idx = i

    best_threshold = BestThreshold.idx / steps
    area_under_curve = fn.calculate_auc(fpr_roc, tpr_roc)

    if show:
        plt.figure(output_name)
        ax = plt.gca()
        lw = 2
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.plot(fpr_roc, tpr_roc, color='darkorange', lw=lw, marker='o', markersize=s_roc)
        plt.plot(fpr_roc[BestThreshold.idx-1], tpr_roc[BestThreshold.idx-1], marker='o', color='red', markersize=s_roc)
        ax.annotate(best_threshold, (fpr_roc[BestThreshold.idx-1], tpr_roc[BestThreshold.idx-1]))
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.draw()
        if save:
            plt.savefig(result_sub_folder+output_name+".png")
        plt.show()

    return best_threshold, area_under_curve


def classification_graph(y_predicted, y_correct, threshold, title="classification_graph", show_green=True, show_red=True, grid=0, result_sub_folder=""):
    y_correct_list = y_correct.values.tolist()
    plt.figure()
    lw = 1
    s = 0.1
    plt.ylim([0.0, 1.05])
    for i, val in enumerate(y_predicted):
        if i % 100 == 0:
            os.system('cls')
            # print(f"Creating figure {int((i / len(y_predicted)) * 100)}%")
        if y_correct_list[i] == 0:
            if show_green:
                plt.scatter(i, val[0], color='green', s=s)
        else:
            if show_red:
                plt.scatter(i, val[0], color='red', s=s)
    plt.plot([0, len(y_correct_list)], [threshold, threshold], color='blue', lw=lw)
    plt.xlabel('Iterator')
    plt.ylabel('Result')

    if grid > 0:
        x = np.linspace(0, len(y_correct_list), grid)
        y = np.linspace(0, 1, grid)
        # writing grid on plot
        for v in enumerate(x):
            v = v[1]
            plt.plot([v, v], [0, 1], lw=0.1, color='black')
        for v in enumerate(y):
            v = v[1]
            plt.plot([0, len(y_predicted)], [v, v], lw=0.1, color='black')
    plt.savefig(result_sub_folder + title + ".png")
    return plt
   
 
def classification_bar_graph(y_predicted, y_correct, title="classification_bar_graph", show_green=True, show_red=True, grid=20, result_sub_folder=""):
    y_correct_list = y_correct.values.tolist()
    x = np.linspace(0, len(y_correct_list), grid)
    y = np.linspace(0, 1, grid)
    # bar graph green
    xan = [0] * grid
    xai = [0] * grid
    for j, v in enumerate(y_predicted):
        for i, val in enumerate(y, start=1):
            if i == grid:
                break
            if y[i] > v >= y[i - 1]:
                if y_correct_list[j] == 0:
                    xan[i] += 1
                elif y_correct_list[j] == 1:
                    xai[i] += 1
    plt.figure()
    if show_green:
        plt.bar(y, xan, color='green', width=0.05, alpha=0.3)
    if show_red:
        plt.bar(y, xai, color='red', width=0.05, alpha=0.3)
    plt.savefig(result_sub_folder + title + ".png")
    return plt


def contour_plot(y_predicted, y_correct, title="contour_plot", show_green=True, show_red=True, grid=20, result_sub_folder=""):
    y_correct_list = y_correct.values.tolist()
    x = np.linspace(0, len(y_correct_list), grid)
    y = np.linspace(0, 1, grid)
    X, Y = np.meshgrid(x, y)
    Zn = [[0 for c in range(grid)] for r in range(grid)]
    Zi = [[0 for c in range(grid)] for r in range(grid)]
    for i, y_val in enumerate(y):
        if i + 1 == len(y):
            break
        for j, x_val in enumerate(x):
            if j + 1 == len(x):
                break
            for k, v in enumerate(y_predicted, start=int(x_val)):
                if k >= x[j + 1]:
                    break
                v = float(v)
                if y_val <= v < y[i + 1]:
                    if y_correct_list[k] == 0:
                        Zn[i][j] += 1
                    else:
                        Zi[i][j] += 1
    plt.figure()
    if show_green:
        plt.contour(X, Y, Zn)
    if show_red:
        plt.contour(X, Y, Zi)
    plt.savefig(result_sub_folder + title + ".png")
    return plt




