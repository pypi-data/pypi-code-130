import numpy as np
from numpy.linalg import inv # 求逆矩阵
from scipy.stats import chi2

class ScoreTest:
    __slots__ = ('n', 'B', 'sigma2', 'y', 'X', 'ms_critical', 'vw_critical','ms_scores', 'vw_scores', 'ms_labels', 'vw_labels')

    def __init__(self, y, X, sigma2, coef):
        self.y = y
        self.n = y.shape[0]
        self.X = self.gene_indep_variable(X, coef)
        self.B = coef
        self.sigma2 = sigma2
        self.ms_critical = chi2.isf(0.05/self.n, 1)
        self.vw_critical = chi2.isf(0.05/self.n, 1)
        self.ms_scores = None
        self.vw_scores = None
        self.ms_labels = None
        self.vw_labels = None
    
    def gene_indep_variable(self, X, coef):
        if len(coef) - X.shape[0] == 1:
            return np.concatenate((np.ones((1,self.n)), X), axis=0)
        elif len(coef) == X.shape[0]:
            return X
        else:
            raise ValueError("X维数与coef维数不匹配")
    
    def mean_shift(self):
        B, X, y = self.B, self.X, self.y
        n, sigma2 = self.n, self.sigma2
        critical = self.ms_critical

        scores = np.zeros(n)
        labels = np.zeros(n)
        for i in range(n):
            Xi = X[:,i]
            scores[i] = (y[i]-np.dot(B, Xi))**2/sigma2/(1-np.dot(np.dot(Xi.reshape(1,-1), inv(np.dot(X, X.T))), Xi.reshape(-1,1)))
            if scores[i] >= critical:
                labels[i] = 1
        self.ms_scores = scores
        self.ms_labels = labels
    
    def variance_weight(self):
        B, X, y = self.B, self.X, self.y
        n, sigma2 = self.n, self.sigma2
        critical = self.vw_critical

        scores = np.zeros(n)
        labels = np.zeros(n)
        for i in range(n):
            Xi = X[:,i]
            scores[i] = n/(2*n-2)*(1-(y[i]-np.dot(B,Xi))**2/sigma2)**2
            if scores[i] >= critical:
                labels[i] = 1
        self.vw_scores = scores
        self.vw_labels = labels
    
    def mengmeng(self):
        print("宝，我成功了，厉害不！")