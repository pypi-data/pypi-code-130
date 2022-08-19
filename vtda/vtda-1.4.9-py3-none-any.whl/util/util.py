# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 10:18:13 2021

@author: ZSL
"""
import numpy as np
import math
import time
import pandas as pd
 #ISO2631/1-1985   GB/T13441-1992 两规范中计权曲线相同
 ###振动计权因子
weight_vibration_z_13441_1992={1:-6,
                     1.25:-5,
                     1.6:-4,
                     2.0:-3,
                     2.5:-2,
                     3.15:-1,
                     4.0:0,
                     5.0:0,
                     6.3:1,
                     8.0:0,
                     10:-2,
                     12.5:-4,
                     16.0:-6,
                     20.0:-8,
                     25.0:-10,
                     31.5:-12,
                     40.0:-14,
                     50.0:-16,
                     63.0:-18,
                     80.0:-20,
                     }
                         
weight_vibration_x_13441_1992={1:0,
                     1.25:0,
                     1.6:0,
                     2.0:0,
                     2.5:-2,
                     3.15:-4,
                     4.0:-6,
                     5.0:-8,
                     6.3:-10,
                     8.0:-12,
                     10:-14,
                     12.5:-16,
                     16.0:-18,
                     20.0:-20,
                     25.0:-22,
                     31.5:-24,
                     40.0:-26,
                     50.0:-28,
                     63.0:-30,
                     80.0:-32,
                     }                         
                         
weight_vibration_y_13441_1992=weight_vibration_x_13441_1992

#ISO2631/1-1997   GB/T13441-2007 两规范中计权曲线相同
###振动计权因子
weight_vibration_z_13441_2007={0.1:-30.11,
                     0.125:-26.26,
                     0.16:-22.05,
                     0.2:-18.33,
                     0.25:-14.81,
                     0.315:-11.60,
                     0.4:-9.07,
                     0.5:-7.57,
                     0.63:-6.77,
                     0.8:-6.43,
                     1:-6.33,
                     1.25:-6.29,
                     1.6:-6.12,
                     2.0:-5.49,
                     2.5:-4.01,
                     3.15:-1.90,
                     4.0:-0.29,
                     5.0:0.33,
                     6.3:0.46,
                     8.0:0.31,
                     10:-0.1,
                     12.5:-0.89,
                     16.0:-2.28,
                     20.0:-3.93,
                     25.0:-5.8,
                     31.5:-7.86,
                     40.0:-10.05,
                     50.0:-12.19,
                     63.0:-14.61,
                     80.0:-17.56, 
                     100:-21.04,
                     125:-25.35,
                     160:-30.91,
                     200:-36.38,
                     250:-42.04,
                     315:-48.00,
                     400:-54.20,                     
                     }

weight_vibration_x_13441_2007={0.1:-24.09,
                     0.125:-20.24,
                     0.16:-16.01,
                     0.2:-12.28,
                     0.25:-8.75,
                     0.315:-5.52,
                     0.4:-2.94,
                     0.5:-1.38,
                     0.63:-0.50,
                     0.8:-0.07,
                     1:0.1,
                     1.25:0.07,
                     1.6:-0.28,
                     2.0:-1.01,
                     2.5:-2.20,
                     3.15:-3.85,
                     4.0:-5.82,
                     5.0:-7.76,
                     6.3:-9.81,
                     8.0:-11.93,
                     10:-13.91,
                     12.5:-15.87,
                     16.0:-18.03,
                     20.0:-19.99,
                     25.0:-21.94,
                     31.5:-23.98,
                     40.0:-26.13,
                     50.0:-28.22,
                     63.0:-30.60,
                     80.0:-33.53, 
                     100:-36.99,
                     125:-41.28,
                     160:-46.84,
                     200:-52.30,
                     250:-57.97,
                     315:-63.92,
                     400:-70.12,                     
                     }

weight_vibration_y_13441_2007=weight_vibration_x_13441_2007

###GBT 3785.1-2010 电声学 声级计
###噪声计权因子
weight_noise_a_3785_2010={10:-70.4,
                     12.5:-63.4,
                     16.0:-56.7,
                     20.0:-50.5,
                     25.0:-44.7,
                     31.5:-39.4,
                     40.0:-34.6,
                     50.0:-30.2,
                     63.0:-26.2,
                     80.0:-22.5, 
                     100:-19.1,
                     125:-16.1,
                     160:-13.4,
                     200:-10.9,
                     250:-8.6,
                     315:-6.6,
                     400:-4.8, 
                     500:-3.2,
                     630:-1.9,
                     800:-0.8, 
                     1000:-0,
                     1250:0.6,
                     1600:1,
                     2000:1.2,
                     2500:1.3,
                     3150:1.2,
                     4000:1.0, 
                     5000:0.5,
                     6300:-0.1,
                     8000:-1.1, 
                     10000:-2.5,
                     12500:-4.3,
                     16000:-6.6,
                     20000:-9.3,                         
                     }

weight_0={0.1:0,
         0.125:0,
         0.16:0,
         0.2:0,
         0.25:0,
         0.315:0,
         0.4:0,
         0.5:0,
         0.63:0,
         0.8:0,
         1:0.0,
         1.25:0,
         1.6:0,
         2.0:0,
         2.5:0,
         3.15:0,
         4.0:0,
         5.0:0,
         6.3:0,
         8.0:0,
         10:0,
         12.5:0,
         16.0:0,
         20.0:0,
         25.0:0,
         31.5:0,
         40.0:0,
         50.0:0,
         63.0:0,
         80.0:0, 
         100:0,
         125:0,
         160:0,
         200:0,
         250:0,
         315:0,
         400:0,                     
         500:0,
         630:0,
         800:0, 
         1000:0,
         1250:0,
         1600:0,
         2000:0,
         2500:0,
         3150:0,
         4000:0, 
         5000:0,
         6300:0,
         8000:0, 
         10000:0,
         12500:0,
         16000:0,
         20000:0,                         
         }


def weight_factor(weight='weight_noise_a_3785_2010',frec='all'):
    '''
    选择项对应的计权因子
    '''
    if weight=='weight_vibration_z_13441_1992':
        weight=weight_vibration_z_13441_1992
    elif weight=='weight_vibration_x_13441_1992' or weight=='weight_vibration_y_13441_1992':
        weight=weight_vibration_y_13441_1992
    elif weight=='weight_vibration_z_13441_2007':
        weight=weight_vibration_z_13441_2007
    elif weight=='weight_vibration_x_13441_2007' or weight=='weight_vibration_y_13441_2007':
        weight=weight_vibration_z_13441_2007
    elif weight=='weight_noise_a_3785_2010':
        weight=weight_noise_a_3785_2010  
    elif weight==None:
        weight=weight_0          
    else:
        print('计权因子输入错误，请检查')
        return None
    res=[]
    if frec=='all':
        for i in weight:
            res.append(weight[i])
    else:
        for i in weight:
            pass
            if int(i)>=frec[0] and int(i)<=frec[1]:
                res.append(weight[i])
    return res
        
    
def fix_num(num='3,5,8-10'):
    '''
    将字符格式的序号转换为list格式的序号
    '''
    
    res_ls1=num.split(',')
    res=[]
    for i in res_ls1:
        pass
        res_ls2=i.split('-')
        if len(res_ls2)>1 and len(res_ls2)<3:
            ls=list(range(int(res_ls2[0]),int(res_ls2[1])+1))
            ls=[str(x) for x in ls]
            res+=ls
        elif len(res_ls2)==1:
            ls=[str(int(res_ls2[0]))]
            res+=ls
        else:
            print('输入编号格式错误，请检查。')
    return res
        
def find_start_end(y,
                   sample_rate=4096,
                   fft_size=4096,
                   window='hanning',
                   cdxs=0.75,
                    ):
    '''
    从能量有效值的角度来判断列车通过的时间起始位置
    '''
    pass
    n_zong=max(math.ceil((len(y)-fft_size)/((1-cdxs)*fft_size))+1,1)#上取整
    y_z=[]
    for i in np.arange(n_zong):
        pass
        y_=y[int(i*(1-cdxs)*fft_size):int(i*(1-cdxs)*fft_size+fft_size)][:int(fft_size)] 
        if len(y_)>0:
            y_z.append(np.sqrt(np.sum([ i*i for i in y_])/(len(y_))))   
    ls=pd.DataFrame(pd.Series.rolling(pd.Series(y_z), 6).mean().diff().shift(-3))
    a=pd.DataFrame(ls.apply(lambda x: x[x==x.min()].index.values[0])).T
    min_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index'] 
    a=pd.DataFrame(ls.apply(lambda x: x[x==x.max()].index.values[0])).T
    max_=a.T.apply(pd.value_counts).reset_index().sort_values(by=0,ascending=False).loc[0,'index']        
      
    return max_,min_

#def fix_frec(weght=None):
#    '''
#    通过计权曲线种类确定频率
#    '''
#    if weght==None:
#        frec=None
#    elif weight=='weight_vibration_z_13441_1992':
#        frec=[1,80]
#    elif weight=='weight_vibration_x_13441_1992' or weight=='weight_vibration_y_13441_1992':
#        weight=weight_vibration_y_13441_1992
#    elif weight=='weight_vibration_z_13441_2007':
#        weight=weight_vibration_z_13441_2007
#    elif weight=='weight_vibration_x_13441_2007' or weight=='weight_vibration_y_13441_2007':
#        weight=weight_vibration_z_13441_2007
#    elif weight=='weight_noise_a_3785_2010':
#        weight=weight_noise_a_3785_2010  
#    else:
#        print('计权因子输入错误，请检查')
#        return None

import os
def demo():  
    work_path=os.getcwd()
    os.startfile(work_path+'\\demo')
        
if __name__ == '__main__':

    weight_factor(weight='weight_vibration_z_13441_1992')
            
    
        