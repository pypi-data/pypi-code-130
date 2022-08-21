name = 'zqpy'
import sys, os

dir_path = os.path.dirname(__file__).replace('\\','/')
dir_name = os.path.basename(dir_path)
for _root, _dirs, _files in os.walk(dir_path):
    sys.path.append(_root)
    imports = []
    # 文件形式引入
    for _file in _files:
        if not _file in ['__init__.py', 'setup.py', 'setup1.py'] and _file.endswith('.py'):
            _file = _file.replace('.py','')
            imports.append(_file)
    # 文件夹形式引入
    for _dir in _dirs:
        if not _dir in ['__pycache__', 'pipy']:
            imports.append(_dir)

    for item in imports:
        print('debug: import %s.%s'%(dir_name, item))
        exec('import %s'%(item))
        # exec('if hasattr(%s, "docs"): %s.docs()'%(item, item))
    break # 只处理当前文件夹
zq_log.log_debug('Modules下所有模块引入完成, 后面整理不常用的类，将import挪动到class类，赋值给self的形式调用，防止不用又在引用')
# class xx():
#     def __init__(self):
#         import time
#         self.time = time
#         print(66)
#     def aaa(self):
#         print(self.time.time())
# xx().aaa()