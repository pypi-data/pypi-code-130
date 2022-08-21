# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 15:08:21 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""
def boxplot_custom(data_dict,**args):
    '''
    根据matplotlib库的箱型图打印方法，自定义箱型图可调整的打印样式。 

    Parameters
    ----------
    data_dict : dict(list,numerical)
        字典结构形式的数据，键为横坐分类数据，值为数值列表.
    **args : keyword arguments
        可调整的箱型图样式参数包括['figsize',  'fontsize',  'frameOn',  'xlabel',  'ylabel',  'labelsize',  'tick_length',  'tick_width',  'tick_color',  'tick_direction',  'notch',  'sym',  'whisker_linestyle',  'whisker_linewidth',  'median_linewidth',  'median_capstyle'].

    Returns
    -------
    paras : dict
        样式更新后的参数值.

    '''
    import matplotlib.pyplot as plt
    
    #计算值提取
    data_keys=list(data_dict.keys())
    data_values=list(data_dict.values())     
    
    #配置与更新参数
    paras={'figsize':(10,10),
           'fontsize':15,
           'frameOn':['top','right','bottom','left'],
           'xlabel':None,
           'ylabel':None,
           'labelsize':15,
           'tick_length':7,
           'tick_width':3,
           'tick_color':'b',
           'tick_direction':'in',
           'notch':0,
           'sym':'b+',
           'whisker_linestyle':None,
           'whisker_linewidth':None,
           'median_linewidth':None,
           'median_capstyle':'butt'}
    
    # print(paras)
    paras.update(args)
    # print(paras)
    
    #根据参数调整打印图表样式
    plt.rcParams.update({'font.size': paras['fontsize']})
    frameOff=set(['top','right','bottom','left'])-set(paras['frameOn'])
   
 
    #图表打印
    fig, ax=plt.subplots(figsize=paras['figsize'])
    ax.boxplot(data_values,
               notch=paras['notch'],
               sym=paras['sym'],
               whiskerprops=dict(linestyle=paras['whisker_linestyle'],linewidth=paras['whisker_linewidth']),
               medianprops={"linewidth": paras['median_linewidth'],"solid_capstyle": paras['median_capstyle']})
    
    ax.set_xticklabels(data_keys) #配置X轴刻度标签
    for f in frameOff:
        ax.spines[f].set_visible(False) #配置边框是否显示
    
    #配置X和Y轴标签
    ax.set_xlabel(paras['xlabel'])
    ax.set_ylabel(paras['ylabel'])
    
    #配置X和Y轴标签字体大小
    ax.xaxis.label.set_size(paras['labelsize'])
    ax.yaxis.label.set_size(paras['labelsize'])
    
    #配置轴刻度样式
    ax.tick_params(length=paras['tick_length'],
                   width=paras['tick_width'],
                   color=paras['tick_color'],
                   direction=paras['tick_direction'])

    plt.show()    
    return paras

#%%
def four_quadrant_diagram(data_dict,method='mean',**args):
    '''
    绘制四象限图。

    Parameters
    ----------
    data_dict : dict(list)
        字典格式数据，包括两组键值.其中键名将用作轴标签
    method : string, optional
        按照均值（mean）或中位数(median)方式划分四象限. The default is 'mean'.
    **args : keyword arguments
        可调整的图表样式参数包括：['figsize', 'fontsize', 'frameOn', 'crosshair_color', 'crosshair_linstyle', 'crosshair_linewidth', 'labelsize', 'tick_length', 'tick_width', 'tick_color', 'tick_direction', 'dot_color', 'dot_size', 'annotation_position_finetune', 'annotation_fontsize', 'annotation_lable', 'annotation_color'].

    Returns
    -------
    None.

    '''
    import matplotlib as mpl 
    import matplotlib.pyplot as plt
    from statistics import mean,median
    
    #解决中文乱字符的问题
    mpl.rcParams['font.sans-serif']=['SimHei']
    mpl.rcParams['font.serif']=['SimHei']  
    
    #计算值提取
    (key_x,x),(key_y,y)=data_dict.items()    

    #配置与更新参数
    paras={'figsize':(10,10),
           'fontsize':15,
           'frameOn':['top','right','bottom','left'],
           'crosshair_color':'red',
           'crosshair_linstyle':'--',
           'crosshair_linewidth':3,
           'labelsize':15,
           'tick_length':7,
           'tick_width':3,
           'tick_color':'b',
           'tick_direction':'in',
           'dot_color':'k',
           'dot_size':50,
           'annotation_position_finetune':0.5,
           'annotation_fontsize':10,
           'annotation_lable':None,
           'annotation_color':'gray',
           }  
    paras.update(args)
    
    #根据参数调整打印图表样式
    plt.rcParams.update({'font.size': paras['fontsize']})
    frameOff=set(['top','right','bottom','left'])-set(paras['frameOn'])    
    
    #图表打印
    fig, ax=plt.subplots(figsize=paras['figsize'])    
    ax.scatter(x,y,c=paras['dot_color'],s=paras['dot_size'])
    
    crosshair_color=paras['crosshair_color']
    crosshair_linestyle=paras['crosshair_linstyle']
    crosshair_linewidth=paras['crosshair_linewidth']
    if method=='mean':
        ax.axhline(y=mean(y), color=crosshair_color, linestyle=crosshair_linestyle, linewidth=crosshair_linewidth)           
        ax.axvline(x=mean(x), color=crosshair_color, linestyle=crosshair_linestyle, linewidth=crosshair_linewidth)     
    elif method=='median':
        plt.axhline(y=median(y), color=crosshair_color, linestyle=crosshair_linestyle, linewidth=crosshair_linewidth)           
        plt.axvline(x=median(x), color=crosshair_color, linestyle=crosshair_linestyle, linewidth=crosshair_linewidth)     

    for f in frameOff:
        ax.spines[f].set_visible(False) #配置边框是否显示  
        
    #标注点    
    if paras['annotation_lable']:
        annotations=paras['annotation_lable']
    else:
        annotations=list(range(len(x)))
        
    annotation_position_finetune=paras['annotation_position_finetune']
    for label,x,y in zip(annotations,x,y):
        ax.annotate(label,(x+annotation_position_finetune,y+annotation_position_finetune),
                    fontsize=paras['annotation_fontsize'],
                    color=paras['annotation_color'])
        
    #配置X和Y轴标签
    ax.set_xlabel(key_x)
    ax.set_ylabel(key_y)  

    #配置X和Y轴标签字体大小
    ax.xaxis.label.set_size(paras['labelsize'])
    ax.yaxis.label.set_size(paras['labelsize'])
    
    #配置轴刻度样式
    ax.tick_params(length=paras['tick_length'],
                   width=paras['tick_width'],
                   color=paras['tick_color'],
                   direction=paras['tick_direction'])      
    
    plt.tight_layout()
    plt.show() 

# four_quadrant_diagram(test_EC_scores,
#                       # method='median',
#                       figsize=(15,15),
#                       fontsize=23,
#                       frameOn=['bottom','left'],
#                       labelsize='30',
#                       dot_size=200,
#                       annotation_fontsize=30,
#                       annotation_lable=test_names,
#                       )      
#%%    

if __name__=="__main__":
    #模块内测试
    #A_测试-boxplot_custom(data_dict,**args)
    #%%
    test_score_lst_dic={'English': [90, 81, 73, 97, 85, 60, 74, 64, 72, 67, 87, 78, 85, 96, 77, 100, 92, 86], 
                        'Chinese': [71, 90, 79, 70, 67, 66, 60, 83, 57, 85, 93, 89, 78, 74, 65, 78, 53, 80], 
                        'history': [73, 61, 74, 47, 49, 87, 69, 65, 36, 7, 53, 100, 57, 45, 56, 34, 37, 70], 
                        'biology': [59, 73, 47, 38, 63, 56, 75, 53, 80, 50, 41, 62, 44, 26, 91, 35, 53, 68]}
    _=boxplot_custom(test_score_lst_dic,
                   figsize=(15,10),
                   fontsize=23,
                   frameOn=['bottom','left'],
                   xlabel='subject',
                   ylabel='score',
                   labelsize='30',
                   tick_color='r',
                   notch=1,
                   sym='rs',
                   whisker_linestyle='--',
                   whisker_linewidth=5,
                   median_linewidth=5
                  )
    #%%
    #B_测试-four_quadrant_diagram(data_dict,method='mean',**args)
    test_EC_scores={'English': [90, 81, 73, 97, 85, 60, 74, 64, 72, 67, 87, 78, 85, 96, 77, 100, 92, 86], 
                   'Chinese': [71, 90, 79, 70, 67, 66, 60, 83, 57, 85, 93, 89, 78, 74, 65, 78, 53, 80], }
    test_names=['Mason', 'Reece', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    four_quadrant_diagram(test_EC_scores,
                          # method='median',
                          figsize=(15,15),
                          fontsize=23,
                          frameOn=['bottom','left'],
                          labelsize='30',
                          dot_size=200,
                          annotation_fontsize=30,
                          annotation_lable=test_names,
                          )   
    #%%