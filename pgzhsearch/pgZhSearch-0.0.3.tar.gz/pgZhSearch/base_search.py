from django.db import models
from django.db.models import F
from django.http import JsonResponse
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib import admin
from .extract_keyword import extract_keywords as _extract_keywords
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet


# region # --- 默认检索权重设置

"""
# --- 若WEIGHT_CONF不为None, 则默认值为0, 可实现单字段检索.

# Django默认用[D, C, B, A]代表该字段的权重
WEIGHT_CONF = {
    'D': 0.2,
    'C': 0.4,
    'B': 0.6,
    'A': 0.8,
}
"""

WEIGHT_CONF = None

RANK__GTE = 0.001        # 相关性检索过滤的最小值

# endregion


# region # --- 不需要改动的变量

search_conf_name = 'search_field_conf'        # 检索配置的字段名
search_vector_field_name = 'search_vector'      # 检索字段名
search_weight_name = 'search_weight_conf'        # 检索权重配置名
search_rank__gte = 'search_rank__gte'       # 关性检索过滤的最小值
search_rank_field_name = 'search_rank'


_WEIGHTS_ORDERING = ['D', 'C', 'B', 'A']       # Django权重的默认顺序, 不能乱改!

# endregion


def get_total_occurance_times_by_keywords(total_qs_ls, search_field_ls, keywords, get_frequence=False, topK=5, rank_field_name=None, rank__gte=None):
    """
    # 关键词次数统计
    - 统计keywords在qs_ls的search_field_ls中是否出现, 以及出现次数.
    - 可以出现次数作为相关性排序依据

    :param total_qs_ls: 用来统计的queryset
    :param search_field_ls: 要匹配的字段
    :param keywords: 用来检索的关键词
    :param topK: 提取关键词的个数
    :param get_frequence: 是否精确计算`keywords`在字段中出现的次数
    :param rank_field_name: annotate出来的排序字段名
    :param rank__gte: 出现次数过滤的最小阈值
    :return: queryset, 且annotate出现次数, 存在`rank_field_name`字段中
    """
    from django.db import models as m
    from django.db.models import functions

    rank_field_name = rank_field_name if rank_field_name else search_rank_field_name
    rank__gte = rank__gte if rank__gte is not None else 1

    if isinstance(keywords, str):
        keywords = extract_keywords(keywords, cut_all=False, topK=topK)

    assert isinstance(keywords, list), 'keywords的类型必须为str或list!'

    search_dc = {}
    occurance_times_ls = []

    for k in range(len(keywords)):
        kw = keywords[k]
        kw_l = len(kw)
        for sf_i in search_field_ls:
            if get_frequence:
                k_name = f'k{k}_{sf_i}_occurance_times'

                # 统计每个`keyword`的出现次数
                dc = {
                    k_name: (functions.Length(sf_i) - functions.Length(
                        functions.Replace(sf_i, m.Value(kw), m.Value('')))) / kw_l
                }
            else:
                k_name = f'k{k}_in_{sf_i}'
                dc = {
                    k_name: m.Exists(total_qs_ls.filter(id=m.OuterRef('id')).filter(**{f'{sf_i}__contains': kw})),   # 判断是否在title中
                }
            occurance_times_ls.append(k_name)
            search_dc.update(dc)
    res_qs_ls: m.QuerySet = total_qs_ls.annotate(**search_dc)

    # show_ls(res_qs_ls.values(*(['id'] + search_field_ls + list(search_dc.keys())))[:3])
    # print(f'--- 检索字段: {search_field_ls}')
    # show_ls(res_qs_ls.values(*(['id'] + list(search_dc.keys())))[:3])

    f_ls = 0
    for i in occurance_times_ls:
        if get_frequence:
            # f_ls += m.F(i)
            f_ls += m.Case(
                m.When(**{f'{i}__isnull': False}, then=m.F(i)),
                default=m.Value(0),
                output_field=m.IntegerField()
            )
        else:
            f_ls += m.Case(
                m.When(**{i: True}, then=m.Value(1)),
                default=0,
                output_field=m.IntegerField()
            )

    # rank_field_name = 'total_occurance_times'
    ret_qs_ls = res_qs_ls.annotate(**{rank_field_name: f_ls})
    ret_qs_ls = ret_qs_ls.filter(**{f'{rank_field_name}__gt': rank__gte}).order_by(*[f'-{rank_field_name}', 'pk'])
    # ret_qsv_ls = ret_qs_ls.values(*['pk', rank_field_name])
    # res_qs_ls.values(rank_field_name)
    ret = ret_qs_ls
    return ret


def get_search_vector(search_conf, config="chinese_zh"):
    vector = None
    for k, v in search_conf.items():
        if vector:
            vector += SearchVector(k, weight=v, config=config)
        else:
            vector = SearchVector(k, weight=v, config=config)
    return vector


def extract_keywords(keywords, cut_all=None, topK=10):
    keywords = _extract_keywords.handle(keywords, cut_all=cut_all, topK=topK)
    return keywords


class SearchQuerySet(QuerySet):
    _weight_conf = None
    _rank__gte = None

    @staticmethod
    def extract_keywords(keywords, cut_all=None):
        return extract_keywords(keywords, cut_all=cut_all)

    @property
    def search_vector_field_name(self):
        global search_vector_field_name
        return search_vector_field_name

    @property
    def search_rank_field_name(self):
        global search_rank_field_name
        return search_rank_field_name

    @property
    def weight_conf(self):
        if self._weight_conf is None:
            if hasattr(self.model, self.search_weight_name) and getattr(self.model, self.search_weight_name):
                self._weight_conf = getattr(self.model, self.search_weight_name)
            else:
                global WEIGHT_CONF
                self._weight_conf = WEIGHT_CONF
        return self._weight_conf

    @property
    def rank__gte(self):
        if self._rank__gte is None:
            if hasattr(self.model, self.search_rank__gte) and getattr(self.model, self.search_rank__gte):
                self._rank__gte = getattr(self.model, self.search_rank__gte)
            else:
                global RANK__GTE
                self._rank__gte = RANK__GTE
        return self._rank__gte

    @property
    def search_rank__gte(self):
        global search_rank__gte
        return search_rank__gte

    @property
    def search_conf_name(self):
        global search_conf_name
        return search_conf_name

    @property
    def search_weight_name(self):
        global search_weight_name
        return search_weight_name

    @property
    def weights_ordering(self):
        global _WEIGHTS_ORDERING
        return _WEIGHTS_ORDERING

    def search(self, keywords, queryset=None, weight_conf=None, cut_all=None, auto_order=True, rank__gte=None, rank_field_name=None):
        """
        综合检索

        :param keywords: 检索关键词
        :param queryset: 基于该queryset进行检索, 默认全部
        :param weight_conf: 权重配置, 为空则使用模型的weight_conf, 模型的weight_conf为空则使用默认的`WEIGHT_CONF`
        :param cut_all: jieba的切词类型, 默认`search`. 取值: {"search": 浏览器检索, True: 全切, False: 简切}.
        :param auto_order: 自动按相关性大小(`search_rank_field_name`对应的值)排序
        :param rank__gte: 最小相关性, 为空则使用模型的对应属性, 模型对应属性为空则使用`RANK__GTE`
        :return: 检索结果的`queryset`
        """

        rank_field_name = rank_field_name if rank_field_name else self.search_rank_field_name

        _keywords = keywords        # 初始`keywords`

        keywords = extract_keywords(keywords, cut_all=cut_all)
        # print(f"*** search ExtractKeywords: {keywords} --- cut_all: {cut_all}")

        query = None
        for kw in keywords:
            tmp = SearchQuery(kw)
            query = tmp if query is None else (query | tmp)

        queryset = queryset if queryset is not None else self
        _queryset = queryset        # 初始`queryset`

        # 实现可以自定义权重的检索(包括前端层面自定义和各个模型层面自定义)
        _weight_conf = weight_conf if weight_conf is not None else self.weight_conf
        if _weight_conf is None:
            queryset = queryset.annotate(**{rank_field_name: SearchRank(F(search_vector_field_name), query)})
        else:
            weights = [_weight_conf.get(w, 0) for w in self.weights_ordering]
            queryset = queryset.annotate(**{rank_field_name: SearchRank(F(search_vector_field_name), query, weights=weights)})

        rank__gte = rank__gte if rank__gte is not None else self.rank__gte
        queryset = queryset.filter(**{search_vector_field_name: query}).filter(**{f'{rank_field_name}__gte': rank__gte})

        if self.model.use_base_orm_search_if_null_res and not queryset.exists():
            search_conf = getattr(self.model, search_conf_name)
            search_field_ls = []

            for k, v in search_conf.items():
                if v in ['A', 'B']:
                    search_field_ls.append(k)

            count = _queryset.count()
            # 看情况使用精确统计频数功能
            get_frequence = True if count < self.model.use_base_orm_search_count__lte else False

            queryset = get_total_occurance_times_by_keywords(
                _queryset,
                search_field_ls,
                keywords=keywords,
                get_frequence=get_frequence,
                rank__gte=1,        # 由于算法不同, 这个的rank代表`匹配词频数`, 取值必须大于1
                rank_field_name=rank_field_name,
            )

        if auto_order:
            queryset = queryset.order_by(f'-{rank_field_name}', 'pk')

        # from bddjango import show_ls, show_json
        # show_json(_weight_conf)
        # show_ls(queryset.values('id', search_rank_field_name')[:5])
        return queryset


class SearchManager(BaseManager.from_queryset(SearchQuerySet)):

    @property
    def search_conf_name(self):
        global search_conf_name
        return search_conf_name

    def with_documents(self):
        assert hasattr(self.model, self.search_conf_name), f'模型{self.model}没有检索字段`{self.search_conf_name}`'
        search_conf = getattr(self.model, self.search_conf_name)
        vector = get_search_vector(search_conf)
        ret = self.get_queryset().annotate(_document=vector)
        return ret


class BaseFullTextSearchModel(models.Model):
    """
    # 全文检索类

    - 用户需要定义检索配置`search_field_conf`.
        * ps: 这个字段修改后得重新migrate数据库, 并admin后台手动更新GIndex.
    - 可选
        - search_weight_conf: 自定义权重配置
        - search_rank__gte: 相关性过滤

    ---

    - eg:

    ```
    search_field_conf = {
        'title': 'A',
        'content': 'B',
    }

    search_weight_conf = {
        'A': 0.9,
        'B': 0.4,
    }

    search_rank__gte = 0.3
    ```
    """
    search_field_conf = None
    search_weight_conf = None
    search_rank__gte = 0.001
    use_base_orm_search_if_null_res = True      # 检索为空时, 启用基础orm检索再检索一遍A和B级别的字段
    use_base_orm_search_count__lte = 100000      # 大于这个数量就关闭精确词频统计功能

    search_vector = SearchVectorField(null=True, blank=True)
    objects = SearchManager()

    @staticmethod
    def extract_keywords(keywords, cut_all=None):
        return extract_keywords(keywords, cut_all=cut_all)

    @property
    def search_vector_field_name(self):
        global search_vector_field_name
        return search_vector_field_name

    @property
    def search_rank_field_name(self):
        global search_rank_field_name
        return search_rank_field_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if 'update_fields' not in kwargs or search_vector_field_name not in kwargs['update_fields']:
            instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            setattr(instance, search_vector_field_name, instance._document)
            instance.save(update_fields=[search_vector_field_name])

    class Meta:
        indexes = [GinIndex(fields=[search_vector_field_name])]
        abstract = True


# region # --- AdminMixin

def rebuild_index(md):
    """
    # admin中用来更新索引

    ## reference:
       - https://juejin.cn/post/6844903480893636616
       - https://cainiaojiaocheng.com/Django/docs/3.2.x/ref/contrib/postgres/search
    """
    print('开始建立索引!', md._meta, md._meta.model_name)
    assert hasattr(md, search_conf_name), f'{md}没有{search_conf_name}字段!'

    search_conf: dict = getattr(md, search_conf_name)
    search_vector = get_search_vector(search_conf)
    md.objects.update(search_vector=search_vector)


class RebuildIndexAdminMixin:
    """
    更新索引AdminMixin
    """

    @admin.action(permissions=['change', 'add'])
    def rebuild_index(self, request, queryset=None, model=None):
        from bdtime import Time
        tt = Time()
        count = self.model.objects.count()
        if count == 0:
            return JsonResponse(data={
                'status': 'error',
                'msg': f'没有数据!'
            })

        rebuild_index(self.model)

        msg = f'成功建立{count}条索引, 耗时: {tt.now(2)}秒.'
        self.message_user(request, msg)

        return JsonResponse(data={
            'status': 'success',
            'msg': f'处理成功! 耗时: {tt.now(2)}秒.'
        })

    rebuild_index.short_description = "更新索引"
    rebuild_index.icon = 'fa fa-spinner'
    rebuild_index.confirm = '确定更新全部索引？'
    rebuild_index.layer = {
        'title': '确定更新全部索引?',
        'tips': '该操作可能比较耗时, 请耐心等候...',
    }


def _get_select_options(select_key, md, none_value_text='全部'):
    assert select_key is not None, '`select_key`不能为空!'

    from bddjango import conv_queryset_to_dc_ls

    qsv_ls = md.objects.distinct(select_key).order_by(select_key).values(select_key)
    option_dc_ls = conv_queryset_to_dc_ls(qsv_ls)

    select_options = []

    if none_value_text:
        none_value_dc = {
            'key': none_value_text,
            'label': none_value_text,
        }
        select_options.append(none_value_dc)

    for option_dc_i in option_dc_ls:
        v = option_dc_i.get(select_key)
        dc = {
            'key': v,
            'label': v,
        }
        select_options.append(dc)

    return select_options


def _get_a_new_test_search_vector_mixin():

    class _TestSearchVectorMixin:
        default_search_keywords = None      # 默认的检索内容, 方便调试
        select_key = None                   # 支持自定义一个过滤字段
        _select_options = None              # 选项

        _none_value_text = '全部'     # 默认搜索`全部`时显示的文本值
        auto_debug = True       # 自动输出debug信息

        add_get_rank_field_to_list_display = True       # 自动增加排序字段
        _tmp_list_display = None

        _self_action_name = 'test_search_vector'

        def get_actions(self, request):
            if self.actions is None:
                self.actions = []
            if self._self_action_name not in self.actions:
                self.actions.append(self._self_action_name)
            ret = super().get_actions(request)
            return ret

        def get_list_display(self, request):
            """
            实现只在调用`test_search_vector`方法时才限时`排序权重`字段
            """
            list_display = super().get_list_display(request)
            _action = request._post.get('_action')
            if _action == self._self_action_name:
                field_to_be_added = 'get_rank'
                if self.add_get_rank_field_to_list_display and field_to_be_added not in list_display:
                    if list_display:
                        list_display = self._tmp_list_display = list_display + [field_to_be_added]
                    else:
                        list_display = [field_to_be_added]
            else:
                if self._tmp_list_display is not None:
                    list_display = self._tmp_list_display
                    self._tmp_list_display = None
            return list_display

        def get_rank(self, obj):
            """
            新方案:　https://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
            """
            rank = None
            field_name = search_rank_field_name
            if hasattr(obj, field_name):
                rank = getattr(obj, field_name)

            if rank:
                ret = round(rank, 3)
            else:
                ret = rank
            return ret

        get_rank.short_description = '排序权重'
        get_rank.allow_tags = True

        @property
        def select_options(self):
            if self._select_options is None:
                if self.select_key is None:
                    return None
                # assert self.select_key, '属性`select_key`不能为空!'
                self._select_options = _get_select_options(self.select_key, self.model, self._none_value_text)
            return self._select_options

        def test_search_vector(self, request, queryset):
            from bddjango import show_ls, show_json
            from bdtime import tt

            tt.__init__()
            query_dc = request.POST

            select_value = query_dc.get(self.select_key)
            if select_value == self._none_value_text:
                select_value = None
            keywords = query_dc.get('keywords', self.default_search_keywords)
            if not keywords:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': '检索关键词`search_keywords`不能为空!'
                })

            kw = BaseFullTextSearchModel.extract_keywords(keywords)

            if select_value:
                qs_ls = self.model.objects.filter(**{self.select_key: select_value})
                qs_ls = self.model.objects.search(keywords=keywords, queryset=qs_ls)
            else:
                qs_ls = self.model.objects.search(keywords=keywords)

            if self.auto_debug:
                try:
                    from bddjango import get_field_names_by_model
                    show_fields = self.list_filter if self.list_filter else get_field_names_by_model(self.model, exclude_fields=[search_vector_field_name])
                    show_ls(qs_ls.values(*(show_fields[:3] + [search_rank_field_name]))[:5])
                except Exception as e:
                    print(f'*** 自动debug信息错误 --- {e}')
                print(f"--- admin ExtractKeywords: {kw}")

            self._ajax_return_qs_ls = qs_ls

            msg_0 = f"处理成功! <br>耗时: {tt.now(3)}秒,<br>返回结果数量: {qs_ls.count()}条.<br>"
            msg_1 = f"""关键词抽取结果: {kw}"""
            msg_all = msg_0 + msg_1
            self.message_user(request, msg_all)
            return JsonResponse(data={
                'status': 'success',
                'msg': msg_0.replace('<br>', ' ')
            })

        test_search_vector.short_description = '综合检索测试'
        test_search_vector.type = 'success'
        test_search_vector.layer = {
            'title': '综合检索',
            'tips': '您好！您可以输入想要咨询的问题，我来为您解答！',
            'params': [
                {
                    # 这里的type 对应el-input的原生input属性，默认为input
                    'type': 'input',
                    # key 对应post参数中的key
                    'key': 'keywords',
                    # 显示的文本
                    'label': '检索条件',
                    # 为空校验，默认为False
                    # 'require': True
                }
            ]
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            select_key_attr_name = 'select_key'
            if hasattr(self, select_key_attr_name) and getattr(self, select_key_attr_name):
                select_key = getattr(self, select_key_attr_name)
                # print(f'--- key: {select_key} --- model: {self.model}')
                dc = {
                    'type': 'select',
                    'key': select_key,
                    'label': '类型',
                    'width': '200px',
                    # size对应elementui的size，取值为：medium / small / mini
                    'size': 'small',
                    # value字段可以指定默认值
                    'value': self._none_value_text,
                    'options': self.select_options,
                }
                # from bddjango import show_ls, show_json
                # show_json(dc)
                self.test_search_vector.layer['params'].insert(0, dc)

    return _TestSearchVectorMixin


class TestSearchVectorMixin:
    """
    # 测试全文检索的mixin

    - 覆写了__init__方法, 必须放在AdminClass的前面!
    - 必须每个class都用一个全新的Mixin, 避免属性共用问题
    """
    @staticmethod
    def get_new():
        # 避免迁移出错
        from .db_utils import judge_db_is_migrating
        if judge_db_is_migrating():
            class _:
                pass
            return _

        return _get_a_new_test_search_vector_mixin()

# endregion



