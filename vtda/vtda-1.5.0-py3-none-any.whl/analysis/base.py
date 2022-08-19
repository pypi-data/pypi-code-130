# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 21:23:50 2021

@author: ZSL
"""
import numpy as np
import math
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from vtda.util.util import weight_factor

#解决中文乱码问题
plt.rcParams["font.sans-serif"]='SimHei'
#解决负号无法正常显示问题
plt.rcParams["axes.unicode_minus"]= False




def choose_windows(name='hanning', N=512,fix_meth='幅值修正'):
    '''
    本函数用来生成窗函数和修正系数
    修正方式分为能量修正和幅值修正   

    Parameters
    ----------
    name : TYPE, optional
        穿函数名. The default is 'hanning'.
    N : TYPE, optional
        生成数据的长度. The default is 512.
    fix_meth : TYPE, optional
        修正方式. The default is '幅值修正'.

    Returns
    -------
    np格式的窗函数
    '''

# Rect/Hanning/Hamming
    if name == 'hamming':
        window =np.hamming(N) 
        xishu_fuzhi=1.85
        xishu_nengliang=1.59
        if fix_meth=='幅值修正':
            res_xishu=xishu_fuzhi
        elif fix_meth=='能量修正':
            res_xishu=xishu_nengliang   
        #np.array([0.54 - 0.46 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
    elif name == 'hanning':
        window=np.hanning(N)
        xishu_fuzhi=2
        xishu_nengliang=1.633
        if fix_meth=='幅值修正':
            res_xishu=xishu_fuzhi
        elif fix_meth=='能量修正':
            res_xishu=xishu_nengliang        
        #window = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
    elif name == 'rect':
        window = np.ones(N)
        xishu_fuzhi=1
        xishu_nengliang=1
        if fix_meth=='幅值修正':
            res_xishu=xishu_fuzhi
        elif fix_meth=='能量修正':
            res_xishu=xishu_nengliang
    return window*res_xishu


def fft(y,
        sample_rate =4096,
        fft_size = 4096,
        window='hanning',
        cdxs=0.75,
        fix_meth='幅值修正',
        meth='线性平均'
        ):
    '''
    傅里叶变换函数
    :param x: 为输入数据
    :param sample_rate: 数据采样率
    :param fft_size: 分析点数，默认为512Hz    
    :param cdxs: 重叠系数,默认为0.75 
    单独运算fft采用幅值修正，计算倍频程及振级采用能量修正
    '''
    #fft_size=len(y)
    try:
        y=y.dropna()
        y=y.fillna(0) 
        y=np.array(y)        
    except:
        pass
    n_zong=max(math.ceil((len(y)-fft_size)/(round((1-cdxs),5)*fft_size))+1,1)#上取整
    res=np.zeros(int(fft_size/2))
    #fix_meth='能量修正'
    #del res_y
    y=y-y.mean()
    res=[]
    for i in np.arange(n_zong):
        pass
        y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)]   
        if len(y_)>0:
            if len(y_)<fft_size: #长度不够进行补零处理
                y_=np.append(y_, np.array([0]*(int(fft_size)-len(y_))), axis=0)
            N=fft_size
            fft_y=np.abs(np.fft.fft(y_*choose_windows(name=window,N=len(y_),fix_meth=fix_meth)))/(0.5*len(y_))
            res.append(fft_y)
    
            # try:
            #     res_y=(fft_y+res_y)/2
            # except:
            #     #第一次没有平均值 
            #     res_y=fft_y
            try:  #经测试先计算最后统一平均的方式和dasp频率特性一致，所以
                res_y+=fft_y[range(int(N/2))]
            except:
                #第一次没有平均值 
                res_y=fft_y[range(int(N/2))]
    # aa=pd.DataFrame(res).T
    # with pd.ExcelWriter(dir_+'/test_fft.xlsx') as writer:
    #     aa.to_excel(writer, sheet_name='计算时间')  
    #res_y=res_y/n_zong
    # pd.DataFrame(asd).plot()       
    res_y[0]=res_y[0]/2
    if n_zong>1:
        rms_z=np.sqrt(np.sum([ i*i for i in y])/(len(y)))
        rms_av=rms_z
        rms_1=np.sqrt(sum(res_y[range(int(N/2))]*res_y[range(int(N/2))])/2)
        xishu=rms_av/rms_1
        res_y=res_y*xishu
        # np.sqrt(sum(res_y1*res_y1)/2)
        # np.sqrt(np.sum([ i*i for i in res_y1])/2)
        #res_y=np.sqrt(res_y[range(int(N/2))]/n_zong)#/((n_zong-1)*(cdxs))#n_zong/np.sqrt(2)
    else:
        res_y=res_y[range(int(N/2))]
    res_x=list(np.arange(0,sample_rate/2,sample_rate/fft_size))
    res_x=res_x[:len(res_y)]
    #res_x=np.linspace(0,sample_rate/2,int(fft_size/2) )
    return res_x,res_y#pd.DataFrame({'frac':res_x,'fft':res_y}).set_index('frac')

#倍频程中心频率计算有两种方法：以2或者10为基底计算 但是两种方法各有利弊，在个别频段均不是整数
#iso266对中心频率进行了取整规定，故不在进行计算，直接引用标准
octave_3_freq={  
        1    :{'low_freq':0.8913,'high_freq':1.122},
        1.25 :{'low_freq':1.122,'high_freq':1.413},
        1.6  :{'low_freq':1.413,'high_freq':1.778},
        2    :{'low_freq':1.778,'high_freq':2.239},
        2.5  :{'low_freq':2.239,'high_freq':2.818}, 
        3.15 :{'low_freq':2.818,'high_freq':3.548},
        4    :{'low_freq':3.548,'high_freq':4.467},
        5    :{'low_freq':4.467,'high_freq':5.623},
        6.3  :{'low_freq':5.623,'high_freq':7.079}, 
        8    :{'low_freq':7.079,'high_freq':8.913}, 
        10   :{'low_freq':8.913,'high_freq':11.22},
        12.5 :{'low_freq':11.22,'high_freq':14.13},
        16   :{'low_freq':14.13,'high_freq':17.78},
        20   :{'low_freq':17.78,'high_freq':22.39},
        25   :{'low_freq':22.39,'high_freq':28.18}, 
        31.5 :{'low_freq':28.18,'high_freq':35.48},
        40   :{'low_freq':35.48,'high_freq':44.67},
        50   :{'low_freq':44.67,'high_freq':56.23},
        63   :{'low_freq':56.23,'high_freq':70.79}, 
        80   :{'low_freq':70.79,'high_freq':89.13}, 
        100  :{'low_freq':89.13,'high_freq':112.2},
        125  :{'low_freq':112.2,'high_freq':141.3},
        160  :{'low_freq':141.3,'high_freq':177.8},
        200  :{'low_freq':177.8,'high_freq':223.9},
        250  :{'low_freq':223.9,'high_freq':281.8}, 
        315  :{'low_freq':281.8,'high_freq':354.8},
        400  :{'low_freq':354.8,'high_freq':446.7},
        500  :{'low_freq':446.7,'high_freq':562.3},
        630  :{'low_freq':562.3,'high_freq':707.9}, 
        800  :{'low_freq':707.9,'high_freq':891.3},
        1000 :{'low_freq':891.3,'high_freq':1122},
        1250 :{'low_freq':1122,'high_freq':1413},
        1600 :{'low_freq':1413,'high_freq':1778},
        2000 :{'low_freq':1778,'high_freq':2239},
        2500 :{'low_freq':2239,'high_freq':2818}, 
        3150 :{'low_freq':2818,'high_freq':3548},
        4000 :{'low_freq':3548,'high_freq':4467},
        5000 :{'low_freq':4467,'high_freq':5623},
        6300 :{'low_freq':5623,'high_freq':7079}, 
        8000 :{'low_freq':7079,'high_freq':8913}, 
        10000:{'low_freq':8913,'high_freq':11220},
        12500:{'low_freq':11220,'high_freq':14130},
        16000:{'low_freq':14130,'high_freq':17780},
        20000:{'low_freq':17780,'high_freq':22390},        
      }


def octave_3(y, 
             sample_rate=4096,
             fft_size = 4096, 
             window='hanning',
             cdxs=0.75,
             meth='线性平均',
             base=0.000001,
             res_type='db',
             frec='all', #输出频率
             ):
    #x=aaaa[28]
    fl=1 #默认起始频谱
    fh=sample_rate/2 #默认截止频率
    #倍频程中心频率计算有两种方法：以2或者10为基底计算 但是两种方法各有利弊，在个别频段均不是整数
    #iso266对中心频率进行了取整规定，故不在进行计算，直接引用标准
#    fc_base = [1,1.25,1.6,2,2.5,3.15,4,5,6.3,8] #1/3倍频程中心频率 基础频率值  其余在此基础上乘10扩展即可
#    fl_base = [0.8913,1.122,1.413,1.778,2.239,2.818,3.548,4.467,5.623,7.079] #1/3倍频程中心频率 基础频率值  其余在此基础上乘10扩展即可
#    fh_base = [1.122,1.413,1.778,2.239,2.818,3.548,4.467,5.623,7.079,8.913] 
#    cf=fc_base+[i*10 for i in fc_base]+[i*100 for i in fc_base]+[i*1000 for i in fc_base]+[i*10000 for i in fc_base]
#    lf=fl_base+[i*10 for i in fl_base]+[i*100 for i in fl_base]+[i*1000 for i in fl_base]+[i*10000 for i in fl_base]
#    rf=fh_base+[i*10 for i in fh_base]+[i*100 for i in fh_base]+[i*1000 for i in fh_base]+[i*10000 for i in fh_base]

    if frec=='all':
        cf=[i for i in octave_3_freq if i<fh ]       
    else:
        #frec=[10,500]
        ls=min(fh,frec[1])
        cf=[i for i in octave_3_freq if i<=ls and i>=frec[0]]   
    
    res_x,res_y_=fft(y,
                     sample_rate=sample_rate,
                     fft_size =fft_size,
                     cdxs=cdxs,
                     fix_meth='能量修正',
                     window=window,
                     meth=meth)
    res_y=[]
    res_x=np.array(res_x)
    res_y_=np.array(res_y_)
    if  (res_x[2]-res_x[1])==1:  #如果分析频率等于采样频率  即分析时长为1s 此处固定化处理  可以提高效率
        pass  
        rms=[0]*len(cf)
        for i in range(len(cf)):
            pass
            if cf[i]==1: #涉及1hz
                pass
                rms[0]=res_y_[1]*res_y_[1]*(1.122-0.8913) #1.25分量
            elif cf[i]==1.25: #涉及1hz
                rms[1]=res_y_[1]*res_y_[1]*(1.413-1.122) #1.25分量
            elif cf[i]==1.6:  #涉及1和2hz          
                rms[2]=rms[2]+res_y_[1]*res_y_[1]*(1.5-1.413)   #1.6分量
                rms[2]=rms[2]+res_y_[2]*res_y_[2]*(1.778-1.5)   #1.6分量
            elif cf[i]==2:  #涉及2hz          
                rms[3]=rms[3]+res_y_[2]*res_y_[2]*(2.239-1.778)        
            elif cf[i]==2.5:  #涉及2、3hz          
                rms[4]=rms[4]+res_y_[2]*res_y_[2]*(2.5-2.239)        
                rms[4]=rms[4]+res_y_[3]*res_y_[3]*(2.818-2.5)                 
            elif cf[i]==3.15:  #涉及3、4hz          
                rms[5]=rms[5]+res_y_[3]*res_y_[3]*(3.5-2.818)        
                rms[5]=rms[5]+res_y_[4]*res_y_[4]*(3.548-3.5) 
            elif cf[i]==4:  #涉及4hz          
                rms[6]=rms[6]+res_y_[4]*res_y_[4]*(4.467-3.548)        
            elif cf[i]==5:  #涉及4、5、6hz          
                rms[7]=rms[7]+res_y_[4]*res_y_[4]*(4.5-4.467)        
                rms[7]=rms[7]+res_y_[5]*res_y_[5]*(5.5-4.5)
                rms[7]=rms[7]+res_y_[6]*res_y_[6]*(5.623-5.5)                
            elif cf[i]==6.3:        
                rms[8]=rms[8]+res_y_[6]*res_y_[6]*(6.5-5.623)        
                rms[8]=rms[8]+res_y_[7]*res_y_[7]*(7.079-6.5)                
            elif cf[i]==8:        
                rms[9]=rms[9]+res_y_[7]*res_y_[7]*(7.5-7.079)        
                rms[9]=rms[9]+res_y_[8]*res_y_[8]             
                rms[9]=rms[9]+res_y_[9]*res_y_[9]*(8.913-8.5)                    
            elif cf[i]==10:        
                rms[10]=rms[10]+res_y_[9]*res_y_[9]*(9.5-8.913)        
                rms[10]=rms[10]+res_y_[10]*res_y_[10]         
                rms[10]=rms[10]+res_y_[11]*res_y_[11]*(11.22-10.5) 
            elif cf[i]==12.5:        
                rms[11]=rms[11]+res_y_[11]*res_y_[11]*(11.5-11.22)        
                rms[11]=rms[11]+res_y_[12]*res_y_[12]             
                rms[11]=rms[11]+res_y_[13]*res_y_[13]
                rms[11]=rms[11]+res_y_[14]*res_y_[14]*(14.13-13.5)  
            elif cf[i]==16:        
                rms[12]=rms[12]+res_y_[14]*res_y_[14]*(14.5-14.13)        
                rms[12]=rms[12]+res_y_[15]*res_y_[15]              
                rms[12]=rms[12]+res_y_[16]*res_y_[16]
                rms[12]=rms[12]+res_y_[17]*res_y_[17]   
                rms[12]=rms[12]+res_y_[18]*res_y_[18]*(17.78-17.5)  
            elif cf[i]==20:        
                rms[13]=rms[13]+res_y_[18]*res_y_[18]*(18.5-17.78)        
                rms[13]=rms[13]+res_y_[19]*res_y_[19]              
                rms[13]=rms[13]+res_y_[20]*res_y_[20]
                rms[13]=rms[13]+res_y_[21]*res_y_[21]   
                rms[13]=rms[13]+res_y_[22]*res_y_[22]*(22.39-21.5)  
            elif cf[i]==25:        
                rms[14]=rms[14]+res_y_[22]*res_y_[22]*(22.5-22.39)        
                rms[14]=rms[14]+res_y_[23]*res_y_[23]              
                rms[14]=rms[14]+res_y_[24]*res_y_[24]
                rms[14]=rms[14]+res_y_[25]*res_y_[25]   
                rms[14]=rms[14]+res_y_[26]*res_y_[26]
                rms[14]=rms[14]+res_y_[27]*res_y_[27]   
                rms[14]=rms[14]+res_y_[28]*res_y_[28]*(28.18-27.5) 
            else:
                ibf= np.where((res_x >= octave_3_freq[cf[i]]['low_freq']) & (res_x < octave_3_freq[cf[i]]['high_freq'])) 
                rms[i]=np.sum([ i*i for i in res_y_[ibf]]) 
            
    else:#如果分析点数与采样频率不相同 则fft后结果不为1，则需要具体分析 会降低分析效率
        rms=[0]*len(cf)
        for i in range(len(cf)):
            pass
            ibf= np.where((res_x >= octave_3_freq[cf[i]]['low_freq']) & (res_x < octave_3_freq[cf[i]]['high_freq'])) 
            rms[i]=np.sum([ i*i for i in res_y_[ibf]]) 
        # res_x1=res_x[:len(res_x)-1]
        # res_x2=res_x[1:len(res_x)]
        # res_x3=(np.array(res_x1)+np.array(res_x2))/2 #求出频谱数据的分界线
        # res_x3_=[i for i in res_x3 if i<=40]
        # print('cuowu ')
        
        # for i in range(len(res_x3_)-1):
        #     pass
        #     res_x3_[i]         
        #     res_x3_[i+1]
        #     i=1
        #     low_freq=octave_3_freq[i]['low_freq']
        #     high_freq=octave_3_freq[i]['high_freq']
        #     [i for i in res_x3 if i<=high_freq and i>=low_freq]   
        

    rms=np.sqrt(np.array(rms)/2)
    for i in range(len(rms)):
        if res_type=='db':
            if rms[i]>0:
                res_y.append(20*math.log10(rms[i]/base))
            else:
                res_y.append(0)
        elif res_type=='线性':
            res_y.append(rms[i])
    
#    for i in range(len(rms)):
#        pass
##        if i == 1: 
#        ibf= np.where((res_x >= lf[i]) & (res_x < rf[i])) 
#        rms=np.sqrt(rms/2)
#        if res_type=='db':
#            if rms>0:
#                res_y.append(20*math.log10(rms/base))
#            else:
#                res_y.append(0)
#        elif res_type=='线性':
#            res_y.append(rms)
    return cf,res_y

def rolling_octave_3( y,
                 weight=None,
                 base=0.000001,                         
                 sample_rate=4096,
                 fft_size = None,
                 fft_len=None,
                 window='hanning',
                 cdxs=0.5,
                 frec='all', #计权因子频率范围
                 n=2, #结果保留精度，即小数点后位数
                 output='dataframe'
                 ):
    '''
    计算滚动倍频程
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    zweight : TYPE, optional
        计权曲线，默认为 None
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
        计权频率的范围，默认为None，可以为[1,80],表示只计算1-80Hz的频率内的能量
    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的振级

    '''
    
    weight=weight_factor(weight=weight,frec=frec) #一定会传入一个计权因子和频率范围
       
    if len(weight)==0:
        print(str(weight)+str(frec)+'计权因子选取错误，请检查')
    #y=aa[1]  res_tigui_acce_21_24['que_dan'][21][300:2000]['que0']
    if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
        sample_rate=1/(y.index[1]-y.index[0])
        y=y.fillna(0)
        y=np.array(y)        
    elif isinstance(y, np.ndarray):
        pass
    else:
        print("{} 错误数据输入格式。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))             
    if fft_size == None :  #不输入分析点数默认
       fft_size= sample_rate
    if fft_len!=None:
       fft_size=fft_len*sample_rate
       
    n_zong=max(math.ceil((len(y)-fft_size)/(round((1-cdxs),5)*fft_size))+1,1)#上取整
    res=np.zeros(int(fft_size/2))
    vl_z=[]
    vl_zonethirds2=[]
    y_z=[]
    deta_x=(fft_size/sample_rate)*round((1-cdxs),5)    
    for i in np.arange(n_zong):
        pass
        y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)] 
        if len(y_)>0:
            res_x,onethird=octave_3(y_,
                                    sample_rate =sample_rate,
                                    fft_size = fft_size,
                                    cdxs=cdxs,
                                    window=window,
                                    res_type='db',
                                    base=base,
                                    frec=frec,
                                    )
            # if len(res_x)>=len(zweight):
            #     zweight=zweight+[0]*(len(res_x)-len(zweight))
            # else:
            #     zweight=zweight[:len(res_x)]
            
            if len(res_x)>=len(weight):
                onethird=onethird[:len(weight)]#zweight+[0]*(len(res_x)-len(zweight))
            else:
                weight=weight[:len(res_x)]#onethird+[0]*(len(weight)-len(res_x))
            vl_zonethird=np.array(weight)+np.array(onethird) 
            vl_z.append(vl_zonethird)
            #print(len(y_),i)
    if output == 'dataframe':
        res=pd.DataFrame(vl_z)
        res.index=list(np.arange(0,deta_x*n_zong,deta_x))
        res.columns=res_x
            
        return res
    elif output == 'list':
              
        return list(np.arange(0,deta_x*n_zong,deta_x)),res_x,vl_z

def base_level(  y,
                 weight=None,
                 base=0.000001,                         
                 sample_rate=4096,
                 fft_size = None,
                 fft_len=None,
                 window='hanning',
                 cdxs=0.5,
                 frec='all', #计权因子频率范围
                 n=2 #结果保留精度，即小数点后位数
                 ):
    '''
    计算振级的基本函数，能够计算Z振级和A声级，本质上只是更换计权曲线和计权频率而已
    Parameters
    ----------
    y : TYPE
        待计算数据，可以为np.ndarray或者 pd.Series格式
    zweight : TYPE, optional
        计权曲线，默认为 None
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
        计权频率的范围，默认为None，可以为[1,80],表示只计算1-80Hz的频率内的能量
    Returns
    -------
    返回两个结果list，一个为时间，另一个为随时间变化的振级

    '''
    
    weight=weight_factor(weight=weight,frec=frec) #一定会传入一个计权因子和频率范围
    #print(frec)
    #print(weight)
#    
#    
#    if frec==None and weight==None:
#        weight=[0]*100 
#    elif frec==None and weight!=None:
#        weight=weight_factor(weight=weight)
#    elif frec!=None and weight==None:
#        weight=[0]*100
#    elif frec!=None and weight!=None:       
#        weight=weight_factor(weight=weight,frec=frec)         
    if len(weight)==0:
        print(str(weight)+str(frec)+'计权因子选取错误，请检查')
    #y=aa[1]  res_tigui_acce_21_24['que_dan'][21][300:2000]['que0']
    if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
        sample_rate=1/(y.index[1]-y.index[0])
        y=y.fillna(0)
        y=np.array(y)        
    elif isinstance(y, np.ndarray):
        pass
    else:
        print("{} 错误数据输入格式。。。".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))             
    if fft_size == None :  #不输入分析点数默认
       fft_size= sample_rate
    if fft_len!=None:
       fft_size=fft_len*sample_rate
    if fft_len==None:
       fft_len=fft_size/sample_rate
              
       
    n_zong=max(math.ceil((len(y)-fft_size)/(round((1-cdxs),5)*fft_size))+1,1)#上取整
    res=np.zeros(int(fft_size/2))
    vl_z=[]
    vl_zonethirds2=[]
    y_z=[]

    for i in np.arange(n_zong):
        pass
        #i=1
        y_=y[int(i*round((1-cdxs),5)*fft_size):int(i*round((1-cdxs),5)*fft_size+fft_size)][:int(fft_size)] 
        #print(i)
        if len(y_)>0:
            res_x,onethird=octave_3(y_,
                                    sample_rate =sample_rate,
                                    fft_size = fft_size,
                                    cdxs=cdxs,
                                    window=window,
                                    res_type='db',
                                    base=base,
                                    frec=frec,
                                    )
            # if len(res_x)>=len(zweight):
            #     zweight=zweight+[0]*(len(res_x)-len(zweight))
            # else:
            #     zweight=zweight[:len(res_x)]
            
            if len(res_x)>=len(weight):
                onethird=onethird[:len(weight)]#zweight+[0]*(len(res_x)-len(zweight))
            else:
                weight=weight[:len(res_x)]#onethird+[0]*(len(weight)-len(res_x))
            vl_zonethird=10**((np.array(weight)+np.array(onethird))*0.1) 
            #print(len(y_),i)
            vl_z_=10*math.log10(sum(vl_zonethird)) 
            vl_z.append(round(vl_z_,n))
            deta_x=(fft_size/sample_rate)*round((1-cdxs),5)
    #res_x=np.linspace(0,deta_x*n_zong,n_zong)
    ls=round(fft_len*(1-cdxs),2)
    ls_z=ls*(n_zong)+fft_len
    res_x=list(np.arange(fft_len,ls_z,ls))            
    return res_x,vl_z


def rms_time(y):
    '''
    在时域内对信号求有效值
    '''
    return np.sqrt(np.sum([ i*i for i in y])/(len(y)))

def rms_frec(y,sample_rate=4096,fft_size = 4096, window='hanning',cdxs=0.5):
    '''
    在频谱内对信号求有效值

    '''
    res_x,res_y_=fft(y,
                     sample_rate=sample_rate,
                     fft_size =fft_size,
                     cdxs=cdxs,
                     fix_meth='能量修正',
                     window=window,
                     meth='线性平均')
    rms=np.sqrt(np.sum([ i*i for i in res_y_])/2)    
    return rms

from scipy import signal

def lvbo_low(lb_q,fq=20,fs=4096,n=8):
    '''
    低通滤波函数
    Parameters
    ----------
    lb_q : TYPE
        滤波前数据
    fq : TYPE, optional
        滤波频率范围
    fs : TYPE, optional
        数据采样频率

    '''
    b,a = signal.butter(n,fq/(fs/2),'low')  #20Hz
    lb_h = signal.filtfilt(b,a,lb_q)
    return lb_h

def lvbo_high(lb_q,fq=20,fs=4096,n=8):
    '''
    高通滤波函数
    Parameters
    ----------
    lb_q : TYPE
        滤波前数据
    fq : TYPE, optional
        滤波频率范围
    fs : TYPE, optional
        数据采样频率

    '''
    b,a = signal.butter(n,fq/(fs/2),'high')  #20Hz
    lb_h = signal.filtfilt(b,a,lb_q)
    return lb_h

def lvbo_daitong(lb_q,fq_s=20,fq_e=50,fs=4096,n=8):
    '''
    带通滤波函数
    Parameters
    ----------
    lb_q : TYPE
        滤波前数据
    fq : TYPE, optional
        滤波频率范围
    fs : TYPE, optional
        数据采样频率

    '''
    # aa=np.random.randn(10000)
    # fq_s=2
    # fq_e=50
    # fs=4096
    # lb_q=aa
    b,a = signal.butter(n,[fq_s/(fs/2),fq_e/(fs/2)],'bandpass')  #20Hz
    lb_h = signal.filtfilt(b,a,lb_q)
    return lb_h

def lvbo_daizu(lb_q,fq_s=2,fq_e=30,fs=500,n=8):
    '''
    带阻滤波函数
    Parameters
    ----------
    lb_q : TYPE
        滤波前数据
    fq : TYPE, optional
        滤波频率范围
    fs : TYPE, optional
        数据采样频率

    '''
    
    b,a = signal.butter(n,[fq_s/(fs/2),fq_e/(fs/2)],'stop')  #20Hz
    lb_h = signal.filtfilt(b,a,lb_q)
    return lb_h

if __name__ == '__main__':
    
    import vtda
    dir_='D:/quant/git/vtda/test_data_dasp'
    name='20210227南宁地铁2号线上行16+018啊'
    data,info=vtda.read_dasp_data(name,dir_=dir_)
    i=10
    j=5
    #dasp  1-5通道频谱有效值:11.2475 14.6698  0.41429  0.03633  0.04221
    #dasp  1-5通道频谱总极值:141.02 143.33  112.36  91.21  92.52
    dasp_rms=np.array([11.2475,14.6698,0.41429,0.03633,0.04221])
    dasp_db=np.array([141.02,143.33,112.36,91.21,92.52])   
    python_rms_time=[]
    python_rms_frec=[]    
    for j in range(1,6):
        pass
        print(j)
        python_rms_time.append(rms_time(data[i][j]) ) 
        python_rms_frec.append(rms_frec(data[i][j],float(info[i][j]['采样频率']),float(info[i][j]['采样频率']),cdxs=0.75))   
 
    a_fft,b_fft=fft(data[i][j],
            sample_rate =float(info[i][j]['采样频率']),
            fft_size = float(info[i][j]['采样频率']),
            cdxs=0.75)
    a2_fft,b2_fft=fft(data[i][j],
            sample_rate =float(info[i][j]['采样频率']),
            fft_size = float(info[i][j]['采样频率']),
            if_octave=True,
            cdxs=0.75)

    plt.figure(figsize=(10, 6))
    plt.plot(a_fft,b_fft)
    plt.plot(a2_fft,b2_fft)    
 
    a_bpc,b_bpc=octave_3(y=data[i][j][int(float(info[i][j]['采样频率']))*10:int(float(info[i][j]['采样频率']))*11],
                 sample_rate =float(info[i][j]['采样频率']),
                 fft_size = float(info[i][j]['采样频率']),
                 cdxs=0.5,
                 meth='线性平均')
    
    
    
    rolling_octave=rolling_octave_3(y=data[i][j],
                 sample_rate =float(info[i][j]['采样频率']),
                 fft_size = float(info[i][j]['采样频率']),
                 cdxs=0.75
                 )

    plt.figure(figsize=(10, 6))
    plt.plot(a_bpc,b_bpc)
    #plt.plot(a2_bpc,b2_bpc)    
    plt.semilogx()

    vl_zonethird=10**((np.array(b_bpc))*0.1) 
    10*math.log10(sum(vl_zonethird)) 
       
    vl_zonethird=10**((np.array(b2_bpc))*0.1) 
    10*math.log10(sum(vl_zonethird)) 
    a1_vlz,b1_vlz=vtda.vibration_level(y=data[i][j], 
                                sample_rate=4096,
                                fft_size = None,
                                fft_len=None,
                                weight='weight_vibration_z_13441_1992',
                                base=0.000001, 
                                window='hanning',
                                cdxs=0.5,
                                n=4 #保留结果小数点后位数
                                )
    a2_vlz,b2_vlz=vtda.vibration_level(y=data[i][j], 
                                sample_rate=4096,
                                fft_size = None,
                                fft_len=None,
                                weight='weight_vibration_z_13441_1992',
                                base=0.000001, 
                                if_octave=True,
                                window='hanning',
                                cdxs=0.5,
                                n=4 #保留结果小数点后位数
                                )  
    n=4096
    y_=y[:n]
    a=np.abs(np.fft.fft(y_*choose_windows(name=window,N=len(y_),fix_meth=fix_meth)))[range(int(n/2))]        
    a_x=list(np.arange(0,n/2,n/len(y_)))
    nn=2
    a2=np.abs(np.fft.fft(y_*choose_windows(name=window,N=len(y_),fix_meth=fix_meth),len(y_)*nn))[range(int(len(y_)*nn/2))]  
    a2_x=list(np.arange(0,n/2,n/len(y_)/nn))
    
    
    plt.figure(figsize=(10, 6))
    plt.plot(a_x,a)
    plt.plot(a2_x,a2) 
    plt.legend(loc ="best",fontsize=15) 
    plt.xlim(1,300)
    plt.ylim(0,0.3)    
    np.sqrt(np.sum([ i*i for i in a])/2)    
    np.sqrt(np.sum([ i*i for i in a2])/2) 

    np.sqrt(np.sum([ i*i for i in y_])/(len(y_)))       