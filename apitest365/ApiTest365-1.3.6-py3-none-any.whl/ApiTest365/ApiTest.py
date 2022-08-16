from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time

def save_data(FCreateOrgId,FUseOrgId,FNumber,FName,FINVOICETITLE,FTAXREGISTERCODE,FINVOICEBANKNAME,FINVOICETEL,FINVOICEBANKACCOUNT,FINVOICEADDRESS,FCustTypeId,FGroup,FTRADINGCURRID,FSETTLETYPEID,FRECCONDITIONID,FTaxRate,FMOBILE,FSALDEPTID,FSALGROUPID,FSELLER ):
    myitem={
        "Model": {
            "FCreateOrgId": {
                "FNumber": FCreateOrgId
            },
            "FNumber": FNumber,
            "FUseOrgId": {
                "FNumber": FUseOrgId
            },
            "FName": FName,
            },
        "FINVOICETITLE": FINVOICETITLE,
        "FTAXREGISTERCODE": FTAXREGISTERCODE,
        "FINVOICEBANKNAME": FINVOICEBANKNAME,
        "FINVOICETEL": FINVOICETEL,
        "FINVOICEBANKACCOUNT": FINVOICEBANKACCOUNT,
        "FINVOICEADDRESS": FINVOICEADDRESS,
        "FCustTypeId": {
            "FNumber": FCustTypeId
        },
        "FGroup": {
            "FNumber": FGroup
        },
        "FTRADINGCURRID": {
            "Fname": FTRADINGCURRID
        },
        "FSALDEPTID": FSALDEPTID,
        "FSALGROUPID":FSALGROUPID,
        "FSELLER":FSELLER ,
            "FSETTLETYPEID": {
            "Fname": FSETTLETYPEID
        },
        "FRECCONDITIONID": {
            "Fname": FRECCONDITIONID
        },
        "FTaxRate": {
            "FNumber": FTaxRate
        },
        "FT_BD_CUSTCONTACT":{
                "FMOBILE": FMOBILE
        }
    }
    return myitem
def save_api(FCreateOrgId,FUseOrgId,FNumber,FName,FINVOICETITLE,FTAXREGISTERCODE,FINVOICEBANKNAME,FINVOICETEL,FINVOICEBANKACCOUNT,FINVOICEADDRESS,FCustTypeId,FGroup,FTRADINGCURRID,FSETTLETYPEID,FRECCONDITIONID,FTaxRate,FMOBILE,FSALDEPTID,FSALGROUPID,FSELLER ,X_KDApi_AcctID,X_KDApi_UserName,X_KDApi_AppID,X_KDApi_AppSec,X_KDApi_ServerUrl):
    # !/usr/bin/python
    # -*- coding:UTF-8 -*-
    # 首先构造一个SDK实例
    api_sdk = K3CloudApiSdk()

    # 然后初始化SDK，需指定相关参数，否则会导致SDK初始化失败而无法使用：

    # 初始化方案一：Init初始化方法，使用conf.ini配置文件
    # config_path:配置文件的相对或绝对路径，建议使用绝对路径
    # config_node:配置文件中的节点名称
    # api_sdk.Init(config_path='conf.ini', config_node='config')

    # 初始化方案二（新增）：InitConfig初始化方法，直接传参，不使用配置文件
    # acct_id:第三方系统登录授权的账套ID,user_name:第三方系统登录授权的用户,app_id:第三方系统登录授权的应用ID,app_sec:第三方系统登录授权的应用密钥
    # server_url:k3cloud环境url(仅私有云环境需要传递),lcid:账套语系(默认2052),org_num:组织编码(启用多组织时配置对应的组织编码才有效)
    api_sdk.InitConfig("X_KDApi_AcctID","许雯琪", "232256_3f1r48FtTMmW4W9sWf3C0z0K7rQXWqNv",
                       "322353d1dfc844a086d8376cc6f70bf6",  "http://cellprobio.gnway.cc/k3cloud")

    # 此处仅构造保存接口的部分字段数据示例，使用时请参考WebAPI具体接口的实际参数列表
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())

    # 调用sdk中的保存接口
    info = api_sdk.Save("BD_Customer", save_data(FCreateOrgId,FUseOrgId,FNumber,FName,FINVOICETITLE,FTAXREGISTERCODE,FINVOICEBANKNAME,FINVOICETEL,FINVOICEBANKACCOUNT,FINVOICEADDRESS,FCustTypeId,FGroup,FTRADINGCURRID,FSETTLETYPEID,FRECCONDITIONID,FTaxRate,FMOBILE,FSALDEPTID,FSALGROUPID,FSELLER ))
    return(info)
if __name__ == '__main__':
    api_sdk = K3CloudApiSdk()
    api_sdk.InitConfig("62f49d037697ee", "许雯琪", "232256_3f1r48FtTMmW4W9sWf3C0z0K7rQXWqNv",
                       "322353d1dfc844a086d8376cc6f70bf6", "http://cellprobio.gnway.cc/k3cloud")
    data = save_data(100,100, "C008054", "浙江亦高生物科技有限公司", "浙江亦高生物科技有限公司","91330402MA7HRCAE3Q", "中国农业银行股份有限公司嘉兴科技支行", "15988314985",
              19380401040011520, "浙江省嘉兴市南湖区大桥镇凌公塘路3339号南湖科创中心8号楼209室", 2, "OEM客户", "人民币", "电汇", "预付100%",
              13.0000000000,  17769612127,"销售部","销售组","销售员")
    res = api_sdk.Save("BD_Customer",data)