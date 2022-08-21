import os, sys, re
import json
import time
import psutil
import threading
import subprocess
import zq_const, zq_log, zq_http, zq_cv, zq_file

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
        zq_log.log_debug('import zqpy.%s.%s'%(dir_name, item))
        exec('import %s'%(item))
        # exec('if hasattr(%s, "docs"): %s.docs()'%(item, item))
    break # 只处理当前文件夹
zq_log.log_debug('Tools下所有模块引入完成')


def tools_run_with_reloader(func):
    ''' 利用的flask的重启模块, 让代码在运行时，修改重启 '''
    from werkzeug._reloader import run_with_reloader
    run_with_reloader(func)

def tools_open_dir(*dirs):
    ''' 打开文件夹列表 '''
    for dir in dirs:
        if not os.path.exists(dir) and not 'storage/emulated/' in dir:
            continue
        try:
            os.startfile(dir)
        except BaseException as e:
            zq_log.log_debug('打开: %s  失败：%s'%(dir,str(e)))

def tools_kill_progress(name, key_words_path):
    '''
    杀掉进程
    name: 进程名字
    key_words_path: 进程关键字路径
    '''
    try:
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            if p.name() == name and key_words_path in p.exe():
                os.system('taskkill /F /IM %s'%name)
                zq_log.log_debug('杀进程: %s'%name)
    except Exception as e:
        zq_log.log_debug('杀进程: %s %s  失败：%s'%(name , key_words_path, str(e)))

def tools_async_fun(f):
    ''' 线程运行方法 '''
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
        return thr
    return wrapper

# def tools_auto_install_import():
#     ''' 自动引入安装没有的库 '''
#     from importlib import import_module
#     class AutoInstallClass():
#         _loaded = set()
#         @classmethod
#         def find_spec(cls, name, path, target=None):
#             if path is None and name not in cls._loaded:
#                 cls._loaded.add(name)
#                 zq_log.log_debug("Installing", name)
#                 try:
#                     result = os.system('pip install {}'.format(name))
#                     if result == 0:
#                         return import_module(name)
#                 except Exception as e:
#                     zq_log.log_debug("Failed", e)
#                     return None
#     zq_log.log_debug('引入自动导入库成功')
#     sys.meta_path.append(AutoInstallClass)

def tools_auto_install_import(package):
    """ 不存在库就安装 """
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)

#region AES加密
def tools_encrypt(data:bytes, pwd:bytes):
    ''' aes 加密bytes '''
    dataLen=len(data)
    pwdLen=len(pwd)
    #获取Key
    key=dataLen//pwdLen*pwd+pwd[:dataLen%pwdLen]
    dataList = []
    #进行循环加密
    for i in range(len(key)):
        newByte=key[i]^data[i]
        #写出二进制文件
        dataList.append(newByte)
    data = bytes(dataList)
    return data

def tools_encryptStr(content:str, pwd:str, encode:str='utf8'):
    ''' aes 加密string '''
    data = tools_encrypt(bytes(content,encode), bytes(pwd,encode))
    return str(data, encode)

def tools_encryptFile(sourcePath:str, savePath:str, pwd:str, encode:str='utf8'):
    ''' aes 加密文件 '''
    fs=open(sourcePath,mode='rb')
    data=fs.read()
    fs.close()
    data = tools_encrypt(data, bytes(pwd,encode))
    if savePath:
        fs=open(savePath,mode='wb')
        fs.write(data)
        fs.close()
    return data
#endregion AES加密

#region AES解密
def tools_decrypt(data:bytes, pwd:bytes):
    ''' aes 解密bytes '''
    return tools_encrypt(data, pwd)
    
def tools_decryptStr(content:str, pwd:str, encode:str='utf8'):
    ''' aes 解密string '''
    return tools_encryptStr(content, pwd, encode)
    
def tools_decryptFile(sourcePath:str, savePath:str, pwd:str, encode:str='utf8'):
    ''' aes 解密文件 '''
    return tools_encryptFile(sourcePath, savePath, pwd, encode)
#endregion AES解密

#region 正则相关
def tools_regex_url(content):
    ''' 获取URL  返回数组 '''
    return re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})*/)+', content)

def tools_regex_double_quotation(content):
    ''' 获取"" 中的内容  返回数组 '''
    return re.findall('"(.*)"', content)

def tools_regex_between_content(a, b, content):
    ''' 获取a b 之间的内容  返回数组 '''
    return re.findall('.*%s(.*)%s.*'%(a,b),content)

def tools_regex_ip(content):
    ''' 正则获取IP地址 '''
    return re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', content)

def tools_regex_text(text, lenth):
    ''' 正则截断字符串【按照指定长度】 '''
    textArr = re.findall('.{'+str(lenth)+'}', text)
    textArr.append(text[(len(textArr)*lenth):])
    return textArr

def tools_regex_number(content, start=''):
    '''正则获取数字start后面的数字'''
    return re.findall('%s%s%s'%(r'(?<=',start,r')\d+\.?\d*'), content)

def tools_regex_all_number(content):
    ''' 正则所有的数字 '''
    return re.findall(r'\d+', content)

#endregion

#region zip相关
import zlib, zipfile
# http://api.1473.cn/LearningMaterials/Node/Node_zlib.aspx
# https://www.cnblogs.com/ManyQian/p/9193199.html

# zlib.compress 用来压缩字符串的bytes类型
def tools_zip_str_compress(message):
    '''字符串加密'''
    bytes_message = message.encode()
    return zlib.compress(bytes_message, zlib.Z_BEST_COMPRESSION)
    
def tools_zip_str_decompress(compressed):
    '''字符串解密'''
    return zlib.decompress(compressed)

# zlib.compressobj 用来压缩数据流，用于文件传输 level[1-9]
def tools_zip_file_compress(inputFile, zlibFile, level=9):
    '''文件加密'''
    infile = open(inputFile, 'rb')
    zfile = open(zlibFile, 'wb')
    compressobj = zlib.compressobj(level)   # 压缩对象
    data = infile.read(1024)                # 1024为读取的size参数
    while data:
        zfile.write(compressobj.compress(data))     # 写入压缩数据
        data = infile.read(1024)        # 继续读取文件中的下一个size的内容
    zfile.write(compressobj.flush())    # compressobj.flush()包含剩余压缩输出的字节对象，将剩余的字节内容写入到目标文件中

def tools_zip_file_decompress(zlibFile, endFile):
    '''文件解密'''
    zlibFile = open(zlibFile, 'rb')
    endFile = open(endFile, 'wb')
    decompressobj = zlib.decompressobj()
    data = zlibFile.read(1024)
    while data:
        endFile.write(decompressobj.decompress(data))
        data = zlibFile.read(1024)
    endFile.write(decompressobj.flush())

def tools_zip_collect_file(input_path, result):
    '''
    对目录进行深度优先遍历
    :param input_path:
    :param result:
    :return:
    '''
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            tools_zip_collect_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)

def tools_zip_dir(input_path, output_path, output_name, password=None):
    '''
    压缩文件夹
    :param input_path: 要被压缩的文件夹路径
    :param output_path: 打出得解压包的路径
    :param output_name: 压缩包名称
    :param password: 密码
    :return:
    '''
    zq_log.log_debug('==开始压缩==')
    output_path = zq_file.dir_auto_path_merage(output_path, output_name)
    zipfiles = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    tools_zip_collect_file(input_path, filelists)
    for file in filelists:
        if file != output_path:
            zipfiles.write(file, file.replace(input_path, ''))
    zipfiles.setpassword((password if password else '666666').encode())
    # 调用了close方法才会保证完成压缩
    zipfiles.close()
    zq_log.log_debug('==压缩成功==')
    return output_path

def tools_zip_unzip_dir(output_path, input_path, password):
    '''
    解压缩文件夹
    :param output_path: 解压缩包的路径
    :param input_path: 压缩文件的路径
    :param password: 密码
    :return:
    '''
    zq_log.log_debug('==开始解压==')
    isok = zipfile.is_zipfile(input_path)
    if isok:
        zipfiles=zipfile.ZipFile(input_path,'r')
        zq_log.log_debug(output_path if output_path else os.path.splitext(input_path)[0])
        zipfiles.extractall(os.path.join(output_path if output_path else os.path.splitext(input_path)[0]),pwd=(password if password else '666666').encode())
        zipfiles.close()
        zq_log.log_debug('==解压成功==')
    else:
        zq_log.log_debug('这不是一个正规的zip压缩包')

def tools_zip_file_by_volume(file_path, block_size, del_source_file=False):
    ''''''
    '''
    文件分卷压缩
    :param file_path: 文件路径
    :param block_size: 分卷大小(b) 1M=1*1024*1024
    :param del_source_file: 是否删除源文件
    :return 压缩有路径
    '''
    file_size = zq_file.file_size(file_path)  # 文件字节数
    path, file_name, suffix = zq_file.file_split(file_path)  # 除去文件名以外的path，文件名, 文件后缀名
    # 添加到临时压缩文件
    zip_file = file_path + '.zip'
    with zipfile.ZipFile(zip_file, 'w') as zf:
        zf.write(file_path, arcname=file_name)
    # 小于分卷尺寸则直接返回压缩文件路径
    if file_size > block_size:
        fp = open(zip_file, 'rb')
        count = file_size // block_size + 1
        # 创建分卷压缩文件的保存路径
        save_dir = path + os.sep + file_name + '_split'
        if os.path.exists(save_dir):
            from shutil import rmtree
            rmtree(save_dir)
        os.mkdir(save_dir)
        # 拆分压缩包为分卷文件
        for i in range(1, count + 1):
            _suffix = 'z{:0>2}'.format(i) if i != count else 'zip'
            name = save_dir + os.sep + file_name.replace(str(suffix), _suffix)
            f = open(name, 'wb+')
            f.write(fp.read(block_size))
        fp.close()
        os.remove(zip_file)     # 删除临时的 zip 文件
        zip_file = save_dir
    if del_source_file:
        os.remove(file_path)
    return zip_file


def tools_zip_unzip_file_by_volume(dir_path, del_source_dir=False):
    '''
    合并多个分卷文件
    :param dir_path: 文件路径
    :return 解压后的文件路径
    '''
    if not '_split' in dir_path:
        dir_path = '%s%s'%(dir_path, '_split')
    zippath = dir_path.replace('_split', '')
    zippath_temp = '%s_temp'%zippath
    filenames = zq_file.dir_get_files(dir_path, True)
    filenames = zq_file.file_sort(filenames)
    with open(zippath_temp, 'wb+') as outfile:
        for fname in filenames:
            with open(fname, 'rb') as infile:
                outfile.write(infile.read())
    tools_zip_unzip_dir(os.path.dirname(zippath), zippath_temp, None)
    os.remove(zippath_temp)
    if del_source_dir:
        zq_file.dir_remove(dir_path, True)
    return zippath

#endregion
#region 字符串相关
def tools_string_to_list(strValue, splite):
    ''' 字符串转列表 去头尾空格 '''
    spliteList = strValue.split(splite)
    spliteList = [i.strip() for i in spliteList]
    return spliteList
#endregion


#region selenium 操作

def tools_track(distance):
    """
    根据计算中的滑块 偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 100

    while current < distance:
        if current < mid:
            # 加速度为正1
            a = 10
        else:
            # 加速度为负1
            a = -15
        # 初速度v0
        v0 = v
        # 当前速度v = v0 + at
        v = v0 + a * t
        # 移动距离x = v0t + 1/2 * a * t^2
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    track.append(distance - current)
    return track

def tools_move_to_gap(selenium_tools, slider, bgUrl, itemUrl, scale):
    """
    智能识别并拖动滑动模块
    :param slider: 移动的滑块 selenium
    :param bgUrl: 背景url
    :param itemUrl: 缺口url
    :param scale: 图片和网页真实渲染的比例 如 # itemPath 得到大小是110 实际渲染大小是68
    """
    bgPath = zq_const.const_merage_caches_dir('cv', 'bg.jpg')
    itemPath = zq_const.const_merage_caches_dir('cv', 'item.png')
    outPath = zq_const.const_merage_caches_dir('cv', 'out.jpg')
    zq_http.https.http_download(bgUrl, bgPath, False)
    zq_http.https.http_download(itemUrl, itemPath, False)
    offset = zq_cv.cv_img_contain_img_points_by_cv2(bgPath, itemPath, outPath)
    offset = offset*scale
    tracks = tools_track(offset)
    selenium_tools.web_node_action_chains_drag(slider, tracks)

#endregion

#region 打包相关

# tools_build('./gui/gui.py', ['./douyin_web/dy_web_selenium.py','./douyin_web/dy_video_command.py'], ['./gui/configs/'], ['./caches/configs'],'./gui/caches/build')
def tools_build(main_py, sub_pys:list, source_configs:list, target_configs:list, out_path:str='./caches/dist'):
    '''
    打包管理 Pyinstaller
    :param main_py_name: 主python入口文件名
    :param sub_py_names: 子python文件名
    :param source_configs: 来源配置
    :param target_configs: 复制到的目标配置 代码自动组合 out_path/target_configs
    :param out_path: 打包路径
    '''
    zq_log.log_debug('开始打包...')

    if out_path == './caches/dist':
        out_path = zq_const.const_merage_caches_dir(out_path)
    zq_file.dir_remove('./dist', True)
    zq_file.dir_remove(out_path, True)
    zq_log.log_debug('刪除上次打包结果完成...')
    command = 'Pyinstaller -F %s'%(main_py)
    if sub_pys and len(sub_pys) > 0:
        sub_py_p = ' -p '.join(sub_pys)
        sub_py_imports = [os.path.basename(sub_item).replace('.py', '') for sub_item in sub_pys]
        sub_py_import = ' --hidden-import '.join(sub_py_imports)
        command = '%s -p %s --hidden-import %s'%(command, sub_py_p, sub_py_import)
    zq_log.log_debug(command)
    popen = subprocess.Popen(command)
    popen.wait()
    zq_log.log_debug('打包完成...')
    zq_file.dir_copy('./dist', out_path)
    zq_file.file_copy('./%s.spec'%os.path.basename(main_py).replace('.py',''), '%s/%s.spec'%(out_path, zq_file.file_split(main_py)[1].replace('.py','')))
    zq_log.log_debug('复制exe打包结果完成...')

    zq_file.dir_remove('./build', True)
    zq_file.dir_remove('./dist', True)
    os.remove('./%s.spec'%os.path.basename(main_py).replace('.py',''))
    zq_log.log_debug('刪除多余文件完成...')

    for index in range(len(source_configs)):
        source_item = source_configs[index]
        target_item = target_configs[index]
        if os.listdir(source_item):
            zq_file.dir_copy(source_item, zq_file.dir_auto_path_merage(out_path, target_item))
        else:
            zq_file.file_copy(source_item, zq_file.dir_auto_path_merage(out_path, target_item))
    zq_log.log_debug('复制配置文件完成...')

    zip_pkg_path = zq_file.dir_auto_path_merage(out_path, '/pkg/')
    zq_file.dir_auto_create(zip_pkg_path)
    tools_zip_dir(out_path, zip_pkg_path, 'build.zip')
    zq_log.log_debug('压缩包完成...')

    zq_log.log_debug('全部完成')
#endregion