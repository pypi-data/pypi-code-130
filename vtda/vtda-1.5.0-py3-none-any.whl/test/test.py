# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 16:16:29 2021

@author: ZSL
"""

import vtda

dir(vtda)
dir_='D:/quant/git/vtda/vtda/test/test_data_dasp'
name='20210227南宁地铁2号线上行16+018啊'
a,b=vtda.read_dasp_data(name,dir_=dir_)
    
   

i=10
j=4
a,b=fft(data[i][j],sample_rate =float(info[i][j]['采样频率']),fft_size = float(info[i][j]['采样频率']),window='rect',cdxs=0.75,fix_meth='幅值修正',meth='线性平均')
plt.plot(a,b)  
a,b=octave_3(data[i][j],sample_rate =float(info[i][j]['采样频率']),fft_size = float(info[i][j]['采样频率']),window='rect',cdxs=0.75,meth='线性平均')

plt.figure(figsize=(15, 12))
plt.plot(a,b) 
plt.semilogx()

vl_zonethird=10**(np.array(b)[:20]*0.1)          
vl_z_=10*math.log10(sum(vl_zonethird)) 
y=data[i][j]
a,b=vl_z(data[i][j],sample_rate=float(info[i][j]['采样频率']),window='hanning',cdxs=0.75)    
plt.figure(figsize=(15, 12))
plt.plot(a,b)     
    
    
from vtda import  handle_vibration_data

dir_='E:/南宁地下数据'
name='20210227南宁地铁2号线上行16+018啊'  
handle_vibration_data(name=name,dir_=dir_)   



    import matplotlib.pyplot as plt
    import matplotlib    
    sample_rate=200
    t_s = 1/sample_rate
    t_start = 0
    t_end = 5
    t = np.arange(t_start, t_end, t_s)
    
    f0 = 5
    f1 = 20
    
    # generate the orignal signal
    y = 1.5*np.sin(2*np.pi*f0*t) + 3*np.sin(2*np.pi*f1*t) #+ np.random.randn(t.size)
    
    # fft
    res1=np.fft.fft(y_*choose_windows(name=window,N=len(y_),fix_meth=fix_meth))
    res1=np.abs(res1)
    res2=res1[range(int(len(res1)/2))]
    res3=res2/len(res2)
    res_x=np.linspace(0,sample_rate/2,int(len(res1)/2))
    
    a,b=fft(y,sample_rate =sample_rate,fft_size = sample_rate,window='rect',cdxs=0.75,fix_meth='幅值修正',meth='线性平均')
        
    
    plt.figure(figsize=(15, 12))
    plt.subplot(511)
    plt.plot(t,y)
    plt.subplot(512)
    plt.plot(res_x,res2)    
    plt.subplot(513)
    plt.plot(res_x,res3) 
    plt.subplot(514)
    plt.plot(a,fft_y[range(int(N/2))]) 
    plt.subplot(515)
    plt.plot(a,b)         