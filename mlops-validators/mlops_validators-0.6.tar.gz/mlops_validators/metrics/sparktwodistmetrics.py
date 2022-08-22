import sys
import pyspark.sql.functions as f
from pyspark.sql.window import Window
from scipy.stats import norm

class SparkTwoDistMetrics:
    
    @classmethod
    def kl_div(self, df_kl_div, dist_A_label, dist_B_label):
        df_kl_div = df_kl_div.withColumn("kl_div", f.col(dist_B_label) *
                                                    f.log(f.col(dist_B_label) / f.col(dist_A_label)))
        return df_kl_div

    @classmethod
    def psi(self, df_psi, dist_A_label, dist_B_label):
        df_psi = df_psi.withColumn("psi", (f.col(dist_B_label) - f.col(dist_A_label)) *
                                              f.log(f.col(dist_B_label) / f.col(dist_A_label)))
        return df_psi
        
    @classmethod
    def chi2(self, df_chi2, dist_A_label, dist_B_label):
        df_chi2 = df_chi2.withColumn("chi2", f.pow(f.col(dist_B_label)-f.col(dist_A_label), 2) / 
                                             f.col(dist_A_label)) 
        return df_chi2    
    
    @classmethod
    def pd_test(self, df_pd, dist_A_label, dist_B_label, dist_B_total_label, dist_prob=0.95):
        inv_norm = norm.ppf(dist_prob)        
        df_pd = df_pd.withColumn("std", f.sqrt(f.col(dist_A_label) * (1-f.col(dist_A_label))) / f.col(dist_B_total_label))
        df_pd = df_pd.withColumn("interval", inv_norm * f.col("std"))
        df_pd = df_pd.withColumn("pd_lower_band", f.col(dist_A_label) - f.col("interval"))
        df_pd = df_pd.withColumn("pd_upper_band", f.col(dist_A_label) + f.col("interval"))  
        df_pd = df_pd.withColumn("pd_result", f.when(f.col(dist_B_label).between(f.col("pd_lower_band"), f.col("pd_upper_band")), "ok")
                                               .when(f.col(dist_B_label) < f.col("pd_lower_band"), "underestimated")
                                               .when(f.col(dist_B_label) > f.col("pd_upper_band"), "overestimated")
                                               .otherwise("undefined"))
        return df_pd
    
    @classmethod
    def iv(self, df_iv, dist_P_label, dist_N_label):
        df_iv = df_iv.withColumn("rr", f.col(dist_P_label) / f.col(dist_N_label))    
        df_iv = df_iv.withColumn("woe", f.log(f.col("rr")))
        df_iv = df_iv.withColumn("iv", (f.col(dist_P_label) - f.col(dist_N_label)) * f.col("woe")) 
        return df_iv    
    
    @classmethod
    def ks(self, df_ks, dist_A_label, dist_B_label, cumsum_label="_cumsum"):
        dist_A_cumsum = f.sum(df_ks[dist_A_label]).over(Window.partitionBy().orderBy().rowsBetween(-sys.maxsize, 0))
        dist_B_cumsum = f.sum(df_ks[dist_B_label]).over(Window.partitionBy().orderBy().rowsBetween(-sys.maxsize, 0))
        dist_A_label_cumsum = dist_A_label+cumsum_label
        dist_B_label_cumsum = dist_B_label+cumsum_label
        df_ks = df_ks.withColumn(dist_A_label_cumsum, dist_A_cumsum)
        df_ks = df_ks.withColumn(dist_B_label_cumsum, dist_B_cumsum)
        df_ks = df_ks.withColumn("diff", f.abs(f.col(dist_A_label_cumsum)-f.col(dist_B_label_cumsum)))
        return df_ks