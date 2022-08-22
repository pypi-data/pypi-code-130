from mlops_validators.tables import SparkTrainValidationTable
from mlops_validators.metrics import SparkTwoDistMetrics
import pyspark.sql.functions as f

class SparkKullbackLeiblerDivergence(SparkTrainValidationTable):
  
    def __init__(self,
                 df_train,
                 df_validation,
                 feature,       
                 shift_distributions=False,          
                 **kwargs):
        super().__init__(df_train, df_validation, feature, **kwargs)    
        if not isinstance(shift_distributions, bool):
            raise ValueError("The shift_distributions must be a bool.")
        self.shift_distributions = shift_distributions
        self.df_kl_div = None
    
    def get_kl_div_table(self, minimal_table=True):
        if minimal_table:
            train_label, validation_label = self.get_values_cross_columns_p()
            return self.df_kl_div.select([self._cross_feature_name, train_label, validation_label, "kl_div"])
        else:
            return self.df_kl_div
    
    def get_total_kl_div(self):         
        return self.df_kl_div.agg(f.sum("kl_div").alias("total_kl_div"))
    
    def fit(self, **kwargs):
        super().fit(calculate_proportions=True, **kwargs)      
        train_label, validation_label = self.get_values_cross_columns_p()
        if self.shift_distributions:
            train_label, validation_label = validation_label, train_label
        self.df_kl_div = SparkTwoDistMetrics.kl_div(self.train_validation_table, train_label, validation_label)         
        return self