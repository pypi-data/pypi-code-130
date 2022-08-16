from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time

def save_data(FNumber,FName,FCOUNTRY):
    myitem={"Model":
        {"FCUSTID": 0,
        "FCreateOrgId": {
            "FNumber": FNumber
        },
        "FUseOrgId": {
            "FNumber": FNumber
        },
        "FName": FName,
        "FCOUNTRY": {
            "FNumber": FCOUNTRY
        },
    }
    }
    return myitem


def save_api(FNumber,FName,FCOUNTRY):
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
    api_sdk.InitConfig('62f49d037697ee', '许雯琪', '232256_3f1r48FtTMmW4W9sWf3C0z0K7rQXWqNv',
                       '322353d1dfc844a086d8376cc6f70bf6', 'http://cellprobio.gnway.cc/k3cloud')

    # 此处仅构造保存接口的部分字段数据示例，使用时请参考WebAPI具体接口的实际参数列表
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())

    # 调用sdk中的保存接口
    info = api_sdk.Save("BD_Customer", save_data(FNumber,FName,FCOUNTRY))
    return info