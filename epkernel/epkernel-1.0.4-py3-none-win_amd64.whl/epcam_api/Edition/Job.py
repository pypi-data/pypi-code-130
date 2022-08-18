import os, sys, json, re
from epcam_api import BASE

def delete_job(job):
    try:
        BASE.job_delete(job)
    except Exception as e:
        print(e)

def create_job(job):
    try:
        if re.search('((?=[\x20-\x7e]+)[^A-Za-z0-9\_\+\-])',job)!=None or job=='eplib':
            return False
        else:
            ret = json.loads(BASE.job_create(job))['status']
            return bool(ret)
    except Exception as e:
        print(e)
        return False
        
def rename_job(src_jobname, dst_jobname):
    try:
        if json.loads(BASE.is_job_open(src_jobname))['paras']['status']== True:
            if re.search('((?=[\x20-\x7e]+)[^A-Za-z0-9\_\+\-])',dst_jobname)!=None or dst_jobname=='eplib':
                return False
            else:
                BASE.job_rename(src_jobname, dst_jobname)
                return True
    except Exception as e:
        print(e)
        return False