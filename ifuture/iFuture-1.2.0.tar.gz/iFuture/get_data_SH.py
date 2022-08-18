#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Created on July 4, 2022
@author: clb
'''
import urllib.error
from urllib.request import urlopen
import json
import pandas as pd
import socket
import time

socket.setdefaulttimeout(20)
class get_data(object):
    def __init__(self, dumpfold, product, start, end):
        # 以上海期货交易所为例
        # 需要获得的数据内容及位置：
        # 流入资金、流出资金——
        # 持空单量、持多单量——交易数据-日统计数据-日交易排名-持买单量（多单）、持卖单量（空单）
        # 收盘价——交易数据-日统计数据-日交易快讯-商品名称:螺纹钢-（主力合约）-收盘价
        # 成交量——交易数据-日统计数据-日交易快讯-商品名称:螺纹钢-（主力合约）-成交手
        # 持仓量——交易数据-日统计数据-日交易快讯-商品名称:螺纹钢-（主力合约）-持仓手
        # 仓单量——交易数据-日统计数据-仓单日报-螺纹钢（仓库+厂库）-正则匹配-总计
        # 净持仓量=持多单量-持空单量
        # 持仓指标=（多单数量-空单数量）/（多单数量+空单数量）*100%
        # self.dumpfold = "/data/intern_2/data/diskData"
        self.dumpfold = dumpfold
        # self.dominantfold = "/home/intern/data/inst_cf/inst_c"
        self.product = product
        self.start = start
        self.end = end
        self.reference = '/trade_scale.csv'
        self.dominantfold = self.dumpfold + '/dominantfold'
        self.dominant_info = self.dumpfold + '/dominantfold' + product + '.csv'
        # self.tick = ['a', 'ag', 'al', 'AP', 'au', 'bu', 'c', 'CF', 'CJ', 'cs', 'cu',
        #         'eb', 'eg', 'FG', 'fu', 'hc', 'i', 'IC', 'IF', 'j', 'jm', 'l', 'lh', 'm', 'MA', 'ni',
        #         'OI', 'p', 'pb', 'PF', 'pg', 'PK', 'pp', 'rb', 'RM', 'ru',
        #         'SA', 'sc', 'sn', 'sp', 'SR', 'ss', 'TA', 'UR', 'v', 'y', 'ZC', 'zn']
        self.tick = ['ag', 'al', 'au', 'bu', 'cu', 'fu', 'hc', 'ni',
                           'pb', 'rb', 'ru', 'sn', 'sp', 'ss', 'zn']
        self.columns = ["TradingDay UpdateTime", "Buy", "Sell", "ClosePrice", "Volume",
                        "Position", "WarehouseReceipt", "NetOpenInterest", "PositionIndex", 'DepositCapital']
        self.dictionary = {'ag': '白银$$SILVER', 'al': '铝$$ALUMINIUM', 'au': '黄金$$GOLD',
                           'bu': ['沥青仓库$$BITUMEN Warehouse', '沥青厂库$$BITUMEN Factory Warehouse',
                                  "石油沥青仓库$$BITUMEN Warehouse", "石油沥青厂库$$BITUMEN Factory Warehouse"],
                           'cu': "铜$$COPPER", 'fu': '燃料油$$FUEL OIL', 'hc': '热轧卷板$$HOT ROLLED COILS',
                           'ni': '镍$$NICKEL', 'pb': '铅$$LEAD',
                           'rb': ['螺纹钢$$REBAR', "螺纹钢仓库$$Rebar Warehouse", "螺纹钢厂库$$Rebar Factory Warehouse"],
                           'ru': '天然橡胶$$NATURAL RUBBER', 'sn': '锡$$TIN',
                           'sp': ['纸浆仓库$$Pulp Warehouse', '纸浆厂库$$Pulp Factory Warehouse'],
                           'ss': ['不锈钢仓库$$Stainless Steel Warehouse', '不锈钢厂库$$Stainless Steel Factory Warehouse'],
                           'zn':"锌$$ZINC"}

    # 查找指定产品在指定日期内的主力合约，规则为成交额最大的合约为主力合约
    def dominant_fold(self):
        try:
            file = pd.DataFrame({'date': pd.date_range(self.start, self.end)})
            file['contract'] = 'nan'
            # 查找主力合约
            for i in range(len(file)):
                date = file.loc[i, 'date'].strftime("%Y%m%d")
                html_SH = urlopen("http://www.shfe.com.cn/data/dailydata/kx/kx" + date + ".dat", timeout=10)
                # <class 'bytes'>
                html = html_SH.read().decode("utf8").encode("utf8")
                # 加载成json的字典形式
                # <class 'dict'>
                my_html = json.loads(html)
                max = 0
                for j in range(len(my_html['o_curinstrument'])):
                    if my_html['o_curinstrument'][j]['PRODUCTID'].strip() != self.product.lower() + '_f': continue
                    else:
                        if my_html['o_curinstrument'][j]['TURNOVER'].strip() >= max:
                            max = my_html['o_curinstrument'][j]['TURNOVER'].strip()
                            file.loc[i, 'contract'] = self.product.lower() + \
                                                      str(my_html['o_curinstrument'][j]['DELIVERYMONTH'].strip())
                        else:continue
                html_SH.close()
            file.to_csv(self.dominant_info)
        except urllib.error.URLError as e:
            print(e.reason)
        except socket.timeout as e:
            print(type(e))
        time.sleep(0.1)

    def run(self):
        for tickname in self.tick:
            print(tickname)
            df = pd.read_csv(self.dominantfold + "/" + tickname + ".csv", header=0, index_col=0,
                             names=['date', 'contract'])
            # 路径不存在需要新建
            filename = self.dumpfold + '/' + tickname + '.csv'
            file = pd.DataFrame([], columns=self.columns)
            file.to_csv(filename, index=False)
            self.inst(df, filename, tickname)

    # 读取主力合约文件夹的数据
    def inst(self, df, filename, tickname):
        j = 0
        data = pd.read_csv(filename, header=0, names=self.columns, engine='python')
        for date in df.index.values:
            date = int(date.strftime("%Y%m%d"))
            if date < 20220524 or date > 20220601: continue
            print('LastestTime:',date)
            dominant_contract = df.loc[date, 'contract']
            if dominant_contract == '0' or 0: continue
            data.loc[j, "TradingDay UpdateTime"] = date
            self.search_1(date, dominant_contract, data, j, tickname)
            self.search_2(date, dominant_contract, data, j)
            self.search_3(date, data, j, tickname)
            self.search_4(date, data, j, dominant_contract, tickname)
            if pd.isnull(data.loc[j, 'Sell']) or pd.isnull(data.loc[j, 'Buy']):
                data.loc[j, 'NetOpenInterest'] = ''
                data.loc[j, 'PositionIndex'] = ''
            else:
                data.loc[j, 'NetOpenInterest'] = int(data.loc[j, 'Buy']) - int(data.loc[j, 'Sell'])
                data.loc[j, 'PositionIndex'] = (int(data.loc[j, 'Buy']) - int(data.loc[j, 'Sell']))\
                                               /(int(data.loc[j, 'Sell']) + int(data.loc[j, 'Buy']))
            j += 1
        data.to_csv(filename, index=False, mode='a', header=False)

    # 查找收盘价、成交量、持仓量
    def search_1(self, date, dominant_contract, data, j, tickname):
        try:
            delivermonth = dominant_contract[-4:]
            # 以螺纹钢20220505为例
            # 'http://www.shfe.com.cn/data/dailydata/kx/kx20160104.dat'
            html_1 = urlopen("http://www.shfe.com.cn/data/dailydata/kx/kx"+ str(date) + ".dat", timeout = 10)
            # <class 'bytes'>
            html = html_1.read().decode("utf8").encode("utf8")
            # 加载成json的字典形式
            # <class 'dict'>
            my_html = json.loads(html)
            # 遍历存在问题，还有一个问题是乱码
            for i in range(len(my_html['o_curinstrument'])):
                if my_html['o_curinstrument'][i]['PRODUCTID'].strip() != tickname.lower() + '_f': continue
                if my_html['o_curinstrument'][i]['DELIVERYMONTH'].strip() != delivermonth: continue
                data.loc[j, 'ClosePrice'] = my_html['o_curinstrument'][i]['CLOSEPRICE']
                data.loc[j, 'Volume'] = my_html['o_curinstrument'][i]['VOLUME']
                data.loc[j, 'Position'] = my_html['o_curinstrument'][i]['OPENINTEREST']
            html_1.close()
        except urllib.error.URLError as e:
            print(e.reason)
        except socket.timeout as e:
            print(type(e))
        time.sleep(0.1)

     # 查找持空单量、持多单量
    def search_2(self, date, dominant_contract, data, j):
        try:
            dominant_contract = dominant_contract.lower()
            html_2 = urlopen("http://www.shfe.com.cn/data/dailydata/kx/pm"+ str(date) + ".dat", timeout = 10)
            "http://www.shfe.com.cn/data/dailydata/kx/pm20220310.dat"
            # <class 'bytes'>
            html = html_2.read().decode("utf8").encode("utf8")
            # 加载成json的字典形式
            my_html = json.loads(html)# <class 'dict'>
            for i in range(len(my_html['o_cursor'])):
                # 这里一定要注意去掉空格什么的
                if my_html['o_cursor'][i]['INSTRUMENTID'].strip() != dominant_contract: continue
                if my_html['o_cursor'][i]['RANK'] != 999: continue
                data.loc[j, 'Buy'] = my_html['o_cursor'][i]['CJ2']
                data.loc[j, 'Sell'] = my_html['o_cursor'][i]['CJ3']
            html_2.close()
        except urllib.error.URLError as e:
            print(e.reason)
        except socket.timeout as e:
            print(type(e))
        time.sleep(0.1)

    # 查找仓单量
    def search_3(self, date, data, j, tickname):
        try:
            "http://www.shfe.com.cn/data/dailydata/20220531dailystock.dat"
            html_3 = urlopen("http://www.shfe.com.cn/data/dailydata/" + str(date) + "dailystock.dat", timeout = 10)
            # <class 'bytes'>
            html = html_3.read().decode("utf8").encode("utf8")
            # 加载成json的字典形式
            # <class 'dict'>
            my_html = json.loads( html)
            a = []
            for i in range(len(my_html['o_cursor'])):
                if my_html['o_cursor'][i]['VARNAME'].strip() not in self.dictionary[tickname.lower()]: continue
                if my_html['o_cursor'][i]['WHABBRNAME'] != '总计$$Total': continue
                a.append(int(my_html['o_cursor'][i]['WRTWGHTS']))
                data.loc[j, 'WarehouseReceipt'] = sum(a)
            html_3.close()
        except urllib.error.URLError as e:
            print(e.reason)
        except socket.timeout as e:
            print(type(e))
        time.sleep(0.1)

    # 计算沉淀资金
    def search_4(self, date, data, j, dominant_contract, tickname):
        # 沉淀资金=收盘价 * 单位（取自对应的数据项） * 交易保证金 / 100  * 空盘量 * 2
        'http://www.shfe.com.cn/data/dailydata/js/js20220701.dat'
        try:
            html_4 = urlopen("http://www.shfe.com.cn/data/dailydata/js/js" + str(date) + ".dat", timeout=10)
            # <class 'bytes'>
            html = html_4.read().decode("utf8").encode("utf8")
            # 加载成json的字典形式
            # <class 'dict'>
            my_html = json.loads(html)
            for i in range(len(my_html['o_cursor'])):
                # 这里一定要注意去掉空格什么的
                if my_html['o_cursor'][i]['INSTRUMENTID'].strip() != dominant_contract: continue
                scale_reference = pd.read_csv(self.reference, header=0, names=['id', 'scale'])
                scale = scale_reference.iloc[scale_reference[scale_reference['id'] == tickname].index, 1]
                data.loc[j, 'DepositCapital'] = 2 * (my_html['o_cursor'][i]['HEDGLONGMARGINRATIO'] +
                                                 my_html['o_cursor'][i]['HEDGSHORTMARGINRATIO']) * int(scale) * \
                                                data.loc[j, 'ClosePrice'] * data.loc[j, 'Position']/(2*(10**8))
            html_4.close()
        except urllib.error.URLError as e:
            print(e.reason)
        except socket.timeout as e:
            print(type(e))
        time.sleep(0.1)
