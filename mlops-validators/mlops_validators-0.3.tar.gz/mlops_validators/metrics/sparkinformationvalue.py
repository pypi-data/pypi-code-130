from mlops_validators.tables import SparkValidationTable
from mlops_validators.metrics import SparkTwoDistMetrics
import pyspark.sql.functions as f

class SparkInformationValue(SparkValidationTable):  
    
    def __init__(self, 
                 df,
                 feature,
                 target,
                 pos_value = "1",
                 neg_value = "0",
                 **kwargs):                
        super().__init__(df, feature, feature_B=target, feature_B_remove_missing=True, **kwargs)    
        if not isinstance(pos_value, str):
            raise ValueError("The pos_value must be a string.")
        if not isinstance(neg_value, str):
            raise ValueError("The neg_value must be a string.")        
        self.pos_value = pos_value
        self.neg_value = neg_value        
        self.df_iv = None    
    
    def get_iv_table(self, minimal_table=True):
        if minimal_table:
            pos_label = self.map_cross_columns_p[self.pos_value]
            neg_label = self.map_cross_columns_p[self.neg_value]
            return self.df_iv.select([self._cross_feature_name, pos_label, neg_label, "rr", "woe", "iv"])
        else:
            return self.df_iv    
    
    def get_total_iv(self):           
        return self.df_iv.agg(f.sum("iv").alias("total_iv"))
    
    def fit(self, **kwargs):
        super().fit(calculate_proportions=True, **kwargs)        
        pos_label = self.map_cross_columns_p[self.pos_value]
        neg_label = self.map_cross_columns_p[self.neg_value]        
        self.df_iv = SparkTwoDistMetrics.iv(self.cross_tbl, pos_label, neg_label)     
        return self 