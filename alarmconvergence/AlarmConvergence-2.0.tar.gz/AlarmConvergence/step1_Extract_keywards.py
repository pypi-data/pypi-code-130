# !/usr/bin python3                                 
# encoding    : utf-8 -*-                            
# @author     :   hmh                               
# @software   : PyCharm      
# @file       :   step1_Extract_keywards.py
# @Time       :   2022/8/22 10:00
import pandas as pd
import jieba.analyse

# 处理标题和摘要，提取关键词。资源对象对应标题，告警内容对应摘要
def getKeywords_textrank(data,topK):
    idList,titleList,abstractList = data['id'],data['资源对象'],data['告警内容']
    ids, titles, keys = [], [], []
    for index in range(len(idList)):
        text = '%s。%s' % (titleList[index], abstractList[index]) # 拼接标题和摘要
        jieba.analyse.set_stop_words("data/stopWord.txt") # 加载自定义停用词表
        print("\"",titleList[index],"\"" , " 10 Keywords - TextRank :")
        keywords = jieba.analyse.textrank(text, topK=topK, allowPOS=('n','nz','v','vd','vn','l','a','d'))  # TextRank关键词提取，词性筛选
        word_split = " ".join(keywords)
        print(word_split)
        keys.append(word_split)
        #keys.append(word_split.encode("utf-8"))
        ids.append(idList[index])
        titles.append(titleList[index])

    result = pd.DataFrame({"id": ids, "title": titles, "key": keys}, columns=['id', 'title', 'key'])
    return result

#关键词提取
dataFile = (r'D:\desktop\crm_8-24时剩余告警\crm3\8-24时CRM3级警告数据剩余告警_有序.xlsx')
data = pd.read_excel(dataFile)
result = getKeywords_textrank(data, 10)
result.to_excel(r"D:\desktop\step1_Extract_keywards.xlsx", index=False)