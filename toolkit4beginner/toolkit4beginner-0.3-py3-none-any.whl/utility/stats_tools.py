# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 18:56:45 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""

def descriptive_statistics(data,measure=None,decimals=2):
    '''
    计算给定数值列表的描述性统计值，包括数量、均值、标准差、方差、中位数、众数、最小值和最大值。
    
    
    Parameters
    ----------
    data : list(numerical)
        待统计的数值列表.
    measure : str, optional
        包括：'count', 'mean', 'std', 'variance', 'median', 'mode', 'min', 'max'. The default is None.
    decimals : int, optional
        小数位数. The default is 2.

    Returns
    -------
    dict
        如果不给定参数measure，则以字典形式返回所有值；否则返回给定measure对应值的表述字符串.

    '''
    import statistics
    
    d_s={
        'count':len(data), #样本数
        'mean':round(statistics.mean(data),decimals), #均值
        'std':round(statistics.stdev(data),decimals), #标准差
        'variance': round(statistics.variance(data),decimals), #方差 
        'median':statistics.median(data), #中位数
        'mode':statistics.mode(data), #众数
        'min':min(data), #最小值
        'max':max(data), #最大值        
        }
    
    if measure:
        return '{}={}'.format(measure,d_s[measure])
    else:
        return d_s
    
def value2values_comparison(x,lst):
    '''
    判断给定的一个值是否在一个列表中，如果在，则返回给定值；如果不在，则返回列表中与其差值绝对值最小的值。

    Parameters
    ----------
    x : numerical
        数值.
    lst : list(numerical)
        用于寻找给定值的参考列表.

    Returns
    -------
    numerical
        列表中最接近给定值的值.

    '''
    import numpy as np
    
    lst_mean=np.mean(lst)
    abs_difference_func=lambda value:abs(x)
    comparisonOF2values=lambda v1,v2:print('x is higher than the average %s of the list.'%lst_mean) if v1>v2 else print('x is lower than the average %s of the list.'%lst_mean)    
        
    if x in lst:
        print("%s in the given list."%x)
        comparisonOF2values(x,lst_mean)   
        return x
    else:
        print('%.3f is not in the list.'%x)
        closest_value=min(lst,key=abs_difference_func)
        print('the nearest value to %s is %s.'%(x,closest_value))
        print("_"*50)
        comparisonOF2values(closest_value,lst_mean)    
        return closest_value
    
    
if __name__=='__main__':  
    #%%
    #A_测试-descriptive_statistics(data,measure=None,decimals=2)
    ranmen_price_lst=[700,850,600,650,980,750,500,890,880,
                     700,890,720,680,650,790,670,680,900,
                     880,720,850,700,780,850,750,780,590,
                     650,580,750,800,550,750,700,600,800,
                     800,880,790,790,780,600,690,680,650,
                     890,930,650,777,700]
    d_s_1=descriptive_statistics(ranmen_price_lst)
    print(d_s_1)
    print('--'*30)
    d_s_2=descriptive_statistics(ranmen_price_lst,'std')
    print(d_s_2)
    d_s_3=descriptive_statistics(ranmen_price_lst,measure='mean',decimals=1)
    print(d_s_3)
    #%%
    #B_测试-value2values_comparison(x,lst)
    ranmen_price_lst=[700,850,600,650,980,750,500,890,880,700,890,720,680,650,790,670,680,900,880,720,850,700,780,850,750,
     80,590,650,580,750,800,550,750,700,600,800,800,880,790,790,780,600,690,680,650,890,930,650,777,700]
    price_x=200.68    
    price_x_closestValue=value2values_comparison(price_x,ranmen_price_lst)    
    print(price_x_closestValue)
    #%%
