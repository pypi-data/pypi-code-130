#from configparser import Interpolation
import numpy as np
from prettytable import PrettyTable

# 众数
def mode(ln):
    ln = np.array(ln)
    return np.argmax(np.bincount(ln))

# 下四分位数
def low25(ln):
    ln = np.array(ln)
    return np.quantile(ln, 0.25, method = 'higher')

# 上四分位数
def up75(ln):
    ln = np.array(ln)
    return np.quantile(ln, 0.75, method = 'lower')

# 极差
def ran(ln):
    ln = np.array(ln)
    return np.max(ln) - np.min(ln)

# 四分位差
def iqr(ln):
    ln = np.array(ln)
    return up75(ln) - low25(ln)

# 异众比率
def diff_mode_rate(ln):
    ln = np.array(ln)
    return len(ln[np.argwhere(ln-mode(ln))])/len(ln)

# 平均绝对误差
def mae(ln):
    ln = np.array(ln)
    return np.mean(np.abs(ln - np.mean(ln)))

# 离散系数
def varia(ln):
    ln = np.array(ln)
    return np.std(ln)/np.mean(ln)

# 偏度系数
def skew(ln):
    ln = np.array(ln)
    n = len(ln)
    m = np.mean(ln)
    s = np.std(ln)
    return (n*np.sum((ln-m)**3))/((n-1)*(n-2)*(s**3))

# 峰度系数
def kurt(ln):
    ln = np.array(ln)
    n = len(ln)
    m = np.mean(ln)
    s = np.std(ln)
    fz = n*(n+1)*np.sum((ln-m)**4) - 3*(np.sum((ln-m)**2))**2*(n-1)
    fm = (n-1)*(n-2)*(n-3)*s**4
    return fz/fm - 3

def des(ls):
    ln = np.array(ls)
    lmean = np.mean(ln) # 均值
    lmode = mode(ln) # 众数
    lmedian = np.median(ln) # 中位数
    lmax = np.max(ln) # 最大值
    lmin = np.min(ln) # 最小值
    llwq = low25(ln) # 下四分位数
    lupq = up75(ln) # 上四分位数
    lvar = np.var(ln) # 方差
    lstd = np.std(ln) # 标准差
    lr = ran(ln) # 极差
    liqr = iqr(ln) # 四分位差
    lrat = diff_mode_rate(ln) # 异众比率
    lad = mae(ln) # 平均差
    lvia = varia(ln) # 离散系数
    lskew = skew(ln) # 偏度系数
    lkurt = kurt(ln) # 峰度系数
    tb1 = PrettyTable(['均值','众数','中位数','最大值','最小值','上四分位数','下四分位数'])
    tb1.add_row([lmean, lmode, lmedian, lmax, lmin, lupq, llwq])
    tb2 = PrettyTable(['标准差','方差','极差','四分位差','异众比率','平均差','离散系数'])
    tb2.add_row([lstd, lvar, lr, liqr, lrat, lad, lvia])
    tb3 = PrettyTable(['峰度系数','偏度系数'])
    tb3.add_row([lkurt, lskew])
    print('描述性统计分析：\n','*'*110)
    print('集中趋势：\n', tb1, '\n离散程度：\n', tb2, '\n分布形状：\n', tb3)
    print('*'*110)
