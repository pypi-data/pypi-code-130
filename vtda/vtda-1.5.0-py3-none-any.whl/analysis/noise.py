# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 17:11:14 2021

@author: ZSL
"""
import numpy as np
import math
import time
import datetime
import pandas as pd
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
                                            )
import matplotlib.pyplot as plt
import matplotlib

#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False

def noise_level(y,
             weight='weight_noise_a_3785_2010',
             sample_rate=4096,
             fft_size = None,
             fft_len=None,
             window='hanning',
             cdxs=0.5,
             base=0.00002,
             n=1                       
             ):
    '''
    计算A声级函数
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    zweight : TYPE, optional
        计权曲线，默认为 #GB/T 3785.1-2010 曲线
    sample_rate : TYPE, optional
        采样点数，默认为4096，如果待计算数据为pd.Series格式，其中有采样频率信息，则优先采用其信息。
    fft_size : TYPE, optional
        分析点数，默认为采样点数，即分析窗长为1秒
    fft_len : TYPE, optional
        分析长度，默认为1秒  其和分析点数功能相同，输入一个即可，分析长度优先级高于分析点数
    window : TYPE, optional
        加窗，默认为汉宁窗
    cdxs : TYPE, optional
        重叠系数，默认为0.5

    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的Z振级

    '''
    if weight=='weight_noise_a_3785_2010': 
        frec=[10,20000]       
    elif weight==None:
        frec='all' #频率为None 表示全部频率都计算 
    else:
        print('计权因子输入错误，请修正')    
    a,b=base_level(  y=y,
                     weight=weight,
                     base=base,
                     sample_rate=sample_rate,
                     fft_size = fft_size,
                     fft_len=fft_len,
                     window=window,
                     cdxs=cdxs,
                     frec=frec,
                     n=n
                     )
    return a,b


def frequency_noise_level(y, 
                        sample_rate=4096,
                        fft_size = None,
                        fft_len=None,
                        weight='weight_noise_a_3785_2010',
                        base=0.00002,                    
                        window='hanning',
                        cdxs=0.5,
                        n=1 #保留结果小数点后位数
                        ):
    '''
    计算分频振级函数，当计权曲线为None时为1/3倍频程计算
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    zweight : TYPE, optional
        计权曲线，默认为None
    sample_rate : TYPE, optional
        采样点数，默认为4096，如果待计算数据为pd.Series格式，其中有采样频率信息，则优先采用其信息。
    fft_size : TYPE, optional
        分析点数，默认为采样点数，即分析窗长为1秒
    window : TYPE, optional
        加窗，默认为汉宁窗
    cdxs : TYPE, optional
        重叠系数，默认为0.5
    frec : TYPE, optional
        计权频率的范围，默认为[4,200],表示只计算4-200Hz的频率内的能量
    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的Z振级

    '''
    if weight=='weight_noise_a_3785_2010':
        frec=[16,200]
    elif weight==None:
        frec='all' #频率为None 表示全部频率都计算 
    else:
        print('计权因子输入错误，请修正')   
#    if frec=='all' and weight==None:
#        weight=[0]*100 
#    elif frec=='all' and weight!=None:
#        weight=weight_factor(weight=weight)
#    elif frec!='all' and weight==None:
#        weight=[0]*100
#    elif frec!='all' and weight!=None:       
#        weight=weight_factor(weight=weight,frec=frec)     
    
    a,b=base_level(  y=y,
                     weight=weight,
                     base=base,
                     sample_rate=sample_rate,
                     fft_size = fft_size,
                     fft_len=fft_len,
                     window=window,
                     cdxs=cdxs,
                     frec=frec,
                     n=n
                     )
    return a,b


def batch_noise_level(data,
                          info,
                          name,
                          dir_,
                          cdxs=0.75,
                          weight='weight_noise_a_3785_2010',
                          base=0.00002,
                          window='hanning',
                          fft_len=None,
                          n=1,
                          num_shiyan='all',
                          num_tongdao='all',
                          ):
    '''
    Parameters
    ----------
    data : TYPE, optional
        数据文件. The default is None.
    info : TYPE, optional
        数据信息. The default is None.
    name : TYPE, optional
        文件名，不要加试验号. The default is None.
    dir_ : TYPE, optional
        路径. The default is None.        
    cdxs : TYPE, optional
        重叠系数. The default is 0.75.
    weight : TYPE, optional
        计权曲线. The default is 'weight_noise_a_3785_2010'.        
    base : TYPE, optional
        基准能量值. The default is 0.00002.         
    num_shiyan : TYPE, optional
        要计算的试验号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.
    num_tongdao : TYPE, optional
        要计算的通道号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.        
    Returns
    -------
    None.

    '''
    if isinstance(num_shiyan, list):
        print('试验号格式输入错误，请输入str格式')
        return None,None
    elif isinstance(num_shiyan, str) and num_shiyan!='all':
        num_shiyan=fix_num(num_shiyan)
        data_={}
        for i in data:
            pass
            if i in num_shiyan:
                data_[i]=data[i]
        data=data_
    if isinstance(num_tongdao, list):
        print('通道号格式输入错误，请输入str格式')
        return None,None
    elif isinstance(num_tongdao, str) and num_tongdao!='all':
        num_tongdao=fix_num(num_tongdao)  
        data_={}
        for i in data:
            pass
            data_[i]={}
            for j in data[i]:
                if j in num_tongdao:
                    data_[i][j]=data[i][j]
        data=data_        

    res_vlz_detail={}
    res_vlz_summarize={}    
    for i in tqdm(data,desc='正在计算A声级（环境噪声、车内噪声）'):
        pass
        df=data[i]
        info_=info[i]
        res_vlz_detail_=[]
        columns_=[]
        res_vlz_summarize_=[['平均数','最小值','25%分位数','50%分位数','75%分位数','最大值']]       
        for j in df:
            pass
            time_,vlz=noise_level(df[j],
                                     sample_rate=float(info_[j]['采样频率']),
                                     fft_size = float(info_[j]['采样频率']),
                                     weight=weight,
                                     base=base,
                                     fft_len=fft_len,
                                     cdxs=cdxs,
                                     window=window,
                                     )
            
            if len(res_vlz_detail_)==0: #第一次需要把频率加上
                res_vlz_detail_.append(time_)
            columns_.append(j)
            res_vlz_detail_.append(vlz)
            res_vlz_summarize_.append([np.array(vlz).mean(),
                                      np.array(vlz).min(),
                                      np.percentile(np.array(vlz),25),
                                      np.percentile(np.array(vlz),50),
                                      np.percentile(np.array(vlz),75),                                      
                                      np.array(vlz).max()])        
        try:  
            ls1=pd.DataFrame(res_vlz_detail_).T.set_index(0)  
            ls1.columns=columns_
            res_vlz_detail[i]=ls1
            ls2=pd.DataFrame(res_vlz_summarize_).T.set_index(0) 
            ls2.columns=columns_
            res_vlz_summarize[i]=ls2
            
        except:
            print("{} 试验号：{}，计算A声级错误。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),i))             

    res_vlz_summary=pd.DataFrame()
    ls_num=[]
    res_vlz_summarize_={}
    for i in res_vlz_summarize:
        pass           
        res_vlz_summarize_[i]=res_vlz_summarize[i]

    for i in res_vlz_summarize_:
        pass
        ls_num.append(int(i)) 
        res_vlz_summary=pd.concat([res_vlz_summary,res_vlz_summarize_[i].iloc[[-1],:]],axis=0)
    res_vlz_summary=pd.concat([res_vlz_summary,pd.DataFrame(res_vlz_summary.min()).T],axis=0)
    res_vlz_summary=pd.concat([res_vlz_summary,pd.DataFrame(res_vlz_summary.max()).T],axis=0)
    res_vlz_summary=pd.concat([res_vlz_summary,pd.DataFrame(res_vlz_summary.mean().apply(lambda x:round(x,1))).T],axis=0)

    num_shiyan_start=min(ls_num)
    num_shiyan_end=max(ls_num)    
    ls_num.append('最小值')
    ls_num.append('最大值')
    ls_num.append('平均值')
    res_vlz_summary['试验号']=ls_num
    res_vlz_summary=res_vlz_summary.set_index('试验号')

   
    with pd.ExcelWriter(dir_+'/res_A声级汇总('+str(num_shiyan_start)+'-'+str(num_shiyan_end)+')-'+name+'.xlsx') as writer:
        res_vlz_summary.to_excel(writer, sheet_name='Z振级汇总')  
    with pd.ExcelWriter(dir_+'/res_A声级详细('+str(num_shiyan_start)+'-'+str(num_shiyan_end)+')-'+name+'.xlsx') as writer:
        for i in res_vlz_detail:
            res_vlz_detail[i].to_excel(writer, sheet_name=str(i))        

def batch_noise_level_ssd(data,
                          info,
                          name,
                          dir_,
                          #cdxs=0.75, #不包含重叠系数，此处应该为全部数据求一次倍频程  而不是算每一秒然后重叠
                          weight='weight_noise_a_3785_2010',
                          base=0.00002,
                          window='hanning',
                          n=1,
                          cdxs=0,
                          num_shiyan='all',
                          num_tongdao='all',
                          ):
    '''
    Parameters
    ----------
    data : TYPE, optional
        数据文件. The default is None.
    info : TYPE, optional
        数据信息. The default is None.
    name : TYPE, optional
        文件名，不要加试验号. The default is None.
    dir_ : TYPE, optional
        路径. The default is None.        
    cdxs : TYPE, optional
        重叠系数. The default is 0.75.
    weight : TYPE, optional
        计权曲线. The default is 'weight_noise_a_3785_2010'.        
    base : TYPE, optional
        基准能量值. The default is 0.00002.         
    num_shiyan : TYPE, optional
        要计算的试验号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.
    num_tongdao : TYPE, optional
        要计算的通道号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.        
    Returns
    -------
    None.

    '''
    if isinstance(num_shiyan, list):
        print('试验号格式输入错误，请输入str格式')
        return None,None
    elif isinstance(num_shiyan, str) and num_shiyan!='all':
        num_shiyan=fix_num(num_shiyan)
        data_={}
        for i in data:
            pass
            if i in num_shiyan:
                data_[i]=data[i]
        data=data_
    if isinstance(num_tongdao, list):
        print('通道号格式输入错误，请输入str格式')
        return None,None
    elif isinstance(num_tongdao, str) and num_tongdao!='all':
        num_tongdao=fix_num(num_tongdao)  
        data_={}
        for i in data:
            pass
            data_[i]={}
            for j in data[i]:
                if j in num_tongdao:
                    data_[i][j]=data[i][j]
        data=data_        

    res_nla_detail={}
    res_nla_summarize={} 
    res_nla_time=[]    
               
    for i in tqdm(data,desc='正在计算A声级（二次结构噪声）'):
        pass
        df=data[i]
        info_=info[i]
        res_nla_detail_=[]
        columns_=[]
        y=df[list(df.keys())[0]] #此处为兼容第一个通道号不是1的情况 采用动态第一个关键值
        start,end=find_start_end(y,
                               sample_rate=float(info_[list(df.keys())[0]]['采样频率']),
                               fft_size=float(info_[list(df.keys())[0]]['采样频率']),
                               window='hanning',
                               cdxs=0.75,
                                ) 
        start_=start*(1-0.75)
        end_=end*(1-0.75)
        res_nla_time.append([i,start_,end_,(end_-start_)])          
        res_nla_summarize_=[['平均数','最小值','25%分位数','50%分位数','75%分位数','最大值']]       
        for j in df:
            pass
            sample_rate=float(info[i][j]['采样频率'])
            y=df[j][int(start_*sample_rate):int(end_*sample_rate+1)]
            res_frec,nla=frequency_noise_level(y=y, 
                                                    sample_rate=sample_rate,
                                                    fft_size=len(y),
                                                    weight=weight,                                                       
                                                    base=base,                    
                                                    window=window,
                                                    cdxs=cdxs,
                                                    n=n #保留结果小数点后位数
                                                    )            
            
            if len(res_nla_detail_)==0: #第一次需要把频率加上
                res_nla_detail_.append(res_frec)
            columns_.append(j)
            res_nla_detail_.append(nla)
            res_nla_summarize_.append([np.array(nla).mean(),
                                      np.array(nla).min(),
                                      np.percentile(np.array(nla),25),
                                      np.percentile(np.array(nla),50),
                                      np.percentile(np.array(nla),75),                                      
                                      np.array(nla).max()])        
        try:  
            ls1=pd.DataFrame(res_nla_detail_).T.set_index(0)  
            ls1.columns=columns_
            res_nla_detail[i]=ls1
            ls2=pd.DataFrame(res_nla_summarize_).T.set_index(0) 
            ls2.columns=columns_
            res_nla_summarize[i]=ls2
            
        except:
            print("{} 试验号：{}，计算A声级错误。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),i))             

    res_nla_summary=pd.DataFrame()
    ls_num=[]
    res_nla_summarize_={}
    for i in res_nla_summarize:
        pass           
        res_nla_summarize_[i]=res_nla_summarize[i]

    for i in res_nla_summarize_:
        pass
        ls_num.append(int(i)) 
        res_nla_summary=pd.concat([res_nla_summary,res_nla_summarize_[i].iloc[[-1],:]],axis=0)
    res_nla_summary=pd.concat([res_nla_summary,pd.DataFrame(res_nla_summary.min()).T],axis=0)
    res_nla_summary=pd.concat([res_nla_summary,pd.DataFrame(res_nla_summary.max()).T],axis=0)
    res_nla_summary=pd.concat([res_nla_summary,pd.DataFrame(res_nla_summary.mean().apply(lambda x:round(x,1))).T],axis=0)

    num_shiyan_start=min(ls_num)
    num_shiyan_end=max(ls_num)    
    ls_num.append('最小值')
    ls_num.append('最大值')
    ls_num.append('平均值')
    res_nla_summary['试验号']=ls_num
    res_nla_summary=res_nla_summary.set_index('试验号')

    res_nla_time=pd.DataFrame(res_nla_time)
    res_nla_time.columns=['实验号','开始时间','结束时间','持续时间']   
    res_nla_time=res_nla_time.set_index('实验号')
    res_nla_time=res_nla_time.sort_index()
    for i in res_nla_time.index:  #此处为兼容有时start大于end的工况
        pass
        if res_nla_time.loc[int(i),'开始时间']>res_nla_time.loc[int(i),'结束时间']:
           ls=res_nla_time.loc[int(i),'开始时间'] 
           res_nla_time.loc[int(i),'开始时间']=res_nla_time.loc[int(i),'结束时间']
           res_nla_time.loc[int(i),'结束时间']=ls
           res_nla_time.loc[int(i),'持续时间']=-res_nla_time.loc[int(i),'持续时间']
              
    with pd.ExcelWriter(dir_+'/res_A声级(二次结构噪声)汇总('+str(num_shiyan_start)+'-'+str(num_shiyan_end)+')-'+name+'.xlsx') as writer:
        res_nla_time.to_excel(writer, sheet_name='计算时间') 
        res_nla_summary.to_excel(writer, sheet_name='Z振级汇总')  
        
    #t2=time.time()
    #print("{} 计算Z振级完成，耗时{}秒。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),round((t2-t1),2)) )               
 
 

if __name__ == '__main__':
    
    pass