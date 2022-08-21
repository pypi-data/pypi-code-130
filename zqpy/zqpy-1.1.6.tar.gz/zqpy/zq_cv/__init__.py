import os, sys, re
import zq_log

dir_path = os.path.dirname(__file__).replace('\\','/')
dir_name = os.path.basename(dir_path)
for _root, _dirs, _files in os.walk(dir_path):
    sys.path.append(_root)
    imports = []
    # 文件形式引入
    for _file in _files:
        if not _file == '__init__.py' and _file.endswith('.py'):
            _file = _file.replace('.py','')
            imports.append(_file)
    # 文件夹形式引入
    for _dir in _dirs:
        if not _dir in ['__pycache__']:
            imports.append(_dir)

    for item in imports:
        zq_log.log_debug('cv模块下的内容不常用，需要单独引入 -> import zqpy.%s.%s'%(dir_name, item))
        # exec('import %s'%(item))
        # exec('if hasattr(%s, "docs"): %s.docs()'%(item, item))
    break # 只处理当前文件夹
# zq_log.log_debug('Tools下所有模块引入完成')