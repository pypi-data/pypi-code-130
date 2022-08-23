# !/usr/bin python3                                 
# encoding    : utf-8 -*-                            
# @author     :   hmh                               
# @software   : PyCharm      
# @file       :   step4_Highlight_2min_0.8sim.py
# @Time       :   2022/8/22 15:02
import pandas as pd

#### 高亮
def highlight(f):
    if f['id'] in c_1['id'].values:
        return ['background-color: yellow;'] * len(f)
    elif f['id'] in c_2['id'].values:
        return ['background-color: red;'] * len(f)
    elif f['id'] in c_3['id'].values:
        return ['background-color: pink;'] * len(f)
    # if f['number'] in c_3['number'].values:
    #     return ['background-color: pink;'] * len(f)
    # elif f['id'] in c_2['id'].values:
    #     return ['background-color: red;'] * len(f)
    # elif f['id'] in c_1['id'].values:
    #     return ['background-color: yellow;'] * len(f)
    else:
        return [''] * len(f)

#筛选出时间差小于120s，相似度大于0.8的告警，返回对应(即index),标黄
df = pd.read_excel(r'D:\desktop\crm_8-24时剩余告警\crm3\8-24时CRM3级警告数据剩余告警_有序.xlsx')
a = df[['id']][(df['cha'] <= 120) & (df['jaccard_coefficient'] >= 0.8)]
a.to_excel(r'D:\desktop\id_2min_cong.xlsx', index=False)
#筛选出时间差小于24h，相似度大于0.8的告警（从），返回对应(即index)，标红
b = df[['id']][(df['cha'] <= 86400) & (df['jaccard_coefficient'] >= 0.8)]
b.to_excel(r'D:\desktop\id_86400_cong.xlsx', index=False)
#筛选出时间差小于24h，首次出现告警（主），标粉
c = df[['id']][(df['cha'] <= 86400) & (df['jaccard_coefficient'] >= 0.8)]-1
c.to_excel(r'D:\desktop\id_2min_zhu.xlsx', index=False)

c_1 = pd.read_excel(r'D:\desktop\id_2min_cong.xlsx')
c_2 = pd.read_excel(r'D:\desktop\id_86400_cong.xlsx')
c_3 = pd.read_excel(r'D:\desktop\id_2min_zhu.xlsx')
# f['id'] = [i for i in range(len(f))]
df.style.apply(highlight, axis=1).to_excel(r'D:\desktop\highlight.xlsx', index=False)