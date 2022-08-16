#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class Data_cleansing():
    """
    功能：数据清洗：
    一、数据查看
        1)展示数据缺失值、unique values、数值变量的平均值、字符变量的众数等： detect

    二、重复值处理，数据删除
        1）查看数据重复情况，并保留唯一数据：drop_duplicates
        2）删除只有唯一值或者只有空值和唯一值的列：drop_feature_single_unique_value
        3）删除指定列：drop_column

    三、缺失值处理
        1）默认删除所有缺失值的行，若指定 to_drop ，则删除指定列缺失值对应的所在行：drop_null
        2）用0填充缺失值：fillna_with_zero
        3）用均值填充缺失值：fillna_with_mean
        4）用中位数填充缺失值：fillna_with_median
        5）用众数填充缺失值：fillna_with_mode
        6）用随机森林算法填充缺失值：fillna_with_randomforest
        7）新增一列标记缺失值：sign_na 

    """
    
    def __init__(self, data):
        """
        :param data			需要空值处理的数据框

        """
        import toad         
        self.data = data

        
    def detect(self):
        """
        方法作用：
        1、展示数据缺失值、unique values、数值变量的平均值、离散值变量的众数等
        ==================================================================================
        :return:    无
        """
        display(toad.detect(self.data))
        
        
    def drop_duplicates(self):
        """
        方法作用：
        1、查看数据重复情况，并保留唯一数据
        ==================================================================================
        :return:    DataFrame, 处理后的数据
        """    
        duplicated = self.data.duplicated().sum()
        if duplicated == 0:
            print('数据无重复值')
        else:
            self.data.drop_duplicates(inplace=True) 
            self.data.reset_index(drop=True,inplace=True)
            print('数据共{}个重复值，已删并保留唯一值'.format(duplicated))
        return self.data
      

    def drop_feature_single_unique_value(self):
        """
        方法作用：
        1、删除只有唯一值或者只有空值和唯一值的列
        ==================================================================================
        :return:    DataFrame, 处理后的数据
        """                
        import pandas as pd
        cols = list(self.data.columns)
        del_cols = []
        for col in cols:
            unique_vals = list(self.data[col].unique())
            if len(unique_vals) == 1:
                del_cols.append(col)
            if len(unique_vals) == 2 and pd.isnull(unique_vals).any(): 
                del_cols.append(col)      
        if len(del_cols) != 0:  
            self.data.drop(del_cols,axis=1,inplace=True)
            print('已删除唯一值或者只有空值和唯一值的列:{}'.format(del_cols))
            return self.data
        else:
            print('没有唯一值或者只有空值和唯一值的列') 
            return self.data
    
    def drop_column(self,to_drop:list):
        """
        方法作用：
        1、删除指定列
        ==================================================================================
        :return:    DataFrame, 处理后的数据
        """      
        self.data.drop(to_drop,axis=1,inplace=True)
        print('{}列已删除'.format(to_drop)) 
        return self.data
    
    
    def drop_null(self,to_drop=None):
        """
        方法作用：
        1、默认删除所有缺失值的所在行
        2、若指定 to_drop ，则删除指定列缺失值对应的所在行
        
        ==================================================================================
        :param to_drop：list 或 None 
        :return:    DataFrame, 处理后的数据
        
        """
        if to_drop is None:
            self.data.dropna(axis=0, how='any',inplace=True)
            self.data.reset_index(drop=True,inplace=True)
            print('已删除所有缺失值行')
        else:
            self.data.dropna(axis=0, subset=to_drop, inplace=True) 
            self.data.reset_index(drop=True,inplace=True)
            print('已删除{}列缺失值行'.format(to_drop))
        return self.data
                 
            
    def fillna_with_zero(self, to_fill=None):
        """
        面向变量：所有变量
        方法作用：
        1、（默认方法）对所有变量，只要是空则用0填充
        2、如果只想对特定特征进行均值填充则指定to_fill参数，例如：to_fill=['age', ...]
        ==================================================================================
        :param to_fill:   str 或 list,   指定特征
        :return:    DataFrame, 处理后的数据
        """
        if to_fill is None:
            self.data.fillna(0, inplace=True)
            print('所有缺失值已用0填充')
        else:
            self.data[to_fill].fillna(0,inplace=True)
            print('{}列缺失值已用0填充'.format(to_fill))
        return self.data
       
        
    def fillna_with_mean(self, to_fill):
        """
        方法作用：
        1、对指定变量，用均值填充，例如：to_fill= 'col1'或 to_fill=['age', ...]
        ==================================================================================
        :param to_fill:   str 或 list,   指定特征
        :return:    DataFrame, 处理后的数据
        """ 
        self.data[to_fill].fillna(self.data["NumberOfDependents"].mean(),inplace=True) 
        print('{}列缺失值已用均值填充'.format(to_fill))
        return self.data

    
    def fillna_with_median(self, to_fill):
        """
        方法作用：
        1、对数值型变量，中位数填充缺失值
        2、如果只想对特定特征进行中位数填充则指定to_fill参数，例如：to_fill= 'col1'或 to_fill=['age', ...]
        ==================================================================================
        :param to_fill:   str 或 list,   指定特征
        :return:    DataFrame, 处理后的数据
        """          
        
        self.data[to_fill].fillna(self.data[to_fill].median(),inplace=True)
        print('{}列缺失值已用中位数填充'.format(to_fill))
        return self.data
            
        
    def fillna_with_mode(self, to_fill:str): 
        """
        方法作用：
        1、对指定列用众数填充缺失值
        ==================================================================================
        :param to_fill:   str ，指定特征
        :return:    DataFrame, 处理后的数据
        """     

        mode = self.data[to_fill].mode()
        if len(mode) == 1:
            self.data[to_fill].fillna(self.data[to_fill].mode()[0],inplace=True)
            print('{}列缺失值已用众数填充'.format(to_fill))
        else:
            print('{}列有多个众数:{}'.format(to_fill,mode))
            self.data[to_fill].fillna(self.data[to_fill].mode()[0],inplace=True)
            print('{}列缺失值已用第1个众数填充'.format(to_fill))
        return self.data

    
    def fillna_with_randomforest(self,to_fill:str):
        """
        方法作用：
        1、用随机森林算法填充缺失值,非缺失值的列作为X
        ==================================================================================
        :param to_fill:   str ，指定特征
        :return:    DataFrame, 处理后的数据
        """    
        from sklearn.ensemble import RandomForestRegressor as rfr
        df = self.data.copy()
        df = df.dropna(axis=1)
        df= pd.concat([df,self.data[to_fill]],axis=1)

        known = df[df[to_fill].notnull()]
        unknown = df[df[to_fill].isnull()]

        X_train = known.drop(to_fill,axis = 1)
        y_train = known[to_fill]

        X_test = unknown.drop(to_fill,axis = 1)

        rfr = rfr(n_estimators=100,random_state=420)
        rfr = rfr.fit(X_train, y_train)
        y_predict = rfr.predict(X_test)
        
        self.data.loc[(self.data[to_fill].isnull()), to_fill] = y_predict
        return self.data
         
        
    def sign_na(self,to_sign:str):
        """
        方法作用：
        新增加一列标记是否为缺失值:缺失标记为1 ，非空标记为0
        新增列的列名为：to_sign + '_if_null'
        ==================================================================================
        :param to_fill:   str ，指定特征
        :return:    DataFrame, 处理后的数据
        """
        self.data[to_sign + '_if_null'] = self.data[to_sign].isnull() * 1  
        print('已对{}列完成缺失值标记，新增{}列'.format(to_sign,to_sign + '_if_null'))
        return self.data


# In[ ]:





# In[ ]:





# In[ ]:




