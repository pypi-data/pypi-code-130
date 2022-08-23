# !/usr/bin python3                                 
# encoding    : utf-8 -*-                            
# @author     :   hmh                               
# @software   : PyCharm      
# @file       :   step3_similarity_calculation.py.py
# @Time       :   2022/8/22 14:27
import pandas as pd
import jieba

# 计算jaccard系数
def Jaccrad(model, reference):  # terms_reference为源句子，terms_model为候选句子
    terms_reference = jieba.cut(reference)  # 默认精准模式
    terms_model = jieba.cut(model)
    grams_reference = set(terms_reference)  # 去重；如果不需要就改为list
    grams_model = set(terms_model)
    temp = 0
    for i in grams_reference:
        if i in grams_model:
            temp = temp + 1
    fenmu = len(grams_model) + len(grams_reference) - temp  # 并集
    jaccard_coefficient = float(temp / fenmu)  # 交集
    return jaccard_coefficient

# #计算文本相似度
# data = pd.read_excel(r'D:\desktop\crm_8-24时剩余告警\crm3\8-24时CRM3级警告数据剩余告警_有序.xlsx')       #读取Excel
# idList, keyList, FtimeList = data['id'], data['key'], data['Ftime']
# ids, keys, Ftimes, jaccard_coefficient = [], [], [], []
# for index in range(len(idList)-1):
#     text_a = '%s' % (keyList[index])  # 文本1
#     text_b = '%s' % (keyList[index+1])  # 文本2
#     jaccard_coefficient = Jaccrad(text_a, text_b)
#     #print(jaccard_coefficient)
#     index = index + 1
#     # value = " ".join(jaccard_coefficient)
#     # data['jaccard_coefficient'] = jaccard_coefficient
#     # types = pd.DataFrame(jaccard_coefficient)
#     # data.to_excel(r'D:/Desktop/values.xlsx', index=False)
