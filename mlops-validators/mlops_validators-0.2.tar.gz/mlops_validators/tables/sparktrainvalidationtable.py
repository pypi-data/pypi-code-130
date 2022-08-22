from mlops_validators.tables import SparkValidationTable

class SparkTrainValidationTable(SparkValidationTable):
    
    def __init__(self,
                 df_train,
                 df_validation,
                 feature,
                 target = None,
                 cross_columns_train_label = "train_",
                 cross_columns_validation_label = "validation_",   
                 cross_columns_train_total_label = "train_total",
                 cross_columns_validation_total_label = "validation_total",
                 train_label_buckets_min = "_train_min",
                 train_label_buckets_max = "_train_max",                 
                 validation_label_buckets_min = "_validation_min",
                 validation_label_buckets_max = "_validation_max",
                 **kwargs):                   
        if cross_columns_train_label == cross_columns_validation_label:
            raise ValueError("The cross_columns_train_label can not be equal cross_columns_validation_label.")
        if cross_columns_train_total_label == cross_columns_validation_total_label:
            raise ValueError("The cross_columns_train_total_label can not be equal cross_columns_validation_total_label.")
        if not (feature in df_train.columns and feature in df_validation.columns):
            raise ValueError("The feature must be in df_train and df_validation DataFrames.")
        if isinstance(target, str):
            if not (target in df_train.columns and feature in df_validation.columns):
                raise ValueError("The target must be in df_train and df_validation DataFrames.")
        super().__init__(df_train, feature, feature_B=target, 
                         cross_columns_label=cross_columns_train_label, 
                         cross_columns_label_total=cross_columns_train_total_label, 
                         buckets_min_label=train_label_buckets_min,
                         buckets_max_label=train_label_buckets_max,
                         **kwargs)        
        self.validation_table = SparkValidationTable(df_validation, 
                                                     feature, feature_B=target, 
                                                     cross_columns_label=cross_columns_validation_label,
                                                     cross_columns_label_total=cross_columns_validation_total_label,
                                                     buckets_min_label=validation_label_buckets_min,
                                                     buckets_max_label=validation_label_buckets_max,
                                                     **kwargs)        
        self.cross_columns_train_label = cross_columns_train_label
        self.cross_columns_validation_label = cross_columns_validation_label
        self.cross_columns_train_total_label = cross_columns_train_total_label
        self.cross_columns_validation_total_label = cross_columns_validation_total_label
        self.validation_cross_tbl = None         
        self.train_validation_table = None  

    def __merge_maps(self, map_one, map_two):
        keys = map_one.keys() | map_two.keys()
        merged_maps = {col: map_one.get(col,[]) + map_two.get(col,[]) for key in keys}
        return merged_maps

    def get_cross_tbl(self):
        return self.train_validation_table
    
    def get_map_cross_columns(self):
        return self.__merge_maps(self.map_cross_columns, self.validation_table.map_cross_columns)

    def get_values_cross_columns(self):
        return super().get_values_cross_columns() + self.validation_table.get_values_cross_columns()

    def get_map_cross_columns_r(self):
        return self.__merge_maps(self.map_cross_columns_r, self.validation_table.map_cross_columns_r)

    def get_values_cross_columns_r(self):
        labels = super().get_values_cross_columns_r() + self.validation_table.get_values_cross_columns_r()
        return labels

    def get_map_cross_columns_p(self):
        return self.__merge_maps(self.map_cross_columns_p, self.validation_table.map_cross_columns_p)

    def get_values_cross_columns_p(self):
        labels = super().get_values_cross_columns_p() + self.validation_table.get_values_cross_columns_p()
        return labels
    
    def fit(self, **kwargs):
        super().fit(**kwargs)                           
        self.validation_cross_tbl = self.validation_table.fit(**kwargs).get_cross_tbl()               
        select_train_columns = [self.cross_tbl[col] for col in self.cross_tbl.columns]
        select_valid_columns = [self.validation_cross_tbl[col] for col in self.validation_cross_tbl.columns if col != self._cross_feature_name]
        select_columns = select_train_columns + select_valid_columns                
        key = self.cross_tbl[self._cross_feature_name] == self.validation_cross_tbl[self._cross_feature_name]            
        self.train_validation_table = self.cross_tbl.join(self.validation_cross_tbl, key, how="fullouter").select(select_columns)        
        self.train_validation_table = self.train_validation_table.sort(self._cross_feature_name) 
        return self