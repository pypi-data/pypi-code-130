#保存
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '于洋', '232258_100AXajE2ooX7WUP5/Qq58Tr4L3WWsoI', 'ed4939dc463142698c8459afd45e0379','http://cellprobio.gnway.cc/k3cloud')
#api_sdk.Init(config_path='conf.ini', config_node='config')

current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
save_data = {"Model": {"FSupplierId": 0,
        "FCreateOrgId": {
            "FNumber": "100"
        },
        "FUseOrgId": {
            "FNumber": "100"
        },
        "FName": "花果山",
        "FShortName": "花果山",
        "FGroup": {
            "FNumber": "7"
        },
        "FCorrespondOrgId": {
            "FNumber": "100"
        },
        "FBaseInfo": {
            "FCountry": {
                "FNumber": "China"
            },
            "FProvincial": {
                "FNumber": "DQ002"
            },
            "FAddress": "东胜神州",
            "FZip": "2220000",
            "FWebSite": "东胜神州",
            "FFoundDate": "2022-08-12 00:00:00",
            "FLegalPerson": "猴子",
            "FRegisterFund": 1.0,
            "FRegisterCode": "123123",
            "FSOCIALCRECODE": "123123",
            "FTendPermit": "123123",
            "FRegisterAddress": "东胜神州",
            "FDeptId": {
                "FNumber": "BM000060"
            },
            "FSupplyClassify": "FW",
            "FSupplierGrade": {
                "FNumber": "DJ01"
            },
            "FCompanyClassify": {
                "FNumber": "GSLL04_SYS"
            },
            "FCompanyNature": {
                "FNumber": "GSXZ001_SYS"
            },
            "FCompanyScale": {
                "FNumber": "GSGM04_SYS"
            }
        },
        "FBusinessInfo": {
            "FParentSupplierId": {
                "FNumber": "101"
            },
            "FSettleTypeId": {
                "FNumber": "JSFS04_SYS"
            },
            "FProviderId": {
                "FNumber": "101"
            },
            "FVmiBusiness": False,
            "FEnableSL": False
        },
        "FFinanceInfo": {
            "FCustomerId": {
                "FNumber": "101"
            },
            "FPayCurrencyId": {
                "FNumber": "PRE001"
            },
            "FPayCondition": {
                "FNumber": "001"
            },
            "FSettleId": {
                "FNumber": "101"
            },
            "FTaxType": {
                "FNumber": "SFL02_SYS"
            },
            "FChargeId": {
                "FNumber": "101"
            },
            "FInvoiceType": "1",
            "FTaxRateId": {
                "FNUMBER": "SL02_SYS"
            }
        }
    }}

print(api_sdk.Save("BD_Supplier", save_data))
