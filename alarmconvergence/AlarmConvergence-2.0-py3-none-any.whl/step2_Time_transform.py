# !/usr/bin python3                                 
# encoding    : utf-8 -*-                            
# @author     :   hmh                               
# @software   : PyCharm      
# @file       :   step2_Time_transform.py.py
# @Time       :   2022/8/22 11:29
import pandas as pd
import jieba.analyse
import time

#时间戳转换
def time_trans(data):
    idList,titleList,abstractList,ftimeList = data['id'],data['资源对象'],data['告警内容'],data['首次发生时间']
    ids, titles, keys, ftimes, ltimes = [], [], [], [], []
    for index in range(len(idList)):
        timeArray1 = time.strptime(ftimeList[index], "%Y-%m-%d %H:%M:%S")
        timestamp1 = time.mktime(timeArray1)
        print(timestamp1)
    return timestamp1
# data = pd.read_excel(r'D:\desktop\crm_8-24时剩余告警\crm3\8-24时CRM3级警告数据剩余告警_有序.xlsx')
# timestamp1 = time_trans(data)

#相邻告警时间差计算
def time_cha(data_1):
    # FtimeList, jaccard_coefficientList = data_1['Ftime'], data_1['jaccard_coefficient']
    cha = data_1['Ftime'].shift(-1) - data_1['Ftime']
    return cha
# data_1 = pd.read_excel(r'D:\desktop\crm_8-24时剩余告警\crm3\8-24时CRM3级警告数据剩余告警_有序.xlsx')
# cha = time_cha(data_1)
# cha.to_excel(r'D:/Desktop/cha.xlsx',index=False)