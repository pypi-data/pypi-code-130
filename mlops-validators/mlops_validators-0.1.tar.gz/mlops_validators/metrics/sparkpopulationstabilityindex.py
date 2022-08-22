from mlops_validators.tables import SparkTrainValidationTable
from mlops_validators.metrics import SparkTwoDistMetrics
import pyspark.sql.functions as f

class SparkPopulationStabilityIndex(SparkTrainValidationTable):
  
    def __init__(self,
                 df_train,
                 df_validation,
                 feature,                 
                 **kwargs):
        super().__init__(df_train, df_validation, feature, **kwargs)    
        self.df_psi = None
    
    def get_psi_table(self, minimal_table=True):
        if minimal_table:
            train_label, validation_label = self.get_values_cross_columns_p()
            return self.df_psi.select([self._cross_feature_name, train_label, validation_label, "psi"])
        else:
            return self.df_psi
    
    def get_total_psi(self):         
        return self.df_psi.agg(f.sum("psi").alias("total_psi"))
    
    def fit(self, **kwargs):
        super().fit(calculate_proportions=True, **kwargs)      
        train_label, validation_label = self.get_values_cross_columns_p()
        self.df_psi = SparkTwoDistMetrics.psi(self.train_validation_table, train_label, validation_label)         
        return self