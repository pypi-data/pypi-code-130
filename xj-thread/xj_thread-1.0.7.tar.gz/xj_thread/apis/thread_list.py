"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块逻辑分发
"""
import datetime
from rest_framework.views import APIView

from ..services.thread_list_service import ThreadListService
# from ..utils.custom_authentication_wrapper import authentication_wrapper
# from ..utils.custom_response import util_response
from django.http import JsonResponse


class ThreadListAPIView(APIView):
    """
    get: 信息表列表
    post: 信息表新增
    """

    # @authentication_wrapper
    def get(self, request, *args, **kwargs):
        params = request.query_params
        size = request.GET.get('size', 20)
        if int(size) > 100:
            return util_response(msg='每一页不可以超过100条', err=40225)
        print("ThreadListAPIView time 1:", datetime.datetime.now())
        # params['category_value'] = request.query_params['category']
        data, error_text = ThreadListService.list(params)
        print("ThreadListAPIView time 2:", datetime.datetime.now())
        print("ThreadListAPIView:", error_text)
        if error_text:
            return JsonResponse({'err': 1000, 'msg': error_text, 'data': data, })
        return JsonResponse({'err': 0, 'msg': 'OK', 'data': data, })
        # return util_response(data=data)
