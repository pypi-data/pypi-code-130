# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 15:23:51 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""
#测试
#%%
from toolkit.graph import graph

test_score_lst_dic={'English': [90, 81, 73, 97, 85, 60, 74, 64, 72, 67, 87, 78, 85, 96, 77, 100, 92, 86], 
                    'Chinese': [71, 90, 79, 70, 67, 66, 60, 83, 57, 85, 93, 89, 78, 74, 65, 78, 53, 80], 
                    'history': [73, 61, 74, 47, 49, 87, 69, 65, 36, 7, 53, 100, 57, 45, 56, 34, 37, 70], 
                    'biology': [59, 73, 47, 38, 63, 56, 75, 53, 80, 50, 41, 62, 44, 26, 91, 35, 53, 68]}
_=graph.boxplot_custom(test_score_lst_dic,
               figsize=(15,10),
               fontsize=23,
               frameOn=['bottom','left'],
               xlabel='subject',
               ylabel='score',
               labelsize='30',
               tick_color='r',
               notch=1,
               sym='rs',
               whisker_linestyle='--',
               whisker_linewidth=5,
               median_linewidth=5
              )
#%%
test_EC_scores={'English': [90, 81, 73, 97, 85, 60, 74, 64, 72, 67, 87, 78, 85, 96, 77, 100, 92, 86], 
               'Chinese': [71, 90, 79, 70, 67, 66, 60, 83, 57, 85, 93, 89, 78, 74, 65, 78, 53, 80], }
test_names=['Mason', 'Reece', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
graph.four_quadrant_diagram(test_EC_scores,
                      # method='median',
                      figsize=(15,15),
                      fontsize=23,
                      frameOn=['bottom','left'],
                      labelsize='30',
                      dot_size=200,
                      annotation_fontsize=30,
                      annotation_lable=test_names,
                      ) 
#%%
from toolkit.utility.general_tools import flatten_lst

nested_lst=[['A','B',['C','D'],'E'],[6,[7,8,[9]]]]  
print(flatten_lst(nested_lst))  
#%%
from toolkit.utility.stats_tools import *

ranmen_price_lst=[700,850,600,650,980,750,500,890,880,700,890,720,680,650,790,670,680,900,880,720,850,700,780,850,750,
 80,590,650,580,750,800,550,750,700,600,800,800,880,790,790,780,600,690,680,650,890,930,650,777,700]
price_x=200.68    
price_x_closestValue=value2values_comparison(price_x,ranmen_price_lst)    
print(price_x_closestValue)
#------------------------------------------------------------------------------
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