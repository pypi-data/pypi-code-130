# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 20:16:41 2021

@author: Administrator
"""

import vtda
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False


from vtda import  (read_dasp_data, #读取dasp数据
                  batch_sperling)  #批量平稳性

dir_='E:/20200620磁各庄实验室/6科研/平稳性/'#目录 注意目录之间需要用 '/' 而不是 '\'
name='北京地铁19号线车辆平稳性测试'#文件名 注意文件名不要带试验号
#读取dasp数据
data,info=vtda.read_dasp_data(name,dir_=dir_,num_shiyan='1',num_tongdao='all')
#选择要计算的通道号,如果把所有通道全部读取了之后，需要挑选某个通道
y=vtda.select_data(data,num_tongdao='1-4') #'1,2,3-6'的格式
#通道号对应的方向
direction=['垂','横','垂','横','垂','横']
batch_sperling(y, 
                sample_rate=5000, #采样频率
                len_=20,  #分析窗长 单位：秒
                window='rect', #窗函数  rect  hanning
                interval=1, #每隔1秒出一个数
                direction=direction, #各通道方向 垂、横
                unit='m/ss',#g
                dir_=dir_,#储存文件目录
                name=name
                )
