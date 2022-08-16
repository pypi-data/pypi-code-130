import ApiTest365.Api_Save as a
import pandas as pd
import numpy as np


data=pd.read_excel('Customer.xlsx')


for i in data.index:
    print(a.Save_Test("BD_Customer",100,100,data.loc[i]["客户编码"],
                 data.loc[i]["客户名称(中文简体)"],
                 data.loc[i]["国家名称"],data.loc[i]["联系电话"],
                 data.loc[i]["发票抬头"],data.loc[i]["纳税登记号"],
                 data.loc[i]["开户银行"],data.loc[i]["开票联系电话"],
                 data.loc[i]["开票通讯地址"],data.loc[i]["客户类别编码"],
                 data.loc[i]["客户分组编码"],data.loc[i]["结算币别"],
                 data.loc[i]["结算方式"],data.loc[i]["收款条件"],
                 data.loc[i]["发票类型"],data.loc[i]["默认税率"],
                 data.loc[i]["客户分类编码"],data.loc[i]["联系人名称"],
                 data.loc[i]["详细地址"],data.loc[i]["移动电话"],
                 data.loc[i]["销售人员名称"],data.loc[i]["销售人员部门"],
                 data.loc[i]["销售组"]))#订单号,需要填入的信息




