#操作接口
from k3cloud_webapi_sdk.main import K3CloudApiSdk

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '于洋', '232258_100AXajE2ooX7WUP5/Qq58Tr4L3WWsoI', 'ed4939dc463142698c8459afd45e0379','http://cellprobio.gnway.cc/k3cloud')
#api_sdk.Init(config_path='conf.ini', config_node='config')

#禁用
print(api_sdk.ExcuteOperation("BD_Supplier", "Forbid", {"Numbers": ["Webb2021031216102410001"]}))
#反禁用
print(api_sdk.ExcuteOperation("BD_Supplier", "Enable", {"Numbers": ["Webb2021031216102410001"]}))
