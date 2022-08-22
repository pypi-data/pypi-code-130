import sys
sys.path.append("D:\Programs\Python\Python39\Lib\site-packages\mpqml")
from My_machine_learning import *


#将要转换的txt文件放到地址位path的文件夹中
def changeTo_utf8(path):
    change_to_utf8('path')

def KS(X, y, test_size=0.2):
    X_train, X_test, y_train, y_test = ks(X, y, test_size)
    return X_train, X_test, y_train, y_test
def SPXY(x, y, test_size=0.2):
    X_train, X_test, y_train, y_test = spxy(X, y, test_size)
    return X_train, X_test, y_train, y_test


##############数据预处理################################
def plotSpectrum(spec, title='原始光谱', x=0, m=5):
    """
    :param spec: shape (n_samples, n_features)
    :return: plt
    """
    p = Pretreatment()
    plt = p.PlotSpectrum(spec, title, x, m)
    return plt

def mean_Centralization(sdata):
    """
    均值中心化
    """
    p = Pretreatment()
    new_data = p.mean_centralization(sdata)
    return new_data

def standardLize(sdata):
    """
    标准化
    """
    p = Pretreatment()
    new_data = p.standardlize(sdata)
    return new_data

def msC(sdata):
    p = Pretreatment()
    new_data = p.msc(sdata)
    return new_data

def De1(sdata):
    """
    一阶差分
    """
    p = Pretreatment()
    new_data = p.D1(sdata)
    return new_data
#
def De2(sdata):
    """
    二阶差分
    """
    p = Pretreatment()
    new_data = p.D2(sdata)
    return new_data
#
def snV(sdata):
    """
    标准正态变量变换
    """
    p = Pretreatment()
    new_data = p.snv(sdata)
    return new_data
#
def max_min_Normalization(sdata):
    """
    最大最小归一化
    """
    p = Pretreatment()
    new_data = p.max_min_normalization(sdata)
    return new_data
#
def vector_Normalization(sdata):
    """
    矢量归一化
    """
    p = Pretreatment()
    new_data = p.vector_normalization(sdata)
    return new_data
#
def sG(sdata):
    # eg:sg = p.sG(x, 4*5+1,2*3,2)
    """
    SG平滑
    待处理
    """
    p = Pretreatment()
    new_data = p.SG(sdata)
    return new_data

def wAVE(data_x):  # 小波变换
    p = Pretreatment()
    new_data = p.wave(data_x)
    return new_data

def move_Avg(data_x, n=15, mode="valid"):
    # 滑动平均滤波
    p = Pretreatment()
    new_data = p.move_avg(data_x,n,mode)
    return new_data
##############数据预处理################################

if __name__ == '__main__':
    # X = np.ones((10,10))
    # y = np.zeros((10,1))
    # X_train, X_test, y_train, y_test = KS(X,y)

    x = np.random.random((100,1000))
    # p = Pretreatment()
    # sg = p.SG(x, 4*5+1,2*3,2)
    # d1 = p.D1(x)
    plotSpectrum(x)
    x1 = sG(x)
    x2 = sG(x)
    plotSpectrum(x1,'1')
    plotSpectrum(x2,'2')
    plt.show()
    print("ok")