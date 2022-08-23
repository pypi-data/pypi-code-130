#!/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
from openpyxl import load_workbook
import pandas as pd
import time
# 首先构造一个SDK实例q
def saveDate(option,conversion_filepath,customer_filepath):
    api_sdk = K3CloudApiSdk()
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    api_sdk.InitConfig(acct_id=option['acct_id'],user_name=option['user_name'],app_id=option['app_id'],
                       app_secret=option['app_secret'],server_url=option['server_url'])
    book = load_workbook(conversion_filepath)
    columns1 = book['结算币别'].columns
    columns2 = book['结算方式'].columns
    columns3 = book['收款条件'].columns
    columns4 = book['默认税率'].columns
    columns5 = book['销售人员部门'].columns
    columns6 = book['销售组'].columns
    columns7 = book['国家名称'].columns
    columns8 = book['地区名称'].columns

    headers1 = [cell.value for cell in next(columns1)]
    headers2 = [cell.value for cell in next(columns2)]
    headers3 = [cell.value for cell in next(columns3)]
    headers4 = [cell.value for cell in next(columns4)]
    headers5 = [cell.value for cell in next(columns5)]
    headers6 = [cell.value for cell in next(columns6)]
    headers7 = [cell.value for cell in next(columns7)]
    headers8 = [cell.value for cell in next(columns8)]

    currencyDict = []
    methodDict = []
    collectionDict = []
    rateDict = []
    departmentDict = []
    groupDict = []
    countryDict =[]
    regionDict=[]
    for col1 in columns1:
        data1 = {}
        for title, cell in zip(headers1, col1):
            data1[title] = cell.value
        currencyDict.append(data1)
    for col2 in columns2:
        data2 = {}
        for title, cell in zip(headers2, col2):
            data2[title] = cell.value
        methodDict.append(data2)

    for col3 in columns3:
        data3 = {}
        for title, cell in zip(headers3, col3):
            data3[title] = cell.value
        collectionDict.append(data3)
    for col4 in columns4:
        data4 = {}
        for title, cell in zip(headers4, col4):
            data4[title] = cell.value
        rateDict.append(data4)
    for col5 in columns5:
        data5 = {}
        for title, cell in zip(headers5, col5):
            data5[title] = cell.value
        departmentDict.append(data5)
    for col6 in columns6:
        data6 = {}
        for title, cell in zip(headers6, col6):
            data6[title] = cell.value
        groupDict.append(data6)
    for col7 in columns7:
        data7 = {}
        for title, cell in zip(headers7, col7):
            data7[title] = cell.value
        countryDict.append(data7)
    for col8 in columns8:
        data8 = {}
        for title, cell in zip(headers8, col8):
            data8[title] = cell.value
        regionDict.append(data8)

    df = pd.read_excel(customer_filepath)
    # null setting
    df = df.fillna('')
    # character conversion
    df = df.astype('str')
    for i in df.index:
        currency = df.loc[i]['结算币别']
        currency1 = currencyDict[0][currency]
        settlement_method = df.loc[i]['结算方式']
        settlement_method1 = methodDict[0][settlement_method]
        terms_collection = df.loc[i]['收款条件']
        terms_collection1 = collectionDict[0][terms_collection]
        rate = df.loc[i]['默认税率']
        rate1 = rateDict[0][rate]
        department = df.loc[i]['销售人员部门']
        department1 = departmentDict[0][department]
        sales_group = df.loc[i]['销售组']
        sales_group1 = groupDict[0][sales_group]
        if df.loc[i]['国家名称']!='':
            name_country =df.loc[i]['国家名称']
            name_country1=countryDict[0][name_country]
        else:
            name_country1=df.loc[i]['国家名称']
        if df.loc[i]['地区名称']!='':
            name_region=df.loc[i]['地区名称']
            name_region1=regionDict[0][name_region]
        else:
            name_region1=df.loc[i]['地区名称']
        data = {
            "FCreateOrgId": 100,
            "FUseOrgId": df.loc[i]['使用组织编码'],
            "FNumber": df.loc[i]["客户编码"],
            "FName": df.loc[i]['客户名称'],
            "FTEL": df.loc[i]['联系电话'],
            "FINVOICETITLE": df.loc[i]['发票抬头'],
            "FTAXREGISTERCODE": df.loc[i]['纳税登记号'],
            "FINVOICEBANKNAME": df.loc[i]['开户银行'],
            "FINVOICETEL": df.loc[i]['开票联系电话'],
            "FINVOICEBANKACCOUNT": df.loc[i]['银行账号'],
            "FINVOICEADDRESS": df.loc[i]['开票通讯地址'],
            "FCustTypeId": df.loc[i]['客户类别编码'],
            "FGroup": df.loc[i]['客户分组编码'],
            "FTRADINGCURRID": currency1,
            "FSETTLETYPEID": settlement_method1,
            "FRECCONDITIONID": terms_collection1,
            "FPRICELISTID": '价目表',
            "FInvoiceType": df.loc[i]['发票类型'],
            "FTaxRate": rate1,
            "F_SZSP_KHFL": df.loc[i]['客户分类编码'],
            "FContactId": "联系人名称",
            "FADDRESS1": df.loc[i]['详细地址'],
            "FMOBILE": df.loc[i]['移动电话'],
            "FSELLER": df.loc[i]['销售人员工号'],
            "FSALDEPTID": department1,
            "FSALGROUPID": sales_group1,
            "FBANKCODE": df.loc[i]['银行账号'],
            "FOPENBANKNAME": df.loc[i]['开户银行'],
            "FShortName":df.loc[i]['简称(中文简体)'],
            "FCOUNTRY":name_country1,
            "FPROVINCIAL":name_region1
        }
        save_data = {
            "Model": {
                "FCreateOrgId": {
                    "FNumber": data['FCreateOrgId']
                },
                "FUseOrgId": {
                    "FNumber": data['FUseOrgId']
                },
                "FNumber": data['FNumber'],
                "FName": data['FName'],
                "FShortName": data['FShortName'],
                "FCOUNTRY": {
                    "FNumber": data['FCOUNTRY']
                },
                "FPROVINCIAL": {
                    "FNumber": data['FPROVINCIAL']
                },
                "FTEL": data['FTEL'],
                "FINVOICETITLE": data['FINVOICETITLE'],
                "FTAXREGISTERCODE": data['FTAXREGISTERCODE'],
                "FINVOICEBANKNAME": data['FINVOICEBANKNAME'],
                "FINVOICETEL": data['FINVOICETEL'],
                "FINVOICEBANKACCOUNT": data['FINVOICEBANKACCOUNT'],
                "FINVOICEADDRESS": data['FINVOICEADDRESS'],
                "FCustTypeId": {
                    "FNumber": data['FCustTypeId']
                },
                "FGroup": {
                    "FNumber": data['FGroup']
                },
                "FTRADINGCURRID": {
                    "FNumber": data['FTRADINGCURRID']
                },
                "FPRICELISTID": {
                    "FNumber": data['FPRICELISTID']
                },
                "FSETTLETYPEID": {
                    "FNumber": data['FSETTLETYPEID']
                },
                "FRECCONDITIONID": {
                    "FNumber": data['FRECCONDITIONID']
                },
                "FInvoiceType": data['FInvoiceType'],
                "FTaxRate": {
                    "FNumber": data['FTaxRate']
                },
                "F_SZSP_KHFL": {
                    "FNumber": data['F_SZSP_KHFL']
                },
                "FT_BD_CUSTLOCATION": [
                    {
                        "FContactId": {
                            "FNumber": data['FContactId'],
                        },
                    }
                ],
                "FT_BD_CUSTCONTACT": [
                    {
                        "FADDRESS1": data['FADDRESS1'],
                        "FMOBILE": data['FMOBILE'],
                    }
                ],
                "FSELLER": {
                    "FNumber": data['FSELLER']
                },
                "FSALDEPTID": {
                    "FNumber": data['FSALDEPTID']
                },
                "FSALGROUPID": {
                    "FNumber": data['FSALGROUPID']
                },

                "FT_BD_CUSTBANK": [
                    {
                        "FBANKCODE": data['FBANKCODE'],
                        "FOPENBANKNAME": data['FOPENBANKNAME'],
                    }
                ],
            }
        }
        # 调用sdk中的保存接口
        print(api_sdk.Save("BD_Customer", save_data))

if __name__ == '__main__':

    option = {"acct_id": '62f49d037697ee',
              "user_name":'刘丹',
              "app_id" : '232257_Wefp3YHozvHe38WFTfSM5byN1t7W0qMv',
               "app_secret": '756d9bc9a44441559a5121b54dd0a4ff',
              "server_url": 'http://cellprobio.gnway.cc/k3cloud'
              }
    conversion_filepath = "D:\转换表.xlsx"
    customer_filepath = "D:\客户V3-1.xlsx"
    saveDate(option, conversion_filepath, customer_filepath)


