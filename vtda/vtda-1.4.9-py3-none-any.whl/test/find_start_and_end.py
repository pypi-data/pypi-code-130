# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 09:49:24 2021

@author: ZSL
"""

import numpy as np
import math
import pandas as pd
import datetime 
import time 
import os
import re

from vtda.util.util import weight_factor
from vtda.analysis.vibration import vibration_level

from vtda.analysis.base import (               choose_windows,
                                               fft,
                                               octave_3,
                                               base_level,
                                               rms_time,
                                               rms_frec,
                                            )
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib
#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False

import vtda 
dir_='D:/quant/git/vtda/test_data_dasp'
name='20210227南宁地铁2号线上行16+018啊'
data,info=vtda.read_dasp_data(name,dir_=dir_)
i=10
j=5
y=data[i][j]


sample_rate=4096
fft_size= sample_rate
cdxs=0.75
n_zong=max(math.ceil((len(y)-fft_size)/((1-cdxs)*fft_size))+1,1)#上取整
res=np.zeros(int(fft_size/2))
vl_z=[]
vl_zonethirds2=[]
y_z=[]

for i in np.arange(n_zong):
    pass
    y_=y[int(i*(1-cdxs)*fft_size):int(i*(1-cdxs)*fft_size+fft_size)][:int(fft_size)] 
    if len(y_)>0:
        y_z.append(rms_time(y_))
        
        
aa=pd.DataFrame(y_z)
#aa.plot(figsize=(10, 7))
diff=aa.diff()
std=pd.Series.rolling(aa, 6).mean().diff().shift(-3)
plt.figure(figsize=(15, 12))
plt.subplot(311)

plt.plot(aa.index,aa[0])
plt.plot(aa.index,[np.percentile(np.array(y_z),75)]*len(aa.index))
plt.plot(aa.index,std*6)


plt.subplot(312)
plt.plot(diff.index,diff[0])
plt.subplot(313)
plt.plot(diff.index,STD(aa,5))

res_vlz_time=[]
for i in res_vlz_detail:
    pass
    aa=res_vlz_detail[i].diff()
    a=pd.DataFrame(aa.apply(lambda x: x[x==x.min()].index.values[0])).T
    min_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index'] 
    a=pd.DataFrame(aa.apply(lambda x: x[x==x.max()].index.values[0])).T
    max_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index']        
    res_vlz_time.append([i,max_,min_,(min_-max_)]) #最小值的时间在后面     
res_vlz_time=pd.DataFrame(res_vlz_time)
res_vlz_time.columns=['实验号','开始时间','结束时间','持续时间']   
res_vlz_time=res_vlz_time.set_index('实验号')
res_vlz_time=res_vlz_time.sort_index()
for i in res_vlz_time.index:
    pass
    if res_vlz_time.loc[int(i),'开始时间']>res_vlz_time.loc[int(i),'结束时间']:
       ls=res_vlz_time.loc[int(i),'开始时间'] 
       res_vlz_time.loc[int(i),'开始时间']=res_vlz_time.loc[int(i),'结束时间']
       res_vlz_time.loc[int(i),'结束时间']=ls
       res_vlz_time.loc[int(i),'持续时间']=-res_vlz_time.loc[int(i),'持续时间']