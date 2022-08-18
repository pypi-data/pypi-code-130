# encoding: utf-8
"""
@project: djangoModel->user_detail_info
@author: 孙楷炎
@synopsis: 用户详细信息操作
@created_time: 2022/6/27 19:42
"""
from rest_framework.views import APIView

from xj_user.services.user_detail_info_service import DetailInfoService, util_response
from xj_user.services.user_service import UserService


# 列表
class getInfoList(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        token_serv, error_text = UserService.check_token(token)
        if error_text:
            return util_response(err=6045, msg=error_text)
        params = request.query_params
        data, err_txt = DetailInfoService.get_info_list(params)
        if not error_text:
            return util_response(data=data)
        return util_response(err=47767, msg=error_text)


# 小程序用户调用
class getInfo(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        token_serv, error_text = UserService.check_token(token)
        if error_text:
            return util_response(err=6045, msg=error_text)
        params = request.query_params.copy()
        params.setdefault("user_id", token_serv['user_id'])
        data, err_txt = DetailInfoService.get_info(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)


class createInfo(APIView):
    def post(self, request):
        return DetailInfoService.create_detail_info(request)


class editInfo(APIView):
    def post(self, request):
        return DetailInfoService.update_detail_info(request)
