# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 16:59:57 2021

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
                                               rolling_octave_3
                                            )
import matplotlib.pyplot as plt
import matplotlib
#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False


def vibration_level(y, 
                    sample_rate=4096,
                    fft_size = None,
                    fft_len=None,
                    weight='weight_vibration_z_13441_1992',
                    base=0.000001, 
                    frec=None,
                    window='hanning',
                    cdxs=0.5,
                    n=1 #保留结果小数点后位数
                    ):
    '''
    计算振级函数,默认为Z振级
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    zweight : TYPE, optional
        计权曲线，默认为 #ISO2631/1-1985  / GB/T13341-1992 曲线
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
    frec : TYPE, optional
        计权频率的范围，默认为[1,80],表示只计算1-80Hz的频率内的能量
    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的Z振级

    '''
    if frec==None:
        pass
        if weight=='weight_vibration_z_13441_1992' : 
            frec=[1,80]
        elif weight=='weight_vibration_x_13441_1992' :
            frec=[1,80]
        elif weight=='weight_vibration_y_13441_1992': 
            frec=[1,80]        
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
    
def frequency_vibration_level(y, 
                                sample_rate=4096,
                                fft_size = None,
                                weight='weight_vibration_z_13441_2007',
                                base=0.000001, 
                                frec=None,
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
    if frec==None:
        if weight=='weight_vibration_z_13441_2007':
            frec=[4,200]
        elif weight=='weight_vibration_x_13441_2007':
            frec=[4,200]
        elif weight=='weight_vibration_y_13441_2007':
            frec=[4,200]        
        elif weight==None:
            frec='all' #频率为None 表示全部频率都计算 
        else:
            print('计权因子输入错误，请修正')
    weight=weight_factor(weight=weight,frec=frec)    
#    if frec=='all' and weight==None:
#        weight=[0]*100 
#    elif frec=='all' and weight!=None:
#        weight=weight_factor(weight=weight)
#    elif frec!='all' and weight==None:
#        weight=[0]*100
#    elif frec!='all' and weight!=None:       
#        weight=weight_factor(weight=weight,frec=frec)     
    
    res_x,onethird=octave_3(y,
                            sample_rate=sample_rate,
                            fft_size=fft_size,
                            window=window,
                            cdxs=cdxs,
                            meth='线性平均',
                            base=base,
                            res_type='db',
                            frec=frec, #输出频率
                            )

    if len(res_x)>=len(weight):
        onethird=onethird[:len(weight)]#zweight+[0]*(len(res_x)-len(zweight))
    else:
        weight=weight[:len(res_x)]#onethird+[0]*(len(weight)-len(res_x))
    onethird=np.around(np.array(weight)+np.array(onethird),n)   
    
    return res_x,onethird




def vl_zong_fft(y,sample_rate=4096,fft_size = 4096, window='hanning',cdxs=0.5):
    '''
    通过fft计算总极值和总有效值
    '''
    res_x,res_y_=fft(y,
                     sample_rate=sample_rate,
                     fft_size = len(y),
                     cdxs=cdxs,
                     fix_meth='能量修正',
                     window=window,
                     meth='线性平均')
    rms=np.sqrt(np.sum([ i*i for i in res_y_])/2)
    ls=20*math.log10(rms*1e6)
    # ls=10**(ls*0.1)
    # 10*math.log10(ls)
    return rms,ls

def batch_vibration_level(data,
                          info,
                          name,
                          dir_,
                          cdxs=0.75,
                          weight='weight_vibration_z_13441_1992',
                          base=0.000001,
                          frec=None,
                          window='hanning',
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
        计权曲线. The default is 'weight_vibration_z_13441_1992'.        
    base : TYPE, optional
        基准能量值. The default is 0.000001. 
    frec : TYPE, optional
        计权频率范围，也是参与计算数据的频率范围，超出频率的数据不参与计算. The default is [1,80].         
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
    #计算Z振级   
    #t1=time.time()
    #print("{} 正在计算Z振级。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))                
    for i in tqdm(data,desc='正在计算Z振级'):
        pass
        df=data[i]
        info_=info[i]
        res_vlz_detail_=[]
        columns_=[]
        res_vlz_summarize_=[['平均数','最小值','25%分位数','50%分位数','75%分位数','最大值']]       
        for j in df:
            pass
            time_,vlz=vibration_level(df[j],
                                     sample_rate=float(info_[j]['采样频率']),
                                     fft_size = float(info_[j]['采样频率']),
                                     weight=weight,
                                     frec=frec,
                                     base=base,
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
            print("{} 试验号：{}，计算Z振级错误。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),i))             

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

   
    with pd.ExcelWriter(dir_+'/res_Z振级汇总('+str(num_shiyan_start)+'-'+str(num_shiyan_end)+')-'+name+'.xlsx') as writer:
        res_vlz_summary.to_excel(writer, sheet_name='Z振级汇总')  
    with pd.ExcelWriter(dir_+'/res_Z振级详细('+str(num_shiyan_start)+'-'+str(num_shiyan_end)+')-'+name+'.xlsx') as writer:
        for i in res_vlz_detail:
            res_vlz_detail[i].to_excel(writer, sheet_name=str(i))        
    #t2=time.time()
    #print("{} 计算Z振级完成，耗时{}秒。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),round((t2-t1),2)) )               


def batch_frequency_vibration_level(data,
                                  info,
                                  name,
                                  dir_,
                                  cdxs=0.75,
                                  weight='weight_vibration_z_13441_2007',
                                  base=0.000001,
                                  n=1,
                                  window='hanning',
                                  num_shiyan='all',
                                  num_tongdao='all',
                                  ):
    '''
    批量计算倍频程/分频振级函数，
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
        计权曲线. The default is 'weight_vibration_z_13441_2007'.        
    base : TYPE, optional
        基准能量值. The default is 0.000001.         
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
    #计算倍频程/分频振级
    if weight==None:
        log='1_3倍频程'
    else:
        log='分频振级'
    t1=time.time()            
    res_octave_3={}  
    res_vlz_time=[]
    for i in tqdm(data,desc='正在计算'+log):
        pass
    
        df=data[i]
        info_=info[i]
        columns_=[]
        res_octave_3_=[]
        #选第一个通道来计算能量分布，通过能量分布来计算
        y=df[list(df.keys())[0]] #此处为兼容第一个通道号不是1的情况 采用动态第一个关键值
        start,end=find_start_end(y,
                               sample_rate=float(info_[list(df.keys())[0]]['采样频率']),
                               fft_size=float(info_[list(df.keys())[0]]['采样频率']),
                               window='hanning',
                               cdxs=0.75,
                                ) 
        start_=start*(1-0.75)
        end_=end*(1-0.75)
        res_vlz_time.append([i,start_,end_,(end_-start_)])       
        for j in df:
            pass
            sample_rate=float(info[i][j]['采样频率'])
            if weight==None:#计算1/3倍频程
                res_frec,octave_3_=frequency_vibration_level(df[j][int(start_*float(info[i][j]['采样频率'])):int(end_*float(info[i][j]['采样频率'])+1)], 
                                                        sample_rate=sample_rate,
                                                        fft_size =sample_rate,
                                                        weight=None,                                                       
                                                        base=base,                    
                                                        window=window,
                                                        cdxs=cdxs,
                                                        n=n #保留结果小数点后位数
                                                        ) 
            else:#计算分频振级
                res_frec,octave_3_=frequency_vibration_level(df[j][int(start_*float(info[i][j]['采样频率'])):int(end_*float(info[i][j]['采样频率'])+1)], 
                                                        sample_rate=sample_rate,
                                                        fft_size =sample_rate,
                                                        weight=weight,                                                       
                                                        base=base,                    
                                                        window=window,
                                                        cdxs=cdxs,
                                                        n=n #保留结果小数点后位数
                                                        )                

            if len(res_octave_3_)==0: #第一次需要把频率加上
                res_octave_3_.append(res_frec)
            res_octave_3_.append(octave_3_)
            columns_.append(j)
        try:
            ls1=pd.DataFrame(res_octave_3_).T.set_index(0)     
            ls1.columns=columns_          
            res_octave_3[i]=ls1   
        except:
            print("{} 计算倍频程错误。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))             
    
#    res_vlz_time=[]
#    for i in res_vlz_detail:
#        pass
#        aa=res_vlz_detail[i].diff()
#        a=pd.DataFrame(aa.apply(lambda x: x[x==x.min()].index.values[0])).T
#        min_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index'] 
#        a=pd.DataFrame(aa.apply(lambda x: x[x==x.max()].index.values[0])).T
#        max_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index']        
#        res_vlz_time.append([i,max_,min_,(min_-max_)]) #最小值的时间在后面     
    res_vlz_time=pd.DataFrame(res_vlz_time)
    res_vlz_time.columns=['实验号','开始时间','结束时间','持续时间']   
    res_vlz_time=res_vlz_time.set_index('实验号')
    res_vlz_time=res_vlz_time.sort_index()
    for i in res_vlz_time.index:  #此处为兼容有时start大于end的工况
        pass
        if res_vlz_time.loc[i,'开始时间']>res_vlz_time.loc[i,'结束时间']:
           ls=res_vlz_time.loc[i,'开始时间'] 
           res_vlz_time.loc[i,'开始时间']=res_vlz_time.loc[i,'结束时间']
           res_vlz_time.loc[i,'结束时间']=ls
           res_vlz_time.loc[i,'持续时间']=-res_vlz_time.loc[i,'持续时间']

   
    res_vlz_summarize_={}
    ls_num=[]
    res_frec_summary=pd.DataFrame()
    res_vlz_summarize_={}
    res_frec_summarize_={}    
    for i in res_octave_3:
        pass  
        ls_num.append(int(i))
        res_vlz_summarize_[i]=res_octave_3[i].max()     
        res_frec_summarize_[i]=res_octave_3[i].idxmax(axis=0)
        
    res_vlz_summary=pd.DataFrame(res_vlz_summarize_).T        
    res_frec_summary=pd.DataFrame(res_frec_summarize_).T        

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




    with pd.ExcelWriter(dir_+'/res_'+log+'汇总('+str(min(list(data.keys())))+'-'+str(max(list(data.keys())))+')-'+name+'.xlsx') as writer:
        res_vlz_time.to_excel(writer, sheet_name='计算时间') 
        res_vlz_summary.to_excel(writer, sheet_name='分频最大振级')  
        res_frec_summary.to_excel(writer, sheet_name='对应频率')     
    with pd.ExcelWriter(dir_+'/res_'+log+'详细('+str(min(list(data.keys())))+'-'+str(max(list(data.keys())))+')-'+name+'.xlsx') as writer:
        res_vlz_time.to_excel(writer, sheet_name='计算时间')  
        for i in res_octave_3:
            #print(i)                       
            res_octave_3[i].to_excel(writer, sheet_name=str(i))
    #time.sleep(1)   
    #t2=time.time()
    #print("{} 计算倍频程完成，耗时{}秒。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),round((t2-t1),2)) )               

def batch_octave_3(data,
                  info,
                  name,
                  dir_,
                  cdxs=0.75,
                  weight=None,
                  base=0.000001,
                  window='hanning',
                  num_shiyan='all',
                  num_tongdao='all',
                  ):
    '''
    batch_frequency_vibration_level本省就具备批量计算分频振级和、倍频程的功能
    此处将其分开是为了方便读者使用
    批量计算倍频程函数，
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
        计权曲线. The default is 'None'.        
    base : TYPE, optional
        基准能量值. The default is 0.000001.         
    num_shiyan : TYPE, optional
        要计算的试验号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.
    num_tongdao : TYPE, optional
        要计算的通道号，默认为'all'，如果需要读取部分可输入:'3,5,6-8'.        
    Returns
    -------
    None.
    '''
    batch_frequency_vibration_level(data=data,
                                  info=info,
                                  name=name,
                                  dir_=dir_,
                                  cdxs=cdxs,
                                  weight=weight,
                                  base=base,
                                  window=window,
                                  num_shiyan=num_shiyan,
                                  num_tongdao=num_tongdao,
                                  )

def batch_fft(data,
              info,
              name,
              dir_,
              cdxs=0.75,
              fft_len =1,
              window='hanning',
              num_shiyan='all',
              num_tongdao='all',
              ):
    '''
    批量计算倍频程/分频振级函数，
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
    base : TYPE, optional
        基准能量值. The default is 0.000001.         
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

    t1=time.time()            
    res_fft={}  
    res_vlz_time=[]
    for i in tqdm(data,desc='正在计算fft'):
        pass
    
        df=data[i]
        info_=info[i]
        columns_=[]
        res_fft_=[]
        #选第一个通道来计算能量分布，通过能量分布来计算
        y=df[list(df.keys())[0]] #此处为兼容第一个通道号不是1的情况 采用动态第一个关键值
        start,end=find_start_end(y,
                               sample_rate=float(info_[list(df.keys())[0]]['采样频率']),
                               fft_size=float(info_[list(df.keys())[0]]['采样频率']),
                               window='hanning',
                               cdxs=0.75,
                                ) 
        start_=start*(1-0.75)
        end_=end*(1-0.75)
        res_vlz_time.append([i,start_,end_,(end_-start_)])       
        for j in df:
            pass
            sample_rate=float(info[i][j]['采样频率'])
            res_frec,fft_=fft(df[j][int(start_*float(info[i][j]['采样频率'])):int(end_*float(info[i][j]['采样频率'])+1)],
                                    sample_rate =sample_rate,
                                    fft_size = fft_len*sample_rate,
                                    window=window,
                                    cdxs=cdxs,
                                    fix_meth='幅值修正',
                                    meth='线性平均'
                                    )
            if len(res_fft_)==0: #第一次需要把频率加上
                res_fft_.append(res_frec)
            res_fft_.append(fft_)
            columns_.append(j)
        try:
            ls1=pd.DataFrame(res_fft_).T.set_index(0)     
            ls1.columns=columns_          
            res_fft[i]=ls1   
        except:
            print("{} 计算fft错误。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))             
    
#    res_vlz_time=[]
#    for i in res_vlz_detail:
#        pass
#        aa=res_vlz_detail[i].diff()
#        a=pd.DataFrame(aa.apply(lambda x: x[x==x.min()].index.values[0])).T
#        min_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index'] 
#        a=pd.DataFrame(aa.apply(lambda x: x[x==x.max()].index.values[0])).T
#        max_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index']        
#        res_vlz_time.append([i,max_,min_,(min_-max_)]) #最小值的时间在后面     
    res_vlz_time=pd.DataFrame(res_vlz_time)
    res_vlz_time.columns=['实验号','开始时间','结束时间','持续时间']   
    res_vlz_time=res_vlz_time.set_index('实验号')
    res_vlz_time=res_vlz_time.sort_index()
    for i in res_vlz_time.index:  #此处为兼容有时start大于end的工况
        pass
        if res_vlz_time.loc[i,'开始时间']>res_vlz_time.loc[i,'结束时间']:
           ls=res_vlz_time.loc[i,'开始时间'] 
           res_vlz_time.loc[i,'开始时间']=res_vlz_time.loc[i,'结束时间']
           res_vlz_time.loc[i,'结束时间']=ls
           res_vlz_time.loc[i,'持续时间']=-res_vlz_time.loc[i,'持续时间']
           
    with pd.ExcelWriter(dir_+'/res_频谱详细('+str(min(list(data.keys())))+'-'+str(max(list(data.keys())))+')-'+name+'.xlsx') as writer:
        res_vlz_time.to_excel(writer, sheet_name='计算时间')  
        for i in res_fft:
            #print(i)                       
            res_fft[i].to_excel(writer, sheet_name=str(i))
    #time.sleep(1)   
    #t2=time.time()
    #print("{} 计算倍频程完成，耗时{}秒。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),round((t2-t1),2)) )               

def batch_rolling_octave_3(data,
              info,
              name,
              dir_,
              cdxs=0.75,
              fft_len =1,
              window='hanning',
              num_shiyan='all',
              num_tongdao='all',
              ):
    '''
    批量计算倍频程/分频振级函数，
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
    base : TYPE, optional
        基准能量值. The default is 0.000001.         
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

    t1=time.time()            

    res_octave_3={}
    for i in tqdm(data,desc='正在滚动倍频程'):
        pass
        df=data[i]
        info_=info[i]
     
        for j in df:
            pass
            sample_rate=float(info[i][j]['采样频率'])
            fft_=rolling_octave_3(df[j],
                                           sample_rate=sample_rate,
                                           fft_size=fft_len*sample_rate,
                                           window=window,
                                           cdxs=cdxs,
                                           )
            res_octave_3[i+'_'+j]=fft_
          
           
    with pd.ExcelWriter(dir_+'/res_滚动1_3倍频程('+str(min(list(data.keys())))+'-'+str(max(list(data.keys())))+')-'+name+'.xlsx') as writer: 
        for i in res_octave_3:
            #print(i)                       
            res_octave_3[i].to_excel(writer, sheet_name=str(i))
    #time.sleep(1)   
    #t2=time.time()
    #print("{} 计算倍频程完成，耗时{}秒。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),round((t2-t1),2)) )               


    
if __name__ == '__main__':
    
    import vtda 
    dir_='D:/quant/git/vtda/test_data_dasp'
    name='20210227南宁地铁2号线上行16+018啊'
    data,info=vtda.read_dasp_data(name,dir_=dir_)
    i=10
    j=5
    y=data[i][j]
    a,b=vibration_level(data[i][j],
                        sample_rate=float(info[i][j]['采样频率']),
                        window='hanning',
                        cdxs=0.75)    
    plt.figure(figsize=(15, 12))
    plt.plot(a,b)    