# !/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time


def save(formid,fCreateOrgIdNum,
         fUseOrgIdNum,fNumber,
         fName,fSpecification,fMaterialGroup,
         f_SZSP_Assistant,fBaseUnitId,
         fOverControlMode,fErpClsID,
         fIsBatchManage,fISMinIssueQty):
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())

    api_sdk = K3CloudApiSdk()

    api_sdk.InitConfig('62f49d037697ee','张志','232255_1eeC0aDJ1rGaSexHx1wrz/9tzNQZ1okE','1bb7607d115547b3b153c43959f054ee','http://cellprobio.gnway.cc/k3cloud')

    data = {
    "NeedUpDateFields": [],
    "NeedReturnFields": [],
    "IsDeleteEntry": "true",
    "SubSystemId": "",
    "IsVerifyBaseDataField": "false",
    "IsEntryBatchFill": "true",
    "ValidateFlag": "true",
    "NumberSearch": "true",
    "IsAutoAdjustField": "false",
    "InterationFlags": "",
    "IgnoreInterationFlag": "",
    "IsControlPrecision": "false",
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
        "FSpecification": fSpecification,
        "FMnemonicCode": "",
        "FOldNumber": "",
        "FDescription": "",
        "FMaterialGroup": {
            "FNumber": fMaterialGroup
        },
        "FDSMatchByLot": "false",
        "FImgStorageType": "",
        "FIsSalseByNet": "false",
        "FForbidReson": "",
        "FExtVar": "",
        "F_SZSP_Assistant": {
            "FNumber": f_SZSP_Assistant
        },
        "F_SZSP_Decimal": 0,
        "F_SZSP_Decimal1": 0,
        "F_SZSP_SBXMH": {
            "FNumber": ""
        },
        "F_SZSP_Decimal2": 0,
        "F_SZSP_MJXMH": {
            "FNumber": ""
        },
        "FSubHeadEntity": {
            "FEntryId": 0,
            "FIsControlSal": "false",
            "FLowerPercent": 0,
            "FUpPercent": 0,
            "FCalculateBase": "",
            "FMaxSalPrice_CMK": 0,
            "FMinSalPrice_CMK": 0,
            "FIsAutoRemove": "false",
            "FIsMailVirtual": "false",
            "FIsFreeSend": "",
            "FTimeUnit": "",
            "FRentFreeDura": 0,
            "FPricingStep": 0,
            "FMinRentDura": 0,
            "FRentBeginPrice": 0,
            "FPriceType": "",
            "FRentStepPrice": 0,
            "FDepositAmount": 0,
            "FLogisticsCount": 0,
            "FRequestMinPackQty": 0,
            "FMinRequestQty": 0,
            "FRetailUnitID": {
                "FNUMBER": ""
            },
            "FIsPrinttAg": "false",
            "FIsAccessory": "false"
        },
        "SubHeadEntity": {
            "FEntryId": 0,
            "FBARCODE": "",
            "FErpClsID": fErpClsID,
            "FFeatureItem": "",
            "FCONFIGTYPE": "",
            "FCategoryID": {
                "FNumber": ""
            },
            "FTaxType": {
                "FNumber": ""
            },
            "FTaxRateId": {
                "FNUMBER": ""
            },
            "FBaseUnitId": {
                "FNumber": fBaseUnitId
            },
            "FIsPurchase": "false",
            "FIsInventory": "false",
            "FIsSubContract": "false",
            "FIsSale": "false",
            "FIsProduce": "false",
            "FIsAsset": "false",
            "FGROSSWEIGHT": 0,
            "FNETWEIGHT": 0,
            "FWEIGHTUNITID": {
                "FNUMBER": ""
            },
            "FLENGTH": 0,
            "FWIDTH": 0,
            "FHEIGHT": 0,
            "FVOLUME": 0,
            "FVOLUMEUNITID": {
                "FNUMBER": ""
            },
            "FSuite": "",
            "FCostPriceRate": 0,
            "FUseOrgId1": {
                "FNumber": ""
            }
        },
        "SubHeadEntity1": {
            "FEntryId": 0,
            "FStoreUnitID": {
                "FNumber": ""
            },
            "FAuxUnitID": {
                "FNumber": ""
            },
            "FUnitConvertDir": "",
            "FStockId": {
                "FNumber": ""
            },
            "FStockPlaceId": {
                "FSTOCKPLACEID__FF100001": {
                    "FNumber": ""
                },
                "FSTOCKPLACEID__FF100002": {
                    "FNumber": ""
                },
                "FSTOCKPLACEID__FF100004": {
                    "FNumber": ""
                },
                "FSTOCKPLACEID__FF100005": {
                    "FNumber": ""
                },
                "FSTOCKPLACEID__FF100006": {
                    "FNumber": ""
                }
            },
            "FIsLockStock": "false",
            "FIsCycleCounting": "false",
            "FCountCycle": "",
            "FCountDay": 0,
            "FIsMustCounting": "false",
            "FIsBatchManage": fIsBatchManage,
            "FBatchRuleID": {
                "FNumber": ""
            },
            "FIsKFPeriod": "false",
            "FIsExpParToFlot": "false",
            "FExpUnit": "",
            "FExpPeriod": 0,
            "FOnlineLife": 0,
            "FRefCost": 0,
            "FCurrencyId": {
                "FNumber": ""
            },
            "FIsEnableMinStock": "false",
            "FIsEnableMaxStock": "false",
            "FIsEnableSafeStock": "false",
            "FIsEnableReOrder": "false",
            "FMinStock": 0,
            "FSafeStock": 0,
            "FReOrderGood": 0,
            "FEconReOrderQty": 0,
            "FMaxStock": 0,
            "FIsSNManage": "false",
            "FIsSNPRDTracy": "false",
            "FSNCodeRule": {
                "FNumber": ""
            },
            "FSNUnit": {
                "FNumber": ""
            },
            "FSNManageType": "",
            "FSNGenerateTime": "",
            "FBoxStandardQty": 0,
            "FUseOrgId2": {
                "FNumber": ""
            }
        },
        "SubHeadEntity2": {
            "FEntryId": 0,
            "FSaleUnitId": {
                "FNumber": ""
            },
            "FSalePriceUnitId": {
                "FNumber": ""
            },
            "FOrderQty": 0,
            "FMinQty": 0,
            "FMaxQty": 0,
            "FOutStockLmtH": 0,
            "FOutStockLmtL": 0,
            "FAgentSalReduceRate": 0,
            "FIsATPCheck": "false",
            "FIsReturnPart": "false",
            "FIsInvoice": "false",
            "FIsReturn": "false",
            "FAllowPublish": "false",
            "FISAFTERSALE": "false",
            "FISPRODUCTFILES": "false",
            "FISWARRANTED": "false",
            "FWARRANTY": 0,
            "FWARRANTYUNITID": "",
            "FOutLmtUnit": "",
            "FTaxCategoryCodeId": {
                "FNUMBER": ""
            },
            "FSalGroup": {
                "FNumber": ""
            },
            "FIsTaxEnjoy": "false",
            "FTaxDiscountsType": "",
            "FUseOrgId3": {
                "FNumber": ""
            },
            "FUnValidateExpQty": "false"
        },
        "SubHeadEntity3": {
            "FEntryId": 0,
            "FBaseMinSplitQty": 0,
            "FPurchaseUnitId": {
                "FNumber": ""
            },
            "FPurchasePriceUnitId": {
                "FNumber": ""
            },
            "FPurchaseOrgId": {
                "FNumber": ""
            },
            "FPurchaseGroupId": {
                "FNumber": ""
            },
            "FPurchaserId": {
                "FNumber": ""
            },
            "FDefaultVendor": {
                "FNumber": ""
            },
            "FChargeID": {
                "FNumber": ""
            },
            "FIsQuota": "false",
            "FQuotaType": "",
            "FMinSplitQty": 0,
            "FIsVmiBusiness": "false",
            "FEnableSL": "false",
            "FIsPR": "false",
            "FIsReturnMaterial": "false",
            "FIsSourceControl": "false",
            "FReceiveMaxScale": 0,
            "FReceiveMinScale": 0,
            "FReceiveAdvanceDays": 0,
            "FReceiveDelayDays": 0,
            "FPOBillTypeId": {
                "FNUMBER": ""
            },
            "FAgentPurPlusRate": 0,
            "FDefBarCodeRuleId": {
                "FNUMBER": ""
            },
            "FPrintCount": 0,
            "FMinPackCount": 0,
            "FUseOrgId4": {
                "FNumber": ""
            }
        },
        "SubHeadEntity4": {
            "FEntryId": 0,
            "FPlanMode": "",
            "FBaseVarLeadTimeLotSize": 0,
            "FPlanningStrategy": "",
            "FMfgPolicyId": {
                "FNumber": ""
            },
            "FOrderPolicy": "",
            "FPlanWorkshop": {
                "FNumber": ""
            },
            "FFixLeadTime": 0,
            "FFixLeadTimeType": "",
            "FVarLeadTime": 0,
            "FVarLeadTimeType": "",
            "FCheckLeadTime": 0,
            "FCheckLeadTimeType": "",
            "FOrderIntervalTimeType": "",
            "FOrderIntervalTime": 0,
            "FMaxPOQty": 0,
            "FMinPOQty": 0,
            "FIncreaseQty": 0,
            "FEOQ": 0,
            "FVarLeadTimeLotSize": 0,
            "FPlanIntervalsDays": 0,
            "FPlanBatchSplitQty": 0,
            "FRequestTimeZone": 0,
            "FPlanTimeZone": 0,
            "FPlanGroupId": {
                "FNumber": ""
            },
            "FATOSchemeId": {
                "FNUMBER": ""
            },
            "FPlanerID": {
                "FNumber": ""
            },
            "FIsMrpComBill": "false",
            "FCanLeadDays": 0,
            "FIsMrpComReq": "false",
            "FLeadExtendDay": 0,
            "FReserveType": "",
            "FPlanSafeStockQty": 0,
            "FAllowPartAhead": "false",
            "FCanDelayDays": 0,
            "FDelayExtendDay": 0,
            "FAllowPartDelay": "false",
            "FPlanOffsetTimeType": "",
            "FPlanOffsetTime": 0,
            "FSupplySourceId": {
                "FNumber": ""
            },
            "FTimeFactorId": {
                "FNumber": ""
            },
            "FQtyFactorId": {
                "FNumber": ""
            },
            "FProductLine": {
                "FNUMBER": ""
            },
            "FWriteOffQty": 0,
            "FPlanIdent": {
                "FNumber": ""
            },
            "FProScheTrackId": {
                "FNumber": ""
            },
            "FDailyOutQty": 0,
            "FUseOrgId7": {
                "FNumber": ""
            }
        },
        "SubHeadEntity5": {
            "FEntryId": 0,
            "FWorkShopId": {
                "FNumber": ""
            },
            "FProduceUnitId": {
                "FNumber": ""
            },
            "FFinishReceiptOverRate": 0,
            "FFinishReceiptShortRate": 0,
            "FProduceBillType": {
                "FNUMBER": ""
            },
            "FOrgTrustBillType": {
                "FNUMBER": ""
            },
            "FIsSNCarryToParent": "false",
            "FIsProductLine": "false",
            "FBOMUnitId": {
                "FNumber": ""
            },
            "FLOSSPERCENT": 0,
            "FConsumVolatility": 0,
            "FIsMainPrd": "false",
            "FIsCoby": "false",
            "FIsECN": "false",
            "FIssueType": "",
            "FBKFLTime": "",
            "FPickStockId": {
                "FNumber": ""
            },
            "FPickBinId": {
                "FPICKBINID__FF100001": {
                    "FNumber": ""
                },
                "FPICKBINID__FF100002": {
                    "FNumber": ""
                },
                "FPICKBINID__FF100004": {
                    "FNumber": ""
                },
                "FPICKBINID__FF100005": {
                    "FNumber": ""
                },
                "FPICKBINID__FF100006": {
                    "FNumber": ""
                }
            },
            "FOverControlMode": fOverControlMode,
            "FMinIssueQty": 0,
            "FISMinIssueQty": fISMinIssueQty,
            "FIsKitting": "false",
            "FIsCompleteSet": "false",
            "FDefaultRouting": {
                "FNumber": ""
            },
            "FStdLaborPrePareTime": 0,
            "FStdLaborProcessTime": 0,
            "FStdMachinePrepareTime": 0,
            "FStdMachineProcessTime": 0,
            "FMinIssueUnitId": {
                "FNUMBER": ""
            },
            "FMdlId": {
                "FNUMBER": ""
            },
            "FMdlMaterialId": {
                "FNUMBER": ""
            },
            "FStandHourUnitId": "",
            "FBackFlushType": "",
            "FFIXLOSS": 0,
            "FUseOrgId6": {
                "FNumber": ""
            },
            "FIsEnableSchedule": "false",
            "FDefaultLineId": {
                "FNUMBER": ""
            }
        },
        "SubHeadEntity7": {
            "FEntryId": 0,
            "FSubconUnitId": {
                "FNumber": ""
            },
            "FSubconPriceUnitId": {
                "FNumber": ""
            },
            "FSubBillType": {
                "FNUMBER": ""
            },
            "FUseOrgId8": {
                "FNumber": ""
            }
        },
        "SubHeadEntity6": {
            "FEntryId": 0,
            "FCheckIncoming": "false",
            "FCheckProduct": "false",
            "FCheckStock": "false",
            "FCheckReturn": "false",
            "FCheckDelivery": "false",
            "FEnableCyclistQCSTK": "false",
            "FStockCycle": 0,
            "FEnableCyclistQCSTKEW": "false",
            "FEWLeadDay": 0,
            "FIncSampSchemeId": {
                "FNUMBER": ""
            },
            "FIncQcSchemeId": {
                "FNUMBER": ""
            },
            "FInspectGroupId": {
                "FNUMBER": ""
            },
            "FInspectorId": {
                "FNUMBER": ""
            },
            "FCheckEntrusted": "false",
            "FCheckOther": "false",
            "FIsFirstInspect": "false",
            "FUseOrgId5": {
                "FNumber": ""
            },
            "FCheckReturnMtrl": "false"
        },
        "FBarCodeEntity_CMK": [
            {
                "FEntryID": 0,
                "FCodeType_CMK": "",
                "FUnitId_CMK": {
                    "FNUMBER": ""
                }
            }
        ],
        "FSpecialAttributeEntity": [
            {
                "FEntryID": 0
            }
        ],
        "FEntityAuxPty": [
            {
                "FEntryID": 0,
                "FAuxPropertyId": {
                    "FNumber": ""
                },
                "FIsEnable1": "false",
                "FIsComControl": "false",
                "FIsAffectPrice1": "false",
                "FIsAffectPlan1": "false",
                "FIsAffectCost1": "false",
                "FIsMustInput": "false",
                "FUseOrgId11": {
                    "FNumber": ""
                },
                "FValueType": ""
            }
        ],
        "FEntityInvPty": [
            {
                "FEntryID": 0,
                "FUseOrgId10": {
                    "FNumber": ""
                },
                "FInvPtyId": {
                    "FNumber": ""
                },
                "FIsEnable": "false",
                "FIsAffectPrice": "false",
                "FIsAffectPlan": "false",
                "FIsAffectCost": "false"
            }
        ]
    }
}


    res=api_sdk.Save(formid, data)

    return res


if __name__ == '__main__':
    pass

