from functools import reduce
from operator import add
from pyspark.sql.window import Window
from pyspark.sql import DataFrame
import pyspark.sql.functions as f
import numpy as np

class SparkValidationTable:

    _comparators = {
        "right_closed_comparison" : lambda int1, int2, value: (value > int1, value <= int2),
        "left_closed_comparison" : lambda int1, int2, value: (value >= int1, value < int2),
        "open" : lambda int1, int2, value: (value > int1, value < int2),
        "closed" : lambda int1, int2, value: (value >= int1, value <= int2)
    }

    _comparators_str_rep = {
        "right_closed_comparison" : "a < x <= b, where x is the feature value and a is the first interval value and b the second.",
        "left_closed_comparison" : "a <= x < b, where x is the feature value and a is the first interval value and b the second.",
        "open" : "a < x < b, where x is the feature value and a is the first interval value and b the second.",
        "closed" : "a <= x <= b, where x is the feature value and a is the first interval value and b the second."
    }
    
    def __init__(self, 
                 df,
                 feature_A,
                 feature_B = None,
                 feature_A_remove_missing = False,
                 feature_B_remove_missing = False,
                 bins = False,
                 sort_buckets = True,
                 cross_columns_label = "value_",
                 cross_columns_label_p = "_proportion",
                 cross_columns_label_r = "_rating",
                 cross_columns_label_total = "total",
                 buckets_label = "buckets",
                 buckets_min_label = "_min",
                 buckets_max_label = "_max",
                 comparator = "right_closed_comparison"):
        
        if not isinstance(df, DataFrame):
            raise ValueError("The df must be a Spark DataFrame SQl instance.")
        else:
            self.df = df

        if not isinstance(feature_A, str):
            raise ValueError("The feature_A must be a string.")
        elif feature_A not in df.columns:
            raise ValueError("The feature_A must be a column of the DataFrame df.")
                
        if not isinstance(feature_A_remove_missing, bool):
            raise ValueError("The feature_A_remove_missing must be a bool.")
        self.feature_A_remove_missing = feature_A_remove_missing

        if self.feature_A_remove_missing:
            self.df = self.df.na.drop(subset=[feature_A]) if self.feature_A_remove_missing else self.df

        if not isinstance(feature_B_remove_missing, bool):
            raise ValueError("The feature_B_remove_missing must be a bool.")
        self.feature_B_remove_missing = feature_B_remove_missing

        if feature_B == None:
            self._feature_B = "feature_B_count"
            self.df = self.df.withColumn(self._feature_B, f.lit(1))
        elif isinstance(feature_B, str):
            if feature_B not in df.columns:
                raise ValueError("The feature_B must be a column of the DataFrame df.")
            self._feature_B = feature_B
            self.df = self.df.na.drop(subset=[feature_B]) if self.feature_B_remove_missing else self.df
        else:
            raise ValueError("The feature_B must be either a string or None.")                

        if isinstance(bins, int) and not isinstance(bins, bool):
            if bins < 1:
                raise ValueError("The bins must be either an integer (>1), a list or False.")
        elif not isinstance(bins, bool) and not isinstance(bins, list):            
            raise ValueError("The bins must be either an integer (>1), a list or False.")
        self.bins = bins

        #if isinstance(bins, list):            
            #self.buckets = np.arange(start=1, stop=len(bins))
        #elif not isinstance(bins, bool) and not isinstance(bins, int):
            #raise ValueError("The bins must be either an integer (>1), a list or False.")
        #elif not isinstance(bins, bool) and bins < 1:
            #raise ValueError("The bins must be either an integer (>1), a list or False.")
        #else:
            #self.buckets = None            
        #self.bins = bins
        
        if not isinstance(sort_buckets, bool):
            raise ValueError("The sort_buckets must be a bool.")

        if not isinstance(cross_columns_label, str):
            raise ValueError("The cross_columns_label must be a string.")
            
        if not isinstance(cross_columns_label_p, str):
            raise ValueError("The cross_columns_label_p must be a string.")
            
        if not isinstance(cross_columns_label_r, str):
            raise ValueError("The cross_columns_label_r must be a string.")
            
        if not isinstance(cross_columns_label_total, str):
            raise ValueError("The cross_columns_label_total must be a string.")
            
        if not isinstance(buckets_label, str):
            raise ValueError("The buckets_label must be a string.")
        
        if not isinstance(buckets_min_label, str):
            raise ValueError("The buckets_min_label must be a string.")
        
        if not isinstance(buckets_max_label, str):
            raise ValueError("The buckets_max_label must be a string.")

        if not comparator in self._comparators.keys():
            raise ValueError("The comparator must be one of the following values: {}.".format(self._comparators.keys()))
                
        self._feature_A = feature_A        
        self.feature_A = feature_A
        self.feature_B = feature_B
        self.bins = bins
        self.sort_buckets = sort_buckets
        self.cross_columns_label = cross_columns_label
        self.cross_columns_label_p = cross_columns_label_p
        self.cross_columns_label_r = cross_columns_label_r
        self.cross_columns_label_total = cross_columns_label_total
        self.buckets_label = buckets_label
        self.buckets_min_label = buckets_min_label
        self.buckets_max_label = buckets_max_label
        self.comparator = comparator        
        self.cross_tbl = None
        self.map_cross_columns = {}
        self.map_cross_columns_p = {}
        self.map_cross_columns_r = {}                        
        self._cross_feature_name = None    
    
    def __append_min_max(self, df_buckets, feature_A):        
        min_label = feature_A+self.buckets_min_label
        max_label = feature_A+self.buckets_max_label
        df_min_max = df_buckets.groupBy(feature_A).agg(f.min(self._feature_A).alias(min_label), 
                                                       f.max(self._feature_A).alias(max_label))        
        columns_select = self.cross_tbl.columns + [min_label, max_label]
        key = self.cross_tbl[self._cross_feature_name] == df_min_max[feature_A]
        self.cross_tbl = self.cross_tbl.join(df_min_max, key, how="left").select(columns_select)

    def __compile_cross_table(self, df_buckets, feature_A, feature_B):
        self.cross_tbl = df_buckets.crosstab(feature_A, feature_B)                 
        self._cross_feature_name = self.cross_tbl.columns[0]
        self.map_cross_columns = {col : self.cross_columns_label+col for col in self.cross_tbl.columns if col != self._cross_feature_name}
        for col in self.map_cross_columns:                 
            self.cross_tbl = self.cross_tbl.withColumnRenamed(col, self.map_cross_columns[col])         
        types = dict(df_buckets.dtypes) 
        self.cross_tbl = self.cross_tbl.withColumn(self._cross_feature_name, f.col(self._cross_feature_name).cast(types[feature_A]))
        if self.calculate_min_max_bins:
            self.__append_min_max(df_buckets, feature_A)
        if self.sort_buckets:
            self.cross_tbl = self.cross_tbl.sort(self.cross_tbl[self._cross_feature_name])
    
    def __compile_from_list_of_bins(self):
        intervals = self._comparators[self.comparator](self.bins[0], self.bins[1], self.df[self._feature_A]) 
        case = f.when((intervals[0] & intervals[1]), 1)
        for bucket in range(1, len(self.bins)-1):
            intervals = self._comparators[self.comparator](self.bins[bucket], self.bins[bucket+1], self.df[self._feature_A]) 
            case = case.when((intervals[0] & intervals[1]), bucket+1)        
        return self.df.withColumn(self.buckets_label, case).select([self.buckets_label, self._feature_A, self._feature_B])
    
    def __generate_table_from_list_of_bins(self):        
        df_buckets = self.__compile_from_list_of_bins()
        self.__compile_cross_table(df_buckets, self.buckets_label, self._feature_B)                
    
    def __generate_table_from_feature(self):
        df_buckets = self.df.select([self._feature_A, self._feature_B])        
        self.__compile_cross_table(df_buckets, self._feature_A, self._feature_B)
    
    def __compile_from_number_of_bins(self): 
        ntile = f.ntile(self.bins).over(Window.orderBy(f.col(self._feature_A)))
        query = self.df.select(f.when(f.col(self._feature_A).isNotNull(), ntile).alias(self.buckets_label), self._feature_A, self._feature_B)        
        return query
    
    def __generate_table_from_number_of_bins(self):
        df_buckets = self.__compile_from_number_of_bins()        
        self.__compile_cross_table(df_buckets, self.buckets_label, self._feature_B)
        
    def __calculate_proportions(self):        
        self.map_cross_columns_p = {col : self.cross_columns_label+col+self.cross_columns_label_p for col in self.map_cross_columns}
        for col in self.map_cross_columns:
            col_sum = self.cross_tbl.agg(f.sum(self.map_cross_columns[col])).first()[0]            
            self.cross_tbl = self.cross_tbl.withColumn(self.map_cross_columns_p[col], 
                                                       f.col(self.map_cross_columns[col]) / col_sum)                    
    
    def __calculate_totals(self):        
        self.cross_tbl = self.cross_tbl.withColumn(self.cross_columns_label_total, 
                                                   reduce(add, [f.col(self.map_cross_columns[col]) for col in self.map_cross_columns]))   
        self._has_calculated_totals = True

    def __calculate_ratings(self):
        self.__calculate_totals()
        self.map_cross_columns_r = {col : self.cross_columns_label+col+self.cross_columns_label_r for col in self.map_cross_columns}
        for col in self.map_cross_columns:
            self.cross_tbl = self.cross_tbl.withColumn(self.map_cross_columns_r[col], 
                                                       f.col(self.map_cross_columns[col]) / f.col(self.cross_columns_label_total))
    
    def get_values_cross_columns(self):
        return list(self.map_cross_columns.values())
            
    def get_map_cross_columns(self):
        return self.map_cross_columns
    
    def get_values_cross_columns_p(self):
        return list(self.map_cross_columns_p.values())
    
    def get_map_cross_columns_p(self):        
        return self.map_cross_columns_p
    
    def get_values_cross_columns_r(self):
        return list(self.map_cross_columns_r.values())
    
    def get_map_cross_columns_r(self):        
        return self.map_cross_columns_r        
    
    def get_comparator_str_rep(self):
        return self._comparators_str_rep[self.comparator]

    def get_cross_tbl(self):
        return self.cross_tbl

    def fit(self, calculate_proportions=False, calculate_totals=False, calculate_min_max_bins=False, calculate_ratings=False):
        if not isinstance(calculate_proportions, bool):
            raise ValueError("The calculate_proportions must be a bool.")
        if not isinstance(calculate_totals, bool):
            raise ValueError("The calculate_totals must be a bool.")
        if not isinstance(calculate_min_max_bins, bool):
            raise ValueError("The calculate_min_max_bins must be a bool.")
        if not isinstance(calculate_ratings, bool):
            raise ValueError("The calculate_ratings must be a bool.")
        self.calculate_min_max_bins = calculate_min_max_bins
        if isinstance(self.bins, list):
            self.__generate_table_from_list_of_bins()               
        elif isinstance(self.bins, bool):                                    
            self.__generate_table_from_feature()
        elif isinstance(self.bins, int):
            self.__generate_table_from_number_of_bins()
        if calculate_proportions:
            self.__calculate_proportions() 
        if calculate_totals:
            self.__calculate_totals()  
        if calculate_ratings:
            self.__calculate_ratings()
        return self