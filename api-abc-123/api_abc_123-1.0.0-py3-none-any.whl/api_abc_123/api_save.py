# !/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time


def save(formid,fCreateOrgIdNum,fUseOrgIdNum,fName):
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())

    api_sdk = K3CloudApiSdk()

    api_sdk.InitConfig('62f49d037697ee','张志','232255_1eeC0aDJ1rGaSexHx1wrz/9tzNQZ1okE','1bb7607d115547b3b153c43959f054ee','http://cellprobio.gnway.cc/k3cloud')

    data = {
    "FMATERIALID": 0,
    "Model": {
        "FCreateOrgId": {
            "FNumber": fCreateOrgIdNum
        },
        "FUseOrgId": {
            "FNumber": fUseOrgIdNum
        },
        "FNumber": "1.1.1.01"+current_time+"0000101",
        "FName": fName,
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
            "FTaxType": {
                "FNumber": "WLDSFL01_SYS"
            },
            "FTaxRateId": {
                "FNUMBER": "SL02_SYS"
            },
            "FBaseUnitId": {
                "FNumber": "Pcs"
            },
            "FIsPurchase": True,
            "FIsInventory": True,
            "FIsSubContract": False,
            "FIsSale": True,
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
                "FNumber": "Pcs"
            },
            "FUnitConvertDir": "1",
            "FIsLockStock": True,
            "FIsCycleCounting": False,
            "FCountCycle": "1",
            "FCountDay": 1,
            "FIsMustCounting": False,
            "FIsBatchManage": False,
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
            "FISMinIssueQty": False,
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


if __name__ == '__main__':
    pass

