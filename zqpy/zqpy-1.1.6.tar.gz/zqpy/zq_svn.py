
import subprocess, os
from xmltodict import parse as xmlParse
import zq_log

class SVN_FILE_STATES:
    Normal = 0  # 000000 正常在svn管理下的最新的文件
    RemoteLocked = 1  # 000001 云端锁定态
    LocalLocked = 2  # 000010 本地锁定态
    Locked = 3  # 000011 已锁定 state and Locked == True
    LocalMod = 4  # 000100 本地有修改需提交
    RemoteMod = 8  # 001000 远程有修改需要更新
    Conflicked = 12  # 001100 冲突 state and Conflicked == Conflicked
    UnVersioned = 16  # 010000 未提交到库
    Error = 32  # 100000 错误状态

def subprocess_popen(args):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo,
        shell=True,
    )
    rst, err = p.communicate()
    try:
        rst = str(rst, 'utf-8')
    except:
        rst = str(rst, 'gbk', errors="-ignore")
    try:
        err = str(err, 'utf-8')
    except:
        err = str(err, 'gbk', errors="-ignore")
    return rst, err

def svn_command_status_xml_sync(path):
    rst, err = subprocess_popen("svn status " + path + " -u --xml")
    if err:
        return None, err
    data = rst
    data = xmlParse(data)
    return data, None

def svn_command_get_all_file_status(rootPath):
    data, info = svn_command_status_xml_sync(rootPath)
    returnDict = {}
    lockRole = ""
    state = SVN_FILE_STATES.Normal
    if info:
        if data is None:
            state = state | SVN_FILE_STATES.UnVersioned
        else:
            state = state | SVN_FILE_STATES.Error
        return returnDict
    target = data["status"]["target"]

    if target and "entry" in target:
        iterList = []
        if not isinstance(target["entry"], list):
            iterList.append(target["entry"])
        else:
            iterList = target["entry"]
        for fileStatusItem in iterList:
            state = SVN_FILE_STATES.Normal
            filePath = fileStatusItem["@path"]
            wc_status = fileStatusItem["wc-status"]
            if "unversioned" == wc_status["@item"]:
                state = state | SVN_FILE_STATES.UnVersioned
            elif "modified" == wc_status["@item"]:
                state = state | SVN_FILE_STATES.LocalMod
            elif "repos-status" in fileStatusItem:
                repos_status = fileStatusItem["repos-status"]
                if "lock" in repos_status and "lock" not in wc_status:
                    info = repos_status["lock"]["owner"]
                    lockRole = info
                    state = state | SVN_FILE_STATES.RemoteLocked
                elif "lock" in wc_status:
                    info = wc_status["lock"]["owner"]
                    lockRole = info
                    state = state | SVN_FILE_STATES.LocalLocked
                elif "modified" == repos_status["@item"]:
                    state = state | SVN_FILE_STATES.RemoteMod
                    info = "%s is modified on remote, you need update first" % filePath
                if "modified" == wc_status["@item"]:
                    state = state | SVN_FILE_STATES.LocalMod
                    info = "%s is modified on local, you need commit first" % filePath
            returnDict[os.path.normcase(filePath)] = [state, info, lockRole]
    return returnDict

def svn_gui_command(command:str, path:list, extCommand:str='', is_wait=True):
    '''
    command: "add"; "commit"; "update"; "revert";log
    '''
    path = [i.replace('\\','/') for i in path]
    all_path = '*'.join(path)
    command_string = "cmd /c tortoiseproc.exe /command:%s /path:\"%s\" %s /closeonend 2"%(command, all_path, extCommand)
    zq_log.log_debug('svn: %s'%command_string)
    if is_wait:
        subprocess.Popen(command_string, stdin=subprocess.PIPE).wait()
    else:
        os.system(command_string)
