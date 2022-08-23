import pandas as pd
import numpy as np

from k3cloud_webapi_sdk.main import K3CloudApiSdk

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '张志', '232255_1eeC0aDJ1rGaSexHx1wrz/9tzNQZ1okE',
                   '1bb7607d115547b3b153c43959f054ee', 'http://cellprobio.gnway.cc/k3cloud')
#数据保存方法
def save(formid,data):
    for i in data.index:
        if str(data.loc[i]["物料编码"])!="":
            model={
                "Model": {
                    "FMATERIALID": 0,
                    "FCreateOrgId": {
                        "FNumber": "100"
                    },
                    "FUseOrgId": {
                        "FNumber": "100"
                    },
                    "FNumber": str(data.loc[i]["物料编码"]),
                    "FName": str(data.loc[i]["物料名称"]),
                    "FSpecification": str(data.loc[i]["规格型号"]),
                    "FDescription": str(data.loc[i]["物料描述"]),
                    "FMaterialGroup": {
                        "FNumber": str(data.loc[i]["物料分组"])
                    },
                    "FDSMatchByLot": False,
                    "FImgStorageType": "A",
                    "FIsSalseByNet": False,
                    "F_SZSP_Decimal": 1.0,
                    "F_SZSP_Decimal1": 1.0,
                    "FSubHeadEntity": {
                        "FIsControlSal": False,
                        "FIsAutoRemove": False,
                        "FIsMailVirtual": False,
                        "FTimeUnit": "H",
                        "FIsPrinttAg": False,
                        "FIsAccessory": False
                    },
                    "SubHeadEntity": {
                        "FErpClsID":  str(data.loc[i]["物料属性"]),
                        "FFeatureItem": "1",
                        "FCategoryID": {
                            "FNumber": str(data.loc[i]["存货类别"])
                        },
                        "FTaxType": {
                            "FNumber": "WLDSFL01_SYS"
                        },
                        "FTaxRateId": {
                            "FNUMBER": str(data.loc[i]["默认税率%"])
                        },
                        "FBaseUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FGROSSWEIGHT":  str(data.loc[i]["毛重"]),
                        "FNETWEIGHT": str(data.loc[i]["净重"]),
                        "FWEIGHTUNITID": {
                            "FNUMBER": str(data.loc[i]["重量单位"])
                        },
                        "FLENGTH": str(data.loc[i]["长"]),
                        "FWIDTH": str(data.loc[i]["宽"]),
                        "FHEIGHT": str(data.loc[i]["高"]),
                        "FVOLUME": str(data.loc[i]["体积"]),
                        "FVOLUMEUNITID": {
                            "FNUMBER": str(data.loc[i]["尺寸单位"])
                        }
                    },
                    "SubHeadEntity1": {
                        "FStoreUnitID": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FUnitConvertDir": "1",
                        "FIsLockStock": True,
                        "FIsCycleCounting": False,
                        "FCountCycle": "1",
                        "FCountDay": 1,
                        "FIsMustCounting": False,
                        "FIsBatchManage": str(data.loc[i]["启用批号管理"]),
                        "FIsKFPeriod": "False" if str(data.loc[i]["启用保质期"])=="" else
                        str(data.loc[i]["启用保质期"]),
                        "FIsExpParToFlot": False,
                        "FCurrencyId": {
                            "FNumber": "PRE001"
                        },
                        "FIsEnableMinStock": False,
                        "FIsEnableMaxStock": False,
                        "FIsEnableSafeStock": True,
                        "FIsEnableReOrder": False,
                        "FSafeStock": str(data.loc[i]["安全库存"]),
                        "FIsSNManage": False,
                        "FIsSNPRDTracy": False,
                        "FSNManageType": "1",
                        "FSNGenerateTime": "1"
                    },
                    "FTaxCategoryCodeId": {
                        "FNUMBER": str(data.loc[i]["税收分类"])
                    },
                    "SubHeadEntity2": {
                        "FSaleUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FSalePriceUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FMaxQty": 100000.0,
                        "FIsATPCheck": False,
                        "FIsReturnPart": False,
                        "FIsInvoice": False,
                        "FIsReturn": True,
                        "FAllowPublish": False,
                        "FISAFTERSALE": True,
                        "FISPRODUCTFILES": True,
                        "FISWARRANTED": False,
                        "FWARRANTYUNITID": "D",
                        "FOutLmtUnit": "SAL",
                        "FIsTaxEnjoy": False,
                        "FUnValidateExpQty": False
                    },
                    "SubHeadEntity3": {
                        "FPurchaseUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FPurchasePriceUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FIsQuota": False,
                        "FQuotaType": "1",
                        "FIsVmiBusiness": False,
                        "FEnableSL": False,
                        "FIsPR": False,
                        "FIsReturnMaterial": True,
                        "FIsSourceControl": False,
                        "FPOBillTypeId": {
                            "FNUMBER": "CGSQD01_SYS"
                        },
                        "FPrintCount": 1,
                        "FMinPackCount": str(data.loc[i]["最小包装数"])
                    },
                    "SubHeadEntity4": {
                        "FPlanningStrategy": "" if str(data.loc[i]["计划策略"])=="" else
                        str(data.loc[i]["计划策略"]),
                        "FMfgPolicyId": {
                            "FNumber": "ZZCL001_SYS"
                        },
                        "FFixLeadTime": str(data.loc[i]["固定提前期"]),
                        "FOrderPolicy": str(data.loc[i]["订货策略"]),
                        "FVarLeadTime": str(data.loc[i]["变动提前期"]),
                        "FVarLeadTimeType": "1",
                        "FCheckLeadTimeType": "1",
                        "FOrderIntervalTimeType": str(data.loc[i]["订货间隔期单位"]) if str(data.loc[i]["订货策略"])=="1" else "3",
                        "FOrderIntervalTime": "1" if str(data.loc[i]["订货策略"])=="1" else
                        str(data.loc[i]["变动提前期"]),
                        "FMaxPOQty": str(data.loc[i]["最大订货量"]),
                        "FMinPOQty": str(data.loc[i]["最小订货量"]),
                        "FIncreaseQty": str(data.loc[i]["最小包装量"]),
                        "FEOQ": "1" if str(data.loc[i]["固定/经济批量"])=="" else
                        str(data.loc[i]["固定/经济批量"]),
                        "FVarLeadTimeLotSize": "1" if str(data.loc[i]["变动提前期批量"])=="" else
                        str(data.loc[i]["变动提前期批量"]),
                        "FIsMrpComBill": True,
                        "FIsMrpComReq": False,
                        "FReserveType": "1",
                        "FPlanSafeStockQty": 100.0,
                        "FAllowPartAhead": False,
                        "FCanDelayDays": 999,
                        "FAllowPartDelay": True,
                        "FPlanOffsetTimeType": "1",
                        "FWriteOffQty": 1.0
                    },
                    "SubHeadEntity5": {
                        "FProduceUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FProduceBillType": {
                            "FNUMBER": "SCDD01_SYS"
                        },
                        "FIsSNCarryToParent": False,
                        "FIsProductLine": False,
                        "FBOMUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FIsMainPrd": False,
                        "FIsCoby": False,
                        "FIsECN": False,
                        "FIssueType": "1",
                        "FOverControlMode": str(data.loc[i]["超发控制方式"]),
                        "FMinIssueQty": "1" if str(data.loc[i]["最小发料批量"])=="" else
                        str(data.loc[i]["最小发料批量"]),
                        "FISMinIssueQty": "False" if str(data.loc[i]["领料考虑最小发料批量"])=="" else
                        str(data.loc[i]["领料考虑最小发料批量"]),
                        "FIsKitting": False,
                        "FIsCompleteSet": False,
                        "FMinIssueUnitId": {
                            "FNUMBER": str(data.loc[i]["基本单位"])
                        },
                        "FStandHourUnitId": "3600",
                        "FBackFlushType": "1",
                        "FIsEnableSchedule": False
                    },
                    "SubHeadEntity7": {
                        "FSubconUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        },
                        "FSubconPriceUnitId": {
                            "FNumber": str(data.loc[i]["基本单位"])
                        }
                    },
                    "SubHeadEntity6": {
                        "FCheckIncoming": False,
                        "FCheckProduct": False,
                        "FCheckStock": False,
                        "FCheckReturn": False,
                        "FCheckDelivery": False,
                        "FEnableCyclistQCSTK": False,
                        "FEnableCyclistQCSTKEW": False,
                        "FCheckEntrusted": False,
                        "FCheckOther": False,
                        "FIsFirstInspect": False,
                        "FCheckReturnMtrl": False
                    },
                    "FEntityInvPty": [
                        {
                            "FInvPtyId": {
                                "FNumber": "01"
                            },
                            "FIsEnable": True,
                            "FIsAffectPrice": False,
                            "FIsAffectPlan": False,
                            "FIsAffectCost": False
                        },
                        {
                            "FInvPtyId": {
                                "FNumber": "02"
                            },
                            "FIsEnable": True,
                            "FIsAffectPrice": False,
                            "FIsAffectPlan": False,
                            "FIsAffectCost": False
                        },
                        {
                            "FInvPtyId": {
                                "FNumber": "03"
                            },
                            "FIsEnable": False,
                            "FIsAffectPrice": False,
                            "FIsAffectPlan": False,
                            "FIsAffectCost": False
                        },
                        {
                            "FInvPtyId": {
                                "FNumber": "04"
                            },
                            "FIsEnable": False,
                            "FIsAffectPrice": False,
                            "FIsAffectPlan": False,
                            "FIsAffectCost": False
                        },
                        {
                            "FInvPtyId": {
                                "FNumber": "06"
                            },
                            "FIsEnable": False,
                            "FIsAffectPrice": False,
                            "FIsAffectPlan": False,
                            "FIsAffectCost": False
                        }
                    ]
                }
            }
            res=api_sdk.Save(formid,model)
            print(res)

#对数据进行处理
def dataPreprocess(data,Cpath):

    '''

    :param data:  excel表中数据
    :param Cpath: 配置表的路径
    :return: 将处理好的数据返回
    '''



    data1 = pd.read_excel(Cpath)
    data1 = np.array(data1)
    d1 = dict(data1)

    data2 = pd.read_excel(Cpath,"基本单位")
    data2 = np.array(data2)
    d2 = dict(data2)

    data3 = pd.read_excel(Cpath, "物料属性")
    data3 = np.array(data3)
    d3 = dict(data3)

    data4 = pd.read_excel(Cpath, "产品大类")
    data4 = np.array(data4)
    d4 = dict(data4)

    data5 = pd.read_excel(Cpath, "默认税率")
    data5 = np.array(data5)
    d5 = dict(data5)

    data6 = pd.read_excel(Cpath, "超发控制方式")
    data6 = np.array(data6)
    d6 = dict(data6)

    data7 = pd.read_excel(Cpath, "订货策略")
    data7 = np.array(data7)
    d7 = dict(data7)

    data8 = pd.read_excel(Cpath, "订货间隔期单位")
    data8 = np.array(data8)
    d8 = dict(data8)

    data9 = pd.read_excel(Cpath, "计划策略")
    data9 = np.array(data9)
    d9 = dict(data9)

    x = 0

    for i in data["存货类别"]:
        if i=="":
            pass
        else:
            data.loc[x,"存货类别"]=d1[i]
            x += 1

    a = 0

    for i in data["基本单位"]:

        if i=="":
            data.loc[a, "基本单位"] ="Pcs"
        else:
            data.loc[a, "基本单位"] = d2[i]

        a += 1

    b = 0

    for i in data["物料属性"]:
        if i=="":
            pass
        else:

            data.loc[b, "物料属性"] = d3[i]

            b += 1

    c = 0

    for i in data["重量单位"]:
        if i=="":
            data.loc[c, "重量单位"] ="kg"
        else:
            data.loc[c, "重量单位"] = d2[i]

        c += 1

    d = 0

    for i in data["尺寸单位"]:
        if i=="":
            data.loc[d, "尺寸单位"] = "m"
        else:
            data.loc[d, "尺寸单位"] = d2[i]
        d += 1

    e = 0

    for i in data["产品大类"]:
        if i == "":
            data.loc[e, "产品大类"] = ""
        else:
            data.loc[e, "产品大类"] = d4[i]
        e += 1

    f = 0

    for i in data["默认税率%"]:
        if i == "":
            data.loc[f, "默认税率%"] = "SL02_SYS"
        else:
            data.loc[f, "默认税率%"] = d5[i]
        f += 1

    g = 0

    for i in data["超发控制方式"]:
        if i == "":
            data.loc[g, "超发控制方式"] = ""
        else:
            data.loc[g, "超发控制方式"] = d6[i]
        g += 1

    h = 0

    for i in data["订货策略"]:
        if i == "":
            data.loc[h, "订货策略"] = ""
        else:
            data.loc[h, "订货策略"] = d7[i]
        h += 1

    l = 0

    for i in data["订货间隔期单位"]:
        if i == "":
            data.loc[l, "订货间隔期单位"] = ""
        else:
            data.loc[l, "订货间隔期单位"] = d8[i]
        l += 1

    n = 0

    for i in data["计划策略"]:
        if i == "":
            data.loc[n, "计划策略"] = ""
        else:
            data.loc[n, "计划策略"] = d9[i]
        n += 1


    return data


def saveData(path,zPath):
    resource = pd.read_excel(path)

    resource = resource.fillna("")

    resource = resource.replace("否", False)
    resource = resource.replace("是", True)

    data = dataPreprocess(resource,zPath)

    save("BD_MATERIAL", data)


if __name__ == '__main__':
    resource = pd.read_excel("D:\物料-2022-8-18(1).xlsx")

    resource=resource.fillna("")

    resource = resource.replace("否", False)
    resource = resource.replace("是", True)

    data=dataPreprocess(resource,"D:\字典.xlsx")

    save("BD_MATERIAL", data)


