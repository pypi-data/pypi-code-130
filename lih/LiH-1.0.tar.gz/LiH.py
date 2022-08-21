# ------------------------------------------------------------------------------
#                         猩猩自定义数学建模数据题模块
# ------------------------------------------------------------------------------
#
#                         模块作者：      谈欣
#                         模块名称：      LiH.py
#                         更新时间：      2022/8/19
#                         联系方式：      1792733991
#
# ------------------------------------------------------------------------------

from scipy.stats import ttest_ind, levene, kstest, ttest_1samp, ttest_rel, mannwhitneyu, wilcoxon
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score, KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


# -----------------------------------------------------------------------------
#                             第一部分：数据探索
# -----------------------------------------------------------------------------


def detection(dataset, cls, a_label):
    # 回归模型
    if cls == 0:
        print(dataset.head(10))
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print("行：%s , 列：%s" % dataset.shape)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.describe())
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.dtypes)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

    # 分类模型
    else:
        print("行：%s , 列：%s" % dataset.shape)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.head(10))
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.describe())
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.dtypes)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        print(dataset.groupby(a_label).size())
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

    x = "输出完毕"
    return x


# ------------------------------------------------------------------------------
#                            第二部分：数据处理部分
# ------------------------------------------------------------------------------

# 定义转换函数：用于将极小型特征或中间型特征转换成极大型特征，方便评价模型的建立
def transform(data, a, model):
    b = np.array(data)

    # 极小型特征处理
    if model == "min":
        x = np.max(b)
        for i in range(0, b.shape[0]):
            b[i] = x - b[i]

    # 中间型特征处理
    if model == "middle":
        x = np.max(np.abs(b - a))
        for i in range(0, b.shape[0]):
            b[i] = 1 - np.abs(b[i] - a) / x

    return b


# 数据标准化或归一化函数
def standardization(x, model):
    # 数据归一化
    if model == 0:
        x_minmax = MinMaxScaler()  # 初始化x的归一
        x_minmax.fit(x)
        y = x_minmax.transform(x)  # 归一化x
    # 数据标准化
    else:
        zscore = StandardScaler()
        y = zscore.fit_transform(x)
    return y


# 数据标准化或归一化后的复原
def inverse(x, model):
    # 数据反归一化
    if model == 0:
        x_minmax = MinMaxScaler()  # 初始化x的归一
        x_minmax.fit(x)
        z = x_minmax.inverse_transform(x)  # x 反归一化
    # 数据反标准化
    else:
        zscore = StandardScaler()
        z = zscore.inverse_transform(x)
    return z


# 数据降维函数（主成分分析）
def demension(data, num):
    # Dummy化（必须删去数据集自带序号）
    x = pd.get_dummies(data)
    # 数据标准化方法之一：中心化
    zscore = StandardScaler()
    x = zscore.fit_transform(x)
    pca = PCA(n_components=num, copy=True,
              whiten=True, svd_solver='auto', tol=0.0, iterated_power='auto', random_state=1)
    pca = pca.fit(x)  # 拟合模型
    x_dr = pca.transform(x)  # 获取新矩阵
    return x_dr


# 数据清洗函数
def clean(data, clas, min_num, max_num):
    # 数值型特征补全
    if clas == "shuzhi":
        # 此特征用的是中位数填补缺失值
        data.fillna(data.median(), inplace=True)
        print(data.isnull().sum())

    # 分类型特征补全
    if clas == "fenlei":
        # 这些特征用的是众数填补缺失值
        data.fillna(data.mode()[0], inplace=True)
        print(data.isnull().sum())

    # 离散数据处理
    if clas == "liqun":
        data.loc[max_num < data, '交易额'] = max_num
        data.loc[min_num > data, '交易额'] = min_num

    return data


# -----------------------------------------------------------------------------
#                         第三部分：数据可视化部分
# -----------------------------------------------------------------------------

'''直方图, 箱线图'''
'''此函数常用于数据可视化中对数值特征的分析'''


def shuzhi(data, name):
    sns.set()
    sns.set_style('ticks')
    plt.figure(figsize=(12, 8))
    plt.subplot(121)
    data[name].hist(bins=80)
    plt.xlabel(name)
    plt.ylabel('Num')
    plt.subplot(122)
    data.boxplot(column=name, showfliers=True, showmeans=True)
    data[name].describe()
    plt.show()
    x = "作图完成"
    return x


'''直方图, 饼图'''
'''此函数常用于数据可视化中对分类标签的可视化'''


def label(data, name):
    plt.subplot(121)
    data[name].value_counts().plot.bar()
    plt.title(name)
    plt.subplot(122)
    train_survived = data[data[name].notnull()]
    sns.set_style('ticks')  # 十字叉
    plt.axis('equal')  # 行宽相同
    train_survived[name].value_counts().plot.pie(autopct='%1.2f%%')
    plt.show()
    x = "作图完成"
    return x


'''直方图'''
'''此函数常用于数据可视化中对分类特征、序数特征的分析'''


def fenlei(data, name):
    data[name].value_counts(normalize=True).plot.bar(figsize=(10, 8), title=name)
    plt.show()
    x = "作图完成"
    return x


def corr_plot(data, model, a_label, min_num):
    # 整体相关性分析
    if model == 0:
        corr = data.corr()
        # 绘制相关性热力图
        heatmap = plt.subplots(figsize=(30, 20))
        heatmap = sns.heatmap(corr, annot=True)
        plt.tight_layout()  # 将作出的图显示完整
        plt.show()

    # 针对标签的相关性分析
    if model == 1:
        corr = data.corr()
        corr = corr[a_label]
        corr[abs(corr) > min_num].sort_values().plot.bar()
        plt.tight_layout()  # 将作出的图显示完整
        plt.show()

    x = "相关性分析完成"
    return x


# -----------------------------------------------------------------------------
#                         第四部分：模型的评估与检验
# -----------------------------------------------------------------------------

# 参数检验（三种t检验函数）
def t_test(x, y, model, num):
    x = np.array(x)
    y = np.array(y)

    # 第一种：独立t检验
    if model == "duli":
        a, b = kstest(x, cdf="norm")  # 独立t检验首先要符合正态分布, p_value 大于 0.05 才可以继续
        c, d = kstest(y, cdf="norm")
        if b > 0.05 & d > 0.05:
            e, f = levene(x, y)  # 然后要通过方差齐性检验, p_value 大于 0.05 才可以继续
            if f > 0.05:
                g, h = ttest_ind(x, y)
                if h < 0.05:
                    print("拒绝原假设,存在差异性")
                    print(ttest_ind(x, y))
                else:
                    print("不能拒绝原假设,不存在差异性")
            else:
                g, h = ttest_ind(x, y, equal_var=False)
                if h < 0.05:
                    print("在未通过方差性检验的情况下拒绝原假设,存在差异性")
                    print(ttest_ind(x, y, equal_var=False))
                else:
                    print("不能拒绝原假设,不存在差异性")
        else:
            print("请移步非参数检验")

    # 第二种：单样本t检验
    if model == "danyangben":
        a, b = kstest(x, cdf="norm")  # 独立t检验首先要符合正态分布, p_value 大于 0.05 才可以继续
        if b > 0.05:
            c, d = ttest_1samp(a=x, popmean=num)  # 指定总体均值
            if d < 0.05:
                print("拒绝原假设,存在差异性")
                print(ttest_1samp(a=x, popmean=num))
            else:
                print("不能拒绝原假设,不存在差异性")
        else:
            print("请移步非参数检验")

    # 第三种：配对样本t检验
    if model == "peidui":
        a, b = kstest(y - x, cdf="norm")  # 独立t检验首先要符合正态分布, p_value 大于 0.05 才可以继续
        if b > 0.05:
            c, d = ttest_rel(x, y)  # 指定总体均值
            if d < 0.05:
                print("拒绝原假设,存在差异性")
                print(ttest_rel(x, y))
            else:
                print("不能拒绝原假设,不存在差异性")
        else:
            print("请移步非参数检验")

    result = "检验正常完成"
    return result


# 非参数检验:
def test_w(x, y, model):
    x = np.array(x)
    y = np.array(y)

    # 独立样本 Mann-Whitney 秩和检验
    if model == "Maan":
        a, b = mannwhitneyu(x, y)
        if b < 0.05:
            print("拒绝原假设,存在差异性")
            print(mannwhitneyu(x, y))
        else:
            print("不能拒绝原假设,不存在差异性")

    # 配对样本或单样本 Wilcoxon 符号秩检验
    if model == "Wilcon":
        a, b = wilcoxon(x, y, correction=True)
        if b < 0.05:
            print("拒绝原假设,存在差异性")
            print(mannwhitneyu(x, y))
        else:
            print("不能拒绝原假设,不存在差异性")

    z = "检验正常完成"
    return z


# 分类、回归模型评价
def model_val(y_pred, y_test, model):
    # 分类模型
    if model == 0:
        print("模型准确率为:\n", accuracy_score(y_test, y_pred))
        print("混淆矩阵为:\n", confusion_matrix(y_test, y_pred))
        print("评估数据结果打印:\n", classification_report(y_test, y_pred))

    # 回归模型
    else:
        print("方差解释分:")
        explained_variance_score(y_test, y_pred, multioutput='raw_values')
        print("平均绝对误差:")
        mean_absolute_error(y_test, y_pred)
        print("均方误差:")
        mean_squared_error(y_test, y_pred)
        print("R方")
        r2_score(y_test, y_pred)

    x = "评价结果打印完毕"
    return x


# 分类器集成voting
def best_clas(x, y):
    models = {}
    models["LR"] = LogisticRegression(max_iter=1000)
    models["LDA"] = LinearDiscriminantAnalysis()
    models["KNN"] = KNeighborsClassifier()
    models["CART"] = DecisionTreeClassifier()
    models["NB"] = GaussianNB()
    models["SVM"] = SVC()
    results = []
    for key in models:
        kfold = KFold(n_splits=10, random_state=5, shuffle=True)
        cv_results = cross_val_score(models[key], x, y, cv=kfold, scoring="accuracy")
        results.append(cv_results)
        print("%s:%f(%f)" % (key, cv_results.mean(), cv_results.std()))

    x = "投票完成"
    return x
