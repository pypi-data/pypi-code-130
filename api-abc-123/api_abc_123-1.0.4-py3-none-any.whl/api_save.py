# !/usr/bin/python
# -*- coding:UTF-8 -*-
import pandas as pd
import numpy as np
from k3cloud_webapi_sdk.main import K3CloudApiSdk

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '张志', '232255_1eeC0aDJ1rGaSexHx1wrz/9tzNQZ1okE',
                   '1bb7607d115547b3b153c43959f054ee', 'http://cellprobio.gnway.cc/k3cloud')


def save_data(formid,fCreateOrgIdNum,
         fUseOrgIdNum,fNumber,
         fName,fSpecification,
         fMaterialGroup,
         f_SZSP_Assistant,
         fBaseUnitId,fIsBatchManage,
         fISMinIssueQty,fIsPurchase):

    data = {
        "Model": {
            "FMATERIALID": 0,
            "FCreateOrgId": {
                    "FNumber": fCreateOrgIdNum
            },
            "FUseOrgId": {
                "FNumber": fUseOrgIdNum
            },
            "FNumber": fNumber,
            "FName": fName,
            "FSpecification":fSpecification,
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
                "FErpClsID": "1",
                "FFeatureItem": "1",
                "FCategoryID": {
                    "FNumber": "CHLB01_SYS"
                },
                "FMaterialGroup": {
                    "FNumber": fMaterialGroup
                },
                "F_SZSP_Assistant": {
                    "FNumber": f_SZSP_Assistant
                },
                "FBaseUnitId": {
                    "FNumber": fBaseUnitId
                },
                "FTaxType": {
                    "FNumber": "WLDSFL01_SYS"
                },
                "FTaxRateId": {
                    "FNUMBER": "SL02_SYS"
                },
                "FIsPurchase": fIsPurchase,
                "FIsInventory": False,
                "FIsSubContract": False,
                "FIsSale": False,
                "FIsProduce": False,
                "FIsAsset": False,
                "FWEIGHTUNITID": {
                    "FNUMBER": "kg"
                },
                "FVOLUMEUNITID": {
                    "FNUMBER": "m"
                }
            },
            "SubHeadEntity1": {
                "FStoreUnitID": {
                    "FNumber": ""
                },
                "FUnitConvertDir": "1",
                "FIsLockStock": True,
                "FIsCycleCounting": False,
                "FCountCycle": "1",
                "FCountDay": 1,
                "FIsMustCounting": False,
                "FIsBatchManage": fIsBatchManage,
                "FIsKFPeriod": False,
                "FIsExpParToFlot": False,
                "FCurrencyId": {
                    "FNumber": "PRE001"
                },
                "FIsEnableMinStock": False,
                "FIsEnableMaxStock": False,
                "FIsEnableSafeStock": False,
                "FIsEnableReOrder": False,
                "FIsSNManage": False,
                "FIsSNPRDTracy": False,
                "FSNManageType": "1",
                "FSNGenerateTime": "1"
            },
            "SubHeadEntity2": {
                "FSaleUnitId": {
                    "FNumber": "Pcs"
                },
                "FSalePriceUnitId": {
                    "FNumber": "Pcs"
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
                    "FNumber": "Pcs"
                },
                "FPurchasePriceUnitId": {
                    "FNumber": "Pcs"
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
                "FMinPackCount": 1.0
            },
            "SubHeadEntity4": {
                "FPlanningStrategy": "1",
                "FMfgPolicyId": {
                    "FNumber": "ZZCL001_SYS"
                },
                "FFixLeadTimeType": "1",
                "FVarLeadTimeType": "1",
                "FCheckLeadTimeType": "1",
                "FOrderIntervalTimeType": "3",
                "FMaxPOQty": 100000.0,
                "FEOQ": 1.0,
                "FVarLeadTimeLotSize": 1.0,
                "FIsMrpComBill": True,
                "FIsMrpComReq": False,
                "FReserveType": "1",
                "FAllowPartAhead": False,
                "FCanDelayDays": 999,
                "FAllowPartDelay": True,
                "FPlanOffsetTimeType": "1",
                "FWriteOffQty": 1.0
            },
            "SubHeadEntity5": {
                "FProduceUnitId": {
                    "FNumber": "Pcs"
                },
                "FProduceBillType": {
                    "FNUMBER": "SCDD01_SYS"
                },
                "FIsSNCarryToParent": False,
                "FIsProductLine": False,
                "FBOMUnitId": {
                    "FNumber": "Pcs"
                },
                "FIsMainPrd": False,
                "FIsCoby": False,
                "FIsECN": False,
                "FIssueType": "1",
                "FOverControlMode": "1",
                "FMinIssueQty": 1.0,
                "FISMinIssueQty": fISMinIssueQty,
                "FIsKitting": False,
                "FIsCompleteSet": False,
                "FMinIssueUnitId": {
                    "FNUMBER": "Pcs"
                },
                "FStandHourUnitId": "3600",
                "FBackFlushType": "1",
                "FIsEnableSchedule": False
            },
            "SubHeadEntity7": {
                "FSubconUnitId": {
                    "FNumber": "Pcs"
                },
                "FSubconPriceUnitId": {
                    "FNumber": "Pcs"
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


    res=api_sdk.Save(formid, data)

    return res



def save(path):
    data = pd.read_excel(str(path))
    for i in data.index:
        print(save_data("BD_MATERIAL", 100, 100, data.loc[i]["物料编码"],
                        data.loc[i]["物料名称"], data.loc[i]["规格型号"],
                        data.loc[i]["物料分组"], int(data.loc[i]["产品大类"]), data.loc[i]["基本单位"],
                        bool(data.loc[i]["启用批号管理"]), bool(data.loc[i]["领料考虑最小发料批量"]),
                        bool(data.loc[i]["允许采购"])))


if __name__ == '__main__':
    # data = pd.read_excel('D:\\瑞至杰新建物料申请0812.xlsx')
    #
    # for i in data.index:
    #     print(save_data("BD_MATERIAL", 100, 100, data.loc[i]["物料编码"],
    #                data.loc[i]["物料名称"], data.loc[i]["规格型号"],
    #                data.loc[i]["物料分组"], int(data.loc[i]["产品大类"]), data.loc[i]["基本单位"],
    #                bool(data.loc[i]["启用批号管理"]), bool(data.loc[i]["领料考虑最小发料批量"]), bool(data.loc[i]["允许采购"])))

    pass

