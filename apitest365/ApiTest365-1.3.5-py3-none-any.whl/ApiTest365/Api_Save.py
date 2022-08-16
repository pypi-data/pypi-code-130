#!/usr/bin/python
# -*- coding:UTF-8 -*-

from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time
def Save_Test(FCreateOrgId,FUseOrgId,FNumber,FName,FCOUNTRY,FTEL,FINVOICETITLE,FTAXREGISTERCODE,FINVOICEBANKNAME,FINVOICETEL,FINVOICEBANKACCOUNT,FINVOICEADDRESS,FCustTypeId,FGroup,FTRADINGCURRID,FSETTLETYPEID,FRECCONDITIONID,FInvoiceType,FTaxRate,F_SZSP_KHFL,FContactId,FADDRESS1,FMOBILE,FSELLER,FSALDEPTID,FSALGROUPID,X_KDApi_AcctID,X_KDApi_UserName,X_KDApi_AppID,X_KDApi_AppSec,X_KDApi_ServerUrl):

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
    api_sdk.InitConfig(X_KDApi_AcctID, X_KDApi_UserName, X_KDApi_AppID, X_KDApi_AppSec,X_KDApi_ServerUrl)

    # 此处仅构造保存接口的部分字段数据示例，使用时请参考WebAPI具体接口的实际参数列表
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    save_data = {
        "Model": {
        "FCreateOrgId": {
            "FNumber": FCreateOrgId
        },
        "FUseOrgId": {
            "FNumber": FUseOrgId
        },
        "FNumber": FNumber,
        "FName": FName,
        "FCOUNTRY": {
            "FNumber": FCOUNTRY
        },
        "FTEL": FTEL,
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
            "FNumber": FTRADINGCURRID
        },
        "FSETTLETYPEID": {
            "FNumber": FSETTLETYPEID
        },
        "FRECCONDITIONID": {
            "FNumber": FRECCONDITIONID
        },
        "FInvoiceType": FInvoiceType,
        "FTaxRate": {
            "FNumber": FTaxRate
        },
        "F_SZSP_KHFL": {
            "FNumber": F_SZSP_KHFL
        },
        "FT_BD_CUSTLOCATION": [
            {
                "FContactId": {
                    "FNumber": FContactId
                },
            }
        ],
        "FT_BD_CUSTCONTACT": [
            {
                "FADDRESS1": FADDRESS1,
                "FMOBILE": FMOBILE,
            }
        ],
        "FSELLER": {
            "FNumber": FSELLER
        },
        "FSALDEPTID": {
            "FNumber": FSALDEPTID
        },
        "FSALGROUPID":{
            "FNumber":FSALGROUPID
        },
    }
}

    # 调用sdk中的保存接口
    res = api_sdk.Save("BD_Customer", save_data)
    return(res)
if __name__ == '__main__':
    save = Save_Test(FCreateOrgId=100,FUseOrgId=100,FNumber='C008054',FName='浙江亦高生物科技有限公司',FCOUNTRY='China',FTEL='0571-86690968',FINVOICETITLE='浙江亦高生物科技有限公司',FTAXREGISTERCODE='91330402MA7HRCAE3Q',FINVOICEBANKNAME='中国农业银行股份有限公司嘉兴科技支行',FINVOICETEL='15988314985',FINVOICEBANKACCOUNT='19380401040011520',FINVOICEADDRESS='浙江省嘉兴市南湖区大桥镇凌公塘路3339号南湖科创中心8号楼209室',FCustTypeId='LB01',FGroup='2',FTRADINGCURRID='PRE001',FSETTLETYPEID='JSFS04_SYS',FRECCONDITIONID='SKTJ05_SP',FInvoiceType='增值税专用发票',FTaxRate='13.0000000000',F_SZSP_KHFL='FL01',FContactId='汪杨',FADDRESS1='邯郸市邯山区滏河南大街288号滏瑞特时代广场B座20层2016',FMOBILE='17769612127',FSELLER='',FSALDEPTID='',FSALGROUPID='',X_KDApi_AcctID='62f49d037697ee',X_KDApi_UserName='许雯琪',X_KDApi_AppID='232256_3f1r48FtTMmW4W9sWf3C0z0K7rQXWqNv',X_KDApi_AppSec='322353d1dfc844a086d8376cc6f70bf6',X_KDApi_ServerUrl='http://cellprobio.gnway.cc/k3cloud')