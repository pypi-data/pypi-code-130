from mlops_validators.tables import SparkTrainValidationTable
from mlops_validators.metrics import SparkTwoDistMetrics
import matplotlib.pyplot as plt
import pyspark.sql.functions as f

class SparkChi2Statistic(SparkTrainValidationTable):
    
    def __init__(self,
                 df_train,
                 df_validation,
                 feature,                 
                 **kwargs):
        super().__init__(df_train, df_validation, feature, **kwargs)   

    @classmethod
    def print_formula(self):    
        formula = r'\chi^2 = \sum_{{i = 1}}^{{n}}\frac{{({0}^i-{1}^i)^2}}{{{0}^i}}'.format("x_{t}", "x_{v}")
        ax = plt.axes() 
        ax.set_xticks([])
        ax.set_yticks([])
        plt.text(0.3, 0.4,'$%s$' %formula, size=30);    

    def get_chi2_table(self, minimal_table=True):
        if minimal_table:
            train_label, validation_label = self.get_values_cross_columns_p()
            return self.df_chi2.select([self._cross_feature_name, train_label, validation_label, "chi2"])
        else:
            return self.df_chi2
    
    def get_statistics(self):                
        return self.df_chi2.agg(f.sum("chi2").alias("chi2_statistics"))
    
    def fit(self, **kwargs):
        super().fit(calculate_proportions=True, **kwargs)                                                       
        train_label, validation_label = self.get_values_cross_columns_p()        
        self.df_chi2 = SparkTwoDistMetrics.chi2(self.train_validation_table, train_label, validation_label)        
        return self  