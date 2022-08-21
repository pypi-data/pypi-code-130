import os, zq_file

_curr_dir, _caches_dir, _configs_dir, _logs_dir, _datas_dir, _cookies_dir, _res_dir, _env_dir, _env_ins_dir, _env_pkg_dir = ('','','','','','','','','','')

def const_set_base_dir(curr_dir):
    '''
    设置修改配置文件存放位置
    '''
    curr_dir = os.path.abspath(curr_dir)
    global _curr_dir, _caches_dir, _configs_dir, _logs_dir, _datas_dir, _cookies_dir, _res_dir, _env_dir, _env_ins_dir, _env_pkg_dir
    _curr_dir = curr_dir
    _caches_dir = '%s/caches'%_curr_dir
    _logs_dir = '%s/logs'%_caches_dir
    _datas_dir = '%s/datas'%_curr_dir
    _configs_dir = '%s/configs'%_datas_dir
    _cookies_dir = '%s/cookies'%_datas_dir
    _res_dir = '%s/res'%_curr_dir
    _env_dir = '%s/env'%curr_dir
    _env_ins_dir = '%s/ins'%_env_dir
    _env_pkg_dir = '%s/pkg'%_env_dir


def const_base_dir():
    ''' 当前项目文件夹 '''
    zq_file.dir_auto_create(_curr_dir)
    return _curr_dir
def const_caches_dir():
    ''' 当前缓存文件夹 '''
    zq_file.dir_auto_create(_caches_dir)
    return _caches_dir
def const_configs_dir():
    ''' 当前配置文件夹 '''
    zq_file.dir_auto_create(_configs_dir)
    return _configs_dir
def const_logs_dir():
    ''' 当前日志文件夹 '''
    zq_file.dir_auto_create(_logs_dir)
    return _logs_dir
def const_datas_dir():
    ''' 当前数据文件夹 '''
    zq_file.dir_auto_create(_datas_dir)
    return _datas_dir
def const_cookies_dir():
    ''' 当前cookies数据文件夹 '''
    zq_file.dir_auto_create(_cookies_dir)
    return _cookies_dir
def const_res_dir():
    ''' 当前资源文件夹 '''
    zq_file.dir_auto_create(_res_dir)
    return _res_dir
def const_env_dir():
    ''' 当前环境文件夹 '''
    zq_file.dir_auto_create(_env_dir)
    return _env_dir
def const_env_ins_dir():
    ''' 当前环境运行文件夹 '''
    zq_file.dir_auto_create(_env_ins_dir)
    return _env_ins_dir
def const_env_pkg_dir():
    ''' 当前环境安装包文件夹 '''
    zq_file.dir_auto_create(_env_pkg_dir)
    return _env_pkg_dir


def const_merage_curr_dir(*path):
    ''' 合并当前文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_base_dir(), *path)
def const_merage_caches_dir(*path):
    ''' 合并缓存文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_caches_dir(), *path)
def const_merage_configs_dir(*path):
    ''' 合并日志文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_configs_dir(), *path)
def const_merage_logs_dir(*path):
    ''' 合并日志文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_logs_dir(), *path)
def const_merage_datas_dir(*path):
    ''' 合并数据文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_datas_dir(), *path)
def const_merage_cookies_dir(*path):
    ''' 合并cookies数据文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_cookies_dir(), *path)
def const_merage_res_dir(*path):
    ''' 合并资源文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_res_dir(), *path)
def const_merage_env_dir(*path):
    ''' 合并环境文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_env_dir(), *path)
def const_merage_env_ins_dir(*path):
    ''' 合并环境运行文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_env_ins_dir(), *path)
def const_merage_env_pkg_dir(*path):
    ''' 合并环境安装包文件夹路径 '''
    return zq_file.dir_auto_path_merage(const_env_pkg_dir(), *path)


const_set_base_dir(os.getcwd())