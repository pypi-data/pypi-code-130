import os, hashlib
from natsort import natsorted
import shutil
import zq_log

# region 文件处理
def file_append(filePath, content, isEnter = False):
    ''' 文件追加 '''
    currDirName = os.path.dirname(filePath)
    if not os.path.exists(currDirName):
        os.makedirs(currDirName)
    fd = os.open(filePath,os.O_RDWR|os.O_APPEND|os.O_CREAT)
    os.write(fd,bytes(content + ('\n' if isEnter else ''), encoding='utf-8'))
    os.close(fd)

def file_write(filePath, content, isEnter = False, isCover=True):
    ''' 文件写入 '''
    currDirName = os.path.dirname(filePath)
    if not os.path.exists(currDirName):
        os.makedirs(currDirName)
    if os.path.exists(filePath) and isCover:
        os.remove(filePath)
    fd = os.open(filePath,os.O_RDWR|os.O_CREAT)
    os.write(fd,bytes(content + ('\n' if isEnter else ''), encoding='utf-8'))
    os.close(fd)

def file_read(filePath, encoding = 'utf-8'):
    ''' 文件读取 '''
    configFs = open(filePath,'r+',encoding = encoding)
    configContent = configFs.read()
    return configContent

def file_exists(filePath):
    ''' 文件是否存在 '''
    return os.path.exists(filePath)

def file_copy(sourceFile, targetFile, isAutodir_create = True):
    ''' 文件复制 '''
    try:
        dirName = os.path.dirname(targetFile)
        if not os.path.exists(dirName) and isAutodir_create:
            os.makedirs(dirName)
        shutil.copyfile(sourceFile, targetFile)
        return True
    except IOError as e:
        zq_log.log_debug('file_copy Error %s'%(str(e)))
        return False

def file_md5(filePath):
    ''' 文件获取MD5 '''
    if not os.path.isfile(filePath):
        return None
    myhash = hashlib.md5()
    f = open(filePath,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def file_sort(fileList):
    ''' 文件排序 '''
    return natsorted(fileList)

def file_get_curr_dir(path):
    ''' 获取文件所在路径 '''
    return os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

def file_size(path):
    ''' 文件大小字节数 '''
    return os.path.getsize(path)

def file_split(path):
    '''
    分割文件路径和文件名和后缀
    :return path, file_name, suffix
    '''
    path, file_name = os.path.split(path)  # 除去文件名以外的path，文件名
    suffix = file_name.split('.')[-1]  # 文件后缀名
    return path, file_name, suffix

#endregion

#region 文件夹操作
def dir_copy(sourceDir, targetDir):
    ''' 文件夹复制 '''
    zq_log.log_debug('当前处理文件夹 %s -> %s' %(sourceDir, targetDir))
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(sourceF):
            #创建目录
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            #文件不存在，或者存在但是大小不同，覆盖
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (file_md5(targetF) != file_md5(sourceF))):
                #2进制文件
                open(targetF, 'wb').write(open(sourceF, 'rb').read())
                zq_log.log_debug (u'%s 复制完毕' %(targetF))
            else:
                zq_log.log_debug (u'%s 已存在，不重复复制' %(targetF))
        if os.path.isdir(sourceF):
            dir_copy(sourceF, targetF)

def dir_get_dirs(dirPath, isCurrDir, excludeList = []):
    ''' 文件夹获取所有文件夹 '''
    dirsTemp = []
    for root, dirs, files in os.walk(dirPath):
        for dir in dirs:
            isAppend = False
            if isCurrDir:
                if root == dirPath:
                    isAppend = True
            else:
                isAppend = True
            if isAppend and not dir in excludeList:
                dirsTemp.append(os.path.join(root, dir))
        if isCurrDir and root == dirPath:
            break
    return dirsTemp

def dir_get_files(dirPath, isCurrDir, excludeList = [], suffix_names = []):
    ''' 文件夹获取所有文件 '''
    filesTemp = []
    for root, dirs, files in os.walk(dirPath):
        for filePath in files:
            isAppend = False
            if isCurrDir:
                if root == dirPath:
                    isAppend = True
            else:
                isAppend = True
            if isAppend and not filePath in excludeList and (len(suffix_names) == 0 or filePath.split('.')[-1] in suffix_names):
                filesTemp.append(os.path.join(root, filePath))
        if isCurrDir and root == dirPath:
            break
    return filesTemp

def dir_auto_create(*dirs):
    ''' 文件夹自动创建 '''
    try:
        for dir in dirs:
            if dir and not os.path.exists(dir):
                os.makedirs(dir)
        return dirs
    except Exception as e:
        zq_log.log_debug('dir_auto_create error: %s'%str(e))
    return None

def dir_auto_create_dir_by_file(*files):
    ''' 文件夹根据文件创建 '''
    try:
        dirs = [os.path.dirname(file) for file in files]
        return dir_auto_create(*dirs)
    except Exception as e:
        zq_log.log_debug('dir_auto_create_dir_by_file error: %s'%str(e))
    return None

def dir_auto_path_merage(*dirs_or_files):
    ''' 文件夹及文件路径合并 '''
    dirs_or_files = [item.replace('\\','/') for item in dirs_or_files]
    for index in range(len(dirs_or_files)):
        if index != len(dirs_or_files)-1:
            if dirs_or_files[index+1].startswith('./'):
                dirs_or_files[index+1] = dirs_or_files[index+1][2:]
            elif dirs_or_files[index+1][1] == ':':
                dirs_or_files[index+1] = dirs_or_files[index+1][3:-1]

            if dirs_or_files[index].endswith('/') and dirs_or_files[index+1].startswith('/'):
                dirs_or_files[index+1] = dirs_or_files[index+1][1:]
            elif not dirs_or_files[index].endswith('/') and not dirs_or_files[index+1].startswith('/'):
                dirs_or_files[index] = '%s/'%dirs_or_files[index]
    return ''.join(dirs_or_files)

def dir_remove(dir_path, contain_parent_dir):
    '''
    删除文件夹
    :param dir_path: 文件夹路径
    :param contain_parent_dir: 是否包含传入的目录一起删除
    '''
    if contain_parent_dir:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            # os.system('rm -rf '%s''%os.path.abspath(dir_path))
    else:
        ls = os.listdir(dir_path)
        for i in ls:
            c_path = os.path.join(dir_path, i)
            if os.path.isdir(c_path):
                dir_remove(c_path, True)
            else:
                os.remove(c_path)
#endregion