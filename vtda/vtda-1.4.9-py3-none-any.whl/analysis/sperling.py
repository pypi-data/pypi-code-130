# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 23:24:12 2021

@author: Administrator
"""

import numpy as np
import math
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from vtda.util.util import weight_factor
import os
#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False
from tqdm import tqdm
from vtda.util.util import (
                                               weight_factor,
                                               fix_num,
                                               find_start_end
                                            )
from vtda.analysis.base import (               choose_windows,
                                               fft,
                                               octave_3,
                                               base_level,
                                               rms_time,
                                               rms_frec,
                                               lvbo_low
                                            )

def sperling(y, 
            sample_rate=4096,
            len_=5,
            window='hanning',
            cdxs=0.8,
            direction='vertical', #horizontal
            unit='m/ss',#g

            ):
    '''
    计算平稳性函数
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    sample_rate : TYPE, optional
        采样点数，默认为4096，如果待计算数据为pd.Series格式，其中有采样频率信息，则优先采用其信息。
    len : TYPE, optional
        分析长度，默认为5秒
    window : TYPE, optional
        加窗，默认为汉宁窗
    cdxs : TYPE, optional
        重叠系数，默认为0
    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的平稳性 如果有速度和里程信息的话，会在第三列和第四列

    '''

    if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
        sample_rate=1/(y.index[1]-y.index[0])
        y=y.fillna(0)
        y=np.array(y)        
    elif isinstance(y, np.ndarray):
        pass
    else:
        print("{} 错误数据输入格式。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))             
    
    if unit=='m/ss':
        pass
    elif unit=='g':
        y=y*9.8
    xishu=3.57    
    fft_size=len_*sample_rate   #此处的size 功能是分段，大概分几段计算  20s情况后边在计算
    n_zong=max(math.ceil((len(y)-fft_size)/(round((1-cdxs),5)*fft_size))+1,1)#上取整
    res=np.zeros(int(fft_size/2))
    res_sperling=[]
    res_x=[]
    for i in tqdm(np.arange(n_zong),desc='正在计算平稳性'):
        pass
        #i=4
        if len_==20: #20s的情况 此处85版规范默认采样频率256Hz,最高分析到128Hz即可。 
            y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)] 
            if len(y_): 
                if len(y_)<len_*sample_rate:
                    li=[]
                    for i in range(10):
                        y__=y_[:sample_rate*2]
                        if len(y__)==sample_rate*2:
                            li.append(y__)
                            y_=y_[sample_rate*2:]
                else:
                    li=np.split(y_,10)
                for ii in li:
                    try:
                        res_x,res_y__=fft(ii,
                                         sample_rate=sample_rate,
                                         fft_size =fft_size/10,
                                         cdxs=0,
                                         fix_meth='能量修正',
                                         window=window,
                                         )
                    except:
                        pass
                    try:  
                        res_y_+=np.array(res_y__)
                    except:
                        #第一次没有平均值 
                        res_y_=np.array(res_y__)
                                                
                res_y_=[x/10 for x in res_y_]
                if direction in ['vertical','v','V','chui','chuixiang','垂','垂向']: #垂向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.9:
                            w_ls=xishu*math.pow((y_fft**3*0.325*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.9 and x_fft<20:
                            w_ls=xishu*math.pow((y_fft**3*400/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=20 and x_fft<=128:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)
                elif direction in ['horizontal','h','H','heng','hengxiang','横','横向']: #横向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.4:
                            w_ls=xishu*math.pow((y_fft**3*0.8*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.4 and x_fft<26:
                            w_ls=xishu*math.pow((y_fft**3*650/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=26 and x_fft<=128:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)            
                res_sperling.append(ww)      
        elif len_==2:#20s的情况 此处85版规范默认采样频率256Hz,最高分析到128Hz即可。
            y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)] 
            if len(y_):
                res_x,res_y_=fft(y_,
                                 sample_rate=sample_rate,
                                 fft_size =fft_size,
                                 cdxs=0,
                                 fix_meth='能量修正',
                                 window=window,
                                 )
    
                if direction in ['vertical','v','V','chui','chuixiang','垂','垂向']: #垂向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.9:
                            w_ls=xishu*math.pow((y_fft**3*0.325*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.9 and x_fft<20:
                            w_ls=xishu*math.pow((y_fft**3*400/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=20 and x_fft<=128:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)
                elif direction in ['horizontal','h','H','heng','hengxiang','横','横向']: #横向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.4:
                            w_ls=xishu*math.pow((y_fft**3*0.8*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.4 and x_fft<26:
                            w_ls=xishu*math.pow((y_fft**3*650/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=26 and x_fft<=128:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)            
    
                res_sperling.append(ww)
        else:#除去2s和20s的情况 此处2019版规范规定最高分析到40Hz。
            y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)] 
            if len(y_):
                res_x,res_y_=fft(y_,
                                 sample_rate=sample_rate,
                                 fft_size =fft_size,
                                 cdxs=0,
                                 fix_meth='能量修正',
                                 window=window,
                                 )
    
                if direction in ['vertical','v','V','chui','chuixiang','垂','垂向']: #垂向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.9:
                            w_ls=xishu*math.pow((y_fft**3*0.325*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.9 and x_fft<20:
                            w_ls=xishu*math.pow((y_fft**3*400/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=20 and x_fft<=40:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)
                elif direction in ['horizontal','h','H','heng','hengxiang','横','横向']: #横向
                    w=[]
                    for i in np.arange(len(res_x)):
                        pass
                        x_fft=res_x[i]
                        y_fft=res_y_[i]
                        if x_fft>=0.5 and x_fft<5.4:
                            w_ls=xishu*math.pow((y_fft**3*0.8*x_fft), 1/10)
                            w.append(w_ls)
                        elif x_fft>=5.4 and x_fft<26:
                            w_ls=xishu*math.pow((y_fft**3*650/(x_fft**3)), 1/10)
                            w.append(w_ls)    
                        elif x_fft>=26 and x_fft<=40:
                            w_ls=xishu*math.pow((y_fft**3/x_fft), 1/10)
                            w.append(w_ls)
                    ww=math.pow(sum([i**10 for i in w]), 1/10)            
    
                res_sperling.append(ww)
            
    ls=round(len_*(1-cdxs),2)
    ls_z=ls*(n_zong)+len_
    res_x=list(np.arange(len_,ls_z,ls))  
#    res_x.append((len(y_)/fft_size)*len_+len_*(n_zong-1))  #解决最后一个不整的问题
    return res_x,res_sperling


def select_data(data,num_shiyan='1',num_tongdao='1,2'):
    '''
    数据选择函数，从既有数据中选择特定数据，一般是只选择一个试验号下面的几个通道

    '''
    num_shiyan=fix_num(num_shiyan)
    num_tongdao=fix_num(num_tongdao)
    data_={}
    if len(num_shiyan)==1:
        data_=data[str(num_shiyan[0])]
        data__={}
        for i in num_tongdao:
            pass    
            data__[str(i)]=data_[str(i)] 
        return data__
    else:
        print('请输入单一试验号')
        return None
    
  
    
def batch_sperling(y, 
                sample_rate=5000, #采样频率
                len_=5,  #分析窗长 单位：秒
                window='rect', #窗函数  rect  hanning
                interval=1, #每隔1秒出一个数
                direction=['垂','横','垂','横','垂','横'], #各通道方向 垂、横
                unit='m/ss',#g
                dir_='/',#储存文件目录
                name='e',
                speed=None, #速度
                mileage=None,#里程 
                nn=300
                ):
    
    cdxs=(len_-interval)/len_
    res={}
    ii=0
    try:
        speed=lvbo_low(speed,fq=3,fs=sample_rate,n=1)     #低通3Hz滤波
    except:
        pass
    for i in y:
        pass
        nowtime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("{} 开始计算_{}通道_{}向_平稳性".format(
            nowtime,
            i,direction[ii]
            ))  
        time.sleep(0.88)           
        time_,spr=sperling(y[i], 
                    sample_rate=sample_rate, #采样频率
                    len_=len_,  #分析窗长 单位：秒
                    window=window, #窗函数  rect  hanning
                    cdxs=cdxs, #重叠系数
                    direction=direction[ii], #或者填横向  #数据方向
                    unit=unit,#g
                    )
        ii=ii+1
        if len(res)==0:
            res['time']=time_
            try:
                ls=[int(i)*sample_rate for i in time_]
                res['speed']=list(np.append(speed[np.array(ls[:-1]).astype(int)],mileage[-1]))
            except:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'没有输入速度信号，跳过计算。')
            try:
                ls=[int(i)*sample_rate for i in time_]
                res['mileage']=list(np.append(mileage[np.array(ls[:-1]).astype(int)],mileage[-1]) )
            except:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'没有输入里程信号，跳过计算。')

        res[i]=spr

    
    res=pd.DataFrame(res)
    col=list(res.columns)  
    try: 
        col.remove('time')
    except:
        pass
    try: 
        col.remove('speed')
    except:
        pass        
    try: 
        col.remove('mileage')
    except:
        pass  
    res_max={}
    for i in col:
        pass
        res_max[i]={}
        res_max[i]['最大值']=round(res[i].max(),2)
        try: 
            res_max[i]['速度']=round(res.loc[np.argmax(res[i]),'speed'],1)       
        except:
            pass
        try: 
            res_max[i]['里程']=round(res.loc[np.argmax(res[i]),'mileage'],3)  
        except:
            pass 
        try: 
            res_max[i]['时间']=res.loc[np.argmax(res[i]),'time']  
        except:
            pass         

    dir_pingwenxing=dir_+'/'+name+'_平稳性计算结果/'
    list_dir=[dir_pingwenxing]
    for i in list_dir:  
        pass          
        isExists=os.path.exists(i)
        if isExists:
            pass
        else:
            os.makedirs(i)


    #nn=200#图上共计点数
    try:
        res=res[res['speed']>2]  
    except:
        pass
    
    try:
        start=res['mileage'].values[0]
        end=res['mileage'].values[-1]
        long=np.array(res['mileage'])         
        short=np.linspace(start,end,nn)        
        res_loc=[]
        for i in short:
            pass
            idx = np.abs(long - i).argmin()
            res_loc.append(long.flat[idx]) 
        res2=res[res['mileage'].isin(res_loc)]             
    except:
        start=res['time'].values[0]
        end=res['time'].values[-1]
        long=np.array(res['time'])
        short=np.linspace(start,end,nn)    
        res_loc=[]
        for i in short:
            pass
            idx = np.abs(long - i).argmin()
            res_loc.append(long.flat[idx]) 
        res2=res[res['time'].isin(res_loc)]  
 
    #加上三个指标的最大值
    for i in col:
        pass
        max_=res.loc[res[i]==res[i].max(),:]
        res2=pd.concat([res2,max_],axis=0)
        
    res2=res2.drop_duplicates() 
    res2=res2.sort_index()
        
    font_size_label=13
    font_size_axis=13
    font_size_legend=13 
    s_size=10
    figsize=(8, 3.905) 
    ls_line=1.5  
    markersize=5      
    font={'size': 20,'color':'red'} 
    for i in col:
        pass
        plt.figure(figsize=figsize) 
        try: 
            x_=res2['mileage']
            plt.xlabel("里程（km）",fontdict={'size'   : font_size_label})  
        except:
            x_=res2['time']
            plt.xlabel("时间（S）",fontdict={'size'   : font_size_label})
        plt.ylabel( '平稳性',fontdict={'size'  : font_size_label}) 
        plt.grid(b='True',linestyle="dashed",linewidth=1) 
        #plt.title(str(i)+'位移',fontsize=font_size_axis)
        plt.axhline(2.5,color = "g",linewidth = '2')
        plt.axhline(2.75,color = "b",linewidth = '2')
        plt.axhline(3,color = "r",linewidth = '2')
        plt.ylim(0,3.02)
        
        #plt.text(loc1, 0.85, '限值', fontdict=font)       
        plt.scatter(x_,res2[i], s=s_size,label='平稳性') 
        #plt.legend(loc ="best",fontsize=font_size_legend)#,title=str(i)+str(lab))    
        plt.savefig(dir_pingwenxing+'/'+i+'_平稳性.png', dpi=200)                  
                
    res_max=pd.DataFrame(res_max).T  
    with pd.ExcelWriter(dir_pingwenxing+datetime.datetime.now().strftime("%Y-%m-%d")+name+'_vtda平稳性计算结果_'+str(len_)+'S.xlsx') as writer:
        res.to_excel(writer, sheet_name='详细')  
        res_max.to_excel(writer, sheet_name='汇总')      
    print("{} 平稳性储存完成。".format(nowtime)) 


