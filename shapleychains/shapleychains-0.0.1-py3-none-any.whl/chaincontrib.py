import numpy as np
import shap
import re
import pandas as pd
from itertools import combinations


class ChainContrib:

    def __init__(self, data, var_x, var_y, estimators, explainer='tree'):
        self.data = data
        self.var_X = var_x
        self.var_Y = var_y
        self.n = len(var_x)
        self.m = len(var_y)
        self.l = len(data)
        self.estimators = estimators
        self.explainer_type = explainer

    def get_direct_contrib(self):
        # direct_values = OrderedDict([])
        direct_values = {}
        data_x = self.data[self.var_X].copy(deep=True)  # test dataset
        Y = self.estimators[0].predict_proba(data_x)[:, 1]  # we use probability predictions (instead of prediction)
        # explain all the predictions in the test set
        if self.explainer_type == 'Kernel':
            explainer = shap.KernelExplainer(self.estimators[0].predict_proba, data_x)
        elif self.explainer_type == 'Deep':
            explainer = shap.DeepExplainer(self.estimators[0], data_x)
        else:
            explainer = shap.TreeExplainer(self.estimators[0])
        shap_values = explainer.shap_values(data_x)
        direct_values['class0'] = shap_values
        for i in range(1, self.m):
            data_x['Y_' + str(i - 1)] = Y.copy()
            Y = self.estimators[i].predict_proba(data_x)[:, 1]
            # explain all the predictions of the test set
            if self.explainer_type == 'Kernel':
                explainer = shap.KernelExplainer(self.estimators[i].predict_proba, data_x)
            elif self.explainer_type == 'Deep':
                explainer = shap.DeepExplainer(self.estimators[i], data_x)
            else:
                explainer = shap.TreeExplainer(self.estimators[i])
            shap_values = explainer.shap_values(data_x)
            direct_values['class' + str(i)] = shap_values
        return direct_values

    @staticmethod
    def get_class_path(nb_class):
        paths = []

        def take_second(elem):
            reversed = sorted(elem, reverse=True)
            paths.append(reversed)
            return reversed

        all_classes = [i for i in range(nb_class)]
        results = [c for r in range(1, len(all_classes) + 1) for c in set(combinations(all_classes, r))]
        sorted(results, key=take_second)
        path = []
        for s in paths:
            path.append(['class' + str(x) for x in s])
        return path

    def get_class_contrib(self, combination, output_contrib, weights):
        temp = []
        for i in range(len(combination)):
            ar = combination[i]

            w = 1
            for j in range(len(ar)):
                index = ':'
                c = int(re.search(r'\d+', str(ar[0])).group())
                try:
                    index = int(re.search(r'\d+', str(ar[j + 1])).group())
                except Exception as e:
                    e
                if index == ':':
                    w *= weights[ar[j]][:self.n]
                else:
                    w *= weights[ar[j]][self.n + index]
            temp.append(output_contrib[c] * w)
        return sum(temp)

    @staticmethod
    def get_coef_shap(shap_values):
        return [np.abs(x) / np.sum(np.abs(x)) if np.sum(np.abs(x)) != 0 else 0 for x in shap_values]

    def get_weights(self, direct_contrib):
        weights = {}
        for key in direct_contrib:
            weights[key] = np.array(self.get_coef_shap(direct_contrib[key][1]))
        return weights

    def get_output_contrib(self, direct_contrib):
        output_contrib = {}
        for key in direct_contrib:
            output_contrib[key] = direct_contrib[key][1][:, self.n:]
        return output_contrib

    @staticmethod
    def get_some_data(oc, w, class_list, i):
        out_oc = {}
        out_w = {}
        for key in class_list:
            out_oc[key] = oc[key][i]
            out_w[key] = w[key][i]
        return out_oc, out_w

    def get_indirect_contrib(self, direct_contrib=None) :

        if None is direct_contrib:
            direct_contrib = self.get_direct_contrib()
        else:
            direct_contrib = direct_contrib.copy()
        output_contrib = self.get_output_contrib(direct_contrib)
        weights = self.get_weights(direct_contrib)
        indirect_contrib = {}
        for key in output_contrib:
            temp = []
            c = int(re.search(r'\d+', key).group())
            all_paths = self.get_class_path(c)
            for i in range(self.l):
                oc, w = self.get_some_data(output_contrib, weights, list(output_contrib.keys()), i)
                temp.append(self.get_class_contrib(all_paths, oc[key], w))
            indirect_contrib[key] = np.array(temp)
        indirect_contrib['class0'] = np.array([])
        return indirect_contrib

