# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 18:35:24 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""
#展平嵌套列表，返回列表
flatten_lst=lambda lst: [m for n_lst in lst for m in flatten_lst(n_lst)] if type(lst) is list else [lst]

def flatten_lst_generator(lst):
    '''
    展平嵌套列表，返回迭代对象。

    Parameters
    ----------
    lst : list
        嵌套列表.

    Yields
    ------
    iterable object
        嵌套列表展平后的迭代对象.

    '''
    try: #使用语句try/except捕捉异常
        for n_lst  in lst: 
             for m in flatten_lst_generator(n_lst):
                yield m
               
    except:  
        yield lst

def infinite_generator():
    '''
    无穷整数生成器。

    Yields
    ------
    i : int
        整数值.

    '''
    i=0
    while True:
        i+=1
        yield i
        
def recursive_factorial(n):
    '''
    阶乘计算。

    Parameters
    ----------
    n : int
        阶乘计算的末尾值.

    Returns
    -------
    int
        阶乘计算结果.

    '''
    if n==1:
        return 1
    else:
        return n*recursive_factorial(n-1)

def start_time():
    '''
    获取当前时间

    Returns
    -------
    start_time : datetime
        返回当前时间.

    '''
    import datetime
    
    start_time=datetime.datetime.now()
    print("start time:",start_time)
    return start_time

def duration(start_time):
    '''
    配合start_time()使用。计算时间长度。

    Parameters
    ----------
    start_time : datetime
        用于计算时间长度的开会时间.

    Returns
    -------
    None.

    '''
    import datetime
    
    end_time=datetime.datetime.now()
    print("end time:",end_time)
    duration=(end_time-start_time).seconds/60
    print("Total time spend:%.2f minutes"%duration)            

if __name__=="__main__":
    #模块内测试
    #A_测试-flatten_lst
    #%%
    nested_lst=[['A','B',['C','D'],'E'],[6,[7,8,[9]]]]  
    print(flatten_lst(nested_lst))       
    #%%
    #B_测试-flatten_lst_generator(lst)
    fl=flatten_lst_generator(nested_lst)
    print(list(fl))
    #%%
    #C_测试-infinite_generator()
    inf=infinite_generator()
    print(next(inf))    
    print(next(inf)) 
    #%%
    #D_测试-recursive_factorial(n)
    print(recursive_factorial(6))
    #%%
    #E_测试-start_time();duration(start_time)
    s_t=start_time()
    for i in range(10**8):value=i
    duration(s_t)    
    #%%
