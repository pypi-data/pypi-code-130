"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块逻辑分发
"""
from rest_framework.views import APIView
from xj_user.services.user_detail_info_service import DetailInfoService

from ..services.thread_list_service import ThreadListService
from ..services.thread_statistic_service import StatisticsService
# from ..utils.custom_authentication_wrapper import authentication_wrapper
from ..utils.custom_response import util_response
from ..utils.join_list import JoinList


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
        data, error_text = ThreadListService.list(params)
        if error_text:
            return util_response(err=1000, msg=error_text)
        # ID列表拆分
        thread_id_list = list(set([item['id'] for item in data['list'] if item['id']]))
        user_id_list = list(set([item['user_id'] for item in data['list'] if item['user_id']]))
        # 用户数据和统计数据
        statistic_list = StatisticsService.statistic_list(id_list=thread_id_list)
        user_info_list = DetailInfoService.get_list_detail(params=None, user_id_list=user_id_list)
        # 用户数据(full_name, avatar), 统计数据(statistic),
        data['list'] = JoinList(l_list=data['list'], r_list=statistic_list, l_key="id", r_key='thread_id').left_join()
        data['list'] = JoinList(l_list=data['list'], r_list=user_info_list, l_key="user_id", r_key='user_id').left_join()
        return util_response(data=data, is_need_parse_json=True)
