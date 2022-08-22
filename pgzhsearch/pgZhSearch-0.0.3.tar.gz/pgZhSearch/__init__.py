try:
    from .base_search import *
except Exception as e:
    print(e)


def version():
    """
    # 更新说明

    - 初始化       # 0.0.1
    - ReadMe出现bug       # 0.0.2
    - 拉取更新. search方法从此支持queryset    # 0.0.3
    """
    return '0.0.3'

