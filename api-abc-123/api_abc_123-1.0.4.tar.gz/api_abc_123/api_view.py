#!/usr/bin/python
# -*- coding:UTF-8 -*-

from k3cloud_webapi_sdk.main import K3CloudApiSdk

api_sdk = K3CloudApiSdk()

api_sdk.InitConfig('62f49d037697ee', '张志', '232255_1eeC0aDJ1rGaSexHx1wrz/9tzNQZ1okE',
                   '1bb7607d115547b3b153c43959f054ee', 'http://cellprobio.gnway.cc/k3cloud')


def data_view(formid,number,isSortBySeq):
    data={
    "CreateOrgId": 0,
    "Number": number,
    "Id": "",
    "IsSortBySeq": isSortBySeq
}
    res=api_sdk.View(formid,data)

    return res



if __name__ == '__main__':
#     d=['1.1.1.01.02.003.000001',
# '1.1.1.01.01.011.000001',
# '1.1.1.01.01.011.000002',
# '1.1.1.01.01.009.000003',
# '1.1.1.01.01.009.000004',
# '1.1.1.01.01.007.000001',
# '1.1.1.01.01.007.000002',
# '1.1.1.01.01.007.000003',
# '1.1.1.01.01.007.000004',
# '1.1.1.01.01.001.000001',
# '1.1.1.01.01.001.000002',
# '1.1.1.01.01.001.000003',
# ]
#
#
#     for i in d:
#         print(print(data_view("BD_MATERIAL",i,True)))

    pass
