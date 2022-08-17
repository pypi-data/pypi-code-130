###################################################
##############   中信一级行业分析 ##################
###################################################

import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from scipy.stats import rankdata
font_name = "SimSun"
mpl.rcParams['font.family']=font_name
mpl.rcParams['font.size']=12
mpl.rcParams['axes.unicode_minus']=False
warnings.filterwarnings("ignore")


db_share = create_engine('postgresql+psycopg2://postgres:cjsc@10.200.114.87/postgres')
db_share.connect()

def get_industries_val(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    val_industries = pd.read_sql("""SELECT * FROM "中信行业指数每日估值" WHERE
                                   "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con=db)
    val_industries['日期'] = pd.to_datetime(val_industries['日期'])
    return val_industries

def get_industries_return(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    ret_industries  = pd.read_sql("""SELECT * FROM "中信行业指数日收益率" WHERE
                                   "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con=db)
    ret_industries['日期'] = pd.to_datetime(ret_industries['日期'])
    return ret_industries

def get_industries_estimate(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    est_industries = pd.read_sql("""SELECT * FROM "中信行业指数一致预期" WHERE
                                   "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con = db)
    est_industries['日期'] = pd.to_datetime(est_industries['日期'])
    return est_industries

def get_industries_roe(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    roe_industries = pd.read_sql("""SELECT * FROM "中信行业加权ROE" WHERE
                                   "报告期" >= '{}' AND "报告期" <= '{}' """.format(start_day, end_day), con=db)
    roe_industries['报告期'] = pd.to_datetime(roe_industries['报告期'])
    return roe_industries    

def get_sector_val(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    """各板块加权估值指标（按照个股的市值加权）"""
    sector_val = \
    pd.read_sql("""SELECT * FROM "板块估值明细(加权)" 
                   WHERE "日期" >= '{}'
                   AND   "日期" <= '{}' """.format(start_day, end_day), con=db)
    sector_val['日期'] = pd.to_datetime(sector_val['日期'])
    return sector_val

def get_sector_return(db = db_share):
    """各个板块年初以来与最近5日收益率"""
    sector_return  = pd.read_sql("板块收益率",con=db)
    return sector_return


###################################################
##############      生成报告      ##################
###################################################

def generate_report():
    """
        指标说明：
        1. 滑动一致预期指标根据 预期指标_FY1, 预期指标_FY2 加权计算得到。
        定义：M1 最近未公开年报公布月份（今年4月末或者明年4月末）
              M2 当前所处月份
              delta_M = M1 - M2
        
        如果 当前为8月，则delta_M = 明年4月 - 今年8月 = 4 + 12 - 8 = 8
        如果 当前为2月，则delta_M = 今年4月 - 今年2月 = 4 - 2 = 2
        
        滑动一致预期指标 = (delta_M) / 12 x 预期指标_FY1 + (12 - delta_M) / 12 x 预期指标_FY2
    """
    #### 收益率与估值
    generate_sector_report()
    
    #### 一致预期
    sector_consensus()
    


def customize_barh(data, x_label, y_label, ax, title='', hue=None):
    """自定义直方图格式"""
    if hue is None:
        plots = \
        sns.barplot(x = x_label,
                    y = y_label,
                    data = data,
                    orient = 'h',
                    color = 'blue',
                    alpha = 0.4,
                    ax = ax)
    else:
        plots = \
        sns.barplot(x = x_label,
                    y = y_label,
                    data = data,
                    orient = 'h',
                    hue=hue,
                    alpha = 0.4,
                    palette=["C0", "C1", "C2", "k"],
                    ax = ax)        
    for bar in plots.patches:
        plots.annotate(format(bar.get_width(), '.2f'),
                       (bar.get_x() + bar.get_width(),
                        bar.get_y()+ bar.get_height()),
                       ha='center', va='center',
                        xytext=(0, 8),
                       fontsize = 10,
                       textcoords='offset points')
    ax.grid(axis='x')
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title(title, fontsize = 22)
    plt.draw()
    

def generate_sector_report():
    """
        计算并展示各个板块加权（总市值加权）估值指标。
        指标说明：
        1. 市盈率(ttm) = 板块内股票总市值之和 / 板块内股票净利润ttm之和
        2. 其余市净率，市销率(ttm)，股息率均以此类推
    """
    val = get_sector_val()
    max_dt = str(val['日期'].max())[:10]
    val.set_index(['日期','指数代码','指数名称','类别'],inplace=True)
    sector_return = get_sector_return()
    
    sector_roe = pd.read_sql("板块ROE",con=db_share)
    new_rpt = sector_roe[['报告期']].drop_duplicates().iloc[-1].astype('str').values[0]
    old_rpt = sector_roe[['报告期']].drop_duplicates().iloc[-2].astype('str').values[0]
    
    N = 250
    for cat in ['消费','科技','宽基指数']:
        fig = plt.figure(figsize = (30,60))
        axes = []
        axes.append(plt.subplot2grid((7,20),(0,0), colspan=5))
        axes.append(plt.subplot2grid((7,20),(0,7), colspan=5))
        axes.append(plt.subplot2grid((7,20),(0,14), colspan=5))
        
        ### 收益率
        df_plot = \
        sector_return.query("""类别 == '{}'""".format(cat))[['指数名称','年初以来收益率']]\
        .sort_values('年初以来收益率',ascending=False)
        customize_barh(df_plot,x_label='年初以来收益率',y_label='指数名称',title='年初以来收益率',ax=axes[0])
        
        df_plot = \
        sector_return.query("""类别 == '{}'""".format(cat))[['指数名称','近5日收益率']]\
        .sort_values('近5日收益率',ascending=False)
        customize_barh(df_plot,x_label='近5日收益率',y_label='指数名称',title='近5日收益率',ax=axes[1])

        for i in range(1,6):
            axes.append(plt.subplot2grid((7,20),(i,0), colspan=5))
            axes.append(plt.subplot2grid((7,20),(i,7), colspan=5))
            axes.append(plt.subplot2grid((7,20),(i,14), colspan=5))
            
        i = 1
        for val_label in ['市盈率(ttm)','市净率','市销率(ttm)','股息率']:
            #### 当前加权估值水平
            df_plot = \
            val[[val_label]].sort_index().unstack(level=[1,2,3])\
            .iloc[[-1]].stack(level=[1,2,3]).reset_index().query("""类别=='{}'""".format(cat))

            customize_barh(data=df_plot[['指数名称',val_label]].sort_values(val_label,ascending=False),
                           x_label = val_label, y_label = '指数名称',
                           title = cat+': '+val_label+'(加权)',
                           ax=axes[3*i])

            #### 当前估值在过去一年中的百分位
            df_plot = \
            val[[val_label]].sort_index().unstack(level=[1,2,3]).iloc[-N:]\
            .apply(lambda x: rankdata(x)[-1] / N * 100).to_frame(val_label+"过去一年中百分位")\
            .reset_index()[['指数名称','类别',val_label+'过去一年中百分位']]

            customize_barh(data=df_plot.query("""类别=='{}'""".format(cat))\
                           [['指数名称',val_label+'过去一年中百分位']]\
                           .sort_values(val_label+'过去一年中百分位',ascending=False),
                           x_label = val_label+'过去一年中百分位', y_label = '指数名称',
                           title = cat+': '+val_label+'在过去一年中百分位',
                           ax=axes[3*i+1])
            axes[3*i+1].set_xlim((0,100))
            
            #### 当前估值从2017年以来的百分位
            df_plot = \
            val[[val_label]].sort_index().unstack(level=[1,2,3])\
            .apply(lambda x: rankdata(x)[-1] / np.sum(~pd.isna(x)) * 100)\
            .to_frame(val_label+'从2017年以来的百分位')\
            .reset_index()[['指数名称','类别',val_label+'从2017年以来的百分位']]

            customize_barh(data=df_plot.query("""类别=='{}'""".format(cat))\
                           [['指数名称',val_label+'从2017年以来的百分位']]\
                           .sort_values(val_label+'从2017年以来的百分位',ascending=False),
                           x_label = val_label+'从2017年以来的百分位', y_label = '指数名称',
                           title = cat+': '+val_label+'从2017年以来的百分位',
                           ax=axes[3*i+2])
            axes[3*i+2].set_xlim((0,100))          
            i += 1
        axes.append(plt.subplot2grid((7,20),(i,0), colspan=5, rowspan=2)) 
        
        df_plot = \
        sector_roe.loc[sector_roe.类别 == cat].sort_values('ROE',ascending=False)[['指数名称','ROE','报告期']]
        customize_barh(data=df_plot, x_label = 'ROE', y_label = '指数名称', hue = '报告期',
                       title = '加权ROE',
                       ax = axes[-1])
            
        fig.suptitle('更新日期:' + max_dt, fontsize = 24, x = 0.5, y = 0.9 )
        plt.savefig(max_dt + '-估值与收益率-' + cat+'.png', dpi=256)

def get_percent(data, label, N = 252*3, ax=None):
    percent = \
    data.set_index(['日期','指数名称'])[label].unstack()\
    .iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
    current_percent = percent.last('1D').transpose()
    current_percent.columns = [label+'三年中百分位']
    df_plot = \
    current_percent.mul(100).sort_values(label+'三年中百分位',ascending=False).reset_index()
    if ax:
        customize_barh(df_plot,
                       x_label=label+'三年中百分位',
                       y_label='指数名称',
                       title=label+'三年中百分位',
                       ax=ax)
    return df_plot

def est_trend(index_consensus, metric_names,
              display_name, axis_label,
              prefix = '', suffix = '(%)',
              unit=1, method = 'diff'):
    """一致预期历史变化趋势图"""
    my_dpi = 128
    nrow = (len(index_consensus['指数名称'].unique())+1) // 2 + 2
    max_dt = str(index_consensus['日期'].max())[:10]
    
    fig = plt.figure(figsize = (20,5*nrow))
    axes = []
    axes.append(plt.subplot2grid((nrow,2),(0,0),colspan=1,rowspan=2))
    axes.append(plt.subplot2grid((nrow,2),(0,1),colspan=1,rowspan=2))

    # 以日频率进行平滑
    index_consensus_day= index_consensus.copy()
    index_consensus_day['day'] = index_consensus_day.日期.dt.day
    index_consensus_day['weight1'] = (365 + 120 - index_consensus_day['day']) % 365 / 365
    index_consensus_day['weight2'] = 1 - index_consensus_day['weight1']
    index_consensus_day[display_name] = \
    index_consensus_day[metric_names[0]] * index_consensus_day['weight1'] + \
    index_consensus_day[metric_names[1]] * index_consensus_day['weight2']


    # 转换为月频率进行平滑
    index_consensus.sort_values('日期',inplace=True)
    index_consensus_month = \
    index_consensus.groupby([index_consensus['日期'].dt.year,
                             index_consensus['日期'].dt.month,
                             index_consensus['指数名称']]).tail(1)

    #### 平滑化处理 以每年4月30日分界
    index_consensus_month['month'] = index_consensus_month['日期'].dt.month
    index_consensus_month['weight1'] = (16.5 - index_consensus_month['month']) % 12 / 12
    index_consensus_month['weight2'] = 1 - index_consensus_month['weight1']
    index_consensus_month[display_name] = \
    index_consensus_month[metric_names[0]] * index_consensus_month['weight1'] + \
    index_consensus_month[metric_names[1]] * index_consensus_month['weight2']

    industries_sort = \
    index_consensus_month[['指数名称',display_name]].groupby('指数名称').mean()\
    .sort_values(display_name,ascending=False).index.tolist()


    #### 当前行业一致预期汇总
    data = \
    index_consensus_month.set_index(['日期','指数名称'])[display_name].unstack()\
    .sort_index().last('1D').stack().sort_values(ascending=False).div(unit)\
    .to_frame(display_name).reset_index().drop('日期',axis=1)
    customize_barh(data=data, x_label=display_name, y_label='指数名称',
                   title = display_name+suffix, ax = axes[0])
    
    if method == 'diff':
        #### 20日内变化 绝对差值
        data_diff = \
        index_consensus_day.set_index(['日期','指数名称'])[display_name].unstack()\
        .sort_index().diff(periods = 20).iloc[-1].sort_values(ascending=False)\
        .to_frame(display_name).reset_index()
        customize_barh(data_diff, x_label = display_name,
                       y_label = '指数名称', title = display_name + '相较20个交易日前差值(%)',
                       ax=axes[1])
    else:
        #### 20日内变化 相对增长        
        data_diff = \
        index_consensus_day.set_index(['日期','指数名称'])[display_name].unstack()\
        .sort_index().pct_change(periods = 20).mul(100).iloc[-1].sort_values(ascending=False)\
        .to_frame(display_name).reset_index()
        customize_barh(data_diff, x_label = display_name,
                       y_label = '指数名称', title = display_name + '相较20个交易日前增长(%)',
                       ax=axes[1])

    for i in range(2,nrow):
        axes.append(plt.subplot2grid((nrow,2),(i,0), colspan=1))
        axes.append(plt.subplot2grid((nrow,2),(i,1), colspan=1))
        
    for i, ind in enumerate(industries_sort):
        i += 2
        data = \
        index_consensus_month.query("""指数名称 == '{}'""".format(ind))[['日期',display_name]]\
        .set_index('日期').div(unit).reset_index()
        sns.lineplot(data = data, x = '日期', y = display_name, ax = axes[i],
                     marker = 'o', linestyle ='--', linewidth = 2)
        axes[i].grid(axis='y')
        axes[i].set_title(ind, fontsize = 20)
        axes[i].set_xlabel('')
        axes[i].set_ylabel(axis_label)
    fig.suptitle("最新日期:" + max_dt,fontsize = 24, x=0.5, y = 0.95)
    plt.savefig(prefix+display_name+'.png',dpi = my_dpi)
    plt.show()
    
def sector_consensus():
    """ 一致预期趋势 """
    data = pd.read_sql("板块一致预期", con=db_share)
    category = pd.read_sql(""" SELECT DISTINCT "指数代码","指数名称","类别" FROM "板块估值明细(加权)" """,
                           con = db_share)
    data = data.merge(category, on=['指数代码','指数名称'])
    latest_date = str(data['日期'].max())[:10]

    for cat in ['宽基指数','消费','科技']:
        #### 净利润一致预期
        est_trend(data.loc[data.类别 == cat], metric_names = ['一致预期净利润(FY1)','一致预期净利润(FY2)'],
                  display_name = '滑动一致预期净利润', axis_label = '净利润（亿元）',
                  unit=1e8, prefix=latest_date + "-" + cat+'-', suffix='(亿元)', method='pct_change')
        
        #### ROE一致预期
        est_trend(data.loc[data.类别 == cat], metric_names = ['一致预期ROE(FY1)','一致预期ROE(FY2)'],
                  display_name = '滑动一致预期ROE', axis_label = 'ROE(%)',
                  unit=1, prefix=latest_date + "-" + cat+'-', suffix='(%)', method='diff')  