
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def xor() -> pd.DataFrame:

    xor = {'X1': {0: 0, 1: 1, 2: 1, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1, 8: 0, 9: 1, 10: 1, 11: 0, 12: 0, 13: 1, 14: 1, 15: 0, 16: 0, 17: 1, 18: 1, 19: 0}, 
    'X2': {0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1, 8: 0, 9: 0, 10: 1, 11: 0, 12: 1, 13: 0, 14: 1, 15: 0, 16: 1, 17: 0, 18: 1, 19: 0}, 
    'X3': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1}, 
    'OR': {0: 1, 1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1, 10: 1, 11: 0, 12: 1, 13: 1, 14: 1, 15: 0, 16: 1, 17: 1, 18: 1, 19: 0}, 
    'AND': {0: 0, 1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1, 8: 0, 9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 1, 15: 0, 16: 0, 17: 0, 18: 1, 19: 0}, 
    'XOR': {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 1, 10: 0, 11: 0, 12: 1, 13: 1, 14: 0, 15: 0, 16: 1, 17: 1, 18: 0, 19: 0}}
    
    return pd.DataFrame(xor)

def get_direct_positive(direct, n):
    n_direct = {}
    for key in direct:
        n_direct[key] = direct[key][1][:, :n]
    return n_direct


def get_direct_unsigned(direct, n):
    n_direct = {}
    for key in direct:
        n_direct[key] = []
        n_direct[key].append(direct[key][0][:, :n])
        n_direct[key].append(direct[key][1][:, :n])
    return n_direct


def get_indirect_unsigned(indirect):
    signed_indirect = {}
    for key in indirect:
        signed_indirect[key] = [-indirect[key], indirect[key]]
    signed_indirect['class0'] = []
    return signed_indirect


def draw_features_contribs(var_x, var_y, direct, indirect):
    """
    Parameters:
    Similar parameters to Shap chains class (var_X, var_Y).
    Direct, indirect -> from Shap chains get contributions.
    Returns:
    Plot non normalized and normalized Shapley contributions with stacked plots.
    Print non normalized Shapley table.
    """

    plt.figure(figsize=(18, 18))
    n = len(var_x)  # nb of features
    k = len(var_y)  # nb of outputs
    shap_chain = pd.DataFrame(index=var_x)  # shap_chain results

    shap_chain['direct_' + str(var_y[0])] = np.mean(np.abs(direct['class0'][1]), axis=0)

    for i in range(1, k):
        shap_chain['direct_' + str(var_y[i])] = np.mean(np.abs(direct['class' + str(i)][1]), axis=0)[:n]
        shap_chain['indirect_' + str(var_y[i])] = np.mean(np.abs(indirect['class' + str(i)]), axis=0)

    shap_chain['total'] = shap_chain.sum(axis=1)

    print("Direct and indirect shapley contributions")
    shap_chain.sort_values(by='total')[list(shap_chain)[:-1]].plot.barh(figsize=(8, 8), stacked=True)
    plt.legend(loc=4)
    #plt.show()

    # sum shapley contributions for each model, in order to normalize
    sum_shap = [shap_chain['direct_' + str(var_y[0])].sum()]
    for i in range(1, k):
        sum_shap.append((shap_chain['direct_' + str(var_y[i])] + shap_chain['indirect_' + str(var_y[i])]).sum())

    # normalize shap values for each model
    shap_chain_normalized = shap_chain.copy(deep=True)
    shap_chain_normalized['direct_' + str(var_y[0])] = shap_chain_normalized['direct_' + str(var_y[0])] / sum_shap[0]
    for i in range(1, k):
        shap_chain_normalized['direct_' + str(var_y[i])] = shap_chain_normalized['direct_' + str(var_y[i])] / sum_shap[
            i]
        shap_chain_normalized['indirect_' + str(var_y[i])] = shap_chain_normalized['indirect_' + str(var_y[i])] / \
                                                             sum_shap[i]

    shap_chain_normalized.drop('total', axis=1, inplace=True)
    shap_chain_normalized['total'] = shap_chain_normalized.sum(axis=1)

    # plt.figure(figsize=(18,18))
    print("Normalized direct and indirect shapley contributions")
    shap_chain_normalized.sort_values(by='total')[list(shap_chain_normalized)[:-1]].plot.barh(figsize=(8, 8),
                                                                                              stacked=True)
    plt.legend(loc=4)
    plt.xlabel("(f) Shapley chains with order = " + str(var_y))
    plt.savefig('normalized.png', bbox_inches="tight", dpi=1000)

    #plt.show()

    shap_chain_normalized = shap_chain_normalized.sort_values(by='total')
    return shap_chain, shap_chain_normalized

