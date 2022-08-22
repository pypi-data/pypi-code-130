import numpy as np
from scipy.stats import norm

class PandasTwoDistMetrics:

    @classmethod
    def kl_div(self, df_kl_div, dist_A_label, dist_B_label):
        df_kl_div["kl_div"] = df_kl_div[dist_B_label] / np.log(df_kl_div[dist_B_label] / df_kl_div[dist_A_label])
        df_kl_div.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_kl_div
    
    @classmethod
    def psi(self, df_psi, dist_A_label, dist_B_label):
        df_psi["psi"] = (df_psi[dist_B_label] - df_psi[dist_A_label]) * np.log(df_psi[dist_B_label] / df_psi[dist_A_label])
        df_psi.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_psi
    
    @classmethod
    def chi2(self, df_chi2, dist_A_label, dist_B_label):
        df_chi2["chi2"] = np.power(df_chi2[dist_B_label] - df_chi2[dist_A_label], 2) / df_chi2[dist_A_label]
        df_chi2.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_chi2 
    
    @classmethod
    def pd_test(self, df_pd, dist_A_label, dist_B_label, dist_B_total_label, dist_prob=0.95):
        inv_norm = norm.ppf(dist_prob)
        df_pd["std"] = np.sqrt(df_pd[dist_A_label] * (1-df_pd[dist_A_label]))/ df_pd[dist_B_total_label]      
        df_pd["interval"] = inv_norm * df_pd["std"]
        df_pd["pd_lower_band"] = df_pd[dist_A_label] - df_pd["interval"]
        df_pd["pd_upper_band"] = df_pd[dist_A_label] + df_pd["interval"]  
        df_pd["pd_result"] = df_pd[dist_B_label].where(df_pd[dist_B_label].between(df_pd["pd_lower_band"], df["pd_upper_band"]), "ok",
                                  df_pd[dist_B_label].where(df_pd[dist_B_label] < df_pd["pd_lower_band"], "underestimated",
                                  df_pd[dist_B_label].where(df_pd[dist_B_label] > df_pd["pd_upper_band"], "overestimated", "undefined")))
        df_pd.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_pd
    
    @classmethod
    def iv(self, df_iv, dist_P_label, dist_N_label):
        df_iv["rr"] = df_iv[dist_P_label] / df_iv[dist_N_label]
        df_iv["woe"] = np.log(df_iv["rr"])
        df_iv["iv"] = (df_iv[dist_P_label] - df_iv[dist_N_label]) * df_iv["woe"] 
        df_iv.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_iv    
    
    @classmethod
    def ks(self, df_ks, dist_A_label, dist_B_label, cumsum_label="_cumsum"):
        dist_A_cumsum = df_ks[dist_A_label].cumsum()
        dist_B_cumsum = df_ks[dist_B_label].cumsum()
        dist_A_label_cumsum = dist_A_label+cumsum_label
        dist_B_label_cumsum = dist_B_label+cumsum_label
        df_ks[dist_A_label_cumsum] = dist_A_cumsum
        df_ks[dist_B_label_cumsum] = dist_B_cumsum
        df_ks["diff"] = np.abs(df_ks[dist_A_label_cumsum] - df_ks[dist_B_label_cumsum])
        df_ks.replace([np.inf, -np.inf], np.nan, inplace=True)
        return df_ks