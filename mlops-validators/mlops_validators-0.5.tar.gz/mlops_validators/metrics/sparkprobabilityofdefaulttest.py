from mlops_validators.tables import SparkTrainValidationTable
from mlops_validators.metrics import SparkTwoDistMetrics

class SparkProbabilityOfDefaultTest(SparkTrainValidationTable):
    
    def __init__(self,
                 df_train,
                 df_validation,
                 feature,
                 target,          
                 target_value = "1",                                                          
                 dist_prob = 0.95,                 
                 **kwargs):                           
        super().__init__(df_train, df_validation, feature, target=target, feature_B_remove_missing=True, **kwargs)          
        if not isinstance(target_value, str):
            raise ValueError("The target_value must be a string.")
        if not isinstance(dist_prob, float):
            raise ValueError("The dist_prob must be a float.")            
        self.target_value = target_value
        self.dist_prob = dist_prob                
        self.df_pd = None        
    
    def get_pd_table(self, minimal_table=True):        
        if minimal_table:            
            pd_train_label = self.map_cross_columns_r[self.target_value]
            pd_validation_label = self.validation_table.map_cross_columns_r[self.target_value]   
            return self.df_pd.select([self._cross_feature_name, pd_train_label, pd_validation_label, "pd_result"])
        else: 
            return self.df_pd        
    
    def fit(self, **kwargs):
        super().fit(calculate_ratings=True, **kwargs)                            
        pd_train_label = self.map_cross_columns_r[self.target_value]
        pd_validation_label = self.validation_table.map_cross_columns_r[self.target_value]      
        self.df_pd = SparkTwoDistMetrics.pd_test(self.train_validation_table, pd_train_label, pd_validation_label, self.cross_columns_validation_total_label, dist_prob=self.dist_prob)       
        return self
 