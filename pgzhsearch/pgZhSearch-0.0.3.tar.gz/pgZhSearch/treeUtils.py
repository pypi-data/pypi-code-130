"""
树的操作

- 抽象模型: Node
"""

from bddjango.django import get_base_queryset
from django.db.models import F
from django.db import models
from django.db.models import Q, QuerySet
from bddjango import get_base_model
# from django.utils.html import format_html
# from . import models, serializers
# from django.urls import path


class Node(models.Model):
    """节点, 树结构"""
    CODE_LENGTH = 16
    code = models.CharField(max_length=CODE_LENGTH, verbose_name="本节点编码", db_column="本节点编码", default=None, null=True, blank=True, unique=True, db_index=True)
    level = models.IntegerField(verbose_name="节点等级", db_column="节点等级", default=None, null=True, blank=True)
    name = models.CharField(max_length=20, verbose_name="节点名", db_column="节点名", default=None, null=True, blank=True)

    parent_code = models.CharField(max_length=32, verbose_name="父节点编码", db_column="父节点编码", default=None, null=True, blank=True, db_index=True)
    # 从根到本节点的路径. 样例格式"2;5;12;". 设深度为10, 每个节点代码长度为2, 则字段长应为(2+1)*10.
    root_path = models.CharField(max_length=CODE_LENGTH*10, verbose_name="根路径", db_column="根路径", default="", null=True, blank=True)

    brother_ordering = models.IntegerField(verbose_name="兄弟顺序", db_column="兄弟顺序", default=None, null=True, blank=True)
    is_sticky = models.BooleanField(verbose_name="置顶", default=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = "树节点表"
        ordering = ['level', '-is_sticky', 'brother_ordering', 'code']
        db_table = '树节点表'
        abstract = True

    def save(self, *args, **kwargs):
        md = get_base_model(self)
        qs_ls = md.objects.all()

        if self.parent_code == -1:
            """根节点"""
            if qs_ls.filter(parent_code=-1).count():
                print('*** 重复保存!')
                return
            else:
                self.level = 0
                self.root_path = ""
                self.code = self.id = 0
                self.name = self.name or 'root'
                try:
                    ret = super().save(*args, **kwargs)
                except Exception as e:
                    print('--- 根节点保存报错: ', e)
                    ret = None
                return ret

        if self.code is None:
            # 找一个最大的来填充code值
            mx = qs_ls.aggregate(mx=models.Max('code')).get('mx')

            error_flag = False
            try:
                mx = int(mx) + 1
            except Exception as e:
                error_flag = True

            if error_flag or qs_ls.filter(**{'code': mx}).exists():
                mx = qs_ls.aggregate(mx=models.Max('pk')).get('mx') + 1

            self.code = mx
            # self.code = self.id if self.id else get_model_max_id_in_db(self)

        if self.parent_code is None:
            self.parent_code = 0  # 默认一级节点

        if self.parent_code == 0:
            self.root_path = ""

        # is_updating = qs_ls.filter(id=self.id).count()      # 创建 or 更新
        # if is_updating:
        #     pass

        # --- 此处处理兄弟节点之间的排序问题
        if self.brother_ordering is None:
            parent = get_node(qs_ls, self.parent_code)
            from django.db.models import Max, QuerySet
            brothers = get_children(qs_ls, parent)
            mx = brothers.aggregate(mx=Max('brother_ordering')).get('mx')
            if not mx:
                mx = 0
            self.brother_ordering = mx + 1

        try:
            parent: Node = qs_ls.get(code=self.parent_code)
        except:
            raise ValueError(f'没找到节点[{self.code}]的父节点[{self.parent_code}]!')

        self.level = parent.level + 1
        if parent.level:
            """父节点不是根节点的情况"""
            add_0 = "" if parent.root_path is None else parent.root_path
            add_1 = "" if parent.code is None else parent.code
            self.root_path = add_0 + f"{add_1};"
        else:
            self.root_path = ""
        ret = super().save(*args, **kwargs)
        return ret


def get_all(tree):
    """获得所有节点"""
    tree_qs = get_base_queryset(tree)
    return tree_qs


def get_node(tree, code):
    tree_qs = get_base_queryset(tree)
    qs = tree_qs.filter(code=code)
    assert qs.count(), f'没找到code为{code}的数据!'
    qq = qs[0]
    return qq


def get_children(tree, node):
    if isinstance(node, (str, int)):
        code = node
    else:
        code = node.code

    tree_qs = get_base_queryset(tree)
    ret = tree_qs.filter(parent_code=code)
    return ret


def get_brothers(tree, node):
    tree = get_base_queryset(tree)
    parent_code = node.parent_code
    cousins = tree.filter(parent_code=parent_code)
    return cousins


def get_descendants(tree, code, get_all=True, add_self=False):
    if isinstance(code, (str, int)):
        node = get_node(tree, code)
        code = node.code
    else:
        node = code
        code = node.code

    if isinstance(code, (str, int)):
        code = int(code)

    if code == 0:
        return get_base_queryset(tree)

    if get_all:
        # 在整个表里面检索
        tree = get_base_queryset(tree)

    level, name = node.level, node.name

    # 根路径上包含该节点的, 则认为是后继节点
    QS = Q()
    reg = f'^{str(code)}$|^{str(code)};|;{str(code)};'
    QS.add(Q(root_path__iregex=reg), Q.OR)

    if add_self:
        QS.add(Q(code=node.code), Q.OR)

    ret = tree.filter(QS)
    return ret


def is_leaf_node(tree, node):
    count = get_children(tree, node).count()
    if count:
        return False
    else:
        return True


def recurrent_traversal(tree, node, visit, order_type=None):
    """
    层级遍历

    visit: 访问函数
    order_type: 排序字段
    """
    if not node:
        return None

    ret = visit(node)
    children_ls = get_children(tree, node)

    if children_ls.count():
        dc_ls = []

        if order_type:
            children_ls = children_ls.order_by(F(order_type).asc(nulls_first=True))     # 同级排序

        for node in children_ls:
            dc = recurrent_traversal(tree, node, visit, order_type)
            if dc is not None:
                dc_ls.append(dc)
        ret['children_ls'] = dc_ls
    else:
        ret['children_ls'] = []
    return ret


def recurrent_discord(tree, node):
    node_ls = get_descendants(tree, node, add_self=True)
    count = node_ls.count()
    node_ls.delete()
    return count


def get_table_count(table):
    return table.objects.count()

