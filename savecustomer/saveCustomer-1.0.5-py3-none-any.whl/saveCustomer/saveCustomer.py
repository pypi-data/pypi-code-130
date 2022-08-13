#!/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time
# 首先构造一个SDK实例
def saveDate(save_data,option):
    api_sdk = K3CloudApiSdk()
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    api_sdk.InitConfig(acct_id=option['acct_id'],user_name=option['user_name'],app_id=option['app_id'],app_secret=option['app_secret'],server_url=option['server_url'])
    # 调用sdk中的保存接口
    res = api_sdk.Save("BD_Customer", save_data)
    return(res)
if __name__ == '__main__':
    option = {"acct_id": '62f49d037697ee',
              "user_name":'刘丹',
              "app_id" : '232257_Wefp3YHozvHe38WFTfSM5byN1t7W0qMv',
               "app_secret": '756d9bc9a44441559a5121b54dd0a4ff',
              "server_url": 'http://cellprobio.gnway.cc/k3cloud'
              }
    save_data = {
        "Model": {
            "FCUSTID": 0,
            "FCreateOrgId": {
                "FNumber": "100"
            },
            "FUseOrgId": {
                "FNumber": "100"
            },
            "FName": "刘丹客户",
            "FCOUNTRY": {
                "FNumber": "China"
            },
            "FINVOICETITLE": "刘丹客户",
            "FIsGroup": "false",
            "FIsDefPayer": "false",
            "FCustTypeId": {
                "FNumber": "LB05"
            },
            "FGroup": {
                "FNumber": "4"
            },
            "FTRADINGCURRID": {
                "FNumber": "PRE001"
            },
            "FSETTLETYPEID": {
                "FNumber": "JSFS04_SYS"
            },
            "FRECCONDITIONID": {
                "FNumber": "SKTJ04_SP"
            },
            "FInvoiceType": "1",
            "FTaxType": {
                "FNumber": "SFL02_SYS"
            },
            "FPriority": 1,
            "FTaxRate": {
                "FNumber": "SL02_SYS"
            },
            "FISCREDITCHECK": "true",
            "FIsTrade": "true",
            "FUncheckExpectQty": "false",
            "F_SZSP_KHFL": {
                "FNumber": "FL01"
            },
            "FT_BD_CUSTOMEREXT": {
                "FEnableSL": "false",
                "FSettleId": {
                    "FNUMBER": "C000005"
                },
                "FChargeId": {
                    "FNUMBER": "C000005"
                },
                "FALLOWJOINZHJ": "false"
            },
            "FT_BD_CUSTBANK": [
                {
                    "FCOUNTRY1": {
                        "FNumber": "China"
                    },
                    "FBANKCODE": "123",
                    "FACCOUNTNAME": "钱钱钱",
                    "FOpenAddressRec": "123",
                    "FOPENBANKNAME": "钱钱钱",
                    "FCNAPS": "111",
                    "FCURRENCYID": {
                        "FNumber": "PRE001"
                    },
                    "FISDEFAULT1": "false"
                }
            ]
        }
    }
    saveDate(save_data,option)