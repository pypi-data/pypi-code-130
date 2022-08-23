# -*- coding: utf-8 -*-

'''
频繁项集挖掘数据集和算法研究资料参考：
	http://fimi.uantwerpen.be/
	http://fimi.uantwerpen.be/data/
	http://fimi.uantwerpen.be/src/
'''


import pandas as pd

from utils_hoo.utils_datsci.Apriori import get_CkSupFreqLk_all as get_FreqSet_Apriori

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules


def genRules(FreqSets, setSups, minConf=0.7):
    '''
    生成关联规则并计算置信度和提升度
    FreqSets: list，所有频繁项集列表。
    setSups: dict，项集支持度，FreqSets中的所有元素必须出现在setSups的keys中。
    （注：输入参数FreqSets和setSups格式同Apriori.get_CkSupFreqSets函数的输出）
    '''

    # 构建可能的规则
    nakeRules = []
    subFreSets = []
    for FreqSet in FreqSets:
        for subFreSet in subFreSets:
            if subFreSet.issubset(FreqSet):
                rule = (FreqSet-subFreSet, subFreSet)
                if rule not in nakeRules:
                    nakeRules.append(rule)
        subFreSets.append(FreqSet)

    # 以最小置信度为条件筛选规则
    Rules = []
    for preSet, postSet in nakeRules:
        Sup = setSups[preSet | postSet]
        preSup = setSups[preSet]
        Conf = Sup / preSup
        if Conf > minConf:
            postSup = setSups[postSet]
            Lift = Conf / postSup
            Rules.append((preSet, postSet, preSup, postSup, Sup, Conf, Lift))

    return Rules


def Apriori_hoo(dataSet, minSup, minConf):
    '''
    Apriori主函数
    dataSet为数据集，list格式，每个元素为一个样本（由不同项组成的事务）
    minSup, minConf分别为最小支持度和最小置信度阈值
    返回list格式规则列表Rules，每条规则包含：
        [前件, 后件, 前件支持度, 后件支持度, 支持度, 置信度, 提升度]
    '''

    FreqLk_all, CkSup_all = get_FreqSet_Apriori(dataSet, minSup)
    FreqSets = [y for x in FreqLk_all for y in x ]
    Rules = genRules(FreqSets, CkSup_all, minConf)

    return Rules


def Rules2df(Rules, joiner='&'):
    '''
    将列表格式Rules（genRules函数的输出格式）转存为pd.DataFrame格式，
    joiner设置项集元素之间的文本连接符
    '''

    dfRules = []
    for preSet, postSet, preSup, postSup, Sup, Conf, Lift in Rules:
        preSet = (' ' + joiner + ' ').join([str(x) for x in list(preSet)])
        postSet = (' ' + joiner + ' ').join([str(x) for x in list(postSet)])
        dfRules.append([preSet, postSet, preSup, postSup, Sup, Conf, Lift])

    dfRules = pd.DataFrame(dfRules)
    dfRules.columns = ['前件', '后件', '前件支持度', '后件支持度', '支持度',
                       '置信度', '提升度']

    dfRules.sort_values(['支持度', '置信度', '前件', '后件'],
                        ascending=[False, False, True, True], inplace=True)

    return dfRules


def Arpiori_mlx(dataSet, minSup, minConf, joiner='&'):
    '''
    调用mlxtend的Apriori算法实现关联规则挖掘
    dataSet为数据集，list格式，每个元素为一个样本（由不同项组成的事务）
    minSup, minConf分别为最小支持度和最小置信度阈值
    返回pd.DataFrame结果
    joiner设置项集元素之间的文本连接符
    '''

    tranEncoder = TransactionEncoder()
    dataAry = tranEncoder.fit(dataSet).transform(dataSet)
    df = pd.DataFrame(dataAry, columns=tranEncoder.columns_)
    FreqSets = apriori(df, min_support=minSup, use_colnames=True)
    Rules = association_rules(FreqSets, min_threshold=minConf)

    Rules['antecedents'] = Rules['antecedents'].apply(lambda x:
                        (' ' + joiner + ' ').join([str(y) for y in list(x)]))
    Rules['consequents'] = Rules['consequents'].apply(lambda x:
                        (' ' + joiner + ' ').join([str(y) for y in list(x)]))
    Rules.sort_values(['support', 'confidence', 'antecedents', 'consequents'],
                      ascending=[False, False, True, True], inplace=True)

    return Rules


def FpGrowth_mlx(dataSet, minSup, minConf, joiner='&'):
    '''
    调用mlxtend的FP-growth算法实现关联规则挖掘
    dataSet为数据集，list格式，每个元素为一个样本（由不同项组成的事务）
    minSup, minConf分别为最小支持度和最小置信度阈值
    返回pd.DataFrame结果
    joiner设置项集元素之间的文本连接符
    '''

    tranEncoder = TransactionEncoder()
    dataAry = tranEncoder.fit(dataSet).transform(dataSet)
    df = pd.DataFrame(dataAry, columns=tranEncoder.columns_)
    FreqSets = fpgrowth(df, min_support=minSup, use_colnames=True)
    Rules = association_rules(FreqSets, min_threshold=minConf)

    Rules['antecedents'] = Rules['antecedents'].apply(lambda x:
                        (' ' + joiner + ' ').join([str(y) for y in list(x)]))
    Rules['consequents'] = Rules['consequents'].apply(lambda x:
                        (' ' + joiner + ' ').join([str(y) for y in list(x)]))
    Rules.sort_values(['support', 'confidence', 'antecedents', 'consequents'],
                      ascending=[False, False, True, True], inplace=True)

    return Rules


if __name__ == '__main__':
    # test1 ------------------------------------------------------------------
    dataSet = [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]
    # dataSet = [['菜品2', '菜品4', '菜品3'], ['菜品1', '菜品5'], ['菜品1', '菜品4'],
    #            ['菜品2', '菜品1', '菜品4', '菜品5'], ['菜品2', '菜品1'],
    #            ['菜品1', '菜品4'], ['菜品2', '菜品1'],
    #            ['菜品2', '菜品1', '菜品4', '菜品3'], ['菜品2', '菜品1', '菜品4'],
    #            ['菜品2', '菜品4', '菜品3']]

    minSup = 0.3
    minConf = 0.5

    # Apriori
    RulesApriHoo = Apriori_hoo(dataSet, minSup, minConf)
    RulesApriHoodf = Rules2df(RulesApriHoo)

    # 使用mlxtend的算法
    RulesApri_mlx = Arpiori_mlx(dataSet, minSup, minConf)
    RulesFpGrow_mlx = FpGrowth_mlx(dataSet, minSup, minConf)


    # test2 ------------------------------------------------------------------
    import time
    from utils_hoo import load_text

    fpath = '../../../DataScience/dataSets/Frequent_Itemset_Mining_Dataset/T10I4D100K.dat'
    dataSet = load_text(fpath, sep=' ', keep_header=False, to_pd=False)

    minSup = 0.01
    minConf = 0.01

    # Apriori
    strt_tm = time.time()
    RulesApriHoo = Apriori_hoo(dataSet, minSup, minConf)
    RulesApriHoodf = Rules2df(RulesApriHoo)
    print('used {}s.'.format(round(time.time()-strt_tm, 6)))

    # 使用mlxtend的算法
    strt_tm = time.time()
    RulesApri_mlx = Arpiori_mlx(dataSet, minSup, minConf)
    print('used {}s.'.format(round(time.time()-strt_tm, 6)))

    strt_tm = time.time()
    RulesFpGrow_mlx = FpGrowth_mlx(dataSet, minSup, minConf)
    print('used {}s.'.format(round(time.time()-strt_tm, 6)))
