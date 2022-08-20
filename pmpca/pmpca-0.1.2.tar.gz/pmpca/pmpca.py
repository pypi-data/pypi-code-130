import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PCA():
   
    ###############

    def __init__ (self, a = 0.9):

        """
        Constructor.
        
        Parameters
        ----------
        a: pandas.DataFrame or numpy.array, optional
            Minimum fraction of accumulated variance 
            for selecting the number of principal components.
        """
        
        self.KPI_train = {}
        self.KPI_test = {}
        self.KPI_lim = {}
        self.alarm = {}
        self.fdr = {}
        self.far = {}
        self.a = a
        
        for kpi in ['T2','Q']:
            self.KPI_lim[kpi] = {}
            self.alarm[kpi] = {}
            self.fdr[kpi] = {}
            self.far[kpi] = {}
        
        self.alarm['comb'] = {}
        self.fdr['comb'] = {}
        self.far['comb'] = {} 
        
    ###############

    def fit(self, X, conf_Q = 0.99, conf_T2 = 0.99, plot = True):

        """
        Fit a PCA model.
        
        Parameters
        ----------
        X: pandas.DataFrame or numpy.array
            Training data.
        conf_Q: float, optional
            Confidence limit for computing the threshold 
            for the Q statistics; 0<conf_Q<1
        conf_T2: float, optional
            Confidence limit for computing the threshold 
            for the T2 statistics; 0<conf_Q<1
        plot: boolean, optional
            Whether to plot data variance X number of components
        """
        
        X = pd.DataFrame(X)
        
        self.conf_T2 = conf_T2
        self.conf_Q = conf_Q
        
        # saving training means and standard deviations
        self.mu_train = X.mean(axis=0)
        self.std_train = X.std(axis=0)        
       
        # normalizing training data
        X = np.array(((X - self.mu_train)/self.std_train))
       
        # calculating the covariance matrix of the data
        Cx = np.cov(X, rowvar=False)
        
        # applying decomposition into eigenvalues and eigenvectors
        self.L, self.P = np.linalg.eig(Cx)
        
        # fractions of explained variance
        fv = self.L/np.sum(self.L)
        
        # fractions of the accumulated explained variance
        fva = np.cumsum(self.L)/sum(self.L)
       
        # defining number of components
        if self.a>0 and self.a<1:
            self.a = np.where(fva>self.a)[0][0]+1 
            
        # calculating T^2 statistic
        T = X@self.P[:,:self.a]
        self.KPI_train['T2'] = np.array([T[i,:]@np.linalg.inv(np.diag(self.L[:self.a]))@T[i,:].T for i in range(X.shape[0])])

        # calculating Q statistic
        e = X - X@self.P[:,:self.a]@self.P[:,:self.a].T
        self.KPI_train['Q']  = np.array([e[i,:]@e[i,:].T for i in range(X.shape[0])])
            
        # calculating detection limits

        # theoretical limit of T^2 statistics
        from scipy.stats import f
        F = f.ppf(conf_T2, self.a, X.shape[0]-self.a)
        self.KPI_lim['T2']['theoretical'] = ((self.a*(X.shape[0]**2-1))/(X.shape[0]*(X.shape[0]-self.a)))*F
        
        # theoretical limit of Q statistics
        theta = [np.sum(self.L[self.a:]**(i)) for i in (1,2,3)]
        ho = 1-((2*theta[0]*theta[2])/(3*(theta[1]**2)))
        from scipy.stats import norm
        nalpha = norm.ppf(conf_Q)
        self.KPI_lim['Q']['theoretical'] = (theta[0]*(((nalpha*np.sqrt(2*theta[1]*ho**2))/theta[0])+1+
                                ((theta[1]*ho*(ho-1))/theta[0]**2))**(1/ho))
        
        # empirical limit of the T^2 statistic
        iT2 = np.sort(self.KPI_train['T2'])
        self.KPI_lim['T2']['percentile'] = iT2[int(conf_T2*X.shape[0])]
        
        # empirical limit of the Q statistic
        iQ = np.sort(self.KPI_train['Q'])
        self.KPI_lim['Q']['percentile'] = iQ[int(conf_Q*X.shape[0])]
        
        # plotting explained variances
        if plot:
            fig, ax = plt.subplots()
            ax.bar(np.arange(len(fv)),fv, color='k')
            ax.plot(np.arange(len(fv)),fva, color='k')
            ax.set_xlabel('Number of components')
            ax.set_ylabel('Data variance')
            ax.set_title('PCA');

    ###############
            
    def predict(self, X, mask_fault = None, redefine_lim = False, 
                compute_far = False, compute_combined = True):
        
        """
        Predict (reconstruct) using the PCA model.
        
        Parameters
        ----------
        X: pandas.DataFrame or numpy.array
            Test data.
        mask_fault: sequence, optional
            Boolean array indicating which observations are faulty.
        redefine_lim: boolean, optional
            If True, the detection limits are redefined using the test data.
        compute_far: boolean, optional
            If True, false alarm rates are computed.
        compute_combined: boolean, optional
            If True, T2 and Q are combined into a unified detection index
        """
            
        # normalizing test data (using training parameters!)
        X = np.array((X - self.mu_train)/self.std_train)

        # calculating T^2 statistic
        T = X@self.P[:,:self.a]
        self.KPI_test['T2'] = np.array([T[i,:]@np.linalg.inv(np.diag(self.L[:self.a]))@T[i,:].T for i in range(X.shape[0])])

        # calculating Q statistic
        e = X - X@self.P[:,:self.a]@self.P[:,:self.a].T
        self.KPI_test['Q']  = np.array([e[i,:]@e[i,:].T for i in range(X.shape[0])])
        
        # calculation contributions to Q
        self.c = np.absolute(X*e)
        
        if redefine_lim:
            # empirical limit of the T^2 statistic
            iT2 = np.sort(self.KPI_test['T2'])
            self.KPI_lim['T2']['percentile'] = iT2[int(self.conf_T2*X.shape[0])]

            # empirical limit of the Q statistic
            iQ = np.sort(self.KPI_test['Q'])
            self.KPI_lim['Q']['percentile'] = iQ[int(self.conf_Q*X.shape[0])]
            
        if mask_fault is not None:
            for kpi in self.KPI_lim:
                for lim in self.KPI_lim[kpi]:
                    self.alarm[kpi][lim] = self.KPI_test[kpi]>self.KPI_lim[kpi][lim]
                    self.fdr[kpi][lim] = np.sum(((mask_fault==1) & (self.alarm[kpi][lim]==mask_fault)))/np.sum((mask_fault==1))
                    if compute_far:
                        self.far[kpi][lim] = np.sum(((mask_fault==0) & (self.alarm[kpi][lim]!=mask_fault)))/np.sum((mask_fault==0))
            if compute_combined:
                for lim in ['theoretical', 'percentile']:
                    self.alarm['comb'][lim] = (self.alarm['T2'][lim] | self.alarm['Q'][lim])
                    self.fdr['comb'][lim] = np.sum(((mask_fault==1) & (self.alarm['comb'][lim]==mask_fault)))/np.sum((mask_fault==1))
                    if compute_far:
                        self.far['comb'][lim] = np.sum(((mask_fault==0) & (self.alarm['comb'][lim]!=mask_fault)))/np.sum((mask_fault==0))
        else:
            if compute_far:
                for kpi in self.KPI_lim:
                    for lim in self.KPI_lim[kpi]:
                        self.alarm[kpi][lim] = self.KPI_test[kpi]>self.KPI_lim[kpi][lim]
                        self.far[kpi][lim] = np.mean(self.alarm[kpi][lim])
                if compute_combined:
                    for lim in ['theoretical', 'percentile']:
                        self.alarm['comb'][lim] = (self.alarm['T2'][lim] | self.alarm['Q'][lim])
                        self.far['comb'][lim] = np.mean(self.alarm['comb'][lim])