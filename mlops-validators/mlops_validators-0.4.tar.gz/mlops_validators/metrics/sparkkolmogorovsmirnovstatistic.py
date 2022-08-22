from mlops_validators.metrics import SparkTwoDistMetrics
from mlops_validators.tables import SparkValidationTable, SparkTrainValidationTable
import pyspark.sql.functions as f

class SparkKolmogorovSmirnovStatistic:
    
    def __init__(self,
                 df_validation,
                 feature,
                 df_train = None,                 
                 target = None,
                 cumsum_label = "_cumsum",                 
                 **kwargs):        
        self._target_validation = False              
        if target != None:            
            self._validation_table = SparkValidationTable(df_validation, feature, feature_B=target, feature_B_remove_missing=True, **kwargs)
            self._target_validation = True                   
        else:            
            self._validation_table = SparkTrainValidationTable(df_train, df_validation, feature, **kwargs)                        
        if not isinstance(cumsum_label, str):
            raise ValueError("The cumsum_label must be a string.")        
        self.cumsum_label = cumsum_label        
        self.df_ks = None

    def get_validation_table(self):        
        return self._validation_table
    
    def get_ks_table(self, minimal_table=True):
        if minimal_table:
            dist_labels = self._validation_table.get_values_cross_columns_p()                                     
            dist_A_label, dist_B_label = dist_labels[0], dist_labels[1]
            return self.df_ks.select([self._validation_table._cross_feature_name, dist_A_label, dist_B_label, "diff"])
        else:
            return self.df_ks
        
    def get_statistics(self):           
        return self.df_ks.agg(f.max("diff").alias("ks_statistics"))      
    
    def fit(self, **kwargs):
        self._validation_table.fit(calculate_proportions=True, **kwargs)        
        dist_labels = self._validation_table.get_values_cross_columns_p()                                     
        dist_A_label, dist_B_label = dist_labels[0], dist_labels[1]
        self.df_ks = SparkTwoDistMetrics.ks(self._validation_table.get_cross_tbl(), dist_A_label, dist_B_label, cumsum_label=self.cumsum_label)                
        return self