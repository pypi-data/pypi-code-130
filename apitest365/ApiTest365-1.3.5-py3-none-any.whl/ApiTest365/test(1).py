
import pandas as pd
import numpy as np


data=pd.read_excel('D:\\瑞至杰新建物料申请0812.xlsx')




for i in data.index:
    print(Save_Test.save("BD_MATERIAL",data.loc[i][""],data.loc[i][""]))#订单号,需要填入的信息



