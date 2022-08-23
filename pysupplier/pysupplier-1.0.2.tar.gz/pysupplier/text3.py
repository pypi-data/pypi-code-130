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
    columns3 = book['默认税率'].columns
    columns4 = book['付款条件'].columns
    columns5 = book['国家'].columns
    columns6 = book['地区'].columns
    columns7 = book['负责部门'].columns
    columns8 = book['供应商等级'].columns
    columns9 = book['供应类别'].columns
    # columns10 = book['发票类型'].columns

    headers1 = [cell.value for cell in next(columns1)]
    headers2 = [cell.value for cell in next(columns2)]
    headers3 = [cell.value for cell in next(columns3)]
    headers4 = [cell.value for cell in next(columns4)]
    headers5 = [cell.value for cell in next(columns5)]
    headers6 = [cell.value for cell in next(columns6)]
    headers7 = [cell.value for cell in next(columns7)]
    headers8 = [cell.value for cell in next(columns8)]
    headers9 = [cell.value for cell in next(columns9)]
    # headers10 = [cell.value for cell in next(columns10)]

    currencyDict = []
    methodDict = []
    rateDict = []
    paymentDict = []
    countryDict = []
    regionDict = []
    departmentDict = []
    gradeDict = []
    supplyclassifyDict = []
    # invoicetypeDict = []

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
        rateDict.append(data3)
    for col4 in columns4:
        data4 = {}
        for title, cell in zip(headers4, col4):
            data4[title] = cell.value
        paymentDict.append(data4)
    for col5 in columns5:
        data5 = {}
        for title, cell in zip(headers5, col5):
            data5[title] = cell.value
        countryDict.append(data5)
    for col6 in columns6:
        data6 = {}
        for title, cell in zip(headers6, col6):
            data6[title] = cell.value
        regionDict.append(data6)
    for col7 in columns7:
        data7 = {}
        for title, cell in zip(headers7, col7):
            data7[title] = cell.value
        departmentDict.append(data7)
    for col8 in columns8:
        data8 = {}
        for title, cell in zip(headers8, col8):
            data8[title] = cell.value
        gradeDict.append(data8)
    for col9 in columns9:
        data9 = {}
        for title, cell in zip(headers9, col9):
            data9[title] = cell.value
        supplyclassifyDict.append(data9)
    # for col10 in columns10:
    #     data10 = {}
    #     for title, cell in zip(headers10, col10):
    #         data10[title] = cell.value
    #     invoicetypeDict.append(data10)

    # print(currencyDict[0])
    # print(methodDict[0])
    # print(rateDict[0])
    # print(paymentDict[0])

    df = pd.read_excel(customer_filepath)
    # null setting
    df = df.fillna('')
    # character conversion
    df = df.astype('str')
    for i in df.index:
        currency = df.loc[i]['结算币别']
        currency1 = currencyDict[0][currency]
        if df.loc[i]['结算方式']!='':
            method = df.loc[i]['结算方式']
            method1 = methodDict[0][method]
        else:
            method1= df.loc[i]['结算方式']
        rate = df.loc[i]['默认税率']
        rate1 = rateDict[0][rate]
        if df.loc[i]['付款条件']!='':
            payment = df.loc[i]['付款条件']
            payment1 = paymentDict[0][payment]
        else:
            payment1 = df.loc[i]['付款条件']
        if df.loc[i]['国家'] != '':
            name_country = df.loc[i]['国家']
            name_country1 = countryDict[0][name_country]
        else:
            name_country1 = df.loc[i]['国家']
        if df.loc[i]['地区'] != '':
            name_region = df.loc[i]['地区']
            name_region1 = regionDict[0][name_region]
        else:
            name_region1 = df.loc[i]['地区']
        department = df.loc[i]['负责部门']
        department1 = departmentDict[0][department]
        grade = df.loc[i]['供应商等级']
        grade1 = gradeDict[0][grade]
        supplyclassify = df.loc[i]['供应类别']
        supplyclassify1 = supplyclassifyDict[0][supplyclassify]
        # if df.loc[i]['发票类型'] != '':
        #     invoicetype = df.loc[i]['发票类型']
        #     invoicetype1 = invoicetypeDict[0][invoicetype]
        # else:
        #     invoicetype1 = df.loc[i]['发票类型']



        data = {
            "FCreateOrgId": 100,

            "FName": df.loc[i]['供应商名称'],
            "FShortName": df.loc[i]['简称'],
            "FGroup": df.loc[i]['供应商分组'],
            "FCountry": name_country1,
            "FProvincial": name_region1,
            "FZip": df.loc[i]['邮政'],
            "FSOCIALCRECODE": df.loc[i]['统一社会信用代码'],
            "FRegisterAddress": df.loc[i]['注册地址'],
            "FDeptId": department1,
            "FSupplyClassify": supplyclassify1,
            "FSupplierGrade": grade1,
            "FSettleTypeId": method1,
            "FPayCurrencyId": currency1,
            "FPayCondition": payment1,
            # "FTaxType": df.loc[i]['税分类'],
            "FInvoiceType": df.loc[i]['发票类型'],
            "FTaxRateId": rate1,
            # "FBankCode": df.loc[i]['银行账号'],
            "FBankHolder": df.loc[i]['账户名称'],
            "FOpenAddressRec": df.loc[i]['开户行地址'],
            "FOpenBankName": df.loc[i]['开户银行'],
            "FCNAPS": df.loc[i]['联行号'],
            "FBankCurrencyId": df.loc[i]['币别'],


        }
        save_data = {
            "Model": {
                "FSupplierId": 0,
                "FCreateOrgId": {
                    "FNumber": data['FCreateOrgId']
                },

                "FName": data['FName'],
                "FShortName": data['FShortName'],
                "FGroup": {
                    "FNumber": data['FGroup']
                },
                "FBaseInfo": {
                    "FCountry": {
                        "FNumber": data['FCountry']
                    },
                    "FProvincial": {
                        "FNumber": data['FProvincial']
                    },
                    "FZip": data['FZip'],
                    "FSOCIALCRECODE": data['FSOCIALCRECODE'],
                    "FRegisterAddress": data['FRegisterAddress'],
                    "FDeptId": {
                        "FNumber": data['FDeptId']
                    },
                    "FSupplyClassify": data['FSupplyClassify'],
                    "FSupplierGrade": {
                        "FNumber": data['FSupplierGrade']
                    }
                },
                "FBusinessInfo": {
                    "FSettleTypeId": {
                        "FNumber": data['FSettleTypeId']
                    },
                    "FVmiBusiness": False,
                    "FEnableSL": False
                },
                "FFinanceInfo": {
                    "FPayCurrencyId": {
                        "FNumber": data['FPayCurrencyId']
                    },
                    "FPayCondition": {
                        "FNumber": data['FPayCondition']
                    },
                    # "FTaxType": {
                    #     "FNumber": data['FTaxType']
                    # },
                    "FInvoiceType": data['FInvoiceType'],
                    "FTaxRateId": {
                        "FNUMBER": data['FTaxRateId']
                    }
                },
                "FBankInfo": [
                    {
                        # "FBankCode": data['FBankCode'],
                        "FBankHolder": data['FBankHolder'],
                        "FOpenAddressRec": data['FOpenAddressRec'],
                        "FOpenBankName": data['FOpenBankName'],
                        "FCNAPS": data['FCNAPS'],
                        "FBankCurrencyId": {
                            "FNumber": data['FBankCurrencyId']
                        },
                        "FBankIsDefault": False
                    }
                ]
            }
        }

        # 调用sdk中的保存接口
        api_sdk.Save("BD_Supplier", save_data)
    return True

if __name__ == '__main__':

    option = {"acct_id": '62f49d037697ee',
              "user_name":'于洋',
              "app_id" : '232258_100AXajE2ooX7WUP5/Qq58Tr4L3WWsoI',
               "app_secret": 'ed4939dc463142698c8459afd45e0379',
              "server_url": 'http://cellprobio.gnway.cc/k3cloud'
              }
    conversion_filepath = "D:\桌面\工作簿1.xlsx"
    customer_filepath = "D:\桌面\供应商.xlsx"
    s=saveDate(option, conversion_filepath, customer_filepath)
    print(s)


