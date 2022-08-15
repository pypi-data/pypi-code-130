from kazoo.client import KazooClient
from django.conf import settings
import json

from microutil.util import local_ip


class GlobalZkClient(object):

    zkClient = KazooClient(hosts=settings.MICRO_ZK_HOST + ':' + str(settings.MICRO_ZK_PORT))
    zkClient.start()
    if hasattr(settings, 'MICRO_ZK_HOST'):
        zk_host = settings.MICRO_ZK_HOST
    else:
        zk_host = '127.0.0.1'
    if hasattr(settings, 'MICRO_ZK_PORT'):
        zk_port = settings.MICRO_ZK_PORT
    else:
        zk_port = 2181
    if hasattr(settings, 'MICRO_HTTP_PORT'):
        micro_http_port = settings.MICRO_HTTP_PORT
    else:
        micro_http_port = 8000

    if hasattr(settings, 'MICRO_SERVICE_NAME'):
        micro_service_name = settings.MICRO_SERVICE_NAME
    else:
        micro_service_name = 'micro'
    value = json.dumps({'host': local_ip(), 'port': micro_http_port})
    # 创建服务子节点
    zkClient.create('/dubbo/' + micro_service_name + '/provider/',
                                   value.encode(), ephemeral=True, sequence=True, makepath=True)
