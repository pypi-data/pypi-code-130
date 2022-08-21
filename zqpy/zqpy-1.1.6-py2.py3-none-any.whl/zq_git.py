import subprocess, os, zq_log

def git_gui_command(command:str, path:list, extCommand:str='', is_wait=True):
    '''
    command: "add"; "commit"; "update"; "revert";log
    '''
    path = [i.replace('\\','/') for i in path]
    all_path = '*'.join(path)
    command_string = "cmd /c TortoiseGitProc.exe /command:%s /path:\"%s\" %s /closeonend 2"%(command, all_path, extCommand)
    zq_log.log_debug('git: %s'%command_string)
    if is_wait:
        subprocess.Popen(command_string, stdin=subprocess.PIPE).wait()
    else:
        os.system(command_string)
