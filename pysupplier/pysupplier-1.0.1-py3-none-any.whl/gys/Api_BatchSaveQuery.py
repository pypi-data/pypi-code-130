#批量保存（轮询方式）
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time

def gen_seq(loop_count):
    prefix = time.strftime('%Y%m%d%H%M%S', time.localtime())
    list_num = []
    for index in range(0, loop_count):
        list_num.append(prefix + str(10000 + index + 1))
    return list_num

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '于洋', '232258_100AXajE2ooX7WUP5/Qq58Tr4L3WWsoI', 'ed4939dc463142698c8459afd45e0379','http://cellprobio.gnway.cc/k3cloud')
#api_sdk.Init(config_path='conf.ini', config_node='config')

count = 50
list_seq = gen_seq(count)
list_data = []
for i in range(0, count):
    list_data.append({
        "FCreateOrgId": {"FNumber": 100},
        "FUserOrgId": {"FNumber": 100},
        "FNumber": "Webb" + list_seq[i],
        "FName": "物料名称-" + list_seq[i]
    })
save_data = {"Model": list_data}

print(api_sdk.BatchSaveQuery("BD_Supplier", save_data))
